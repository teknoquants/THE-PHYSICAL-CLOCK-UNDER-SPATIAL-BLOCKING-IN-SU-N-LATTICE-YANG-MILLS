# Python validation for the W2a-R white paper

This suite checks *The Physical Clock under Spatial Blocking in SU(N) Lattice Yang–Mills*. The [verified report](verified/REPORT.md) covers all ten numbered statements in the manuscript and gives separate entries for additional results, assumptions, open inputs and numerical tables. The [machine-readable results](verified/results.json) and [raw logs](verified/logs/) accompany the report.

## Run the checks

Extract the entire ZIP into one directory. The dedicated validation download puts the eight Python files next to this guide. In the complete exercise, open `Python-Validation/`. The `W2aR/` directory is the project to use as a GitHub repository.

Use Python 3.12. For a full proof check install the Lean toolchain manager (elan) with Lake available on your command path. The included project selects Lean 4.36.0 and pins Mathlib. A first run on a new machine needs network access to obtain those dependencies. From the directory containing this guide, run

```bash
python3 -m pip install -r requirements.txt
python3 run_validation.py
```

For just the Python and manuscript checks, run `python3 run_validation.py --python-only`. The report will mark the Lean stage **NOT RUN**. To select a report directory, add `--output PATH`. Each run creates a fresh subdirectory under `validation-results/` by default, containing `REPORT.md`, `results.json`, logs and regenerated CSV files. A failed stage or claim diagnostic returns a nonzero exit code.

## Scripts

| File | What it checks |
| --- | --- |
| [run_validation.py](run_validation.py) | Runs the suite, the original 46 checks, the table generator and the proof replay. Writes the report. |
| [paper_claims.py](paper_claims.py) | Links each named result and additional input to its mathematical status, executable check and applicable Lean declarations. |
| [check_proofs.py](check_proofs.py) | Compares the ten Appendix B listings with source, checks Table 3 links, rebuilds the prelude and six frozen modules, and audits each proof's transitive axioms. |
| [check_clock.py](check_clock.py) | Tests matching, telescoping, gamma-product drift, truncation shifts, the reciprocal bound and conditional transfer. |
| [check_dispersion.py](check_dispersion.py) | Tests the finite-volume definition, free dispersion and blocked poles. Provides examples that probe the assumptions needed in interacting arguments. |
| [check_wilson.py](check_wilson.py) | Checks symbolic kernel and moment identities, independent numerical evaluations, 90 printed table values and the published coefficient residuals. |
| [test_validation.py](test_validation.py) | Six regression tests exercise changed statements, proof text, table entries, incomplete axiom transcripts and open-claim classification. |
| [common.py](common.py) | Locates the included Lean project, captures subprocess output, and compares regenerated and released data. |

[SupplementalProofs.lean](SupplementalProofs.lean) contains six additional proof terms with their hypotheses. The kernel checks these, the 17 declarations in the frozen release and all 20 supporting proofs from the listings. The report names each supporting lemma, including private declarations, and lists its transitive axioms. The original validators remain in the project's `validation/w2a/` and `scripts/` directories. The complete manuscript is in the project's `report/W2aR-White-Paper.md`.

## Reading the report

Each row names the exact scope of its evidence. **FORMAL** identifies a statement with a corresponding Lean proof under the displayed hypotheses. **CONDITIONAL** records a deduction whose physical application needs additional inputs. **ANALYTIC** identifies a paper argument for which the report specifies which steps Lean checks and which steps have symbolic or numerical support. **DEFINITION** and **NUMERICAL** identify the construction or values tested.

Five interacting or regularity inputs remain **OPEN**. The strong-coupling endpoint is an **ASSUMPTION**, and the two group-specific optional Wilson shifts are **UNEVALUATED**. The independent quadratures agree for SU(2) and SU(3), while their differences from the printed coefficient pairs exceed the stated rounding tolerance. That comparison keeps its **DISCREPANCY** status even when the diagnostic reproduces it.

The mathematical sections of the supplied Markdown edition have frozen fingerprints in `reviewed_sections.json`. Edits to those sections require reviewing the corresponding checks before accepting updated fingerprints. Changes to an appendix proof are also checked directly against the source. The raw Lean transcript is generated locally by the included checker.

## License

Every distributed Python script contains the complete [MIT License](LICENSE).
