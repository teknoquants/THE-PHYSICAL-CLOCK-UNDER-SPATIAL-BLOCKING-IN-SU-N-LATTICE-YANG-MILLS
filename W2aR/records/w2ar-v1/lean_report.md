# W2a-R · machine-checked declarations

17 declarations passed the axiom audit (14 L1 and 3 L2).
L1 denotes a proved mathematical implication. L2 names the physical or trajectory input supplied to that implication.

| Declaration | Target | Code | Hypotheses beyond the stated mathematical inequalities | Axioms |
|---|---|---|---|---|
| `W2.Common.free_clock_sinc_bounds` | W2a-R.5, free branch / W2b.10 | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.Common.A_enclosure` | W2a Definition 1 / §8, SU(2) and SU(3) | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.time_unit_scaling` | W2a Proposition 1 | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.kinetic_ratio_clock` | W2a Corollary 2 | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.first_order_compat` | W2a Lemma 6 | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.no_regular_clock` | W2a Corollary 7 | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.step_error_schemeA` | W2a-R.1(A) | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.step_error_schemeB` | W2a-R.1(B) | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.drift_gamma_identity` | W2a Theorem 4, finite product | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.drift_asymptotic` | W2a Theorem 4, asymptotic (stretch) | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.drift_iff_kappa_ne_zero` | W2a-R.3, coefficient criterion | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.clock_step_bound` | W2a Theorem 8 | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.clock_product_telescope` | W2a Corollary 9 | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.physical_clock_composes` | W2a Theorem 15 | L2 | DispersionHyp; ClockRegularityHyp | Classical.choice, Quot.sound, propext |
| `W2.W2aR.isotropic_telescopes` | W2a-R.2 | L2 | ClockRegularityHyp (physicalRatio as defined) | Classical.choice, Quot.sound, propext |
| `W2.W2aR.intermediate_step_count` | W2a Proposition 18 | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.transfer_bound` | W2a Theorem 12 | L2 | RunningBoundHyp; explicit per-step/endpoint assumptions | Classical.choice, Quot.sound, propext |

Packet SHA-256 `6d7172e1f5e5e6306a2775339598fccc131ed1d2b75391592d3552929a1d9b95`.
Raw output SHA-256 `e797d27f6ab187e9dcb34c2ef89c9ac73d5f1a1a94604d9a29d1bdcd0b3f806a`.
Verification used a fresh Lean 4.36.0 process.
