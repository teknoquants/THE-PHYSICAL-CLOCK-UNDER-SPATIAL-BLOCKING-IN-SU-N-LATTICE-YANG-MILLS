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

"""Symbolic Wilson-kernel reductions and independent checks of the reported numbers."""
from decimal import Decimal
from itertools import product
import csv
import re

import sympy as sp

from common import require


def group_dependence(data):
    n, i1, i2, i3, i4 = sp.symbols('N I1 I2 I3 I4', nonzero=True)
    electric = i2 / 144
    magnetic = (1 - 1 / n**2) * i1 / 24 - 5 * i2 / 288 + i3 / 48 + i4 / 128
    substituted = (-4 * n * (magnetic - electric)).subs({i3: i2 / 3 - i1 / 6, i4: 4 * i2 - 8 * i1 / 3})
    target = -(5 * i1 + 4 * i2) * n / 72 + i1 / (6 * n)
    require(sp.expand(substituted - target) == 0, 'electric/magnetic signs, normalization and group reduction')
    # Verify the differential identity before taking the symmetric angular averages.
    u = sp.symbols('u', real=True)
    transverse = sp.symbols('transverse', positive=True)
    radius = sp.sqrt(sp.sin(u)**2 + transverse)
    primitive = sp.sin(2 * u) / radius
    derivative = 2 * (1 - 2 * sp.sin(u)**2) / radius - sp.sin(2 * u)**2 / (2 * radius**3)
    require(sp.trigsimp(sp.diff(primitive, u) - derivative) == 0, 'angular derivative before integration by parts')
    require(primitive.subs(u, 0) == 0 and primitive.subs(u, sp.pi / 2) == 0, 'both angular boundary terms')
    # After the integration by parts: 0 = 2 I2 - 4 I1/3 - I4/2.
    require(sp.solve(2 * i2 - 4 * i1 / 3 - i4 / 2, i4) == [4 * i2 - 8 * i1 / 3], 'integration-by-parts coefficient')
    # b⁴ and sin²(2u) give I1 = 3 J + 6 I3 and I4 = 4(I2/3−J).
    j = sp.symbols('J')
    moment = sp.solve([i1 - 3 * j - 6 * i3, i4 - 4 * (i2 / 3 - j), i4 - 4 * i2 + 8 * i1 / 3], (i3, i4, j))
    require(sp.simplify(moment[i3] - (i2 / 3 - i1 / 6)) == 0, 'permutation-symmetric moment reduction')
    with (data / 'hamiltonian_quadrature.csv').open() as f:
        rows = list(csv.DictReader(f))
    require({int(r['order']) for r in rows} >= {20, 32, 48}, 'spatial orders')
    for r in rows:
        if int(r['order']) < 20:
            continue
        a, b, c, d = (float(r[k]) for k in ('I1', 'I2', 'I3', 'I4'))
        require(abs(c - b / 3 + a / 6) < 1e-10 and abs(d - 4 * b + 8 * a / 3) < 1e-10, 'integral identities in the direct quadrature')
    return 'Reduced the Wilson kernel for general N; verified the two moment identities against the independent spatial moments at orders 20, 32 and 48.'


def coefficients(data):
    with (data / 'coefficients.csv').open() as f:
        rows = list(csv.DictReader(f))
    require([int(r['N']) for r in rows] == [2, 3], 'SU(2) and SU(3) coverage')
    published = {2: (Decimal('0.09958'), Decimal('-0.06798')), 3: (Decimal('0.18018'), Decimal('-0.15405'))}
    residuals = []
    for row in rows:
        n = int(row['N'])
        cs, ct = published[n]
        require(Decimal(row['karsch_csigma']) == cs and Decimal(row['karsch_ctau']) == ct, 'published inputs')
        ref = float(ct - cs)
        numeric = float(row['c1'])
        residual = abs(numeric - ref)
        require(abs(numeric - float(row['bessel_c1'])) < 2e-12, 'spatial versus Bessel quadrature')
        require(abs(residual - float(row['abs_difference'])) < 1e-14, 'residual against printed pair')
        require(residual > 1e-5 and row['within_published_pair_rounding'] == 'False', 'published rounding diagnostic')
        residuals.append(f'SU({n}) {residual:.8g}')
    return 'Both quadratures agree within 2×10⁻¹². Absolute printed-pair residuals: ' + ', '.join(residuals) + '. Both exceed 10⁻⁵.'


def local_shift_values():
    # Distinct candidate pairs can satisfy exactly the same coefficient identity.
    for e, b in product([sp.Rational(-1, 4), sp.Rational(1, 3)], [sp.Rational(0), sp.Rational(1, 2)]):
        delta = (b - e) / 2
        require((e - b) / 2 == -delta, 'coefficient convention')
    return 'Distinct choices satisfy the same identity. The optional group-specific shift is unevaluated in this paper.'


def table_rows(paper, label):
    piece = paper.split('**Table ' + label + '.', 1)
    require(len(piece) == 2, 'missing manuscript table ' + label)
    grid = re.search(r'(?m)^\|[^\n]*\n(?:\|[^\n]*\n)+', piece[1])
    require(grid is not None, 'missing table cells ' + label)
    return [[v.strip() for v in line.strip().strip('|').split('|')] for line in grid.group().strip().splitlines()]


def number(cell):
    cell = cell.replace('−', '-').strip('$')
    cell = re.sub(r'\\times10\^\{(-?\d+)\}', r'e\1', cell)
    return Decimal(cell)


def printed(cell, actual):
    value = number(cell)
    quant = Decimal(1).scaleb(value.as_tuple().exponent)
    require(abs(value - Decimal(str(actual))) <= abs(quant) / 2 + Decimal('2e-15'), f'printed {cell} versus recomputed {actual}')


def published_tables(data, paper):
    def read(name):
        with (data / name).open() as file:
            return list(csv.DictReader(file))
    groups = read('coefficients.csv')
    t1 = table_rows(paper, '1')
    t2 = table_rows(paper, '2')
    require(len(t1) == 8 and len(t2) == 4 and t1[0][1:] == ['SU(2)', 'SU(3)'], 'coefficient table dimensions')
    keys = ['c1', 'bessel_c1', 'karsch_csigma', 'karsch_ctau', 'karsch_B2', 'abs_difference']
    for r, k in zip(t1[2:], keys, strict=True):
        for cell, group in zip(r[1:], groups, strict=True):
            printed(cell, group[k])
    for r, group in zip(t2[2:], groups, strict=True):
        require(r[0] == f"SU({group['N']})", 'model group label')
        for cell, k in zip(r[1:], ['A', 'Cxi_schemeB', 'model_Cxi_schemeA', 'model_schemeB_Mmatch_bound'], strict=True):
            printed(cell, group[k])
    trial = read('clock_products.csv')
    t = table_rows(paper, 'A1')
    slopes = [float(number(x)) for x in t[0][2:]]
    require(len(t) == 11 and len(slopes) == 6 and len(trial) == 48, 'clock product dimensions')
    seen = set()
    lookup = {(int(r['N']), int(r['K']), float(r['trial_c1'])): r for r in trial}
    for row in t[2:-1]:
        n = int(re.fullmatch(r'SU\((\d+)\)', row[0])[1])
        k = int(row[1])
        seen.add((n, k))
        for c1, cell in zip(slopes, row[2:], strict=True):
            printed(cell, lookup[n, k, c1]['product'])
    require(seen == set(product((2, 3), (10, 100, 1000, 10000))) and t[-1][0] == 'Both', 'clock trajectory grid')
    for c1, cell in zip(slopes, t[-1][2:], strict=True):
        printed(cell, 1 / (1 + c1 / 6))
    require(max(float(row['abs_difference']) for row in trial) < 1.54e-14, 'endpoint error at published precision')
    free = read('free_clock.csv')
    t = table_rows(paper, 'A2')
    require(len(t) == 6, 'free table dimensions')
    for row, item in zip(t[2:], free, strict=True):
        require(row[0] == item['L'], 'free-box size label')
        for cell, k in zip(row[1:], ['mode_clock', 'sinc', 'remainder', 'upper'], strict=True):
            printed(cell, item[k])
    return 'All 90 printed numeric results in Tables 1, 2, A1 and A2 match their fresh calculations at the displayed precision.'
