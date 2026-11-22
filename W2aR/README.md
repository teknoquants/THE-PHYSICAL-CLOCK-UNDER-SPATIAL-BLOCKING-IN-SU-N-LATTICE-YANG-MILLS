# W2a-R · The physical clock under spatial blocking

Read the mathematical supplement in [report/W2aR-report.pdf](report/W2aR-report.pdf). The project implements the six W2a-R modules from the supplied W2 skeleton and the shared free-clock prerequisite. The complete Lake build passed with Lean 4.36.0. The final self-contained packet checks all 17 released declarations.

The W2b and W2d extract is included with the report. Page 4 specifies the spectral quantity used for W2d.7 and the open inputs W2d.2 and W2d.4. The reference confirms W2b.9 at tree level. W2a-R.7 still uses `DispersionHyp`. [Supplied extract](report/references/W2b_Prop9_and_W2d_Thm7.docx)

The attachment review documents the pre-licensing edition of the project. Its comparison with the supplied Word source refers to that edition. The current licence-bearing final packet and transcript have new digests. A fresh local replay of that source and a rerun of the six return checks are recorded in [the attachment verification record](records/attachment-review/verification.txt).

## Paper validation

[Python-Validation/](Python-Validation/) contains the eight Python scripts for the white paper, with a full MIT licence in each script. From this repository root, run

```bash
python3 -m pip install -r requirements.txt
python3 Python-Validation/run_validation.py
```

The [verified report](Python-Validation/verified/REPORT.md) records each numbered result, the proof or diagnostic that checks it, and every open input. The [complete paper](report/W2aR-White-Paper.md) includes the ten original Lean listings. Six further proof terms are in [SupplementalProofs.lean](Python-Validation/SupplementalProofs.lean). See the [validation guide](Python-Validation/README.md) for a Python-only run.

## Repository and citation

Project repository `[GITHUB_URL]`. Archival DOI `[DOI]`. Roger Cooperman and A.E. Petrunina V.V., *The Physical Clock under Spatial Blocking in SU(N) Lattice Yang–Mills*, XISOSIS, Vienna, 22 November 2026.

The GitHub workflow builds Lean, runs the paper-validation suite and uploads the claim report, Lean transcripts and freshly generated CSV files.

## Reproduce the checks

Use a shell with `elan`, `lake` and Python 3 available. The project selects the exact Lean version from `lean-toolchain`. The checked-in Lake manifest pins Mathlib and its dependencies. The first dependency and cache fetch needs network access.

```bash
lake exe cache get
python3 scripts/replay.py
python3 scripts/test_packet.py
python3 -m pip install -r requirements.txt
python3 validation/w2a/run_all.py
python3 scripts/validate_w2ar.py
```

The packet scripts use only Python's standard library and the pinned Lean environment. On this run the W2a numerical suite passed 46/46 checks. The W2a-R numerical script regenerates every CSV and reports the comparison with Karsch's printed coefficients, including the unresolved difference beyond the rounding precision.

## Check the prelude and Trig

`python3 scripts/replay.py` runs the stages in order and records their results. The first two stages can also be run individually.

```bash
python3 scripts/make_packet.py --prelude
lake env lean packets/prelude.lean > records/w2ar-v1/prelude.out
python3 scripts/check_return.py packets/prelude.lean packets/prelude.lean records/w2ar-v1/prelude.out

python3 scripts/make_packet.py W2/Common/Trig.lean --unit W2aR --emit-return
lake env lean returns/Trig.lean > returns/Trig.out
python3 scripts/check_return.py packets/Trig.lean returns/Trig.lean returns/Trig.out
```

The prelude checks 26 declarations from `Basic.lean` and `Hypotheses.lean`. The Trig packet has one editable proof, `W2.Common.free_clock_sinc_bounds`. Both packets can be generated before the six target modules exist.

## Freeze the statements and check the six returns

Run `python3 scripts/review_packet.py` to reconstruct the reviewed statements and verify their SHA-256 digest. The freeze includes definitions, quantifiers, hypotheses and conclusions for all 16 target propositions. The [statement review](frozen/README.md) records the mathematical decisions. The replay generates and retains all six fill packets before checking the proofs, in the order Constants, TimeUnit, Matching, Drift, Clock and Threshold.

For example, the following commands recreate the retained Clock fill packet. The `--emit-return` option supplies the completed proof bodies from this checkout for a local replay. To evaluate someone else's solution, save that person's complete packet as `returns/Clock.lean` and their raw Lean output as `returns/Clock.out`.

```bash
python3 scripts/make_packet.py W2/W2aR/Clock.lean --unit W2aR --emit-return
lake env lean returns/Clock.lean > returns/Clock.out
python3 scripts/check_return.py packets/Clock.lean returns/Clock.lean returns/Clock.out
```

The comparison runs against the locally retained envelope. Only marked theorem proof bodies may change. The checker verifies the statement freeze, compiles the returned file again, compares its actual output with the submitted transcript, validates the transitive axiom list, then writes the accepted module to `extracted/W2/W2aR/Clock.lean`. The six extracted files in this release match the project sources byte-for-byte.

## Final packet and transcripts

```bash
python3 scripts/make_packet.py --final W2aR
lake env lean records/w2ar-v1/final.lean > records/w2ar-v1/final.local.out
python3 scripts/axiom_audit.py records/w2ar-v1/final.local.out \
  --file records/w2ar-v1/final.lean --report records/w2ar-v1/lean_report.md
```

For the hosted run, paste the complete contents of [W2aR_final.txt](packets/W2aR_final.txt) into a new conversation with the exercise's Lean assistant and download its raw `final.out`. The following command preserves the downloaded bytes at `records/w2ar-v1/final.out` and then compares them with a fresh local Lean run. If they differ, the command reports the discrepancy and retains the submitted bytes.

```bash
python3 scripts/axiom_audit.py /path/to/downloaded/final.out --record-hosted \
  --file records/w2ar-v1/final.lean --report records/w2ar-v1/hosted-audit.md
```

A separate hosted assistant replay has not been recorded. The verified local transcript is [final.local.out](records/w2ar-v1/final.local.out). A second Lean run in an empty directory with the W2 object libraries excluded reproduced it byte for byte.

| Path | Contents |
|---|---|
| `frozen/W2aR_review_final.lean` | Original reviewed definitions, hypothesized inputs, 16 target propositions and shared free-clock proof |
| `scripts/released.tsv` | All 17 Lean declarations, result labels and hypothesis codes |
| `packets/` | Prelude, Trig proof template, six target-module templates and the final check-only packet, each as Lean and paste-ready text |
| `returns/` | Completed Trig and six module packets with their raw compiler transcripts |
| `records/w2ar-v1/` | Statement digest, build logs, check results, final Lean source, local transcript and axiom audit |
| `numerical/` | Hamiltonian integrals, anisotropic-limit comparison, constants, 48 clock products and free finite-volume tests |
| `validation/README.md` | Numerical tests cross-referenced to Lean and to the physical targets |
| `report/` | PDF, editable LaTeX source and data-driven table generator |

The release has 14 L1 and 3 L2 declarations. The audit admits only `propext`, `Classical.choice` and `Quot.sound`. The report identifies the physical inputs to each conditional result.

The other W2 subprojects are the future-series stubs from the supplied ZIP. The root build reports module-style warnings for those inherited files. All six W2a-R modules and the self-contained final file compile cleanly. The original skeleton and the upstream W2a validation scripts use the included MIT license.

To rebuild the PDF after regenerating the numerical files, run `python3 report/render_tables.py`, enter `report/` and run `xelatex W2aR-report.tex`. The typesetting source uses Liberation Serif, Open Sans and DejaVu Sans Mono.

## MIT License

SPDX-License-Identifier: MIT

Copyright (c) 2026 Roger Cooperman; A.E. Petrunina V.V.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
