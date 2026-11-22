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

import Mathlib.Analysis.SpecialFunctions.Trigonometric.Bounds
import Mathlib.Analysis.Calculus.Deriv.Mul
import Mathlib.Tactic

/-! Auxiliary proofs for the W2a-R paper. The seventeen frozen release declarations
are rechecked separately. The kernel identity below assumes the moment reductions.
The free-mode lemmas concern the specified linearized dispersion. -/
namespace W2.PaperValidation
open scoped BigOperators

theorem gap_shift_invariant (rest moving vacuum shift p : ℝ) :
    (((moving + shift) - (vacuum + shift)) ^ 2 -
     ((rest + shift) - (vacuum + shift)) ^ 2) / p ^ 2 =
    ((moving - vacuum) ^ 2 - (rest - vacuum) ^ 2) / p ^ 2 := by ring

/-- All aliased components used in the sum have a larger squared lattice momentum. -/
theorem alias_energy_separation (t : Fin 3 → ℝ) (s : Finset (Fin 3)) (hs : s.Nonempty)
    (positive : ∀ j ∈ s, 0 < Real.cos (2 * t j)) :
    (∑ j ∈ s, Real.sin (t j) ^ 2) < ∑ j ∈ s, Real.cos (t j) ^ 2 := by
  apply Finset.sum_lt_sum_of_nonempty hs
  intro j hj
  have h := positive j hj
  rw [Real.cos_two_mul] at h
  nlinarith [Real.sin_sq_add_cos_sq (t j)]

/-- Component magnitudes t = |a p_i|/2. Their ratio bounds the free phase error in all directions. -/
theorem free_phase_enclosure (t : Fin 3 → ℝ) (ρ : ℝ) (hρ : 0 ≤ ρ)
    (small : ρ ≤ 1) (ht : ∀ j, 0 ≤ t j ∧ t j ≤ ρ) (pos : 0 < ∑ j, (t j) ^ 2) :
    let speed := Real.sqrt ((∑ j, Real.sin (t j) ^ 2) / ∑ j, t j ^ 2)
    1 - ρ ^ 2 / 6 ≤ speed ∧ speed ≤ 1 := by
  dsimp only
  have lower_nonneg : 0 ≤ 1 - ρ ^ 2 / 6 := by nlinarith [sq_nonneg ρ, mul_self_le_mul_self hρ small]
  have component (j : Fin 3) : (1 - ρ ^ 2 / 6) ^ 2 * t j ^ 2 ≤ Real.sin (t j) ^ 2 := by
    have bound := mul_self_le_mul_self (ht j).1 (ht j).2
    have lh : (1 - ρ ^ 2 / 6) * t j ≤ Real.sin (t j) := by
      nlinarith [Real.sin_ge_sub_cube (ht j).1, mul_nonneg (sub_nonneg.mpr bound) (ht j).1]
    have square := mul_self_le_mul_self (mul_nonneg lower_nonneg (ht j).1) lh
    nlinarith only [square]
  have upper (j : Fin 3) : Real.sin (t j) ^ 2 ≤ t j ^ 2 := by
    have habs : |Real.sin (t j)| ≤ t j := by simpa [abs_of_nonneg (ht j).1] using (Real.abs_sin_le_abs (x := t j))
    rw [sq_le_sq]; simpa [abs_of_nonneg (ht j).1] using habs
  constructor
  · apply Real.le_sqrt_of_sq_le
    apply (le_div_iff₀ pos).mpr
    rw [Finset.mul_sum]
    exact Finset.sum_le_sum (fun j _ => component j)
  · apply (Real.sqrt_le_iff).mpr
    constructor
    · norm_num
    · simpa using (div_le_one pos).mpr (Finset.sum_le_sum (fun j _ => upper j))

/-- Group reduction after substitution of the two analytic moment identities in §6. -/
theorem kernel_group_dependence (I₁ I₂ N : ℝ) (hN : N ≠ 0) :
    -4 * N * ((1 - 1 / N ^ 2) * I₁ / 24 - 7 * I₂ / 288 +
      (I₂ / 3 - I₁ / 6) / 48 + (4 * I₂ - 8 * I₁ / 3) / 128) =
      -(5 * I₁ + 4 * I₂) / 72 * N + (I₁ / 6) / N := by
  field_simp [hN]; ring

/-- Differentiating a full response times a Wilson truncation correction. -/
theorem local_shift_derivative (F d : ℝ → ℝ) (δ : ℝ)
    (hF : HasDerivAt F 0 0) (hF₀ : F 0 = 1) (hd : HasDerivAt d (-δ) 0) :
    HasDerivAt (fun x => F x * d x) (-δ) 0 := by
  simpa [hF₀, Pi.mul_def] using hF.mul hd

/-- Proposition 8.2, with a uniform lower bound on c and quadratic direct remainder. -/
theorem reciprocal_remainder (c : ℝ → ℝ) (a M m xs : ℝ) (hm : 0 < m) (hM : 0 ≤ M)
    (floorBound : ∀ x ∈ Set.Icc 0 xs, m ≤ c x)
    (remainder : ∀ x ∈ Set.Icc 0 xs, |c x - (1 + a * x)| ≤ M * x ^ 2) :
    ∀ x ∈ Set.Icc 0 xs, |1 / c x - (1 - a * x)| ≤
      ((a ^ 2 + (1 + |a| * xs) * M) / m) * x ^ 2 := by
  intro x hx
  have hx₀ : 0 ≤ x := hx.1
  have hxs : 0 ≤ xs := hx₀.trans hx.2
  have hc : 0 < c x := hm.trans_le (floorBound x hx)
  have factor : |1 - a * x| ≤ 1 + |a| * xs := calc
    |1 - a * x| ≤ |(1 : ℝ)| + |a * x| := abs_sub _ _
    _ ≤ 1 + |a| * xs := by
      rw [abs_one, abs_mul, abs_of_nonneg hx₀]
      exact add_le_add_right (mul_le_mul_of_nonneg_left hx.2 (abs_nonneg _)) _
  have algebra : 1 - c x * (1 - a * x) = a ^ 2 * x ^ 2 - (c x - (1 + a * x)) * (1 - a * x) := by ring
  have numerator : |1 - c x * (1 - a * x)| ≤ (a ^ 2 + (1 + |a| * xs) * M) * x ^ 2 := calc
    _ = _ := congrArg abs algebra
    _ ≤ |a ^ 2 * x ^ 2| + |(c x - (1 + a * x)) * (1 - a * x)| := abs_sub _ _
    _ ≤ a ^ 2 * x ^ 2 + (M * x ^ 2) * (1 + |a| * xs) := by
      rw [abs_of_nonneg (mul_nonneg (sq_nonneg a) (sq_nonneg x)), abs_mul]
      exact add_le_add_right (mul_le_mul (remainder x hx) factor (abs_nonneg _) (mul_nonneg hM (sq_nonneg _))) _
    _ = _ := by ring
  have quotient : 1 / c x - (1 - a * x) = (1 - c x * (1 - a * x)) / c x := by field_simp
  rw [quotient, abs_div, abs_of_pos hc]
  calc
    _ ≤ ((a ^ 2 + (1 + |a| * xs) * M) * x ^ 2) / c x := div_le_div_of_nonneg_right numerator hc.le
    _ ≤ ((a ^ 2 + (1 + |a| * xs) * M) * x ^ 2) / m := div_le_div_of_nonneg_left (by positivity) hm (floorBound x hx)
    _ = _ := by ring

end W2.PaperValidation

#print axioms W2.PaperValidation.gap_shift_invariant
#print axioms W2.PaperValidation.alias_energy_separation
#print axioms W2.PaperValidation.free_phase_enclosure
#print axioms W2.PaperValidation.kernel_group_dependence
#print axioms W2.PaperValidation.local_shift_derivative
#print axioms W2.PaperValidation.reciprocal_remainder
