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

"""Shared paths and fail-closed checks for the W2a-R paper validators."""
from pathlib import Path
import csv
import math
import os
import subprocess

HERE = Path(__file__).resolve().parent


def require(condition, explanation):
    if not condition:
        raise ValueError(explanation)


def project_root():
    for path in (HERE.parent, HERE.parent / 'W2aR', HERE / 'W2aR'):
        if (path / 'lean-toolchain').is_file() and (path / 'scripts/released.tsv').is_file():
            return path
    raise FileNotFoundError('Extract the whole ZIP. The W2aR Lean project is required by this suite.')


def execute(command, cwd, log):
    env = os.environ.copy()
    env.pop('PYTHONOPTIMIZE', None)  # The legacy numerical programs include executable assertions.
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    with log.open('wb') as output:
        process = subprocess.run(command, cwd=cwd, env=env, stdout=output, stderr=subprocess.STDOUT)
    if process.returncode:
        tail = '\n'.join(log.read_text(encoding='utf-8', errors='replace').splitlines()[-7:])
        raise RuntimeError(f'{Path(str(command[0])).name} exited {process.returncode}. {log.name}\n{tail}')
    return log.read_text(encoding='utf-8')


def compare_csvs(published, generated):
    expected = {p.name for p in published.glob('*.csv')}
    actual = {p.name for p in generated.glob('*.csv')}
    require(expected == actual and len(actual) == 6, 'All six numerical tables must be regenerated.')
    for name in sorted(expected):
        with (published / name).open() as original, (generated / name).open() as fresh:
            a, b = csv.DictReader(original), csv.DictReader(fresh)
            require(a.fieldnames == b.fieldnames, f'{name}: wrong columns')
            pairs = list(zip(a, b, strict=True))
            require(bool(pairs), f'{name}: empty table')
            for i, (before, after) in enumerate(pairs, 1):
                for key, old in before.items():
                    new = after[key]
                    if old == new:
                        continue
                    if key in {'N', 'K', 'L', 'direction', 'order', 'within_published_pair_rounding'}:
                        raise ValueError(f'{name} row {i}: changed {key}')
                    # Allow floating-point implementation differences, including tiny roundoff diagnostics.
                    require(math.isclose(float(old), float(new), rel_tol=3e-10, abs_tol=4e-14), f'{name} row {i}: changed {key} ({old} versus {new})')
