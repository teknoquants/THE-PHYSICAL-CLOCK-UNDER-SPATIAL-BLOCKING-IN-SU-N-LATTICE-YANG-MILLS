# Numerical and Lean cross-references

The [paper-validation suite](../Python-Validation/README.md) links all numbered results and open hypotheses to their evidence. Its [verified report](../Python-Validation/verified/REPORT.md) includes the original numerical checks described below.

The nine Python sources in `w2a/` implement the original validation suite, including its runner and common utilities. The upstream Git blob identities, before expansion of the MIT notices, are recorded in `records/w2ar-v1/baseline-source.tsv`. Each successful numerical check is retained in `records/w2ar-v1/w2a_validation.out`. [Pinned upstream W2a revision](https://github.com/teknoquants/Weak-Coupling-Matching-and-the-Running-Time-Unit-Under-Spatial-Blocking-in-SU-N-Lattice-Yang-Mills/commit/c91a1dc1a3d6862f86767cd81127aa4b2c057afd)

| Python source or numerical table | Checks | Corresponding Lean declaration or physical status |
|---|---:|---|
| `validate_part1_time_unit.py` | 5 | `time_unit_scaling`, `kinetic_ratio_clock` |
| `validate_part2_matching.py` | 6 | Coefficient and tree identities related to `first_order_compat` and `no_regular_clock` |
| `validate_part3_drift.py` | 5 | `drift_gamma_identity`, `drift_asymptotic`, `drift_iff_kappa_ne_zero` |
| `validate_part4_running_clock.py` | 7 | `clock_step_bound`, `clock_product_telescope`, `first_order_compat`, `no_regular_clock` |
| `validate_part5_threshold.py` | 5 | `time_unit_scaling` and the constituent bounds of `transfer_bound` |
| `validate_numerical_tables.py` | 11 | `A_enclosure`, drift product checks, quartic running comparison |
| `validate_part6_composition_threshold.py` | 7 | `physical_clock_composes`, `isotropic_telescopes`, `intermediate_step_count`. Schur and transfer identities are also exercised numerically. |
| `free_clock.csv` | 4 box sizes | `W2.Common.free_clock_sinc_bounds` |
| `blocked_free_modes.csv` | 8 box/momentum pairs | Tree two-link pole argument R.6 |
| `clock_products.csv` | 48 products | `isotropic_telescopes` under the exact one-loop model |
| `hamiltonian_quadrature.csv`, `anisotropic_limit.csv`, `coefficients.csv` | 5 quadrature orders, 6 anisotropies, 2 groups | R.8 numerical matching and the constants entering `step_error_schemeA` and `step_error_schemeB` |

The new numerical checks are implemented in `scripts/validate_w2ar.py`. The one-dimensional Bessel evaluation and the three-dimensional Brillouin-zone cubature use different representations of the same one-loop kernel. The published-table rounding diagnostic is recorded as `False` for both groups.

## MIT License

SPDX-License-Identifier: MIT

Copyright (c) 2026 Roger Cooperman; A.E. Petrunina V.V.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
