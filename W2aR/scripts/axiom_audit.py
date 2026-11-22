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

"""Replay and audit the complete check-only packet with its retained statements."""
import argparse
from pathlib import Path
from tempfile import TemporaryDirectory
from packet import (ROOT, FINAL, make, inventory, verify_source, audit_stdout, run_lean_bytes,
                    digest, ensure, error_exit)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', nargs='?', type=Path, help='saved Lean output to compare with replay')
    parser.add_argument('--file', type=Path, help='final check-only Lean source')
    parser.add_argument('--report', type=Path, default=ROOT/'lean_report.md')
    parser.add_argument('--parse', type=Path, help='audit a saved output only; labeled as offline parsing')
    parser.add_argument('--record-hosted', action='store_true',
                        help='save the supplied hosted transcript byte for byte before running the audit')
    args = parser.parse_args()
    ensure(not (args.parse and args.output), 'Choose one transcript.')
    ensure(not args.record_hosted or args.output is not None, '--record-hosted requires the actual hosted output file.')
    submitted = args.output.read_bytes() if args.output else None
    if args.record_hosted:
        dest = ROOT/'records/w2ar-v1/final.out'
        dest.parent.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(dir=dest.parent) as tmp:
            staged = Path(tmp)/'final.out'
            staged.write_bytes(submitted)
            staged.replace(dest)
    source = make()
    file = args.file or ROOT/'packets'/(FINAL+'.lean')
    if not args.file and not file.exists():
        file.parent.mkdir(exist_ok=True)
        file.write_text(source)
    given = file.read_bytes().decode()
    verify_source(source, given)
    raw = args.parse.read_bytes() if args.parse else run_lean_bytes(file)
    if submitted is not None:
        ensure(submitted == raw, 'Final transcript differs from the fresh Lean run.')
    output = raw.decode('utf-8')
    results = audit_stdout(output, given)
    rows = inventory()
    n1 = sum(r[2]=='L1' for r in rows)
    report = ['# W2a-R · machine-checked declarations', '',
              f'{len(rows)} declarations passed the axiom audit ({n1} L1 and {len(rows)-n1} L2).',
              'L1 denotes a proved mathematical implication. L2 names the physical or trajectory input supplied to that implication.', '',
              '| Declaration | Target | Code | Hypotheses beyond the stated mathematical inequalities | Axioms |',
              '|---|---|---|---|---|']
    for name,label,code,hyp in rows:
        deps = ', '.join(sorted(results[name])) or 'none'
        report.append(f'| `{name}` | {label} | {code} | {hyp} | {deps} |')
    report += ['',f'Packet SHA-256 `{digest(given)}`.',
               f'Raw output SHA-256 `{digest(output)}`.',
               'Verification used '+('offline transcript parsing.' if args.parse else 'a fresh Lean 4.36.0 process.')]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text('\n'.join(report)+'\n')
    if not args.output and not args.parse:
        (ROOT/'axiom_audit.log').write_bytes(raw)
    print(f'AUDIT PASSED | {len(rows)} declarations | {n1} L1 | {len(rows)-n1} L2')


if __name__ == '__main__':
    error_exit(main)
