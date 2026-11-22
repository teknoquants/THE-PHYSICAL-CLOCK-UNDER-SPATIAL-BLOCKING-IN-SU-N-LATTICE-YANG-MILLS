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

"""Compare a return with the retained packet, rerun Lean, audit, and extract."""
import argparse
from pathlib import Path
from packet import ROOT, FINAL, PRELUDE, verify_source, audit_stdout, run_lean_bytes, substitute, ensure, error_exit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('retained','candidate','transcript'):
        parser.add_argument(key, type=Path)
    args = parser.parse_args()
    retained = args.retained.read_bytes().decode()
    source = args.candidate.read_bytes().decode()
    meta, proofs = verify_source(retained, source)
    actual = run_lean_bytes(args.candidate)
    ensure(args.transcript.read_bytes() == actual, 'Submitted output differs from a fresh local Lean run.')
    audit = audit_stdout(actual.decode('utf-8'), source)
    if meta['module']:
        path = Path(meta['module'])
        output = ROOT/'extracted'/path
        output.parent.mkdir(exist_ok=True, parents=True)
        module = (ROOT/path).read_text()
        output.write_text(substitute(module, {k:proofs[k] for k in meta['editable']}))
    label = meta['module'] or (PRELUDE if meta['mode'] == 'prelude' else FINAL)
    noun = 'record' if len(audit) == 1 else 'records'
    print(f'CHECK PASSED | {label} | {len(audit)} axiom {noun}')


if __name__ == '__main__':
    error_exit(main)
