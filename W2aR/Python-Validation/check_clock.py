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

"""Exact and high-precision checks for the time unit, matching, drift and transfer."""
from fractions import Fraction as Q
from itertools import product
import math

import mpmath as mp
import sympy as sp

from common import require


def time_unit():
    ge, gb, z, zp = sp.symbols('ge gb z zp', positive=True)
    t, v, fine, coarse = sp.symbols('t v fine coarse', nonzero=True)
    isotropic = ge * gb * t / 2 + v / (ge * gb)
    anisotropic = ge**2 * t / 2 + v / gb**2
    require(sp.cancel(anisotropic - ge / gb * isotropic) == 0, 'Hamiltonian coefficient scaling')
    require(sp.cancel((z * fine) / (zp * coarse) - z / zp * (fine / coarse)) == 0, 'gap ratio scaling')
    h = sp.diag(2, 2, 7)
    for scale in (sp.Rational(1, 5), sp.Rational(1), sp.Rational(7, 3)):
        eigenvalues = (scale * h).eigenvals()
        require(eigenvalues == {2 * scale: 2, 7 * scale: 1}, 'degenerate ground eigenspace')
        require(max(eigenvalues) - min(eigenvalues) == 5 * scale, 'first distinct gap')
    return 'Exact coefficient and gap-ratio identities; three positive scalings of a degenerate ground space.'


def matching():
    xstar, a, b = Q(1, 4), Q(1, 2), Q(1, 8)
    aplus = a + b * xstar
    q = 1 / (1 - aplus * xstar)
    count = 0
    nonzero = False
    for c1, rem, factor, step_sign, x in product(
            [Q(-1, 3), Q(0), Q(2, 5)], [Q(0), Q(1, 3)], [-1, 1], [-1, 0, 1], [Q(1, 16), Q(1, 8), Q(1, 5)]):
        d = a + step_sign * b * x
        y = x / (1 - d * x)
        floor = 1 - abs(c1) * xstar - rem * xstar**2
        require(0 < x <= y <= xstar and floor > 0, 'step admissibility')
        require(abs(1 / y - 1 / x + a) <= b * x and b * xstar <= a / 2 and aplus * xstar <= Q(1, 2), 'running assumptions')
        vx, vy = 1 - c1 * x, 1 - c1 * y
        ux, uy = vx + factor * rem * x * x, vy + factor * rem * y * y
        actual = uy / ux  # c(x)/c(y), since u = 1/c.
        require(ux * actual == uy, 'full matching equality')
        ca = (abs(c1) * aplus * q + rem * (1 + q * q)) / floor
        cb = 6 * a * abs(c1)
        mb = rem * (1 + q * q) / floor
        residual = vx * actual / vy - 1
        require(abs(uy / ux - 1) <= ca * x * x and abs(vy / vx - 1) <= cb * x * x, 'step error')
        require(abs(residual) <= mb * x * x and abs(actual - 1) <= (cb + mb + cb * mb * xstar * xstar) * x * x, 'physical mismatch bound')
        nonzero |= residual != 0
        count += 1
    require(nonzero, 'a quadratic reciprocal remainder must expose a truncated mismatch')
    return f'{count} admissible rational steps checked exactly, including zero and nonzero truncation residuals.'


def endpoint():
    x, a, b, d, c1, c2 = sp.symbols('x A B d c1 c2')
    y = x / (1 - (a + d * x) * x)
    c = lambda t: 1 + c1 * t + c2 * t * t
    expansion = sp.series(c(x) / c(y), x, 0, 3).removeO().expand()
    require(sp.simplify(expansion - (1 - c1 * a * x**2)) == 0, 'quadratic coefficient for a perturbed step')
    for n in (0, 1, 2, 9, 24):
        for shift in (-1, 0, 1):
            end = Q(1, 6)
            path = [end]
            for k in range(n):
                delta = Q(1, 3) + Q(shift, 100 * (k + 1))
                path.append(1 / (1 / path[-1] + delta))
            path.reverse()
            values = [1 - t / 3 + t * t / 5 for t in path]
            direct = math.prod(s / t for s, t in zip(values, values[1:]))
            require(direct == values[0] / values[-1], 'finite telescoping product')
            require(path[0] <= 1 / (1 / end + n * (Q(1, 3) - Q(1, 100))), 'uniform inverse decrement bound')
    return 'Series through degree two and exact telescoping for 15 paths, including zero steps and perturbed decrements.'


def drift_product():
    with mp.workdps(65):
        for b, a, k in [('1.7', '.4', '-.2'), ('2.3', '.7', '0'), ('1.8', '.5', '.3')]:
            b, a, k = map(mp.mpf, (b, a, k))
            q = b / a
            s = k / a
            limit = mp.gamma(q) / mp.gamma(q + s)
            for n in (0, 1, 9, 63):
                direct = mp.fprod(1 + k / (b + a * j) for j in range(n + 1))
                ratio = mp.rf(q + s, n + 1) / mp.rf(q, n + 1)
                require(mp.almosteq(direct, ratio), 'inclusive gamma product endpoints')
            def error(n):
                gamma = mp.exp(mp.loggamma(n + 1 + q + s) - mp.loggamma(n + 1 + q))
                return abs(gamma * limit / n**s - limit)
            if k:
                require(error(10000) < error(100) / 20 and error(10000) < mp.mpf('.0005'), 'normalized drift limit')
            else:
                require(direct == 1 and error(100) == 0, 'zero drift multiplier')
    return 'High-precision finite products and normalized large-length limits for negative, zero and positive drift.'


def no_linear_drift():
    k, rho, s = sp.symbols('k rho s')
    require(sp.expand(k + rho * s - s - (k - (1 - rho) * s)) == 0, 'first-order compatibility')
    x, a, b, c1, c2 = sp.symbols('x a b c1 c2')
    y = x / (1 - a * x)
    c = lambda t: 1 + c1 * t + c2 * t * t
    require(sp.diff(c(x) / c(y), x).subs(x, 0) == 0, 'physical linear coefficient')
    require(sp.simplify((k + rho * s - s).subs(rho, 1)) == k, 'at unit input slope only zero k can match')
    return 'The physical ratio has zero linear coefficient; the compatibility obstruction at unit slope is exactly κ.'


def truncation_shift():
    x, e, b, delta, f = sp.symbols('x e b delta f')
    local = sp.sqrt((1 + e * x) / (1 + b * x))
    full = (1 + f * x**2) * (1 - delta * x)
    require(sp.simplify(sp.diff(local, x).subs(x, 0) - (e - b) / 2) == 0, 'electric/magnetic half-difference')
    require(sp.diff(full, x).subs(x, 0) == -delta, 'sign of the omitted-operator correction')
    return 'Differentiated both definitions at zero; matching their slopes gives (κE−κB)/2 = −Δc_irr.'


def reciprocal():
    x, a, r = sp.symbols('x a r')
    c = 1 + a * x + r
    require(sp.expand(1 - c * (1 - a * x) - (a * a * x * x - r * (1 - a * x))) == 0, 'direct-to-inverse identity')
    floor = Q(1, 2)
    xs = Q(1, 4)
    evaluations = 0
    for a0, b in product([Q(-1), Q(0), Q(2, 3)], [Q(-1, 2), Q(0), Q(3, 4)]):
        maximum = (a0 * a0 + (1 + abs(a0) * xs) * abs(b)) / floor
        for k in range(13):
            t = xs * k / 12
            cx = 1 + a0 * t + b * t * t
            require(cx >= floor and abs(1 / cx - (1 - a0 * t)) <= maximum * t * t, 'direct-to-inverse remainder bound')
            evaluations += 1
    return f'Exact numerator identity and {evaluations} rational cases including zero, both signs and endpoints.'


def transfer():
    # Saturate the local loss and the propagation inequality, then check the global bound.
    a, xs, r = .3, 1 / 6, .5
    c4, cl, ca = .21, .18, .07
    tail, delta = 4., 1.
    aw, mbar = .2, 1.3
    d = (4 / (math.e * tail * delta))**(4 / delta)
    s = (c4 + cl * d) * (xs**2 + xs / a) + 4 / 3 * ca * (aw * mbar)**2
    for n in (0, 1, 2, 7, 30):
        cert = mbar
        losses = []
        for k in reversed(range(n)):
            x = 1 / (1 / xs + a * (n - k))
            spacing = aw * 2**(k + 1 - n)
            loss = c4 * x * x + cl * math.exp(-tail / (math.sqrt(x)**delta)) + ca * (spacing * cert)**2
            require(0 <= loss <= r, 'loss assumptions')
            losses.append(loss)
            cert *= 1 - loss
        require(sum(losses) <= s and cert >= mbar * math.exp(-s / (1 - r)), 'ultraviolet certificate')
    for lo, hi, step in [(Q(0), Q(2), Q(1)), (Q(1, 3), Q(2), Q(3, 4)), (Q(2), Q(2), Q(1))]:
        u = hi
        starts = 0
        while lo < u <= hi:
            starts += 1
            u -= step
        require(starts == math.ceil((hi - lo) / step), 'threshold count including the last overshoot')
    return 'Five saturated transfer chains and three exact threshold cases, including empty and overshooting segments.'
