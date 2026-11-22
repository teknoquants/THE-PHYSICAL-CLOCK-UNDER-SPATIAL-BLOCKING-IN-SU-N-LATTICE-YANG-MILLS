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

"""Finite-volume, free spectral and interacting-hypothesis diagnostics for §§4, 5 and 8."""
from itertools import product
import math

import mpmath as mp
import numpy as np
import sympy as sp

from common import require


def box_definition():
    vacuum, rest, momentum, shift = sp.symbols('E0 Er Ep s')
    def gap_difference(v, r, p):
        return (p - v)**2 - (r - v)**2
    require(sp.expand(gap_difference(vacuum + shift, rest + shift, momentum + shift) -
                      gap_difference(vacuum, rest, momentum)) == 0, 'vacuum energy shift')
    for size in (3, 4, 7):
        phase = np.exp(2j * np.pi / size)
        translation = np.roll(np.eye(size), 1, axis=0)
        projectors = [sum(phase**(-k * z) * np.linalg.matrix_power(translation, z)
                          for z in range(size)) / size for k in range(size)]
        require(np.allclose(sum(projectors), np.eye(size), atol=1e-13), 'momentum resolution of identity')
        for k, projector in enumerate(projectors):
            require(np.max(np.abs(projector @ projector - projector)) < 1e-13, 'momentum idempotence')
            require(np.max(np.abs(translation @ projector - phase**k * projector)) < 1e-13, 'momentum character sign')
            require(np.max(np.abs(projector @ projectors[(k + 1) % size])) < 1e-13, 'momentum orthogonality')
    for n in (2, 3):
        # Average over the three Z_N factors for arbitrary winding characters.
        for winding in product(range(n), repeat=3):
            value = math.prod(sum(np.exp(2j * np.pi * k * w / n) for k in range(n)) / n for w in winding)
            require(abs(value - int(winding == (0, 0, 0))) < 1e-13, 'centre-neutral projection')
    return 'Exact gap-shift identity, cyclic momentum projectors for three sizes and all centre characters for N=2,3.'


def sinc_bound():
    with mp.workdps(75):
        for size in (2, 3, 4, 7, 16, 63, 512, 100000):
            t = mp.pi / size
            for mass in (mp.mpf('0'), mp.mpf('.3'), mp.mpf('4')):
                energy = mp.sqrt(mass**2 + 4 * mp.sin(t)**2)
                speed = mp.sqrt(energy**2 - mass**2) / (2 * t)
                require(abs(speed - mp.sin(t) / t) < mp.mpf('1e-60'), 'mass cancellation on the free branch')
                remainder = speed - 1 + t * t / 6
                require(0 <= remainder <= t**4 / 120, 'signed quartic bound')
        lead = (mp.sin(t) / t - 1 + t * t / 6) / t**4
        require(abs(lead - 1 / mp.mpf(120)) < mp.mpf('1e-12'), 'sharp quartic coefficient')
    return '24 free-branch gap computations at 75 digits, including L=2 and L=100000; checked both signed inequalities.'


def free_pole():
    u = sp.symbols('u', real=True)
    require(sp.trigsimp(sp.cos(u)**2 - sp.sin(u)**2 - sp.cos(2 * u)) == 0, 'alias gap identity')
    aliases = list(product((0, 1), repeat=3))
    checked = 0
    for direction, magnitude, spacing in product([(1, 0, 0), (1, 1, 1), (2, -1, 3), (0, -2, 1)], [.05, .13, .21], [.5, 1.7]):
        p = magnitude * np.array(direction, dtype=float) / spacing
        angles = spacing * p / 2
        rho = np.max(abs(angles))
        require(0 < rho < np.pi / 4, 'low momentum')
        energies, residues = [], []
        for alias in aliases:
            angle = angles + np.pi * np.array(alias) / 2
            k = 2 * np.sin(angle) / spacing
            energy = np.linalg.norm(k)
            # Sum diagonal transverse residues, including the two-link form factor.
            residue = np.sum(4 * np.cos(angle)**2 * (1 - (k / energy)**2)) / (2 * energy)
            require(residue >= -1e-13, 'transverse spectral positivity')
            energies.append(energy)
            residues.append(residue)
        require(residues[0] > 0 and min(energies[1:]) > energies[0], 'unique low pole with overlap')
        ratio = energies[0] / np.linalg.norm(p)
        require(1 - rho * rho / 6 - 2e-15 <= ratio <= 1 + 2e-15, 'all-direction phase-speed enclosure')
        # The effective energy of the two-time correlator approaches the minimum visible pole.
        w = np.array(residues)
        e = np.array(energies)
        time = 40 / (min(e[1:]) - e[0])
        shifted = e - e[0]
        late = e[0] - math.log(np.dot(w, np.exp(-shifted * (time + 1))) / np.dot(w, np.exp(-shifted * time)))
        require(abs(late - e[0]) < 1e-12, 'visible spectral pole from the two-time covariance')
        checked += 1
    return f'Exact alias identity and all eight aliases in {checked} momentum/spacing cases; bounded the phase speed and recovered the late-time pole.'


def finite_volume_hypothesis():
    L = sp.symbols('L', positive=True)
    require(sp.limit(L**2 / L, L, sp.oo) == sp.oo, 'nonuniform rate example')
    with mp.workdps(50):
        values = [n * n * (1 - mp.sin(mp.pi / n) / (mp.pi / n)) for n in (4, 8, 16, 128, 1024)]
        require(all(0 <= v <= mp.pi**2 / 6 for v in values), 'free finite-size control')
    return 'The free L²-scaled error stays bounded. A comparison sequence with error 1/L converges while its scaled error diverges. The interacting uniform bound is open.'


def dispersion_hypothesis():
    x, lam, p = sp.symbols('x l p', positive=True)
    energy = sp.sqrt(1 + p**2)
    scale = 1 + lam * x
    speed2 = sp.cancel(((scale * energy)**2 - scale**2) / p**2)
    require(sp.simplify(speed2 - scale**2) == 0, 'spectral time dilation')
    h = np.diag([0., 1., 1.4])
    factors = [1., 1.13]
    for factor in factors:
        _, vecs = np.linalg.eigh(factor * h)
        require(np.allclose(np.outer(vecs[:, 0], vecs[:, 0]), np.diag([1., 0., 0.])), 'equal ground-state law')
    require(sp.diff(scale, x).subs(x, 0) == lam, 'a one-loop difference remains possible')
    return 'Equal ground-state projectors coexist with different propagation speeds in a calculation with fixed time units. The interacting one-loop law remains open.'


def defect_lower_bound():
    # A finite projected channel can move upward while satisfying a one-sided lower comparison.
    x = sp.symbols('x', positive=True)
    difference = (1 + x)**2 - 1
    require(sp.expand(difference) == 2 * x + x**2 and difference.subs(x, sp.Rational(1, 7)) > 0, 'upward shift witness')
    return 'A positive spectral shift satisfies the one-sided comparison in a model channel. Obtaining the W2d.2 uniform small-field estimate requires interacting input.'


def loss_cancellation():
    x, kmean, kclock, s, t = sp.symbols('x kmean kclock s t')
    ansatz = (s * kmean + t * kclock) * x + x**2
    require(sp.diff(ansatz, x).subs({x: 0, kmean: 0, kclock: 0}) == 0, 'linear loss cancellation under the ansatz')
    require(sp.diff(ansatz + x, x).subs({x: 0, kmean: 0, kclock: 0}) == 1, 'an additional independent linear term survives')
    return 'The proposed two-mismatch ansatz cancels its linear term. Its completeness for the interacting W2d.4 defect remains open.'


def regularity_hypothesis():
    x = sp.symbols('x', positive=True)
    perturbation = x**2 * sp.log(x)
    require(sp.limit(perturbation / x, x, 0, dir='+') == 0, 'agreement of the linear coefficient')
    require(sp.limit(abs(perturbation) / x**2, x, 0, dir='+') == sp.oo, 'lack of uniform quadratic remainder')
    return 'A normalized comparison clock with x² log(x) has the prescribed slope and an unbounded quadratic remainder. This tests the role of regularity.'


def endpoint_hypothesis():
    xs = sp.Rational(1, 6)
    x = sp.symbols('x', real=True)
    extension = 1 + (x - xs)**3
    for order in range(3):
        require(sp.diff(extension - 1, x, order).subs(x, xs) == 0, 'C² joining at weak cutoff')
    require(extension.subs(x, 1) != 1, 'different strong endpoint values')
    return 'Two positive extensions agree on the weak interval and through two derivatives at the cutoff, and yield different endpoint clocks. The strong endpoint needs independent data.'
