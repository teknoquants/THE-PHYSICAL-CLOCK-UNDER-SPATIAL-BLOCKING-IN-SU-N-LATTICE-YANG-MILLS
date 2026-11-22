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

"""Match Appendix B to source, then recheck proofs in a fresh pinned Lean project."""
from hashlib import sha256
from pathlib import Path
import json
import re
import shutil
import sys

from common import HERE, execute, require

SUPPLEMENT = ('gap_shift_invariant', 'alias_energy_separation', 'free_phase_enclosure',
              'kernel_group_dependence', 'local_shift_derivative', 'reciprocal_remainder')
AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}


def inventory(project):
    entries = {}
    for line in (project / 'scripts/released.tsv').read_text(encoding='utf-8').splitlines():
        if not line or line.startswith('#'):
            continue
        name, target, level, assumptions = line.split('\t')
        require(name not in entries, 'Duplicate released theorem ' + name)
        entries[name] = {'target': target, 'level': level, 'assumptions': assumptions}
    require(len(entries) == 17, 'Unexpected number of frozen declarations')
    return entries


def reviewed_passages(body):
    result = {}
    segments = re.split(r'^# ', body, flags=re.MULTILINE)
    for section in segments:
        heading, _, remainder = section.partition('\n')
        if re.match(r'^[1-9]\s', heading) or heading.startswith('Appendix A  '):
            require(heading not in result, 'Duplicate section ' + heading)
            result[heading] = sha256(remainder.strip().encode('utf-8')).hexdigest()
    return result


def check_manuscript(project, paper, claimed):
    text = paper.read_text(encoding='utf-8')
    body, appendix = text.split('# Appendix B  Complete Lean development', 1)
    pattern = r'(?m)^\*\*(Theorem|Lemma|Proposition|Corollary|Definition|Conjecture)\s+(\d+\.\d+)\b'
    numbered = [f'{kind} {number}' for kind, number in re.findall(pattern, body)]
    require(len(numbered) == len(set(numbered)) and set(numbered) == set(claimed),
            'Numbered claim inventory differs from the paper: ' + str(sorted(set(numbered) ^ set(claimed))))
    for label in ('Uniform finite-volume hypothesis', 'One-loop dispersion hypothesis', 'Optional shift from Wilson truncation',
                  'Conditional transfer of a gap estimate', 'nonperturbative control', 'strong-coupling endpoint', 'W2d.2', 'W2d.4'):
        require(label.lower() in body.lower(), 'Missing claim or assumption: ' + label)
    pattern = r'^`(W2/[\w./-]+\.lean)`\s*\n```lean\n(.*?)^```[ \t]*$'
    listings = re.findall(pattern, appendix, re.M | re.S)
    require(len(listings) == len(dict(listings)) == 10, 'Ten distinct Appendix B files are required.')
    # Bind the algebra and proof checks to the actual assumptions and proof text of this edition.
    # Bibliography, citation placeholders and the cover can change without altering this binding.
    sections = reviewed_passages(body)
    expected_sections = json.loads((HERE / 'reviewed_sections.json').read_text(encoding='utf-8'))
    require(sections.keys() == expected_sections.keys(), 'Mathematical section inventory changed.')
    for key, digest in sections.items():
        require(digest == expected_sections[key], 'Mathematical text changed and needs review: ' + key)
    declarations = inventory(project)
    # Table 3 supplies not just theorem names but the actual source for each clickable link.
    t3 = body.split('**Table 3.', 1)[1].split('\n\nThe prelude', 1)[0]
    links = re.findall(r'\[`([\w]+)`\]\(#lean-source-(\d+)\)', t3)
    known = {n.rsplit('.', 1)[-1]: n for n in declarations}
    require(len(links) == len(declarations) and {n for n, _ in links} == set(known), 'Table 3 is incomplete or contains a duplicate.')
    for name, position in links:
        require(1 <= int(position) <= len(listings), f'{name} has an invalid Appendix B link.')
        filepath, source = listings[int(position) - 1]
        require('-- W2 PROOF BEGIN ' + known[name] + '\n' in source, f'{name} points to the wrong listing {filepath}')
    for filename, source in listings:
        require((project / filename).read_bytes() == source.encode('utf-8'), 'Paper source differs from project: ' + filename)
    return body, {name: source for name, source in listings}


def audit_records(transcript, expected):
    result = {}
    record = re.compile(r"^'([\w.]+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)$")
    for line in transcript.splitlines():
        if line.startswith('"W2 packet '):
            continue
        match = record.fullmatch(line)
        require(match is not None, 'Unexpected Lean output: ' + line)
        name, axioms = match.groups()
        deps = {a.strip() for a in (axioms or '').split(',') if a.strip()}
        require(name not in result and deps <= AXIOMS, 'Unexpected or duplicate axiom record for ' + name)
        result[name] = sorted(deps)
    require(list(result) == list(expected), 'Incomplete or out-of-order axiom records.')
    return result


def source_proofs(listings):
    """Index the declarations in the ten source listings, including private lemmas."""
    declaration = re.compile(r"^\s*(private\s+)?(?:theorem|lemma)\s+([\w']+)")
    proofs = {}
    for filename, source in listings.items():
        namespace = ''
        for line_number, line in enumerate(source.splitlines(), 1):
            if line.startswith('namespace '):
                namespace = line.split()[1]
            elif line.startswith('end '):
                namespace = ''
            match = declaration.match(line)
            if match:
                name = f'{namespace}.{match[2]}' if namespace else match[2]
                require(name not in proofs, 'Duplicate proof name ' + name)
                proofs[name] = {
                    'source': filename,
                    'line': line_number,
                    'visibility': 'private' if match[1] else 'public',
                }
    return proofs


def audit_all_source_proofs(project, clean, listings, released, final_packet, logs):
    proofs = source_proofs(listings)
    project_sources = {
        file.relative_to(project).as_posix(): file.read_text(encoding='utf-8')
        for file in sorted((project / 'W2').rglob('*.lean'))
    }
    require(proofs == source_proofs(project_sources), 'Appendix B and the active W2 project have different proof inventories.')
    require(len(proofs) == 37 and released.keys() <= proofs.keys(), 'The reviewed Appendix B proof inventory has changed.')
    # The packet already contains all proof terms in one module, including private names.
    # Retain those terms and replace its final print commands with one query per proof.
    terms, marker, _ = final_packet.read_text(encoding='utf-8').partition('#print axioms ')
    require(bool(marker), 'Missing final packet audit commands.')
    commands = ''.join(f'#print axioms {name}\n' for name in proofs)
    instrumented = clean / 'AllPaperProofs.lean'
    instrumented.write_text(terms + commands, encoding='utf-8')
    raw = execute(['lake', 'env', 'lean', '-DwarningAsError=true', instrumented.name],
                  clean, logs / 'all-source-axioms.out')
    # Lean prints private constants under an internal module prefix. Strip only that prefix.
    private_prefix = re.compile(r"^'_private\.[\w.]+?\.\d+\.(W2\.[\w.]+)' ")
    normalized = []
    private_names = set()
    for line in raw.splitlines():
        match = private_prefix.match(line)
        if match:
            name = match[1]
            private_names.add(name)
            line = f"'{name}' " + line[match.end():]
        normalized.append(line)
    require(private_names == {name for name, info in proofs.items() if info['visibility'] == 'private'},
            'Private declarations in the Lean transcript differ from the source inventory.')
    axioms = audit_records('\n'.join(normalized), proofs)
    require(all(axioms[name] == released[name] for name in released), 'Independent audit changed a released dependency.')
    return {
        name: {**where, 'axioms': axioms[name]}
        for name, where in proofs.items() if name not in released
    }


def validate(project, listings, work, logs):
    if shutil.which('lake') is None:
        raise RuntimeError('Lake is unavailable. Install elan for the full check, or select --python-only.')
    clean = work / 'lean-project'
    clean.mkdir()
    for name in ('W2', 'scripts', 'frozen'):
        shutil.copytree(project / name, clean / name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for name in ('W2.lean', 'lean-toolchain', 'lake-manifest.json', 'lakefile.toml', 'LICENSE'):
        shutil.copy2(project / name, clean / name)
    for filename, source in listings.items():
        (clean / filename).write_bytes(source.encode('utf-8'))
    cache = project / '.lake/packages'
    (clean / '.lake').mkdir()
    cached = False
    if (cache / 'mathlib/.lake/build/lib/lean/Mathlib').is_dir():
        try:
            (clean / '.lake/packages').symlink_to(cache.resolve(), target_is_directory=True)
            cached = True
        except OSError:
            pass  # Some Windows configurations disallow directory symlinks.
    if not cached:
        execute(['lake', 'exe', 'cache', 'get'], clean, logs / 'lake-cache.log')
    execute([sys.executable, 'scripts/replay.py'], clean, logs / 'lean-replay.log')
    execute([sys.executable, 'scripts/test_packet.py'], clean, logs / 'packet-regressions.log')
    record = Path('records/w2ar-v1')
    output = (clean / record / 'final.local.out').read_bytes()
    require(output == (clean / record / 'isolated-final.out').read_bytes(), 'Isolated Lean output differs from fresh packet output.')
    require(output == (project / record / 'final.local.out').read_bytes(), 'Fresh Lean output differs from the archived release.')
    for name in ('prelude', 'Trig', 'Constants', 'TimeUnit', 'Matching', 'Drift', 'Clock', 'Threshold', 'W2aR_final'):
        for suffix in ('.lean', '.txt'):
            filename = Path('packets') / (name + suffix)
            require((clean / filename).read_bytes() == (project / filename).read_bytes(), 'Reconstructed packet differs: ' + str(filename))
        if name not in ('prelude', 'W2aR_final'):
            returned = Path('returns') / (name + '.lean')
            require((project / returned).read_bytes() == (clean / returned).read_bytes(), 'Archived return differs: ' + name)
    released = audit_records(output.decode(), inventory(project))
    (logs / 'released-axioms.out').write_bytes(output)
    shutil.copyfile(clean / record / 'checks.out', logs / 'packet-checks.out')
    shutil.copyfile(clean / record / 'toolchain.out', logs / 'toolchain.out')
    extra = HERE / 'SupplementalProofs.lean'
    source = extra.read_text(encoding='utf-8')
    require(re.search(r'\b(sorry|sorryAx|admit|axiom)\b', source) is None, 'Supplement contains an unproved axiom or placeholder.')
    # Ignore all saved proof outputs. Ask a new Lean process to typecheck the additional proof terms.
    shutil.copyfile(extra, clean / 'SupplementalProofs.lean')
    raw = execute(['lake', 'env', 'lean', '-DwarningAsError=true', 'SupplementalProofs.lean'], clean, logs / 'supplemental-axioms.out')
    supplemental = audit_records(raw, ['W2.PaperValidation.' + n for n in SUPPLEMENT])
    supporting = audit_all_source_proofs(project, clean, listings, released, clean / record / 'final.lean', logs)
    descriptions = inventory(project)
    for name in descriptions:
        descriptions[name]['axioms'] = released[name]
    return {'released': descriptions, 'supporting': supporting, 'supplemental': supplemental,
            'raw_output_sha256': sha256(output).hexdigest(), 'final_packet_sha256': sha256((clean / record / 'final.lean').read_bytes()).hexdigest()}
