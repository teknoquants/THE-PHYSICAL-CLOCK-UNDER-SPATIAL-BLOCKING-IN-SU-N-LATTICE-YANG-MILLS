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

"""Map the paper's statements and open inputs to runnable evidence and exact Lean names."""
from dataclasses import dataclass
from functools import partial
from typing import Callable

import check_clock as clock
import check_dispersion as spectrum
import check_wilson as wilson


@ dataclass(frozen=True)
class Claim:
    label: str
    title: str
    target: str
    status: str
    test: Callable[[], str]
    lean: tuple[str, ...]
    scope: str


def claims(data, manuscript):
    return [
        Claim('§1–2', 'Time-unit and gap-ratio scaling', 'W2a Prop. 1 / Cor. 2', 'FORMAL', clock.time_unit,
              ('time_unit_scaling', 'kinetic_ratio_clock'), 'Symmetric finite-dimensional operators and positive time units.'),
        Claim('Theorem 2.1', 'Matching errors for two calibrations', 'R.1', 'FORMAL', clock.matching,
              ('step_error_schemeA', 'step_error_schemeB', 'clock_step_bound'), 'Physical identification of F requires speed preservation and time covariance.'),
        Claim('Theorem 3.1', 'Uniform endpoint limit', 'R.2', 'CONDITIONAL', clock.endpoint,
              ('isotropic_telescopes', 'clock_product_telescope', 'physical_clock_composes'), 'The physical interpretation assumes dispersion; uniformity uses a fixed regular clock and the stated running bounds.'),
        Claim('Proposition 3.2', 'Power-law drift of a linear multiplier', 'R.3 / W2a Thm. 4', 'FORMAL', clock.drift_product,
              ('drift_gamma_identity', 'drift_asymptotic', 'drift_iff_kappa_ne_zero'), 'Exact one-loop sequence with positive denominators and b + κ > 0.'),
        Claim('Corollary 3.3', 'Physical drift coefficient', 'R.3', 'CONDITIONAL', clock.no_linear_drift,
              ('first_order_compat', 'no_regular_clock', 'isotropic_telescopes', 'drift_iff_kappa_ne_zero'), 'Follows by combining the physical ratio expansion with the drift criterion.'),
        Claim('Definition 4.1', 'Clock on a centre-neutral excitation branch', 'R.4', 'DEFINITION', spectrum.box_definition,
              ('gap_shift_invariant',), 'Tests the gap expression and model group projectors. Identifying the physical glueball branch requires spectral input.'),
        Claim('Lemma 4.2', 'Free axial speed and finite-size remainder', 'R.5 free branch', 'FORMAL', spectrum.sinc_bound,
              ('free_clock_sinc_bounds',), 'Prescribed free dispersion, L ≥ 2 and nonnegative rest mass.'),
        Claim('§4 interacting estimate', 'Uniform interacting finite-volume hypothesis', 'R.5 interacting branch', 'OPEN', spectrum.finite_volume_hypothesis,
              (), 'Constants uniform in both L and g and the interacting branch identification remain open.'),
        Claim('Proposition 5.1', 'Unit speed of the retained free mode', 'R.6 / W2b.9', 'ANALYTIC', spectrum.free_pole,
              ('alias_energy_separation', 'free_phase_enclosure'), 'Lean checks the alias separation inequality and the all-direction free phase bound. The two-time pole and overlap argument is analytic.'),
        Claim('§5 interacting speed', 'One-loop dispersion hypothesis', 'R.7 / W2d.7', 'OPEN', spectrum.dispersion_hypothesis,
              (), 'Preservation of the selected interacting pole through one loop has no proof in this release.'),
        Claim('§5 W2d.2', 'Uniform small-field defect estimate', 'R.7 input', 'OPEN', spectrum.defect_lower_bound,
              (), 'The model diagnoses the limitation of a one-sided comparison; a uniform gauge-theory estimate remains open.'),
        Claim('§5 W2d.4', 'Cancellation of the interacting order-g² loss', 'R.7 input', 'OPEN', spectrum.loss_cancellation,
              (), 'The algebraic cancellation assumes the two-mismatch ansatz. Completeness of that ansatz is open.'),
        Claim('Proposition 6.1', 'Group dependence of the Hamiltonian-limit kernel', 'R.8', 'ANALYTIC', partial(wilson.group_dependence, data),
              ('kernel_group_dependence',), 'Lean checks the group reduction after the moment identities. The input kernel and integral reductions are analytic inputs.'),
        Claim('§6–7 numerical comparison', 'Wilson coefficients and printed rounding', 'R.8', 'DISCREPANCY', partial(wilson.coefficients, data),
              (), 'The two evaluations use the same kernel. The published-pair residuals exceed rounding for SU(2) and SU(3).'),
        Claim('Proposition 8.1', 'Optional shift from Wilson truncation', 'R.9 coefficient identity', 'CONDITIONAL', clock.truncation_shift,
              ('local_shift_derivative',), 'Exact differentiation given the coefficient conventions and the assumed expansions.'),
        Claim('§8 Wilson shift values', 'Group-specific Wilson truncation shifts', 'R.9 optional values', 'UNEVALUATED', wilson.local_shift_values,
              (), 'The numerical values of Δc_irr for SU(2) and SU(3) are undetermined by the coefficient identity.'),
        Claim('Proposition 8.2', 'Passage from a direct remainder to its reciprocal', 'R.10 implication', 'FORMAL', clock.reciprocal,
              ('reciprocal_remainder',), 'The supplement checks the quantified bound for every x in the interval, given the direct remainder and positive floor.'),
        Claim('§8 regularity', 'Nonperturbative regularity on the weak interval', 'R.10 input', 'OPEN', spectrum.regularity_hypothesis,
              (), 'Positive C² regularity and a uniform remainder for the interacting clock remain open.'),
        Claim('§8 strong endpoint', 'Control of the strong-coupling endpoint clock', 'R.10 endpoint', 'ASSUMPTION', spectrum.endpoint_hypothesis,
              (), 'An independent strong-coupling value is required when the endpoint lies outside the weak interval.'),
        Claim('§8 conditional transfer', 'Conditional transfer and intermediate step count', 'W2a Thm. 12 / Prop. 18', 'CONDITIONAL', clock.transfer,
              ('transfer_bound', 'intermediate_step_count'), 'Requires the stated per-step loss, running, propagation and endpoint inequalities.'),
        Claim('§7 / Appendix A', 'Printed coefficient, step, product and free-box tables', 'Tables 1, 2, A1, A2', 'NUMERICAL', partial(wilson.published_tables, data, manuscript),
              ('A_enclosure',), 'The release theorem encloses A. Python validates the other displayed numerical values from newly generated data.'),
    ]
