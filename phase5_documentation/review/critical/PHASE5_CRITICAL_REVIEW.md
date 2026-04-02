# Phase 5 Critical Review: CMS H->tautau Signal Strength Measurement

**Reviewer:** Critical reviewer
**Date:** 2026-03-25
**Artifact:** `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md` (1603 lines, 70-page PDF)
**References checked:** `observed_results.json`, `diagnostics_full.json`, `STRATEGY.md`, `references.bib`, `conventions/extraction.md`

---

## Regression Checklist (Mandatory)

- [ ] **GoF toy distribution inconsistent with observed chi2?** YES. The full-data combined GoF yields p = 0.000 for ALL three approaches (NN score chi2 = 33.1 exceeds all 198 converged toy values, range [10.2, 28.6]). This is documented in the AN and investigated. Per-category chi2/bin values are individually acceptable (0.80-1.19). The investigation attributes this to the 5% Baseline and 31% VBF normalization deficits. While this is documented, it remains a genuine GoF failure that cannot be dismissed. **However, the per-category decomposition and NP pull analysis demonstrate the signal strength extraction is not biased.** The regression trigger is checked but not tripped because the investigation satisfies the documentation requirements.

- [x] **Single systematic > 80% of total?** NO. The largest single systematic (MET unclustered, impact 0.285 on full data) is 26% of the total sigma(mu) = 1.08. Well below the 80% threshold.

- [ ] **All binding commitments fulfilled?** PARTIAL. See Finding F1 below for specific gaps.

- [x] **Result > 30% from reference?** NO. mu = 0.63 vs published mu = 0.78; pull = -0.13 sigma. Excellent consistency.

- [x] **chi2 identically zero?** NO. On real data, chi2 values are 33-39. The Asimov chi2 = 0 is by construction and correctly noted.

---

## Category A Findings (Must Resolve)

### F1. Number inconsistency: Abstract vs body text for primary result

The abstract states `mu = 0.64 +/- 1.08`. The body text consistently states `mu = 0.63 +/- 1.08` (lines 1258, 1272, 1286, 1500, 1506). The conclusions paragraph at line 1518 also uses `0.64`. The JSON gives mu_hat = 0.6346, which rounds to 0.63, not 0.64.

**Classification: (A)** -- The abstract is the most visible part of the AN; an inconsistent central value undermines trust. Must be corrected to 0.63 everywhere (or 0.635 if higher precision is desired).

### F2. Systematic impact numbers internally inconsistent between per-source subsections and the Asimov impact ranking table

The per-systematic subsection prose reports impact values that do not match the Asimov impact ranking table (@tbl:impact-ranking):

| Systematic | Subsection prose (impact) | Asimov table (total impact) | Rank in prose | Rank in table |
|---|---|---|---|---|
| TES | +0.323/-0.422, total 0.376 | 0.214 | 1st | 4th |
| MES | +0.225/-0.346, total 0.291 | 0.404 | 2nd | 1st |
| JES | -0.096/+0.213, total 0.165 | 0.267 | 4th | 3rd |
| MET uncl. | -0.266/+0.047, total 0.191 | 0.354 | 3rd | 2nd |
| Trigger eff | +/-0.086 | 0.093 | 5th | 7th |
| Lumi | +/-0.069 | 0.066 | 6th | 10th |

The subsection prose numbers appear to be from an earlier iteration (pre-review fix), while the Asimov impact ranking table was updated. The full-data impact table (@tbl:full-impact) is consistent with the JSON.

**Classification: (A)** -- Stale numbers from an earlier phase propagating into the final AN. Every per-systematic subsection needs its impact value updated to match the current Asimov table or (better) the full-data table in @tbl:full-impact.

### F3. Systematic summary table (@tbl:syst-summary) uses Asimov impacts, not full-data impacts

The systematic summary table at line 790 is captioned "Impact on mu" and presents values that match the Asimov impact ranking table (e.g., MES = 0.404, MET uncl = 0.354, JES = 0.267, TES = 0.214). However, the full-data impact ranking (@tbl:full-impact) shows substantially different values (MET uncl = 0.285, JES = 0.214, MES = 0.148). The summary table should either be clearly labeled as "Asimov expected" or updated to show the observed data impacts (preferably the latter, since this is the final AN version).

**Classification: (A)** -- Multiple tables present different impact values without clear labeling of which is expected vs observed. A reader comparing the summary table to the full-data ranking will find contradictions.

### F4. Missing `results/` directory with machine-readable outputs

The AN specification requires a `results/` directory with CSV/JSON for spectra, uncertainties, and covariance matrices. No such directory exists under `phase5_documentation/`. While `phase4_inference/4c_observed/outputs/` contains JSON results, the Phase 5 requirement is that `results/` be a self-contained, documented directory in the documentation output.

**Classification: (A)** -- Required by `methodology/analysis-note.md` and `methodology/appendix-checklist.md`.

### F5. No covariance matrix discussion or presentation

The AN specification (`methodology/analysis-note.md`) requires:
- Full covariance matrix (statistical + systematic) in the appendix
- Per-source correlation matrices
- Total covariance and correlation matrices
- Recommendation for downstream use

The AN contains zero mentions of "covariance" anywhere in the document. For a signal strength measurement, the covariance between bins (used in the profile likelihood) is implicitly handled by pyhf, but the AN must document the correlation structure for the reader. At minimum, the NP correlation matrix from the post-fit should be presented.

**Classification: (A)** -- Explicitly required by `methodology/analysis-note.md` and `methodology/appendix-checklist.md`.

### F6. Phase labels in body text table headers

Two tables contain internal phase labels in their headers:
- Line 1030: column header "QCD (4a)" in @tbl:10pct-qcd
- Line 1284: column headers "Expected (4a)", "10% data (4b)", "Full data (4c)" in @tbl:three-way-comparison

The Phase 5 CLAUDE.md states: "Removed internal phase labels from body text." While the change log claims this was done, two instances remain.

**Classification: (A)** -- Per methodology specification, internal phase labels must not appear in the AN body.

---

## Category B Findings (Should Fix)

### F7. Limitation index missing several strategy labels

The strategy defines labels [A1]-[A4], [L1]-[L3], [D1]-[D13]. The limitation index (@tbl:limitation-index) is missing:
- **[A2]** TauPlusX trigger stream constraint
- **[D2]** Cross-section normalization strategy (YR4 vs tutorial values)
- **[D5]** Primary trigger selection
- **[D12]** SVfit not implemented

All four are binding decisions from Phase 1 that should be tracked for audit completeness.

**Classification: (B)** -- The missing labels are all documented in the body text, but the limitation index exists specifically as a one-stop registry. Incomplete registry defeats its purpose.

### F8. Systematic breakdown figure missing

The AN specification (`methodology/analysis-note.md`) explicitly requires: "The systematic uncertainties section must contain a figure showing the relative contribution of each source to the total. Acceptable formats: waterfall chart, horizontal bar chart, or stacked bar chart." The impact ranking bar chart (@fig:impact-ranking, @fig:full-impact) partially satisfies this by showing per-NP impacts, but the specification calls for a figure showing **relative contributions to the total** (fractional breakdown). The existing figures show absolute Delta-mu, not percentages of the total uncertainty budget.

**Classification: (B)** -- The impact ranking figures are close to satisfying this requirement, but a dedicated fractional breakdown figure would be more informative. The existing figures already convey the key message.

### F9. Error budget narrative paragraph incomplete

The AN specification requires an error budget narrative after the summary table discussing: (a) which sources dominate and why, (b) whether statistically or systematically limited, (c) concrete improvements to reduce dominant sources, (d) resolving power.

The text at line 781-783 addresses (a) and (b) well. However, (c) is deferred to the Future Directions section rather than placed adjacent to the error budget. The resolving power is stated in the Expected Results section but not repeated in the systematic section.

**Classification: (B)** -- The information exists but is split across sections rather than concentrated in the error budget discussion as specified.

### F10. Per-cut distribution figures incomplete

The AN specification states: "Every selection cut needs a before/after distribution plot." The AN includes tau ID working point comparison plots (3 figures), the transverse mass regions figure, and kinematic distributions in the signal region. However, there are no before/after plots for:
- The muon isolation tightening (0.15 to 0.1)
- The OS pair selection
- The muon impact parameter requirements

**Classification: (B)** -- The most important cuts (tau ID, mT) have distribution plots. The missing cuts are either trivially efficient (Delta R > 0.5 removes zero events per the cutflow) or standard object quality cuts where before/after plots provide limited physics insight.

### F11. Reproduction contract lacks workflow diagram

The reproduction contract (Appendix B, Section @sec:appendix-reproduction) describes the pipeline steps but does not include the required "workflow diagram showing the execution DAG: inputs -> processing steps -> outputs, with systematic variation branches shown" as specified in `methodology/analysis-note.md`.

**Classification: (B)** -- The textual description is adequate for reproduction, but the specification explicitly requires a DAG diagram.

### F12. Signal injection test pulls all exactly 0.000 -- suspicious

All signal injection test pulls in Tables @tbl:injection-nn, @tbl:injection-mvis, @tbl:injection-mcol are reported as 0.000. The text says "below 0.01" and attributes this to numerical precision. On Asimov data this is expected (the Asimov dataset IS the model prediction), so the test verifies workspace assembly rather than statistical properties. However, the conventions/extraction.md requires closure tests on statistically independent samples. A signal injection on Asimov with pull = 0.000 is a self-consistency check, not an independent closure test.

The AN correctly frames these as workspace validation rather than independent closure. However, the validation summary table reports these as "Fit unbiased" and "Fit linearity" which slightly overstates what the test proves.

**Classification: (B)** -- The framing should acknowledge that Asimov signal injection tests pull = 0.000 by construction and that this validates the workspace algebra, not the method's robustness to statistical fluctuations.

### F13. Z normalization uncertainty inconsistency: 12% vs per-source decomposition

Section @sec:syst-znorm states the Z normalization is 12%, decomposed as the quadrature sum of 4% (theory) + 5% (trigger) + 8% (tau ID loosening) + 2% (statistical). The quadrature sum is sqrt(4^2 + 5^2 + 8^2 + 2^2) = sqrt(16 + 25 + 64 + 4) = sqrt(109) = 10.4%, not 12%. The text says 12% but the decomposition gives 10.4%.

**Classification: (B)** -- Rounding inconsistency. The 12% is presumably a rounded-up conservative value, but the decomposition should either add up correctly or state explicitly that it is rounded up.

---

## Category C Findings (Suggestions)

### F14. NN feature table has 15 rows but claims 14 features

Table @tbl:nn-features lists 15 features (tau pT, mvis, Njets, MET, DeltaR, mu pT, tau decay mode, mT, DeltaPhi, MET significance, mu eta, tau eta, leading jet pT, leading jet eta, Nb-jets). The text says "14 input features." Count the table rows: that is 15, not 14. Either one entry is not actually used (e.g., MET significance shows "N/A" for ROC AUC, suggesting it may not be used as an individual feature) or the count is wrong.

**Classification: (C)** -- Minor counting discrepancy that should be clarified.

### F15. Table caption typo

Table @tbl:full-impact caption ends with a double period: "...dominate the uncertainty budget.." (line 1380).

**Classification: (C)**

### F16. "the the" duplication

Line 1294: "as anticipated in the the 10% validation interpretation." Line 1218: "already observed in the 10% validation (the 10% validation)." These are minor prose issues.

**Classification: (C)**

### F17. Change log format uses a table instead of the specified bulleted list format

The specification in `methodology/analysis-note.md` shows the change log using bulleted lists grouped by version. The AN uses a pipe table format instead. The table is functional but differs from the specification.

**Classification: (C)** -- Not materially different; the table format is arguably more compact.

### F18. BibTeX entries for unused citations

The `references.bib` file contains entries `Gaiser:1982yw`, `Li:1983fv`, `Ellis:1987xu`, `pyhf_joss`, and `ParticleDataGroup:2022pth` that do not appear as citations in the AN text (none of these keys are referenced with `[@...]`). These are harmless (pandoc-citeproc ignores unused entries) but create unnecessary clutter.

**Classification: (C)**

### F19. Collinear mass reference citation

The collinear approximation method (Section @sec:disc-mcol) is used but no foundational reference is cited for the collinear approximation technique itself. A citation to Ellis, Stirling, Webber or a relevant tau physics paper would strengthen the methodology.

**Classification: (C)** -- The method is well-known and self-explanatory, but the AN spec encourages citing foundational methodology references.

---

## Number Consistency Spot-Checks (10 key numbers)

| # | Quantity | AN value | JSON/Diagnostics value | Status |
|---|---------|---------|----------------------|--------|
| 1 | NN mu_hat (full) | 0.63 | 0.6346 | PASS (rounds correctly) |
| 2 | NN mu_err (full) | 1.08 | 1.079 | PASS |
| 3 | NN obs_significance | 0.61 | 0.606 | PASS |
| 4 | NN obs_limit_95 | 2.85 | 2.846 | PASS |
| 5 | mvis mu_hat (full) | -6.70 | -6.700 | PASS |
| 6 | mcol mu_hat (full) | -10.74 | -10.744 | PASS |
| 7 | NP pull norm_wjets_vbf | -1.89 | -1.891 | PASS |
| 8 | NP pull shape_jes | -1.41 | -1.410 | PASS |
| 9 | Full data impact MET uncl. | 0.285 | 0.285 | PASS |
| 10 | Abstract mu | **0.64** | 0.6346 | **FAIL** (should be 0.63) |

9/10 pass. 1 failure: abstract uses 0.64 instead of 0.63.

---

## Strategy Commitment Traceability

| Commitment | Status in AN | Finding |
|------------|-------------|---------|
| [D1] Four approaches | Three completed, NN MET regression dropped (documented as [D13]) | PASS |
| [D2] YR4 cross-sections | Implemented per Strategy | PASS |
| [D3] W+jets from high-mT | SF = 0.999, documented | PASS |
| [D4] QCD from SS | R_OS/SS = 0.979, documented | PASS |
| [D5] Primary trigger | Used throughout | PASS |
| [D6] Z normalization 10-15% | 12% implemented | PASS |
| [D7] Loose tau ID | Implemented with optimization study | PASS |
| [D8] Anti-muon Tight | Implemented | PASS |
| [D9] MVA vs cut-based | NN + BDT comparison done | PASS |
| [D10] Baseline + VBF categories | Implemented | PASS |
| [D11] Common mu for categories | Implemented | PASS |
| [D12] SVfit not implemented | Documented limitation | PASS |
| [D13] NN MET regression dropped | Documented with justification | PASS |

All binding strategy commitments are fulfilled or formally downscoped with documentation.

---

## Checklist Summary

| Requirement | Status |
|-------------|--------|
| LaTeX math delimiters throughout | PASS |
| One subsection per systematic source | PASS (21 sources with subsections) |
| Per-cut event selection with distributions | PARTIAL (main cuts covered, minor cuts missing) |
| MVA diagnostics (ROC, overtraining, importance, data/MC) | PASS |
| Data/MC comparison for every selection variable | PASS (11 variables shown) |
| Fit diagnostic plots | PASS (NP pulls, GoF, post-fit comparisons) |
| Full covariance matrix in appendix | **FAIL** |
| Machine-readable results/ directory | **FAIL** |
| Comparison to published data with quantitative metric | PASS (pull = -0.13 sigma) |
| pixi.toml has `all` task | PASS |
| Experiment log non-empty | PASS (543 lines) |
| No empty sections | PASS (all sections have prose before figures) |
| Numerical self-consistency | **FAIL** (abstract + per-source impacts) |
| >= 15 unique citations | PASS (22 unique citation keys) |
| No local filesystem paths | PASS |
| No $\pm$ standalone math | PASS |
| Figure paths resolve | PASS |
| Page count in range | PASS (70 pages) |
| Validation summary table | PASS |
| Resolving power statement | PASS |
| Comparison overlay figure | PASS (@fig:mu-comparison-published, @fig:mu-comparison-all) |
| Systematic breakdown figure | PARTIAL (impact ranking shown, not fractional breakdown) |

---

## Verdict

**CONDITIONAL PASS** -- The AN is comprehensive (70 pages), well-structured, and contains the required physics content. The primary result is robustly presented with extensive validation. However, six Category A findings must be resolved before final acceptance:

1. Fix the abstract and line 1518 to use mu = 0.63 (not 0.64)
2. Update per-systematic subsection impact values to match current tables
3. Resolve the Asimov vs full-data labeling in the summary table
4. Add a `results/` directory with machine-readable outputs
5. Add covariance/correlation discussion (at minimum the NP correlation matrix)
6. Remove the two remaining phase labels from table headers

The Category B findings should be addressed but do not block acceptance.
