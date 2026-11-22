# Mathematical statement review

The SHA-256 digest of `W2aR_review_final.lean` is `134a4dabe2cab4082188264678991daa489d80518781b8bd7fa41eeb6afdb84f`. First check the prelude and the shared Trig return. Then run `python3 scripts/review_packet.py` from the project root to reconstruct the freeze and compare it with this digest. Each of the six module checks and the final packet check repeat the comparison. The fill packets also fix the proof support added after statement review.

| Review question | Frozen interpretation |
|---|---|
| What is the clock argument? | Every shared clock takes the squared coupling. The weak interval includes the positive endpoint and excludes zero. Clock regularity uses a normalized extension to the closed interval. |
| Which remainder is used? | R.1 bounds the reciprocal clock. R.2 assumes a positive regular reference speed, including a direct quadratic remainder. Their constants can differ. |
| Which constants are uniform? | Theorem 8 requires the same quadratic remainder over the entire interval. In Corollary 9 the cutoff is chosen before the trajectory and the calibrated function when the numerical constants and terminal coupling are fixed. In R.2 the function is fixed before the cubic-error constant and cutoff, and each applies to all admitted steps or trajectories. |
| Which way are ratios taken? | A calibration ratio is output over input. With input clock one, the speed-matching response is the fine speed divided by the coarse reference speed. Their endpoint formulas agree for the reciprocal calibration. |
| Where do physical assumptions enter? | Theorem 15 quantifies over every admitted incoming datum and every positive input clock. Speed preservation and time covariance are separate fields. R.2 uses their resulting physical ratio. |
| How are gaps defined? | Finite-dimensional time scaling uses a second distinct eigenvalue above the entire ground eigenspace. The box-clock expression subtracts squared energy gaps on the same excitation branch. The free lemma supplies the dispersion it uses. |
| Which statements have nontrivial conclusions? | RunningBoundHyp supplies local inverse decrements and admissible values. The transfer loss sum, geometrical factor and UV lower bound are derived. Intermediate step counting allows an overshoot at the last step. |
| What did the review freeze? | Basic, Hypotheses, the completed Trig prerequisite, and 16 proposition definitions in Constants, TimeUnit, Matching, Drift, Clock and Threshold. Later proofs are attached by explicit type ascription to those propositions. |

The full MIT header is the sole change to the original mathematical checkpoint. Reconstructing the earlier format after removing that exact header reproduces its original SHA-256 `aab2b25bd2cc9c6be0785f2ea407103eadf9ef63aa814bc03bf0fcd482ac513a`. The replay verifies both digests.

## MIT License

SPDX-License-Identifier: MIT

Copyright (c) 2026 Roger Cooperman; A.E. Petrunina V.V.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
