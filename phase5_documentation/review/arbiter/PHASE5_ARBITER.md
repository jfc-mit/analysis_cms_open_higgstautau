# Phase 5 Arbiter Verdict: CMS H->tautau Signal Strength Measurement

**Arbiter:** Phase 5 arbiter
**Date:** 2026-03-25
**Artifact:** `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.{md,tex,pdf}` (70 pages)
**Reviews adjudicated:** Physics, Critical, Constructive, Plot Validator, Rendering, BibTeX

---

## Executive Summary

Six reviewers produced a total of 14 Category A, 34 Category B, and 26 Category C findings. After independent verification and cross-reviewer adjudication, I consolidate these into **8 Category A** (must resolve), **15 Category B** (must fix before PASS), and **13 Category C** (suggestions to apply before commit). No regression triggers are tripped. The verdict is **ITERATE**.

The analysis note is comprehensive (70 pages), well-structured, and presents a credible measurement of mu(H->tautau) = 0.63 +/- 1.08 that is consistent with the SM and the published CMS result. The issues identified are all addressable within the current framework without phase regression.

---

## Regression Checklist (Mandatory)

- [x] **Validation test failures without 3 documented remediation attempts?** NO. The GoF p=0.000 failure has documented remediation: retry logic (14.8% -> 1.0% toy failures), LLR alternative test statistic, per-category decomposition, NP pull analysis. Three distinct remediation paths attempted.
- [x] **Single systematic > 80% of total uncertainty?** NO. Largest single systematic (MET unclustered, impact 0.285) is 26% of sigma(mu) = 1.08.
- [x] **GoF toy distribution inconsistent with observed chi2?** YES -- but investigated. Observed chi2 = 33.1 exceeds all 198 converged toys. Per-category chi2/bin values are individually acceptable (0.80-1.19). Investigation confirms this is genuine, arising from the known 5%/31% normalization deficits. The regression trigger is checked but NOT tripped because: (a) the per-category decomposition demonstrates the signal strength extraction is not biased, (b) per-category fits yield consistent mu values, (c) remediation attempts are documented. However, the AN must add an explicit coverage statement (see ADJ-A3 below).
- [x] **Flat-prior gate excluding > 50% of bins?** NO.
- [x] **Tautological comparison presented as independent validation?** NO. The Asimov signal injection tests (pull = 0.000) are correctly identified as workspace checks, though the body text overframes them (see ADJ-B2).
- [x] **Visually identical distributions that should be independent?** NO.
- [x] **Result > 30% relative deviation from reference?** NO. mu = 0.63 vs published mu = 0.78; pull = -0.13 sigma.
- [x] **All binding commitments [D1]-[D13] fulfilled?** YES. Critical reviewer confirmed all 13 strategy commitments are fulfilled or formally downscoped with documentation.
- [x] **Fit chi2 identically zero?** NO. On real data, chi2 = 33.1 (NN score). Asimov chi2 = 0 is by construction and correctly noted.

**No regression triggers fired.**

---

## Structured Adjudication Table

### Category A: Must Resolve (8 items)

| ID | Finding | Raised by | Corroborated | Arbiter independent verification | Final classification |
|----|---------|-----------|-------------|--------------------------------|---------------------|
| ADJ-A1 | Abstract says mu=0.64; body text says mu=0.63. JSON gives 0.6346 -> rounds to 0.63. | Physics (C5), Critical (F1), Constructive (A1) | 3/3 reviewers agree | **VERIFIED.** Lines 18, 1518 say 0.64; lines 1258, 1272, 1286, 1500, 1506, change log say 0.63. The JSON is authoritative: 0.6346 rounds to 0.63. | **A -- must fix.** Abstract + line 1518 must use 0.63. |
| ADJ-A2 | Per-systematic subsection impact values are stale (e.g., TES subsection says 0.376, Asimov table says 0.214) | Critical (F2), Constructive (A3) | 2/2 agree | **VERIFIED.** Subsection prose at lines 698, 704, 710, 716 quotes TES=0.376, MES=0.291, MET uncl=0.191, JES=0.165 -- none match the Asimov impact table at lines 762-778 (TES=0.214, MES=0.404, MET=0.354, JES=0.267). These are stale numbers from a pre-review iteration. | **A -- must fix.** Update all per-subsection impact values to match either the Asimov table or (preferably) the full-data table. |
| ADJ-A3 | GoF p=0.000: no explicit coverage statement about what this means for the uncertainty on mu | Physics (A1) | Only Physics raised | **VERIFIED.** The AN at lines 1414-1418 discusses the GoF failure thoroughly but never states the statistical implication: that a GoF failure means the profile likelihood uncertainty may not have correct frequentist coverage. The per-category analysis provides a robustness argument, but the explicit coverage caveat is missing. | **A -- must fix.** Add an explicit statement in both the GoF section and conclusions: "The GoF p=0.000 means the quoted uncertainty may not have nominal frequentist coverage. The per-category results (Baseline: 0.61 +/- 1.60, VBF: -0.04 +/- 1.34) provide a robustness check, as the Baseline-only result is consistent with the combined result and the Baseline category has acceptable per-category GoF." |
| ADJ-A4 | Missing results/ directory with machine-readable outputs | Critical (F4) | Only Critical raised | **VERIFIED.** No `results/` directory exists under `phase5_documentation/outputs/`. The methodology (`analysis-note.md`) and Phase 5 CLAUDE.md both require a `results/` directory with CSV/JSON for spectra, uncertainties, and covariance matrices. While `phase4_inference/4c_observed/outputs/` contains JSON results, the Phase 5 requirement is self-contained outputs. | **A -- must fix.** Create `phase5_documentation/outputs/results/` with (at minimum): observed_results.json, diagnostics_full.json, and the NP correlation matrix. Symlinks to Phase 4c outputs are acceptable if documented. |
| ADJ-A5 | Missing covariance/correlation matrix discussion | Critical (F5), Physics (B2 partial) | 2 reviewers raised related concerns | **VERIFIED.** Zero mentions of "covariance" or "correlation matrix" in the AN. The methodology specification requires the NP correlation matrix in an appendix. For a single-POI measurement the bin covariance is implicit in pyhf, but the NP correlation structure must be documented for the reader. | **A -- must fix.** Add a subsection or appendix with the post-fit NP correlation matrix (at minimum the top-10 most correlated pairs) and a brief discussion of the correlation structure. |
| ADJ-A6 | Phase labels remain in two table headers: "QCD (4a)" at line 1030, and "Expected (4a) / 10% data (4b) / Full data (4c)" at line 1284 | Critical (F6) | Only Critical raised | **VERIFIED.** Confirmed at lines 1030 and 1284. The change log claims phase labels were removed, but these two instances remain. | **A -- must fix.** Replace "(4a)" with "(Asimov)" or "(expected)" and "(4b)"/"(4c)" with "(10% subsample)"/"(full dataset)" in both table headers. |
| ADJ-A7 | Duplicate entries in systematic summary table: Z->tautau norm appears twice (0.097 and 0.036), "Missing bkg norm" (0.047) and "Missing backgrounds" (0.032) appear to be the same source | Constructive (A2) | Only Constructive raised | **VERIFIED.** Lines 797 and 805 both list "Z->tautau norm" with different impact values (0.097 and 0.036). Lines 803 and 807 list "Missing bkg norm" (0.047) and "Missing backgrounds" (0.032). The Asimov impact table (lines 762-778) lists Z->tautau norm once (0.097) and "Missing bkg norm" once (0.047). The duplicates at lines 805 and 807 appear to be the VBF-specific normalization variants that should have distinct names, or they should be removed. | **A -- must fix.** Resolve duplicates: either merge with correct values, or differentiate with labels (e.g., "Z norm (baseline)" vs "Z norm (VBF)"). |
| ADJ-A8 | gof_toys_10pct.pdf uses ax.set_title() and is missing the CMS experiment label | Plot validator (F1) | Only Plot validator raised | **VERIFIED independently** against plotting methodology rules. The `ax.set_title()` call and missing CMS label are both explicit violations of the mandatory plotting rules. | **A -- must fix.** Remove title, add CMS experiment label, and fix figsize to maintain standard aspect ratio. |

### Category B: Must Fix Before PASS (15 items)

| ID | Finding | Raised by | Final classification | Rationale |
|----|---------|-----------|---------------------|-----------|
| ADJ-B1 | Systematic summary table (@tbl:syst-summary) uses Asimov impacts, not full-data impacts, without clear labeling | Critical (F3) | **B** | The table caption says "Impact on mu" without specifying Asimov vs observed. The full-data impact table exists separately. The summary table should either be labeled "Asimov expected" or updated to full-data values. This is confusing but the values are internally consistent with the Asimov ranking table -- the issue is labeling, not correctness. Fix: Add "on Asimov data" to the summary table caption or update values. |
| ADJ-B2 | Signal injection tests are trivial (Asimov gives pull=0.000 by construction); validation summary table overframes them as "Fit unbiased" | Physics (B1), Critical (F12) | **B** | Two reviewers agree. The tests validate workspace algebra, not method robustness to statistical fluctuations. Fix: Relabel as "workspace sanity check" in the validation summary table and add a sentence acknowledging the construction. |
| ADJ-B3 | NP over-constraint discussion needed (TES to 0.18, MES to 0.32 on full data) | Physics (B2) | **B** | The TES constraint to 0.18 of its prior is unusually tight for a single channel. The AN discusses this for TES at line ~1537 but the full-data constraint (0.18) is even tighter than the Asimov constraint (0.26) discussed after template smoothing. A paragraph comparing to published analysis NP constraints would address this. |
| ADJ-B4 | Impact ranking reshuffling between Asimov and full data insufficiently discussed | Physics (B3) | **B** | TES drops from #4 (impact 0.214) to ~#15 (impact 0.025) -- a factor 8.5 reduction. The AN presents both tables but does not discuss the dramatic reshuffling. A brief paragraph comparing Tables @tbl:impact-ranking and @tbl:full-impact would close this gap. |
| ADJ-B5 | JES/MET propagation contradiction: Section 7.3 text says "with propagation to MET and re-evaluation of VBF categorization" but Table @tbl:syst-summary says "no MET" | Physics (B4) | **B** | Confirmed at line 794: the summary table lists JES as "Shape, +/-3% (no MET)". The subsection text at line 710 describes MET propagation through VBF categorization. This is a direct contradiction. Fix: Correct the summary table entry. |
| ADJ-B6 | norm_wjets_baseline has zero impact on mu despite +1.24 sigma pull | Physics (B5) | **B** | A NP pulled by 1.24 sigma with exactly zero impact is suspicious. This should be investigated and explained (likely near-perfect degeneracy with another NP or numerical precision issue). A brief note in the text would suffice. |
| ADJ-B7 | Back-of-envelope calculation needed for m_vis/m_col negative mu values | Physics (B6) | **B** | The quantitative argument (S/B ~ 0.003 means a 5% normalization offset produces ~19 units of mu shift) is important for the reader to understand why non-discriminating observables give order-10 negative mu. This is a 2-sentence addition. |
| ADJ-B8 | Z normalization uncertainty decomposition: quadrature sum gives 10.4%, not 12% | Critical (F13) | **B** | sqrt(4^2 + 5^2 + 8^2 + 2^2) = sqrt(109) = 10.4%. The text claims 12%. Either the decomposition is incomplete (missing a ~5-6% component) or the 12% is a deliberate conservative rounding. Fix: Either correct the decomposition or state explicitly that 12% includes a conservative rounding margin. |
| ADJ-B9 | NN feature table lists 15 rows but text says 14 features | Critical (F14 as C), Constructive (B3) | **B (upgraded from C)** | Two reviewers independently caught this discrepancy. The count matters for the NN architecture description. Fix: Count features correctly and reconcile text with table. |
| ADJ-B10 | Absolute numeric fontsize in 6+ plotting scripts | Plot validator (F2) | **B** | Widespread use of fontsize=8, 10, 12 across multiple scripts. Per methodology, numeric font sizes are prohibited. These should use relative string sizes. The figures are currently legible, so this is B not A. |
| ADJ-B11 | "Figures 1 through Figure 1" confusion from composited tau ID plots | Rendering (B4) | **B** | This is a rendering artifact that produces confusing text on page 8. Fix: Rewrite to use panel references "Figure 1(a)", "Figure 1(b)", "Figure 1(c)". |
| ADJ-B12 | Overfull hbox (33pt) from wide inline quadrature sum formula | Rendering (B2) | **B** | The formula at lines 2265-2275 extends 33pt past the right margin. Fix: Convert to a display equation. |
| ADJ-B13 | "Figures X through Figure Y" awkward cross-reference phrasing (3 instances) | Rendering (B3) | **B** | Pandoc-crossref artifact producing awkward "Figures 31 through Figure 33" instead of "Figures 31-33". Fix in the markdown source. |
| ADJ-B14 | Suspicious orphan BibTeX entries: Gaiser:1982yw and Li:1983fv have unverifiable metadata | BibTeX (A2, A3) | **B (downgraded from A)** | These entries are orphans -- not cited in the AN. Their presence is harmless to compilation. The suspicious titles are a hygiene concern but do not affect the rendered document. Fix: Remove both entries. Cost: 2 minutes. |
| ADJ-B15 | Ellis:1987xu is an orphan book typed as @article; pyhf_joss and ParticleDataGroup:2022pth are orphans | BibTeX (A1, B3, B4) | **B** | Five orphan entries in the BibTeX file. None affect compilation or the rendered bibliography. Fix: Remove orphans that are not needed; for PDG, either cite it (SM constants are used) or remove. For pyhf_joss, either cite alongside pyhf or remove. |

### Category C: Suggestions (13 items)

| ID | Finding | Source | Note |
|----|---------|--------|------|
| ADJ-C1 | Cross-section era difference (YR4 vs NNLO+NNLL) not mentioned when comparing mu values | Physics (C1) | Minor but worth a sentence in the comparison section. |
| ADJ-C2 | Tau fake rate shape not acknowledged as a potential limitation | Physics (C2) | One sentence acknowledging normalization-only treatment may undercover shape effects. |
| ADJ-C3 | Trigger turn-on: no study possible, should state explicitly | Physics (C3) | State that no trigger efficiency measurement was possible with Open Data. |
| ADJ-C4 | b-veto design choice not discussed | Physics (C4) | Brief sentence explaining the choice. |
| ADJ-C5 | Published comparison could use per-channel mu_tau_h result if available | Physics (B7) | Downgraded to C: the full combination is a valid comparison target. The per-channel result may not be published separately. Worth checking but not blocking. |
| ADJ-C6 | "the the" typos at lines 270 and 1294 | Critical (F16), Constructive (B1) | Trivial fix. |
| ADJ-C7 | Prose reference to internal investigation artifacts at line 1418 | Constructive (B2) | Replace glob-pattern file references with proper figure cross-references or remove. |
| ADJ-C8 | More standalone figures (30) than composites (22) in the rendered PDF | Rendering (B1) | The spec prefers more composites. Several runs of 3+ standalone figures could be merged. Not blocking given the 70-page count is within range. |
| ADJ-C9 | Inconsistent math delimiter ($<$ vs \( ) at line 761 | Rendering (C1) | Cosmetic. |
| ADJ-C10 | Broken cross-refs in alt text attributes (invisible in PDF) | Rendering (C2) | Accessibility metadata only; invisible to readers. |
| ADJ-C11 | Add pileup validation figure (pv_npvs.pdf exists but is not referenced) | Constructive (C1) | Good suggestion -- the figure exists and would support the "<2% impact" claim. |
| ADJ-C12 | Include VBF-specific kinematic distributions (vbf_mjj, vbf_deta) to support VBF deficit discussion | Constructive (C10 partial) | Would strengthen the VBF deficit section, which is an important part of the AN. |
| ADJ-C13 | Scikit-learn BibTeX entry missing DOI/URL; Cranmer:2012sba should be @techreport | BibTeX (B1, B2) | Bibliographic hygiene. |

---

## Dismissed Findings (with justification)

| ID | Finding | Source | Dismissal rationale |
|----|---------|--------|-------------------|
| None | | | All findings are accepted. No dismissals. |

All findings from all six reviewers are either accepted at their original severity, upgraded, or downgraded with stated rationale. No findings are dismissed. The arbiter cannot dismiss findings when the fix is < 1 hour of agent time, and all findings above meet this criterion.

---

## Cross-Reviewer Agreement Analysis

**Strong agreement (3+ reviewers):**
- ADJ-A1 (mu=0.64 vs 0.63): Physics, Critical, Constructive all flagged this. Unanimous -- accept at A.

**Two-reviewer agreement:**
- ADJ-A2 (stale subsection impacts): Critical and Constructive. Both independently identified the same discrepancy. Accept at A.
- ADJ-B2 (signal injection trivial): Physics and Critical. Accept at B.
- ADJ-B9 (14 vs 15 features): Critical and Constructive. Upgraded from C to B due to corroboration.

**Single-reviewer findings verified independently:**
- ADJ-A3 (GoF coverage): Only Physics raised. Verified: no "coverage" or "frequentist" appears in the AN. Accept at A.
- ADJ-A4 (results/ directory): Only Critical raised. Verified: directory does not exist. Accept at A.
- ADJ-A5 (covariance matrix): Only Critical raised. Verified: zero mentions. Accept at A.
- ADJ-A8 (gof_toys_10pct plot violations): Only Plot validator raised. Verified against methodology rules. Accept at A.

**Severity changes:**
- BibTeX A2, A3 (suspicious orphan entries) -> ADJ-B14: Downgraded because they are orphans with no impact on the rendered document.
- BibTeX A1 (Ellis:1987xu wrong type) -> ADJ-B15: Downgraded; orphan with no impact on output.
- Physics B7 (per-channel comparison) -> ADJ-C5: Downgraded; the full combination is a valid comparison target.
- Critical F14 (14 vs 15 features) -> ADJ-B9: Upgraded from C to B due to corroboration from Constructive.

---

## Motivated Reasoning Check

The arbiter must check whether the verdict is influenced by desire to pass the analysis rather than genuine assessment:

1. **Am I minimizing Category A findings?** No. I have 8 Cat A items, which is a substantial list. I did not downgrade any finding from A to B unless the impact on the rendered document is demonstrably zero (BibTeX orphans).

2. **Am I accepting weak reviewer PASSes?** No. The Physics reviewer said ITERATE, the Critical reviewer said CONDITIONAL PASS (meaning iterate), the Constructive reviewer found 3 Cat A items, the Plot validator said FAIL, the Rendering reviewer said PASS with B items, and the BibTeX reviewer said CONDITIONAL PASS. The overall picture is ITERATE.

3. **Am I dismissing valid findings as "out of scope"?** No. Zero findings dismissed. All are accepted.

4. **Would a journal referee accept this AN in its current state?** No. The stale numbers in the per-systematic subsections (ADJ-A2), the inconsistent primary result in the abstract (ADJ-A1), and the missing coverage statement (ADJ-A3) would all be caught in peer review. The missing covariance discussion (ADJ-A5) and missing machine-readable outputs (ADJ-A4) are checklist requirements.

5. **Are the Category B items genuinely B, or should any be A?** Reviewed each: the B items are clarity and completeness improvements that weaken the AN but do not introduce incorrect statements. The A items are factual errors, missing required content, or methodology violations.

---

## Cost Estimates for Fixes

| Priority | Items | Estimated agent time | Approach |
|----------|-------|---------------------|----------|
| Cat A fixes | ADJ-A1, A2, A5, A6, A7 | 30-45 min | Note writer: text edits (numbers, labels, add covariance subsection) |
| Cat A fixes | ADJ-A3 | 15 min | Note writer: add coverage paragraph to GoF section and conclusions |
| Cat A fixes | ADJ-A4 | 15 min | Executor: create results/ directory with symlinks and documentation |
| Cat A fixes | ADJ-A8 | 20 min | Executor: fix plotting script, regenerate figure |
| Cat B fixes | ADJ-B1 through B15 | 60-90 min | Note writer (B1-B9, B11-B13), executor (B10), BibTeX edits (B14-B15) |
| Cat C fixes | ADJ-C1 through C13 | 30-45 min | Note writer: sentence additions and minor edits |
| Recompile | PDF recompilation | 10 min | Typesetter |
| **Total** | | **~3-4 hours** | |

---

## Verdict

**ITERATE.**

The analysis note is comprehensive, the physics is credible, and the primary result (mu = 0.63 +/- 1.08) is well-supported. However, 8 Category A findings must be resolved before PASS:

1. **ADJ-A1:** Fix abstract and line 1518 to use mu = 0.63 (not 0.64)
2. **ADJ-A2:** Update all per-systematic subsection impact values to match the current impact ranking tables
3. **ADJ-A3:** Add explicit GoF coverage statement to the GoF section and conclusions
4. **ADJ-A4:** Create `results/` directory with machine-readable outputs
5. **ADJ-A5:** Add NP correlation matrix discussion (subsection or appendix)
6. **ADJ-A6:** Remove remaining phase labels "(4a)", "(4b)", "(4c)" from table headers
7. **ADJ-A7:** Resolve duplicate entries in the systematic summary table
8. **ADJ-A8:** Fix gof_toys_10pct.pdf: remove title, add CMS label, fix figsize

Additionally, 15 Category B items must be fixed before final PASS. These are all tractable: text edits, number reconciliation, bibliographic cleanup, and one plotting script fix.

**No regression triggers are fired.** All issues are addressable within the Phase 5 framework. After fixes, the PDF must be recompiled and a re-review (1-bot: critical reviewer + plot validator) is recommended to verify the fixes are complete and no new issues were introduced.

**Recommended fix order:**
1. Note writer: address all text-level Cat A and Cat B items in a single pass
2. Executor: fix the plotting script (ADJ-A8, ADJ-B10) and create results/ directory (ADJ-A4)
3. BibTeX cleanup (ADJ-B14, ADJ-B15, ADJ-C13)
4. Typesetter: recompile PDF
5. Re-review (1-bot)
