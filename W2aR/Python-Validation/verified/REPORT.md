# W2a-R paper validation

**Execution**  Passed · **Lean**  VERIFIED

Python 3.12.14. Manuscript SHA-256 `415100a560c401bef64ca0a618961aa26f964b3ee131f0ab69c13ff613c3ecbc`.

A passed diagnostic records the outcome of that test. The status column records the scope of the mathematical result. Open inputs, the optional coefficient and the published numerical discrepancy keep their own status.

## Verification stages

- **Manuscript — PASS**. 10 numbered statements, 10 byte-identical Appendix B modules, and all 17 theorem links in Table 3.
- **Baseline — PASS**. 46 of 46 checks in seven original programs.
- **Numerical data — PASS**. Compared all six freshly generated CSVs with the released data.
- **Coverage — PASS**. 21 distinct rows cover the release inventory, supplemental results and open inputs.
- **Regression controls — PASS**. Six controls exercised altered claims, embedded proof text, printed coefficients, axiom records and open-input classifications.
- **Lean — PASS**. Fresh Lean 4.36.0 processes accepted all 17 frozen proofs, all 20 supporting proofs and 6 supplemental proofs. The six returned modules and isolated final packet also passed.

## Paper results and hypotheses

| Paper result | Mathematical status | Python check | Lean evidence |
| --- | --- | --- | --- |
| §1–2 · Time-unit and gap-ratio scaling | FORMAL | PASS · `check_clock.py / time_unit` | `time_unit_scaling`, `kinetic_ratio_clock` |
| Theorem 2.1 · Matching errors for two calibrations | FORMAL | PASS · `check_clock.py / matching` | `step_error_schemeA`, `step_error_schemeB`, `clock_step_bound` |
| Theorem 3.1 · Uniform endpoint limit | CONDITIONAL | PASS · `check_clock.py / endpoint` | `isotropic_telescopes`, `clock_product_telescope`, `physical_clock_composes` |
| Proposition 3.2 · Power-law drift of a linear multiplier | FORMAL | PASS · `check_clock.py / drift_product` | `drift_gamma_identity`, `drift_asymptotic`, `drift_iff_kappa_ne_zero` |
| Corollary 3.3 · Physical drift coefficient | CONDITIONAL | PASS · `check_clock.py / no_linear_drift` | `first_order_compat`, `no_regular_clock`, `isotropic_telescopes`, `drift_iff_kappa_ne_zero` |
| Definition 4.1 · Clock on a centre-neutral excitation branch | DEFINITION | PASS · `check_dispersion.py / box_definition` | `gap_shift_invariant` |
| Lemma 4.2 · Free axial speed and finite-size remainder | FORMAL | PASS · `check_dispersion.py / sinc_bound` | `free_clock_sinc_bounds` |
| §4 interacting estimate · Uniform interacting finite-volume hypothesis | OPEN | PASS · `check_dispersion.py / finite_volume_hypothesis` | — |
| Proposition 5.1 · Unit speed of the retained free mode | ANALYTIC | PASS · `check_dispersion.py / free_pole` | `alias_energy_separation`, `free_phase_enclosure` |
| §5 interacting speed · One-loop dispersion hypothesis | OPEN | PASS · `check_dispersion.py / dispersion_hypothesis` | — |
| §5 W2d.2 · Uniform small-field defect estimate | OPEN | PASS · `check_dispersion.py / defect_lower_bound` | — |
| §5 W2d.4 · Cancellation of the interacting order-g² loss | OPEN | PASS · `check_dispersion.py / loss_cancellation` | — |
| Proposition 6.1 · Group dependence of the Hamiltonian-limit kernel | ANALYTIC | PASS · `check_wilson.py / group_dependence` | `kernel_group_dependence` |
| §6–7 numerical comparison · Wilson coefficients and printed rounding | DISCREPANCY | PASS · `check_wilson.py / coefficients` | — |
| Proposition 8.1 · Optional shift from Wilson truncation | CONDITIONAL | PASS · `check_clock.py / truncation_shift` | `local_shift_derivative` |
| §8 Wilson shift values · Group-specific Wilson truncation shifts | UNEVALUATED | PASS · `check_wilson.py / local_shift_values` | — |
| Proposition 8.2 · Passage from a direct remainder to its reciprocal | FORMAL | PASS · `check_clock.py / reciprocal` | `reciprocal_remainder` |
| §8 regularity · Nonperturbative regularity on the weak interval | OPEN | PASS · `check_dispersion.py / regularity_hypothesis` | — |
| §8 strong endpoint · Control of the strong-coupling endpoint clock | ASSUMPTION | PASS · `check_dispersion.py / endpoint_hypothesis` | — |
| §8 conditional transfer · Conditional transfer and intermediate step count | CONDITIONAL | PASS · `check_clock.py / transfer` | `transfer_bound`, `intermediate_step_count` |
| §7 / Appendix A · Printed coefficient, step, product and free-box tables | NUMERICAL | PASS · `check_wilson.py / published_tables` | `A_enclosure` |

## Evidence and limits

**§1–2 · Time-unit and gap-ratio scaling**  
Exact coefficient and gap-ratio identities; three positive scalings of a degenerate ground space. Symmetric finite-dimensional operators and positive time units.

**Theorem 2.1 · Matching errors for two calibrations**  
108 admissible rational steps checked exactly, including zero and nonzero truncation residuals. Physical identification of F requires speed preservation and time covariance.

**Theorem 3.1 · Uniform endpoint limit**  
Series through degree two and exact telescoping for 15 paths, including zero steps and perturbed decrements. The physical interpretation assumes dispersion; uniformity uses a fixed regular clock and the stated running bounds.

**Proposition 3.2 · Power-law drift of a linear multiplier**  
High-precision finite products and normalized large-length limits for negative, zero and positive drift. Exact one-loop sequence with positive denominators and b + κ > 0.

**Corollary 3.3 · Physical drift coefficient**  
The physical ratio has zero linear coefficient; the compatibility obstruction at unit slope is exactly κ. Follows by combining the physical ratio expansion with the drift criterion.

**Definition 4.1 · Clock on a centre-neutral excitation branch**  
Exact gap-shift identity, cyclic momentum projectors for three sizes and all centre characters for N=2,3. Tests the gap expression and model group projectors. Identifying the physical glueball branch requires spectral input.

**Lemma 4.2 · Free axial speed and finite-size remainder**  
24 free-branch gap computations at 75 digits, including L=2 and L=100000; checked both signed inequalities. Prescribed free dispersion, L ≥ 2 and nonnegative rest mass.

**§4 interacting estimate · Uniform interacting finite-volume hypothesis**  
The free L²-scaled error stays bounded. A comparison sequence with error 1/L converges while its scaled error diverges. The interacting uniform bound is open. Constants uniform in both L and g and the interacting branch identification remain open.

**Proposition 5.1 · Unit speed of the retained free mode**  
Exact alias identity and all eight aliases in 24 momentum/spacing cases; bounded the phase speed and recovered the late-time pole. Lean checks the alias separation inequality and the all-direction free phase bound. The two-time pole and overlap argument is analytic.

**§5 interacting speed · One-loop dispersion hypothesis**  
Equal ground-state projectors coexist with different propagation speeds in a calculation with fixed time units. The interacting one-loop law remains open. Preservation of the selected interacting pole through one loop has no proof in this release.

**§5 W2d.2 · Uniform small-field defect estimate**  
A positive spectral shift satisfies the one-sided comparison in a model channel. Obtaining the W2d.2 uniform small-field estimate requires interacting input. The model diagnoses the limitation of a one-sided comparison; a uniform gauge-theory estimate remains open.

**§5 W2d.4 · Cancellation of the interacting order-g² loss**  
The proposed two-mismatch ansatz cancels its linear term. Its completeness for the interacting W2d.4 defect remains open. The algebraic cancellation assumes the two-mismatch ansatz. Completeness of that ansatz is open.

**Proposition 6.1 · Group dependence of the Hamiltonian-limit kernel**  
Reduced the Wilson kernel for general N; verified the two moment identities against the independent spatial moments at orders 20, 32 and 48. Lean checks the group reduction after the moment identities. The input kernel and integral reductions are analytic inputs.

**§6–7 numerical comparison · Wilson coefficients and printed rounding**  
Both quadratures agree within 2×10⁻¹². Absolute printed-pair residuals: SU(2) 5.0148444e-05, SU(3) 6.2367011e-05. Both exceed 10⁻⁵. The two evaluations use the same kernel. The published-pair residuals exceed rounding for SU(2) and SU(3).

**Proposition 8.1 · Optional shift from Wilson truncation**  
Differentiated both definitions at zero; matching their slopes gives (κE−κB)/2 = −Δc_irr. Exact differentiation given the coefficient conventions and the assumed expansions.

**§8 Wilson shift values · Group-specific Wilson truncation shifts**  
Distinct choices satisfy the same identity. The optional group-specific shift is unevaluated in this paper. The numerical values of Δc_irr for SU(2) and SU(3) are undetermined by the coefficient identity.

**Proposition 8.2 · Passage from a direct remainder to its reciprocal**  
Exact numerator identity and 117 rational cases including zero, both signs and endpoints. The supplement checks the quantified bound for every x in the interval, given the direct remainder and positive floor.

**§8 regularity · Nonperturbative regularity on the weak interval**  
A normalized comparison clock with x² log(x) has the prescribed slope and an unbounded quadratic remainder. This tests the role of regularity. Positive C² regularity and a uniform remainder for the interacting clock remain open.

**§8 strong endpoint · Control of the strong-coupling endpoint clock**  
Two positive extensions agree on the weak interval and through two derivatives at the cutoff, and yield different endpoint clocks. The strong endpoint needs independent data. An independent strong-coupling value is required when the endpoint lies outside the weak interval.

**§8 conditional transfer · Conditional transfer and intermediate step count**  
Five saturated transfer chains and three exact threshold cases, including empty and overshooting segments. Requires the stated per-step loss, running, propagation and endpoint inequalities.

**§7 / Appendix A · Printed coefficient, step, product and free-box tables**  
All 90 printed numeric results in Tables 1, 2, A1 and A2 match their fresh calculations at the displayed precision. The release theorem encloses A. Python validates the other displayed numerical values from newly generated data.

## Proof replay

| Frozen declaration | Classification | Application assumptions | Transitive axioms |
| --- | --- | --- | --- |
| `W2.Common.free_clock_sinc_bounds` | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.Common.A_enclosure` | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.time_unit_scaling` | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.kinetic_ratio_clock` | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.first_order_compat` | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.no_regular_clock` | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.step_error_schemeA` | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.step_error_schemeB` | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.drift_gamma_identity` | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.drift_asymptotic` | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.drift_iff_kappa_ne_zero` | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.clock_step_bound` | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.clock_product_telescope` | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.physical_clock_composes` | L2 | DispersionHyp; ClockRegularityHyp | Classical.choice, Quot.sound, propext |
| `W2.W2aR.isotropic_telescopes` | L2 | ClockRegularityHyp (physicalRatio as defined) | Classical.choice, Quot.sound, propext |
| `W2.W2aR.intermediate_step_count` | L1 | - | Classical.choice, Quot.sound, propext |
| `W2.W2aR.transfer_bound` | L2 | RunningBoundHyp; explicit per-step/endpoint assumptions | Classical.choice, Quot.sound, propext |

### Supporting proofs in Appendix B

Lean rechecked the following proof terms individually, including the private lemmas.

| Declaration | Source and line | Visibility | Transitive axioms |
| --- | --- | --- | --- |
| `W2.Common.cos_le_quartic` | `W2/Common/Trig.lean:40` | private | Classical.choice, Quot.sound, propext |
| `W2.Common.sin_le_quintic` | `W2/Common/Trig.lean:56` | private | Classical.choice, Quot.sound, propext |
| `W2.W2aR.stepBounds` | `W2/W2aR/Estimates.lean:44` | public | Classical.choice, Quot.sound, propext |
| `W2.W2aR.calibration_floor` | `W2/W2aR/Estimates.lean:65` | public | Classical.choice, Quot.sound, propext |
| `W2.W2aR.clockEstimate` | `W2/W2aR/Estimates.lean:74` | public | Classical.choice, Quot.sound, propext |
| `W2.W2aR.eig_scale` | `W2/W2aR/TimeUnit.lean:74` | private | Classical.choice, Quot.sound, propext |
| `W2.W2aR.eigval_scale` | `W2/W2aR/TimeUnit.lean:81` | private | Classical.choice, Quot.sound, propext |
| `W2.W2aR.combineFactors` | `W2/W2aR/Matching.lean:98` | private | Classical.choice, Quot.sound, propext |
| `W2.W2aR.drift_split` | `W2/W2aR/Drift.lean:67` | private | Classical.choice, Quot.sound, propext |
| `W2.W2aR.gamma_prod` | `W2/W2aR/Drift.lean:77` | private | Classical.choice, Quot.sound, propext |
| `W2.W2aR.product_ratio` | `W2/W2aR/Clock.lean:97` | private | Classical.choice, Quot.sound, propext |
| `W2.W2aR.initial_small` | `W2/W2aR/Clock.lean:105` | private | Classical.choice, Quot.sound, propext |
| `W2.W2aR.deviation` | `W2/W2aR/Clock.lean:123` | private | Classical.choice, Quot.sound, propext |
| `W2.W2aR.physical_product` | `W2/W2aR/Clock.lean:174` | private | Classical.choice, Quot.sound, propext |
| `W2.W2aR.derivative_step` | `W2/W2aR/Clock.lean:190` | private | Classical.choice, Quot.sound, propext |
| `W2.W2aR.cubic_speed` | `W2/W2aR/Clock.lean:226` | private | Classical.choice, Quot.sound, propext |
| `W2.W2aR.sum_squares_running` | `W2/W2aR/Threshold.lean:92` | private | Classical.choice, Quot.sound, propext |
| `W2.W2aR.sum_artifacts` | `W2/W2aR/Threshold.lean:112` | private | Classical.choice, Quot.sound, propext |
| `W2.W2aR.large_field` | `W2/W2aR/Threshold.lean:136` | private | Classical.choice, Quot.sound, propext |
| `W2.W2aR.loss_log` | `W2/W2aR/Threshold.lean:165` | private | Classical.choice, Quot.sound, propext |

### Supplemental proof terms

- `W2.PaperValidation.gap_shift_invariant` · Classical.choice, Quot.sound, propext
- `W2.PaperValidation.alias_energy_separation` · Classical.choice, Quot.sound, propext
- `W2.PaperValidation.free_phase_enclosure` · Classical.choice, Quot.sound, propext
- `W2.PaperValidation.kernel_group_dependence` · Classical.choice, Quot.sound, propext
- `W2.PaperValidation.local_shift_derivative` · Classical.choice, Quot.sound, propext
- `W2.PaperValidation.reciprocal_remainder` · Classical.choice, Quot.sound, propext

Final packet SHA-256 `6d7172e1f5e5e6306a2775339598fccc131ed1d2b75391592d3552929a1d9b95`. Local compiler transcript SHA-256 `e797d27f6ab187e9dcb34c2ef89c9ac73d5f1a1a94604d9a29d1bdcd0b3f806a`.

The raw logs for this run are in `logs/`. The project and validation scripts are distributed under the MIT License.
