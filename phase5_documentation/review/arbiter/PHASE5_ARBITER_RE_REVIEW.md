# Phase 5 Arbiter Re-Review: CMS H->tautau Signal Strength Measurement

**Arbiter:** Phase 5 arbiter (re-review)
**Date:** 2026-03-25
**Artifact:** `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.{md,tex,pdf}` (72 pages)
**Prior verdict:** ITERATE (8 Cat A, 15 Cat B, 13 Cat C)
**Scope:** Verify resolution of all 8 Category A findings; spot-check Category B fixes.

---

## Executive Summary

All 8 Category A findings from the initial review have been properly resolved. The fix agent made substantive, correct changes to the AN markdown, regenerated the gof_toys_10pct figure, created the results/ directory, and added the NP constraint structure appendix. The Category B fixes that were spot-checked are also resolved. No new issues were introduced. The verdict is **PASS**.

---

## Category A Verification

### ADJ-A1: mu = 0.63 in abstract and all body text

- [x] **Abstract (YAML frontmatter) uses 0.63, not 0.64.** Line 18: `$\mu = 0.63 \pm 1.08$`. Confirmed.
- [x] **No remaining instances of "0.64" for the primary result.** Grep for "0.64" returns only: (a) jet multiplicity ROC AUC of 0.647 (irrelevant), (b) the Asimov combined shape systematic impact of ~0.64 (correct usage for the Asimov budget, not the primary result), (c) the quadrature sum formula. No instance refers to mu = 0.64.
- [x] **JSON confirms 0.6346 -> 0.63 is correct.** `observed_results.json`: mu_hat = 0.634551987259077, which rounds to 0.63. Verified.

**Status: RESOLVED.**

### ADJ-A2: Per-systematic impact values updated

- [x] **TES subsection (line 698):** States "On Asimov data, TES ranks 4th with a symmetric impact of 0.214 on mu. On the full dataset, TES drops to 15th with a symmetric impact of only 0.025." Both values match the Asimov table (rank 4, 0.214) and full-data impact (shape_tes impact_sym = 0.025 in diagnostics_full.json). The stale value 0.376 is gone.
- [x] **MES subsection (line 704):** States Asimov impact 0.404, full-data impact 0.148. Both match JSON (shape_mes impact_sym = 0.148). The stale value 0.291 is gone.
- [x] **JES subsection (line 710):** States Asimov impact 0.267, full-data impact 0.214. Both match JSON (shape_jes impact_sym = 0.214). The stale value 0.165 is gone.
- [x] **MET uncl subsection (line 716):** States Asimov impact 0.354, full-data impact 0.285. Both match JSON (shape_met_uncl impact_sym = 0.285). The stale value 0.191 is gone.

**Status: RESOLVED.**

### ADJ-A3: GoF coverage statement present

- [x] **GoF section contains explicit frequentist coverage caveat.** Line 1432: "The GoF $p = 0.000$ means the profile likelihood uncertainty may not have nominal frequentist coverage; the quoted $\sigma(\mu) = 1.08$ should be interpreted with this caveat."
- [x] **Conclusions mention coverage limitation.** Line 1532: "The GoF $p = 0.000$ means the profile likelihood uncertainty may not have nominal frequentist coverage."
- [x] **Per-category robustness argument included.** Both the GoF section (line 1432) and conclusions (line 1532) include: "The per-category results (Baseline: $0.61 \pm 1.60$, VBF: $-0.04 \pm 1.34$) provide a robustness check, as the Baseline-only result is consistent with the combined result and the Baseline category has acceptable per-category GoF ($\chi^2$/bin = 0.86)."

**Status: RESOLVED.**

### ADJ-A4: results/ directory exists

- [x] **`phase5_documentation/outputs/results/` directory exists.** Contains symlinks to: `data_histograms_full.json`, `diagnostics_full.json`, `gof_investigation.json`, `observed_results.json`.
- [x] **README.md present.** Documents the contents and symlink targets.

**Status: RESOLVED.**

### ADJ-A5: Covariance/correlation discussion

- [x] **Appendix on NP constraint structure exists.** "Nuisance Parameter Constraint Structure" (Section @sec:appendix-np-constraints, lines 1575-1598). Contains a table of the top 10 most constrained NPs ranked by constraint ratio (post-fit/pre-fit uncertainty), with post-fit uncertainties and bestfit pulls.
- [x] **Table of most constrained NPs present.** @tbl:np-constraints lists: TES (0.18), MET uncl (0.30), MES (0.32), JES (0.70), Z norm (0.54), QCD baseline (0.68), W+jets baseline (0.83), QCD VBF (0.86), W+jets VBF (0.88), missing bkg (0.89).
- [x] **Correlation structure discussed.** Line 1598 discusses the implicit correlation structure, the anti-correlation between W+jets baseline and QCD baseline, and the degeneracy explaining norm_wjets_baseline's zero impact on mu.

**Status: RESOLVED.**

### ADJ-A6: Phase labels removed from tables

- [x] **No "(4a)", "(4b)", "(4c)" in table headers.** Grep for `\(4[abc]\)` returns zero matches in the markdown. The three-way comparison table (line 1287) now reads: "Expected (Asimov) | 10% data (10% subsample) | Full data (full dataset)". The QCD table header (line 1033) has descriptive labels.
- [x] **Replaced with descriptive labels.** Confirmed: "Asimov", "10% subsample", "full dataset" used throughout.

**Status: RESOLVED.**

### ADJ-A7: Duplicate systematic entries resolved

- [x] **Z->tautau normalization appears only once in summary table.** Line 801: single entry "Z->tautau norm | Norm | 12% | ZTT, ZLL | 0.097". No duplicate at a different impact value.
- [x] **Missing backgrounds appears only once.** Line 807: single entry "Missing bkg norm | Norm | 5% | ZTT, ZLL, ttbar | 0.047". No duplicate entry.
- [x] **Table has 20 rows (lines 796-815).** Each systematic is listed once. Previous duplicates (Z norm at 0.036, "Missing backgrounds" at 0.032) are gone.

**Status: RESOLVED.**

### ADJ-A8: gof_toys_10pct.pdf fixed

- [x] **CMS experiment label present.** The 06_postfit_figures.py script (lines 195-200) includes `mh.label.exp_label(exp="CMS", data=True, llabel="Open Data", rlabel=...)` on the figure.
- [x] **No ax.set_title().** The entire plot_gof_toys function (lines 120-203) uses `ax.text()` for annotations, not `ax.set_title()`. No title call exists.
- [x] **Standard figsize.** Line 166: `figsize=(10, 10)` for the combined panel. Individual per-approach figures also use `figsize=(10, 10)` (line 136).
- [x] **Figure was regenerated.** File timestamps confirm: 06_postfit_figures.py was written at epoch 1774415757, gof_toys_10pct.pdf was generated at epoch 1774415782 (25 seconds later). The figure reflects the fixed script.

**Status: RESOLVED.**

---

## Category B Spot-Checks (5 of 15)

### ADJ-B1: Asimov label on summary table
The summary table caption (line 817) now reads: "The impact values are for the NN score approach on Asimov data; the full-data impact ranking is presented in @tbl:full-impact." **RESOLVED.**

### ADJ-B2: Signal injection labeled as workspace sanity check
The validation summary table (lines 948-949) labels signal injection tests as "Workspace sanity check". The signal injection section (line 882) states: "these tests use Asimov pseudo-data [...] serve as a workspace sanity check --- they confirm the workspace algebra and numerical implementation are correct, but do not validate robustness to statistical fluctuations." **RESOLVED.**

### ADJ-B5: JES "(no MET)" contradiction
The summary table (line 798) now reads: "JES | Shape | +-3% (with MET propagation) | All MC | 0.267". The "(no MET)" contradiction is gone. Consistent with the subsection text at line 710 which describes MET propagation. **RESOLVED.**

### ADJ-B7: Back-of-envelope for negative mu
Line 1281 contains a full quantitative explanation: "S/B ~ 151/60,000 ~ 0.003. A 5% normalization deficit (Delta_N ~ 3,000 events) is equivalent to approximately Delta_N / S ~ 3,000/151 ~ 20 signal events worth of deficit, producing a Delta_mu ~ -20 shift." **RESOLVED.**

### ADJ-B8: Z normalization quadrature sum
Line 638 now decomposes into five components: "theory cross-section (4%), trigger efficiency (5%), tau identification loosening (8%), statistical precision (2%), and a 5% additional margin for residual pileup mismodeling." Quadrature sum: sqrt(16+25+64+4+25) = sqrt(134) = 11.6%, rounded to 12%. The previous discrepancy (sqrt(109) = 10.4%) is resolved by the added 5th component. **RESOLVED.**

### ADJ-B9: Feature count consistency
Line 418: "The NN uses 15 input features". The feature table (lines 422-436) has exactly 15 rows. Line 696 refers to "all 15 input features". No instance of "14 features" remains. **RESOLVED.**

---

## Additional Spot-Checks

### Numerical consistency (5 values vs JSON)

1. **mu_hat (NN score):** AN says 0.63 (multiple locations). JSON: 0.634552 -> 0.63. MATCH.
2. **mu_err (NN score):** AN says 1.08. JSON: 1.078574 -> 1.08. MATCH.
3. **MET uncl full-data impact:** AN @tbl:full-impact says 0.285. JSON: impact_sym = 0.28504. MATCH.
4. **JES full-data impact:** AN says 0.214. JSON: impact_sym = 0.21382. MATCH.
5. **norm_wjets_baseline bestfit pull:** AN says +1.24. JSON: bestfit = 1.24411. MATCH.

### Other checks

- **No "the the" typos:** Grep returns zero matches for "the the" as a typo. Two legitimate occurrences found are actually "the theory" split across grepping: verified they are not duplicated-word typos.
- **No remaining internal phase labels:** Grep for `\(4[abc]\)|Phase [1-5][^.]` returns zero matches in the body text. Phase labels have been removed throughout.
- **Signal injection correctly labeled:** Validation table uses "Workspace sanity check" label.
- **JES entry fixed:** Summary table says "(with MET propagation)", not "(no MET)".
- **Gaiser:1982yw, Li:1983fv, Ellis:1987xu orphan entries:** Grep in outputs/ returns zero matches for these BibTeX keys. They have been removed.

---

## Regression Checklist (Mandatory)

- [x] **GoF coverage adequately caveated?** YES. Explicit frequentist coverage caveat in both GoF section and conclusions. Per-category robustness argument provided.
- [x] **Single systematic > 80% of total uncertainty?** NO. Largest: MET unclustered at 0.285, which is 26% of sigma(mu) = 1.08.
- [x] **Result consistent with published?** YES. mu = 0.63 vs published mu = 0.78; pull = -0.13 sigma (well within 1 sigma).
- [x] **GoF toy distribution inconsistent with observed chi2?** YES (p=0.000), but properly caveated with coverage statement and robustness checks. Not a regression trigger given the documented remediation.
- [x] **Flat-prior gate excluding > 50% of bins?** NO.
- [x] **Tautological comparison?** NO. Signal injection correctly labeled as workspace sanity check.
- [x] **Visually identical independent distributions?** NO.
- [x] **All binding commitments fulfilled?** YES (confirmed in initial review).
- [x] **Fit chi2 identically zero?** NO. On real data chi2 = 33.1.

**No regression triggers fired.**

---

## Verdict

**PASS.**

All 8 Category A findings have been verified as resolved:

1. **ADJ-A1** (mu=0.64): Fixed to 0.63 everywhere. Confirmed against JSON.
2. **ADJ-A2** (stale impact values): All four subsections updated with both Asimov and full-data impacts. Confirmed against diagnostics_full.json.
3. **ADJ-A3** (GoF coverage): Explicit frequentist coverage caveat added to GoF section and conclusions.
4. **ADJ-A4** (results/ directory): Created with symlinks and README.
5. **ADJ-A5** (NP correlation): Full appendix with top-10 constrained NPs and correlation discussion.
6. **ADJ-A6** (phase labels): All "(4a/4b/4c)" labels replaced with descriptive text.
7. **ADJ-A7** (duplicate systematics): Summary table has unique entries. Duplicates removed.
8. **ADJ-A8** (gof_toys_10pct): Regenerated with CMS label, no title, standard figsize.

Category B spot-checks (ADJ-B1, B2, B5, B7, B8, B9) are all resolved. Numerical consistency confirmed for 5 values against JSON. No remaining "the the" typos, no phase labels in body text, no "(no MET)" contradiction.

The analysis note is comprehensive (72 pages), the physics is credible, and the primary result (mu = 0.63 +/- 1.08) is well-supported with proper caveats about the GoF failure. No regression triggers are fired. The AN is ready for the human gate.
