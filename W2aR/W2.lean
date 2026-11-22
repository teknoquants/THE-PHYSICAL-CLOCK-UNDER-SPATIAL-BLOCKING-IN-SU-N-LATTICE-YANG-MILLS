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

-- Root of the W2 Lean library: one import per module (keep in sync with W2/).
import W2.Common.Basic
import W2.Common.Constants
import W2.Common.Trig
import W2.Common.Hypotheses
import W2.Framework.Schur
import W2.W2aR.Estimates
import W2.W2aR.TimeUnit
import W2.W2aR.Matching
import W2.W2aR.Drift
import W2.W2aR.Clock
import W2.W2aR.Threshold
import W2.W2b.GapRatio
import W2.W2b.Artifact
import W2.W2b.Normalization
import W2.W2b.Symbol
import W2.W2c.DimensionCount
import W2.W2c.EliminatedGap
import W2.W2d.Retained
import W2.W2d.Artifact
import W2.W2d.FreeCheck
import W2.W2e.ClockInvariance
import W2.W2e.Loss
import W2.W2f.Assembly
import W2.W2f.Constants
import W2.W2f.Master
