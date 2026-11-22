# SPDX-License-Identifier: MIT
# MIT License
#
# Copyright (c) 2026 Roger Cooperman; A.E. Petrunina V.V.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Common definitions for W2a-R statement freezes and self-contained Lean packets."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

import review_packet

ROOT = review_packet.ROOT
BASE = review_packet.PATHS[:3]
MODULES = review_packet.PATHS[3:]
HELPER = 'W2/W2aR/Estimates.lean'
TRIG_PATH = 'W2/Common/Trig.lean'
TRIG = 'W2.Common.free_clock_sinc_bounds'
PRELUDE = 'prelude'
FINAL = 'W2aR_final'
LEGACY_FINAL = 'W2aR-final'
ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}
FILL = '  sorry\n'
START = '-- W2 PROOF BEGIN '
END = '-- W2 PROOF END '
SLOTS = re.compile(r'^-- W2 PROOF BEGIN ([\w.]+)\n(.*?)^-- W2 PROOF END \1\n', re.S | re.M)


def ensure(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def check_review():
    review_packet.check_original_review()
    built = review_packet.assemble()
    saved = (ROOT / 'frozen/W2aR_review_final.lean').read_bytes()
    ensure(hashlib.sha256(saved).hexdigest() == review_packet.EXPECTED,
           'Retained mathematical checkpoint digest mismatch.')
    ensure(built.encode() == saved, 'A frozen definition, import, quantifier or target changed.')


def slots(source):
    matches = list(SLOTS.finditer(source))
    names = [m[1] for m in matches]
    ensure(len(names) == len(set(names)) == source.count(START) == source.count(END),
           'Duplicate, missing or malformed proof boundaries.')
    return {m[1]: m[2] for m in matches}


def substitute(source, replacements):
    def edit(m):
        return START+m[1]+'\n'+replacements.get(m[1], m[2])+END+m[1]+'\n'
    return SLOTS.sub(edit, source)


def inventory():
    rows = []
    for line in (ROOT / 'scripts/released.tsv').read_text().splitlines():
        if line and not line.startswith('#'):
            name, label, code, hypotheses = line.split('\t')
            ensure(code in {'L1','L2'} and (code != 'L2' or hypotheses != '-'), 'Invalid release inventory.')
            rows.append((name, label, code, hypotheses))
    ensure(len({r[0] for r in rows}) == len(rows) and rows, 'Empty or duplicate release inventory.')
    return rows


def section(path):
    source = review_packet.module_body(path)
    imports = [line.split('import ',1)[1] for line in source.splitlines()
               if line.startswith(('import ', 'public import '))]
    lines = [line for line in source.splitlines()
             if not line.startswith(('import ', 'public import '))
             and line.strip() not in ('module', '@[expose] public section',
                                       '-- W2 PROOF IMPORTS', '-- W2 END IMPORTS')]
    return imports, f'-- W2 MODULE BEGIN {path}\n'+'\n'.join(lines).strip()+f'\n-- W2 MODULE END {path}\n'


def metadata(source):
    head = source.splitlines()[0]
    ensure(head.startswith('-- W2-PACKET '), 'Missing packet metadata.')
    return json.loads(head.removeprefix('-- W2-PACKET '))


def make(module=None, *, filled=False, prelude=False):
    """Assemble early prerequisites independently of the six-module statement freeze."""
    ensure(not (prelude and module is not None), 'A prelude packet takes no module.')
    ensure(module is None or module in [TRIG_PATH, *MODULES], 'Unrecognized W2a-R module.')

    if prelude:
        paths = BASE[:2]
        declaration = re.compile(r'^(?:noncomputable )?(?:abbrev|def|structure) ([\w.]+)', re.M)
        audit = ['W2.Common.' + name for path in paths
                 for name in declaration.findall((ROOT / path).read_text())]
        ensure(audit and len(audit) == len(set(audit)), 'Empty or duplicate prelude inventory.')
        edit = []
        checks = ''.join('#check ' + name + '\n' for name in audit)
        mode = 'prelude'
    elif module == TRIG_PATH:
        paths = BASE
        ensure(set(slots((ROOT / module).read_text())) == {TRIG}, 'Shared Trig proof slot changed.')
        audit = [TRIG]
        edit = [TRIG]
        checks = '#check ' + TRIG + '\n'
        mode = 'fill'
    else:
        check_review()
        targets = MODULES if module is None else [module]
        paths = [*BASE, HELPER, *targets]
        proven = {name for path in targets for name in slots((ROOT / path).read_text())}
        released = [row[0] for row in inventory()]
        audit = [name for name in released if name in proven or name == TRIG]
        ensure(set(audit) == proven | {TRIG}, 'Unregistered or missing declarations.')
        if module is None:
            ensure(audit == released, 'Release inventory and all proof slots disagree.')
        edit = [name for name in audit if module and name != TRIG]
        checks = ''.join(f'example : {name}.statement := {name}\n' for name in audit if name != TRIG)
        mode = 'fill' if module else 'check'

    imports, sections = [], []
    for path in paths:
        mods, body = section(path)
        imports.extend(m for m in mods if not m.startswith('W2.') and m not in imports)
        sections.append(body)
    meta = dict(format=2, unit='W2aR', module=module, mode=mode,
                editable=edit, audit=audit, review=review_packet.EXPECTED)
    text = '-- W2-PACKET '+json.dumps(meta,sort_keys=True,separators=(',',':'))+'\n'+review_packet.LICENSE_HEADER+'module\n\n'
    text += ''.join('public import '+m+'\n' for m in imports)+'\n@[expose] public section\n\n'
    text += '\n'.join(sections)
    text += '\n'+checks
    text += ''.join('#print axioms '+n+'\n' for n in audit)
    frozen = substitute(text, dict.fromkeys(edit, FILL))
    stamp = digest(frozen)
    return (text if filled or module is None else frozen)+f'#eval "W2 packet {stamp}"\n'


def verify_source(retained, candidate):
    meta = metadata(retained)
    expected = make(meta['module'], prelude=meta['mode'] == 'prelude')
    ensure(retained == expected, 'Retained packet disagrees with the verified checkout.')
    allowed = meta['editable']
    original, returned = slots(retained), slots(candidate)
    ensure(original.keys() == returned.keys(), 'Proof slot names changed.')
    ensure(substitute(candidate, {k:original[k] for k in allowed}) == retained,
           'Return changed frozen text outside an editable proof.')
    for k in allowed:
        body = returned[k]
        ensure(body.strip() and all(not line.strip() or line.startswith('  ') for line in body.splitlines()),
               'Each proof must be an indented tactic body: '+k)
    ensure(not re.search(r'\b(sorry|admit|sorryAx)\b', candidate), 'Unresolved proof placeholder.')
    return meta, returned


def run_lean_bytes(file):
    proc = subprocess.run(['lake', 'env', 'lean', str(file.resolve())], cwd=ROOT,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ensure(proc.returncode == 0, 'Lean rejected the file:\n'+proc.stdout.decode('utf-8', errors='replace'))
    return proc.stdout


def run_lean(file):
    return run_lean_bytes(file).decode('utf-8')


def audit_stdout(output, source):
    meta = metadata(source)
    stamp = re.search(r'^#eval "(W2 packet [a-f0-9]{64})"\n\Z',source,re.M)
    ensure(stamp and output.splitlines()[-1:] == ['"'+stamp[1]+'"'], 'Missing terminal packet stamp.')
    result = {}
    pattern = r"^'([\w.]+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)$"
    for m in re.finditer(pattern, output, re.M):
        name = m[1]
        ensure(name not in result, 'Duplicate axiom record: '+name)
        deps = {a.strip() for a in (m[2] or '').split(',') if a.strip()}
        ensure(deps <= ALLOWED, f'{name} uses disallowed axioms {deps-ALLOWED}')
        result[name] = deps
    ensure(list(result) == meta['audit'], 'Missing, unexpected or out-of-order axiom records.')
    return result


def error_exit(action):
    try:
        action()
    except (ValueError, KeyError, OSError, IndexError) as e:
        raise SystemExit('CHECK FAILED: '+str(e))
