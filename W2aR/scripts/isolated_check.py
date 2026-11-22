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

"""Check the self-contained final file with dependencies only, in an empty directory."""
import os
import subprocess
import tempfile
from pathlib import Path
from packet import ROOT, make, verify_source, audit_stdout, ensure


def environment_value(*args):
    return subprocess.check_output(['lake','env',*args], cwd=ROOT, text=True).strip()


def main():
    record = ROOT/'records/w2ar-v1'
    source = record/'final.lean'
    text = source.read_bytes().decode('utf-8')
    verify_source(make(), text)
    prefix = Path(environment_value('lean','--print-prefix'))
    packages = (ROOT/'.lake/packages').resolve()
    entries = [(ROOT/p).resolve() for p in environment_value('printenv','LEAN_PATH').split(os.pathsep) if p]
    deps = [str(p) for p in entries if p.is_relative_to(packages)]
    ensure(deps, 'No dependency libraries found.')
    env = os.environ.copy()
    env['LEAN_PATH'] = os.pathsep.join(deps)
    with tempfile.TemporaryDirectory(dir=ROOT/'.lake') as work:
        candidate = Path(work)/'Final.lean'
        candidate.write_bytes(source.read_bytes())
        proc = subprocess.run([prefix/'bin/lean',candidate.name],cwd=work,env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    expected = (record/'final.local.out').read_bytes()
    ensure(proc.returncode == 0 and proc.stdout == expected,
           'Isolated replay differs from the release transcript:\n'+proc.stdout.decode('utf-8'))
    result = audit_stdout(proc.stdout.decode('utf-8'),text)
    (record/'isolated-final.out').write_bytes(proc.stdout)
    print(f'ISOLATED CHECK PASSED | {len(result)} declarations | project W2 libraries excluded')


if __name__ == '__main__':
    main()
