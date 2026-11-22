-- W2-PACKET {"audit":["W2.Common.free_clock_sinc_bounds"],"editable":[],"format":1,"mode":"final-review","module":null}
/-
SPDX-License-Identifier: MIT
MIT License

Copyright (c) 2026 Roger Cooperman; A.E. Petrunina V.V.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
-/

module

public import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
public import Mathlib.Analysis.SpecialFunctions.Log.Basic
public import Mathlib.Analysis.Calculus.ContDiff.Defs
public import Mathlib.Analysis.SpecialFunctions.Trigonometric.Bounds
public import Mathlib.Analysis.Calculus.Deriv.MeanValue
public import Mathlib.Analysis.Calculus.Deriv.Pow
public import Mathlib.Tactic
public import Mathlib.Analysis.InnerProductSpace.Symmetric
public import Mathlib.LinearAlgebra.Eigenspace.Basic
public import Mathlib.Analysis.SpecialFunctions.Gamma.Basic
public import Mathlib.Analysis.SpecialFunctions.Pow.Real
public import Mathlib.Topology.Algebra.InfiniteSum.Real
public import Mathlib.Algebra.Order.Floor.Ring

@[expose] public section

-- W2 MODULE BEGIN W2/Common/Basic.lean
-- W2 IMPORT public import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
-- W2 IMPORT public import Mathlib.Analysis.SpecialFunctions.Log.Basic

/-! Shared W2a-R conventions. Every clock takes the **squared** coupling `x = g²`.
Index `k` increases from the ultraviolet toward the infrared. -/
namespace W2.Common

abbrev Clock := ℝ → ℝ
abbrev Trajectory := ℕ → ℝ

noncomputable def A (N : ℕ) : ℝ := 11 * (N : ℝ) * Real.log 2 / (12 * Real.pi ^ 2)

def weak (xs x : ℝ) : Prop := 0 < x ∧ x ≤ xs

noncomputable def fullClock (c : Clock) (x : ℝ) : ℝ := 1 / c x

def truncClock (c₁ x : ℝ) : ℝ := 1 - c₁ * x

/-- `speed h x z` is the speed measured after blocking with input clock `z`.
The output time unit is determined by matching to the reference at `y`. -/
noncomputable def matchedClock {ι : Type*} (c : Clock) (speed : ι → ℝ → ℝ → ℝ)
    (h : ι) (x y z : ℝ) : ℝ := speed h x z / c y

/-- Physical response once time covariance and exact preservation of speed are imposed. -/
noncomputable def physicalRatio (c : Clock) (x y z : ℝ) : ℝ := z * c x / c y

noncomputable def oneLoopBack (b a : ℝ) (n : ℕ) : ℝ := 1 / (b + a * n)

/-- Paper's quadratic product includes both endpoints `0` and `K`. -/
noncomputable def driftProduct (b a κ : ℝ) (K : ℕ) : ℝ :=
  ∏ n ∈ Finset.range (K + 1), (1 + κ * oneLoopBack b a n)

def aPlus (a B xs : ℝ) : ℝ := a + B * xs

noncomputable def stepQ (a B xs : ℝ) : ℝ := 1 / (1 - aPlus a B xs * xs)

noncomputable def clockFloor (s M xs : ℝ) : ℝ := 1 - |s| * xs - M * xs ^ 2

noncomputable def stepConstant (a B xs s M : ℝ) : ℝ :=
  (|s| * aPlus a B xs * stepQ a B xs + M * (1 + stepQ a B xs ^ 2)) /
    clockFloor s M xs

noncomputable def matchConstant (a B xs c₁ Mc : ℝ) : ℝ :=
  Mc * (1 + stepQ a B xs ^ 2) / clockFloor (-c₁) Mc xs

def blockConstant (C M xs : ℝ) : ℝ := C + M + C * M * xs ^ 2

def stepData (a B xs x y : ℝ) : Prop :=
  weak xs x ∧ weak xs y ∧ 0 ≤ B ∧ 0 < a - B * xs ∧ aPlus a B xs * xs < 1 ∧
  |1 / y - 1 / x + a| ≤ B * x

/-- Uniform remainder of a calibrated clock on the weak interval. -/
def hasRemainder (u : Clock) (xs s M : ℝ) : Prop :=
  0 ≤ M ∧ ∀ x, weak xs x → |u x - (1 + s * x)| ≤ M * x ^ 2

/-- Axial lattice momentum in units of one fine link. -/
noncomputable def p₁ (L : ℕ) : ℝ := 2 * Real.pi / L

/-- Quotient of free lattice energy `2 sin(p/2)` by continuum momentum. -/
noncomputable def freeClock (L : ℕ) : ℝ := 2 * Real.sin (p₁ L / 2) / p₁ L

/-- Squared clock from energy gaps in a fixed momentum and centre-flux sector.
The zero-momentum excitation is on the same branch as the moving excitation. -/
noncomputable def boxClockSq (L : ℕ) (E₀ Erest Emoving : ℝ) : ℝ :=
  ((Emoving - E₀) ^ 2 - (Erest - E₀) ^ 2) / (p₁ L) ^ 2

end W2.Common
-- W2 MODULE END W2/Common/Basic.lean

-- W2 MODULE BEGIN W2/Common/Hypotheses.lean
-- W2 IMPORT public import W2.Common.Basic
-- W2 IMPORT public import Mathlib.Analysis.Calculus.ContDiff.Defs

/-! Physical and trajectory inputs used by W2a-R. The structures are predicates on
specified data. Constructing them for a particular gauge theory is a separate task. -/
namespace W2.Common

/-- R.10-type regularity on the closed squared-coupling interval, using a normalized
extension to zero. `M` is uniform in `x`. The direct and inverse remainders differ. -/
structure ClockRegularityHyp (c : Clock) (xs c₁ : ℝ) : Prop where
  cutoff_pos : 0 < xs
  normalized : c 0 = 1
  positive : ∀ x, weak xs x → 0 < c x
  smooth : ContDiffOn ℝ 2 c (Set.Icc 0 xs)
  remainder : ∃ M : ℝ, hasRemainder c xs c₁ M

/-- The extra cubic remainder in the published W2a Theorem 15, with `x = g²`. -/
def cubicClockExpansion (c : Clock) (xs c₁ : ℝ) : Prop :=
  ∃ c₂ D : ℝ, 0 ≤ D ∧ ∀ x, weak xs x →
    |c x - (1 + c₁ * x + c₂ * x ^ 2)| ≤ D * x ^ 3

/-- Hypotheses (i) and (ii) of W2a Theorem 15. `h` ranges over every admitted
incoming effective datum. `speed` is measured in physical units. -/
structure DispersionHyp {ι : Type*} (c : Clock) (speed : ι → ℝ → ℝ → ℝ)
    (xs : ℝ) : Prop where
  preserves : ∀ h x, weak xs x → speed h x 1 = c x
  time_covariant : ∀ h x z, weak xs x → 0 < z → speed h x z = z * speed h x 1

/-- Backward inverse-coupling increment, imposed stepwise through a finite weak run.
No bound on its summed losses is supplied by this structure. -/
structure RunningBoundHyp (x : Trajectory) (J : ℕ) (xs amin : ℝ) : Prop where
  amin_pos : 0 < amin
  cutoff_pos : 0 < xs
  values : ∀ k ≤ J, weak xs (x k)
  decrement : ∀ k < J, amin ≤ 1 / x k - 1 / x (k + 1)

/-- The interacting finite-box estimate R.5 as an optional input. Both constants
are chosen before the box size and the coupling. -/
def finiteVolumeBound (c : Clock) (cL : ℕ → Clock) (xs : ℝ) : Prop :=
  ∃ U V : ℝ, 0 ≤ U ∧ 0 ≤ V ∧ ∀ L : ℕ, 2 ≤ L → ∀ x, weak xs x →
    |cL L x - c x| ≤ (U + V * x ^ 2) / (L : ℝ) ^ 2

end W2.Common
-- W2 MODULE END W2/Common/Hypotheses.lean

-- W2 MODULE BEGIN W2/Common/Trig.lean
-- W2 IMPORT public import W2.Common.Basic
-- W2 IMPORT public import Mathlib.Analysis.SpecialFunctions.Trigonometric.Bounds
-- W2 IMPORT public import Mathlib.Analysis.Calculus.Deriv.MeanValue
-- W2 IMPORT public import Mathlib.Analysis.Calculus.Deriv.Pow
-- W2 IMPORT public import Mathlib.Tactic

/-! Free axial lattice clock, shared by W2b.10 and W2a-R.5 at order zero. -/
namespace W2.Common

/-- The quartic cosine upper polynomial follows by integration from the cubic sine lower bound. -/
private theorem cos_le_quartic {x : ℝ} (hx : 0 ≤ x) :
    Real.cos x ≤ 1 - x ^ 2 / 2 + x ^ 4 / 24 := by
  let f (t : ℝ) := 1 - t ^ 2 / 2 + t ^ 4 / 24 - Real.cos t
  have hd (t : ℝ) : deriv f t = -t + t ^ 3 / 6 + Real.sin t := by
    simp (disch := fun_prop) [f]
    ring
  have hm : MonotoneOn f (Set.Ici 0) := by
    apply monotoneOn_of_deriv_nonneg (convex_Ici 0) (by fun_prop)
    · exact fun _ _ => by dsimp [f]; fun_prop
    · intro t ht
      rw [hd]
      have ht' : 0 ≤ t := interior_subset ht
      linarith [Real.sin_ge_sub_cube ht']
  have he := hm (show (0 : ℝ) ∈ Set.Ici 0 by simp) hx hx
  simpa [f, sub_nonneg] using he

private theorem sin_le_quintic {x : ℝ} (hx : 0 ≤ x) :
    Real.sin x ≤ x - x ^ 3 / 6 + x ^ 5 / 120 := by
  let f (t : ℝ) := t - t ^ 3 / 6 + t ^ 5 / 120 - Real.sin t
  have hd (t : ℝ) : deriv f t = 1 - t ^ 2 / 2 + t ^ 4 / 24 - Real.cos t := by
    simp (disch := fun_prop) [f]
    ring
  have hm : MonotoneOn f (Set.Ici 0) := by
    apply monotoneOn_of_deriv_nonneg (convex_Ici 0) (by fun_prop)
    · exact fun _ _ => by dsimp [f]; fun_prop
    · intro t ht
      rw [hd]
      exact sub_nonneg.mpr (cos_le_quartic (interior_subset ht))
  have he := hm (show (0 : ℝ) ∈ Set.Ici 0 by simp) hx hx
  simpa [f, sub_nonneg] using he

/-- For every periodic side `L ≥ 2`, the free clock is exactly sinc. Its error after
subtracting `1 − (π/L)²/6` is between zero and `(π/L)⁴/120`. The last clause
recovers its square from free dispersion for any energy origin and rest mass. -/
theorem free_clock_sinc_bounds (L : ℕ) (hL : 2 ≤ L) :
    let t := Real.pi / (L : ℝ)
    freeClock L = Real.sin t / t ∧
      0 ≤ freeClock L - (1 - t ^ 2 / 6) ∧
      freeClock L - (1 - t ^ 2 / 6) ≤ t ^ 4 / 120 ∧
      (∀ E₀ m : ℝ, 0 ≤ m → boxClockSq L E₀ (E₀ + m)
        (E₀ + Real.sqrt (m ^ 2 + (2 * Real.sin (p₁ L / 2)) ^ 2)) = (freeClock L) ^ 2) := by
-- W2 PROOF BEGIN W2.Common.free_clock_sinc_bounds
  let t := Real.pi / (L : ℝ)
  change freeClock L = Real.sin t / t ∧ _
  have hL' : 0 < (L : ℝ) := by exact_mod_cast (show 0 < L by omega)
  have ht : 0 < t := div_pos Real.pi_pos hL'
  have hp : p₁ L = 2 * t := by unfold p₁ t; ring
  have he : freeClock L = Real.sin t / t := by
    rw [freeClock, hp, show 2 * t / 2 = t by ring]
    field_simp
  rw [he]
  refine ⟨rfl, ?_, ?_, ?_⟩
  · apply sub_nonneg.mpr
    apply (le_div_iff₀ ht).mpr
    linarith only [Real.sin_ge_sub_cube ht.le, show (1 - t ^ 2 / 6) * t = t - t ^ 3 / 6 by ring]
  · apply sub_le_iff_le_add.mpr
    apply (div_le_iff₀ ht).mpr
    linarith only [sin_le_quintic ht.le,
      show (t ^ 4 / 120 + (1 - t ^ 2 / 6)) * t = t - t ^ 3 / 6 + t ^ 5 / 120 by ring]
  · intro E₀ m _
    rw [← he, boxClockSq, freeClock, add_sub_cancel_left, add_sub_cancel_left,
      Real.sq_sqrt (by positivity), add_sub_cancel_left, div_pow]
-- W2 PROOF END W2.Common.free_clock_sinc_bounds

end W2.Common
-- W2 MODULE END W2/Common/Trig.lean

-- W2 MODULE BEGIN W2/Common/Constants.lean
-- W2 IMPORT public import W2.Common.Basic

namespace W2.Common

/-- W2a Def. 1, §8. Both rational intervals have width `10⁻⁹`. -/
def A_enclosure.statement : Prop :=
  128755903 / 10^9 < A 2 ∧ A 2 < 128755904 / 10^9 ∧
  193133855 / 10^9 < A 3 ∧ A 3 < 193133856 / 10^9

end W2.Common
-- W2 MODULE END W2/Common/Constants.lean

-- W2 MODULE BEGIN W2/W2aR/TimeUnit.lean
-- W2 IMPORT public import W2.Common.Basic
-- W2 IMPORT public import Mathlib.Analysis.InnerProductSpace.Symmetric
-- W2 IMPORT public import Mathlib.LinearAlgebra.Eigenspace.Basic

namespace W2.W2aR

/-- A gap above the entire ground eigenspace. Multiplicity within a level is allowed. -/
def firstGap {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℂ E]
    (H : Module.End ℂ E) (e δ : ℝ) : Prop :=
  0 < δ ∧ H.HasEigenvalue (e : ℂ) ∧ H.HasEigenvalue ((e + δ : ℝ) : ℂ) ∧
    ∀ t : ℝ, H.HasEigenvalue (t : ℂ) → e ≤ t ∧ (e < t → e + δ ≤ t)

/-- W2a Prop. 1. Quantification includes self-adjoint Hamiltonians with a
multiple ground level. The gap clause applies whenever there is a second level. -/
def time_unit_scaling.statement : Prop :=
  ∀ (E : Type) [NormedAddCommGroup E] [InnerProductSpace ℂ E]
    [FiniteDimensional ℂ E] (T V : Module.End ℂ E),
    T.IsSymmetric → V.IsSymmetric → ∀ gE gB : ℝ, 0 < gE → 0 < gB →
    let x := gE * gB
    let ξ := gE / gB
    let H := ((x / 2 : ℝ) : ℂ) • T + ((1 / x : ℝ) : ℂ) • V
    let Hξ := ((gE ^ 2 / 2 : ℝ) : ℂ) • T + ((1 / gB ^ 2 : ℝ) : ℂ) • V
    Hξ = (ξ : ℂ) • H ∧
    (∀ (e : ℝ) (v : E), Hξ.HasEigenvector ((ξ * e : ℝ) : ℂ) v ↔ H.HasEigenvector (e : ℂ) v) ∧
    (∀ e δ : ℝ, firstGap Hξ (ξ * e) (ξ * δ) ↔ firstGap H e δ)

/-- W2a Cor. 2. Squared couplings `x,y`, fine spacing `a`, and two positive clocks.
The certificate inequality fixes the orientation of the time ratio. -/
def kinetic_ratio_clock.statement : Prop :=
  ∀ x y a z z' gap m η : ℝ, 0 < x → 0 < y → 0 < a → 0 < z → 0 < z' →
    let ck := x / (2 * a)
    let ck' := y / (2 * (2 * a))
    (z * gap) / a = z * (gap / a) ∧
    2 * ck / ck' = 4 * x / y ∧
    2 * (z * ck) / (z' * ck') = (z / z') * (2 * ck / ck') ∧
    ((1 - η) * (z' * m) ≤ z * (gap / a) ↔ (1 - η) * (z' / z) * m ≤ gap / a)

end W2.W2aR
-- W2 MODULE END W2/W2aR/TimeUnit.lean

-- W2 MODULE BEGIN W2/W2aR/Matching.lean
-- W2 IMPORT public import W2.Common.Basic

namespace W2.W2aR
open W2.Common

/-- W2a Lemma 6, equality of the first-order output and calibration coefficients. -/
def first_order_compat.statement : Prop :=
  ∀ κ ρ s : ℝ, κ + ρ * s = s ↔ (1 - ρ) * s = κ

/-- W2a Cor. 7 for a time-covariant response, whose input slope is one. -/
def no_regular_clock.statement : Prop :=
  ∀ κ : ℝ, κ ≠ 0 → ¬ ∃ s : ℝ, κ + 1 * s = s

/-- W2a-R.1(A). The full clock's exact matching makes the actual block error
identical to the calibration-ratio error. -/
def step_error_schemeA.statement : Prop :=
  ∀ (c : Clock) (a B xs x y c₁ Mc : ℝ), stepData a B xs x y →
    (∀ t, weak xs t → 0 < c t) → hasRemainder (fullClock c) xs (-c₁) Mc →
    0 < clockFloor (-c₁) Mc xs →
    let u := fullClock c
    let C := stepConstant a B xs (-c₁) Mc
    physicalRatio c x y (u x) = u y ∧
    |u y / u x - 1| ≤ C * x ^ 2 ∧
    |physicalRatio c x y (u x) / u x - 1| ≤ blockConstant C 0 xs * x ^ 2

/-- W2a-R.1(B). The truncated calibration has zero Taylor remainder. Its residual
against the physical response is controlled using the full reciprocal remainder.
The denominator of `matchConstant` includes `Mc * xs²`. -/
def step_error_schemeB.statement : Prop :=
  ∀ (c : Clock) (a B xs x y c₁ Mc : ℝ), stepData a B xs x y →
    (∀ t, weak xs t → 0 < c t) → hasRemainder (fullClock c) xs (-c₁) Mc →
    0 < clockFloor (-c₁) Mc xs → B * xs ≤ a / 2 →
    aPlus a B xs * xs ≤ 1 / 2 → |c₁| * xs ≤ 1 / 2 →
    let u := truncClock c₁
    let C := 6 * a * |c₁|
    let R := matchConstant a B xs c₁ Mc
    hasRemainder u xs (-c₁) 0 ∧ |u y / u x - 1| ≤ C * x ^ 2 ∧
    |physicalRatio c x y (u x) / u y - 1| ≤ R * x ^ 2 ∧
    |physicalRatio c x y (u x) / u x - 1| ≤ blockConstant C R xs * x ^ 2

end W2.W2aR
-- W2 MODULE END W2/W2aR/Matching.lean

-- W2 MODULE BEGIN W2/W2aR/Drift.lean
-- W2 IMPORT public import W2.Common.Basic
-- W2 IMPORT public import Mathlib.Analysis.SpecialFunctions.Gamma.Basic
-- W2 IMPORT public import Mathlib.Analysis.SpecialFunctions.Pow.Real

namespace W2.W2aR
open W2.Common Filter
open scoped Topology

/-- W2a Theorem 4, exact finite product. The condition `-b < κ` ensures positivity. -/
def drift_gamma_identity.statement : Prop :=
  ∀ (b a κ : ℝ) (K : ℕ), 0 < b → 0 < a → -b < κ →
    let q := b / a
    let σ := κ / a
    driftProduct b a κ K = Real.Gamma ((K : ℝ) + 1 + q + σ) * Real.Gamma q /
      (Real.Gamma ((K : ℝ) + 1 + q) * Real.Gamma (q + σ))

/-- W2a Theorem 4, L3 stretch target. The ultraviolet limit includes the prefactor. -/
def drift_asymptotic.statement : Prop :=
  ∀ b a κ : ℝ, 0 < b → 0 < a → -b < κ →
    Tendsto (fun K : ℕ => driftProduct b a κ K / (K : ℝ) ^ (κ / a)) atTop
      (𝓝 (Real.Gamma (b / a) / Real.Gamma (b / a + κ / a)))

/-- W2a-R.3 at coefficient level. `κ/a` is the exponent in Theorem 4. -/
def drift_iff_kappa_ne_zero.statement : Prop :=
  ∀ b a κ : ℝ, 0 < b → 0 < a → -b < κ →
    (κ / a ≠ 0 ↔ κ ≠ 0) ∧ ((¬ ∃ s : ℝ, κ + s = s) ↔ κ ≠ 0) ∧
    (κ = 0 → ∀ K, driftProduct b a κ K = 1)

end W2.W2aR
-- W2 MODULE END W2/W2aR/Drift.lean

-- W2 MODULE BEGIN W2/W2aR/Clock.lean
-- W2 IMPORT public import W2.Common.Hypotheses

namespace W2.W2aR
open W2.Common

noncomputable def ratioProduct (u : Clock) (x : Trajectory) (J : ℕ) : ℝ :=
  ∏ k ∈ Finset.range J, u (x (k + 1)) / u (x k)

/-- W2a Theorem 8, including its explicit denominator and uniform remainder. -/
def clock_step_bound.statement : Prop :=
  ∀ (u : Clock) (a B xs x y s M : ℝ), stepData a B xs x y →
    hasRemainder u xs s M → 0 < clockFloor s M xs →
    |u y / u x - 1| ≤ stepConstant a B xs s M * x ^ 2

/-- W2a Cor. 9. The first clause is exact, including the empty product. The second
chooses a single cutoff before all admitted trajectories and calibrations sharing
the given constants, at a fixed terminal squared coupling `xt`. -/
def clock_product_telescope.statement : Prop :=
  (∀ (u : Clock) (x : Trajectory) (J : ℕ), (∀ k ≤ J, u (x k) ≠ 0) →
    ratioProduct u x J = u (x J) / u (x 0)) ∧
  ∀ a B xs s M xt : ℝ, weak xs xt → 0 ≤ B → 0 < a - B * xs →
    0 ≤ M → 0 < clockFloor s M xs → ∀ ε : ℝ, 0 < ε → ∃ J₀ : ℕ,
    ∀ J ≥ J₀, ∀ (u : Clock) (x : Trajectory), hasRemainder u xs s M →
    x J = xt → (∀ k ≤ J, weak xs (x k)) →
    (∀ k < J, stepData a B xs (x k) (x (k + 1))) → |ratioProduct u x J - u xt| < ε

/-- W2a Theorem 15. Speed covariance and preservation are separately quantified
physical inputs. Matching speeds at two successive squared couplings composes. -/
def physical_clock_composes.statement : Prop :=
  ∀ (ι : Type) (c : Clock) (speed : ι → ℝ → ℝ → ℝ) (xs c₁ : ℝ),
    DispersionHyp c speed xs → ClockRegularityHyp c xs c₁ →
    ∀ (h : ι) (x y : ℝ), weak xs x → weak xs y →
    (∀ z : ℝ, 0 < z → matchedClock c speed h x y z = physicalRatio c x y z) ∧
    matchedClock c speed h x y (fullClock c x) = fullClock c y

/-- W2a-R.2. The physical response is already expressed in reference-speed units.
The same cubic-error constant works for every admitted step. The same cutoff
works for every trajectory of length `J` with the stated endpoint. -/
def isotropic_telescopes.statement : Prop :=
  ∀ (c : Clock) (a B xs c₁ : ℝ), ClockRegularityHyp c xs c₁ →
    0 ≤ B → 0 < a - B * xs → aPlus a B xs * xs < 1 →
    (∃ D : ℝ, 0 ≤ D ∧ ∀ x y, stepData a B xs x y →
      |physicalRatio c x y 1 - (1 - c₁ * a * x ^ 2)| ≤ D * x ^ 3) ∧
    (∀ (x : Trajectory) (J : ℕ), (∀ k ≤ J, weak xs (x k)) →
      (∏ k ∈ Finset.range J, physicalRatio c (x k) (x (k + 1)) 1) = c (x 0) / c (x J)) ∧
    (∀ xt : ℝ, weak xs xt → ∀ ε : ℝ, 0 < ε → ∃ J₀ : ℕ, ∀ J ≥ J₀,
      ∀ x : Trajectory, x J = xt → (∀ k ≤ J, weak xs (x k)) →
      (∀ k < J, stepData a B xs (x k) (x (k + 1))) →
      |(∏ k ∈ Finset.range J, physicalRatio c (x k) (x (k + 1)) 1) - 1 / c xt| < ε)

end W2.W2aR
-- W2 MODULE END W2/W2aR/Clock.lean

-- W2 MODULE BEGIN W2/W2aR/Threshold.lean
-- W2 IMPORT public import W2.Common.Hypotheses
-- W2 IMPORT public import Mathlib.Analysis.SpecialFunctions.Pow.Real
-- W2 IMPORT public import Mathlib.Topology.Algebra.InfiniteSum.Real
-- W2 IMPORT public import Mathlib.Algebra.Order.Floor.Ring

namespace W2.W2aR
open W2.Common

/-- W2a Prop. 18. Count starts inside the intermediate region. An endpoint
crossing need not stop exactly at the lower inverse-coupling threshold. -/
def intermediate_step_count.statement : Prop :=
  ∀ (M : ℕ) (u : ℕ → ℝ) (lo hi aInt : ℝ), 0 < aInt → lo ≤ hi →
    (∀ k < M, lo < u k ∧ u k ≤ hi) →
    (∀ k, k + 1 < M → aInt ≤ u k - u (k + 1)) →
    M ≤ ⌈(hi - lo) / aInt⌉₊

/-- W2a Theorem 12. `v (k+1)` is the certificate actually propagated at step k.
The running input is local. The loss sum and the ultraviolet certificate are conclusions. -/
def transfer_bound.statement : Prop :=
  ∀ (J : ℕ) (x spacing η v : ℕ → ℝ) (xs amin r C₄ CL Ca c δ aw mbar zL mIR bridge : ℝ),
    RunningBoundHyp x J xs amin → 0 ≤ r → r < 1 →
    0 ≤ C₄ → 0 ≤ CL → 0 ≤ Ca → 0 < c → 0 < δ → δ < 2 →
    0 ≤ aw → 0 ≤ mbar → 0 < zL → 0 < mIR → 0 < bridge →
    (∀ k < J, 0 < spacing k) → (∀ k, k + 1 < J → spacing (k + 1) = 2 * spacing k) →
    (0 < J → spacing (J - 1) ≤ aw) →
    (∀ k < J, 0 ≤ v (k + 1) ∧ v (k + 1) ≤ mbar) →
    (∀ k < J, 0 ≤ η k ∧ η k ≤ r ∧ η k ≤ C₄ * (x k) ^ 2 +
      CL * Real.exp (-c / ((Real.sqrt (x k)) ^ δ)) + Ca * (spacing k * v (k + 1)) ^ 2) →
    (∀ k < J, (1 - η k) * v (k + 1) ≤ v k) → zL * mIR * bridge ≤ v J →
    let D := (4 / (Real.exp 1 * c * δ)) ^ (4 / δ)
    let S := (C₄ + CL * D) * (xs ^ 2 + xs / amin) + (4 / 3) * Ca * (aw * mbar) ^ 2
    (∑' j : ℕ, (1 / 4 : ℝ) ^ j) = 4 / 3 ∧
    (∀ t : ℝ, 0 ≤ t → t ≤ r → -Real.log (1 - t) ≤ t / (1 - r)) ∧
    (∑ k ∈ Finset.range J, η k) ≤ S ∧ zL * mIR * bridge * Real.exp (-S / (1 - r)) ≤ v 0

end W2.W2aR
-- W2 MODULE END W2/W2aR/Threshold.lean

#check W2.Common.A_enclosure.statement
#check W2.W2aR.time_unit_scaling.statement
#check W2.W2aR.kinetic_ratio_clock.statement
#check W2.W2aR.first_order_compat.statement
#check W2.W2aR.no_regular_clock.statement
#check W2.W2aR.step_error_schemeA.statement
#check W2.W2aR.step_error_schemeB.statement
#check W2.W2aR.drift_gamma_identity.statement
#check W2.W2aR.drift_asymptotic.statement
#check W2.W2aR.drift_iff_kappa_ne_zero.statement
#check W2.W2aR.clock_step_bound.statement
#check W2.W2aR.clock_product_telescope.statement
#check W2.W2aR.physical_clock_composes.statement
#check W2.W2aR.isotropic_telescopes.statement
#check W2.W2aR.intermediate_step_count.statement
#check W2.W2aR.transfer_bound.statement
#print axioms W2.Common.free_clock_sinc_bounds
#eval "W2 final-review 9772df065518478965c86bdc743f7e77d01844c29eed04d0a4c9ad2fdb90eea1"
