#!/usr/bin/env python3
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

"""Check the prelude, Trig, the statement freeze, six module returns and the final packet."""
import shutil
import subprocess
import sys
from pathlib import Path

from packet import (ROOT, BASE, MODULES, FINAL, PRELUDE, TRIG_PATH, ensure, make,
                    run_lean_bytes)

RECORD = ROOT/'records/w2ar-v1'
PACKETS = ROOT/'packets'


def execute(command, log=None):
    cmd = [str(x) for x in command]
    proc = subprocess.run(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if log is not None:
        (RECORD/log).write_bytes(proc.stdout)
    output = proc.stdout.decode('utf-8')
    if proc.returncode:
        raise SystemExit(output)
    return output


def verify_return(retained, candidate, transcript):
    transcript.write_bytes(run_lean_bytes(candidate))
    verdict = execute([sys.executable, 'scripts/check_return.py', retained, candidate, transcript]).strip()
    print(verdict, flush=True)
    return verdict


def fill_module(module):
    filename = Path(module).name
    candidate = ROOT/'returns'/filename
    candidate.parent.mkdir(exist_ok=True)
    candidate.write_bytes(make(module, filled=True).encode('utf-8'))
    verdict = verify_return(PACKETS/filename, candidate, candidate.with_suffix('.out'))
    ensure((ROOT/'extracted'/module).read_bytes() == (ROOT/module).read_bytes(),
           'Extracted module differs: '+module)
    return verdict


def main():
    RECORD.mkdir(parents=True, exist_ok=True)
    version = execute(['lake', 'env', 'lean', '--version'])
    ensure('version 4.36.0,' in version, 'Lean 4.36.0 is required.')
    (RECORD/'toolchain.out').write_bytes((version+execute(['lake', '--version'])).encode('utf-8'))

    execute([sys.executable, 'scripts/make_packet.py', '--prelude'])
    prelude = PACKETS/(PRELUDE+'.lean')
    lines = [verify_return(prelude, prelude, RECORD/'prelude.out')]

    execute([sys.executable, 'scripts/make_packet.py', TRIG_PATH, '--unit', 'W2aR'])
    lines.append(fill_module(TRIG_PATH))
    execute(['lake', 'build', *[s[:-5].replace('/', '.') for s in BASE]], 'prerequisites.out')

    execute([sys.executable, 'scripts/review_packet.py'], 'statements.sha256')
    (RECORD/'review.out').write_bytes(run_lean_bytes(ROOT/'frozen/W2aR_review_final.lean'))
    # Retain all six templates before serializing any of the six proof returns.
    for module in MODULES:
        execute([sys.executable, 'scripts/make_packet.py', module, '--unit', 'W2aR'])
    for module in MODULES:
        lines.append(fill_module(module))
    execute(['lake', 'build', *[s[:-5].replace('/', '.') for s in MODULES]], 'modules.out')

    execute([sys.executable, 'scripts/make_packet.py', '--final', 'W2aR'])
    final = RECORD/'final.lean'
    shutil.copyfile(PACKETS/(FINAL+'.lean'), final)
    local = RECORD/'final.local.out'
    lines.append(verify_return(PACKETS/(FINAL+'.lean'), final, local))
    lines.append(execute([sys.executable, 'scripts/axiom_audit.py', local, '--file', final,
                          '--report', RECORD/'lean_report.md']).strip())
    lines.append(execute([sys.executable, 'scripts/isolated_check.py'], 'isolated-check.out').strip())
    execute(['lake', 'build'], 'build.out')
    (RECORD/'checks.out').write_bytes(('\n'.join(lines)+'\n').encode('utf-8'))
    print('\n'.join(lines[-2:]))


if __name__ == '__main__':
    main()
