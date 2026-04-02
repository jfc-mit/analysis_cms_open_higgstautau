# Phase 3 Critical Review: H->tautau Selection

**Reviewer:** Critical reviewer (1-bot)
**Artifact:** `phase3_selection/outputs/SELECTION.md`
**Date:** 2026-03-24

---

## Summary

Phase 3 delivers a competent event selection, background estimation, NN discriminant training, collinear mass implementation, and three-approach comparison. The Strategy decision labels are largely fulfilled. However, several significant issues must be addressed before advancement. The most critical are: (1) the NN score data/MC plot is missing the QCD template, creating a systematic data/MC mismatch visible in the plot; (2) no alternative NN architecture was trained as required by the Phase 3 CLAUDE.md; (3) no quantitative data/MC chi2 assessment on NN input variables is provided; and (4) VBF category thresholds deviate from Strategy without formal decision revision.

---

## Category A Findings (Must Resolve)

### A1. Missing alternative NN architecture

The Phase 3 CLAUDE.md explicitly requires: "Train >=1 alternative architecture (NN if BDT, vice versa)" and the pre-review self-check lists "For MVA: input variable quality gate table, >=1 alternative architecture." Only a single scikit-learn MLPClassifier was trained. No BDT or alternative architecture comparison is present. This is a mandatory checklist item.

**Required action:** Train at least one alternative classifier (e.g., BDT via scikit-learn GradientBoostingClassifier or similar) and report a quantitative comparison (AUC, expected significance) against the primary NN.

### A2. No NN input variable data/MC quality gate table

The review methodology (Section 6.4) states: "Any input with data/MC chi2/ndf > 5 that enters the classifier without documented justification or calibration is Category A." The SELECTION.md Section 8 states data/MC comparisons were produced but provides no quantitative chi2/ndf assessment for any of the 14 NN input variables. The NN was trained without documenting whether the inputs are well-modeled.

Data/MC kinematic plots exist for 5 of the 14 inputs (tau_pt, mu_pt, met_pt, njets, delta_r) in the Baseline category. Missing entirely: mu_eta, tau_eta, met_significance, mvis (as NN input validation separate from approach comparison), mt, delta_phi_mutau, lead_jet_pt, lead_jet_eta, nbjets.

**Required action:** Produce a quality gate table listing chi2/ndf (data vs MC) for all 14 NN input variables in the signal region. Document any variable with chi2/ndf > 5 and either justify its inclusion, apply a calibration, or remove it.

### A3. NN score data/MC plot missing QCD contribution

The NN score data/MC comparison (nn_score_baseline.pdf, nn_score_vbf.pdf) does not include the QCD template. This is visible in the plot: data systematically exceeds MC across most NN score bins in the Baseline category. The code in `07_plots.py` line 302 explicitly comments "# QCD for NN: we don't have NN scores for SS data easily, skip QCD for now." This is not acceptable -- the QCD template is a known ~11,000 event contribution. Without it, the NN score data/MC agreement cannot be assessed, and this is the primary fitting observable.

**Required action:** Compute NN scores for SS data and SS MC events (this requires running the trained NN on the SS region npz files). Produce NN score data/MC plots with the QCD template included. Report the data/MC chi2/ndf for the NN score distribution.

### A4. VBF category thresholds changed from Strategy without formal revision

The Strategy [D10] specifies VBF category requirements of mjj > 300 GeV and |delta_eta_jj| > 2.5. The SELECTION.md Section 4 uses mjj > 200 GeV and |delta_eta_jj| > 2.0. The Phase 2 exploration (Section 8.2) optimized these thresholds and found the looser values give better S/sqrt(B), which is a legitimate optimization. However, this constitutes a change to a [D]-labeled strategy decision. The artifact does not note this deviation or reference a formal strategy revision.

**Required action:** Either document this as a formal strategy revision (noting the Phase 2 optimization result that motivated the change and updating STRATEGY.md) or revert to the committed thresholds. A binding decision [D10] cannot be silently modified -- it must be explicitly revised with documented justification per the methodology.

---

## Category B Findings (Must Fix Before PASS)

### B1. Cutflow shows dR > 0.5 cut removes zero events

The cutflow table (Section 2.1) shows identical counts for "OS pair" and "dR > 0.5" rows across all samples (e.g., ggH: 8,069 -> 8,069, DY: 63,279 -> 63,279). This means the dR cut is entirely redundant given the preceding selections. While this is not wrong (the pair selection naturally produces well-separated pairs), the cut should either be documented as a sanity check that removes no events (not a selection criterion) or investigated to confirm no events are lost. As stated, it inflates the cutflow with a no-op step, which is misleading.

**Required action:** Add a note to the cutflow explaining that dR > 0.5 is inherently satisfied by the pair selection criteria and tau/muon eta requirements. Do not present it as an active selection step in the monotonic cutflow.

### B2. Collinear mass template uses m_vis as QCD proxy

In `07_plots.py` line 316, the QCD template for the collinear mass plot uses `lambda d, sn: d["mvis"]` as a proxy rather than the actual collinear mass values. This means the QCD shape in the mcol distribution is wrong -- it shows the visible mass shape, not the collinear mass shape. Since the collinear mass is being evaluated as a fitting approach, its data/MC plot must use the correct QCD template shape.

**Required action:** Compute collinear mass values for SS data and SS MC events and use those for the QCD template in the mcol data/MC plots. Alternatively, if collinear mass values are already saved for SS regions, use them directly.

### B3. Overtraining check plot uses ax.bar instead of mplhep histplot

The overtraining check plot (`nn_overtraining.pdf`, `04_nn_discriminant.py` line 291-299) uses `ax.bar()` for train distributions and `ax.errorbar()` for test distributions. The methodology requires `mh.histplot()` for all binned data (plotting rule from `appendix-plotting.md`). Additionally, the error bar calculation `yerr=np.sqrt(h_sig_test / max(len(sig_test), 1))` appears incorrect -- this divides the bin height by the total number of events, which does not give the correct Poisson uncertainty for normalized density histograms.

**Required action:** Use `mh.histplot()` for the overtraining distributions. Fix the error bar calculation for density-normalized histograms.

### B4. W+jets SF uncertainty formula may undercount

The SF_W statistical uncertainty in `02_background_estimation.py` line 101 is computed as `sqrt(N_data + N_non_w_mc) / N_W_MC`. This treats the MC statistical uncertainty as Poisson on raw counts, but the non-W MC events have non-unit weights. The correct uncertainty propagation should account for weighted MC statistics: `sum(w_i^2)` rather than `sum(w_i)` for the MC variance term. Given that DY events have weight ~1.3 and W+jets events have weight ~0.5-2.5, this could materially affect the uncertainty estimate.

**Required action:** Use proper weighted uncertainty propagation for the SF_W calculation, or document that the current formula is approximate and verify the impact is small.

### B5. Missing data/MC plots for VBF category kinematic variables

The SELECTION.md Section 8 states "Data/MC comparison plots were produced for all discriminant variables in both Baseline and VBF categories." However, the code in `07_plots.py` (lines 321-332) produces kinematic variable plots only for the Baseline category (tau_pt, mu_pt, met_pt, njets, delta_r). The VBF category gets only mvis, nn_score, and mcol plots. Given that the VBF category has very different background composition (ttbar is a much larger fraction), kinematic variable data/MC checks in the VBF category are necessary.

**Required action:** Produce tau_pt, mu_pt, met_pt, njets, and delta_r data/MC plots for the VBF category.

### B6. Approach comparison does not use consistent QCD treatment

In `06_approach_comparison.py`, the cut-based approach (line 108) estimates QCD in the Higgs window as `qcd_yield * 0.2` -- a rough 20% estimate with no basis. The NN approach does not include QCD at all (background histograms sum only MC). The collinear mass approach also omits QCD. These inconsistencies undermine the quantitative comparison. If QCD is ~16% of the total background (11,200 / 72,111), ignoring it systematically biases the significance estimates.

**Required action:** Apply consistent QCD treatment across all three approaches in the comparison. Use the actual QCD template shape for each observable.

---

## Category C Findings (Suggestions)

### C1. OS/SS ratio below both reference values

The measured OS/SS ratio of 0.979 is below both the tutorial value (0.80 -- note: this seems inverted in the artifact; 0.80 would mean more SS than OS, which is unusual for QCD) and the published analysis value (1.06). The artifact states the measured value "is between these," but 0.979 is actually above 0.80 and below 1.06. This is consistent but the phrasing is ambiguous. The measured OS/SS ratio < 1 means slightly more QCD in SS than OS, which is somewhat unusual -- typically QCD has OS/SS >= 1. This warrants a brief discussion of whether the MC subtraction in the anti-isolated region might be biased.

### C2. Zeppenfeld centrality disposition unclear

The Phase 2 exploration (Section 8.3) evaluated the Zeppenfeld centrality cut and decided to retain it as a "soft cut" at zep < 1.0. However, the Phase 3 VBF category definition (Section 4) does not mention any Zeppenfeld requirement. The variable is computed in the code but apparently not applied. The disposition of this variable should be clarified -- is it applied as a VBF category cut, used as an NN input, or dropped entirely?

### C3. Signal shown as step histogram, not mplhep histplot

In `07_plots.py` line 187, the signal is drawn with `ax.step()` which is listed as a disallowed function in the plotting rules ("never `ax.step()`, `ax.bar()`"). Use `mh.histplot()` with `histtype='step'` instead.

### C4. Feature importance methodology is weak

The NN feature importance (Section 6, figure `nn_feature_importance.pdf`) uses first-layer weight magnitudes as a proxy for importance. This is a known poor estimator for neural networks -- it does not account for feature scaling (StandardScaler was applied, so scales are normalized, but the relationship between weight magnitude and feature contribution is still nonlinear). Consider permutation importance or SHAP values for a more reliable ranking.

### C5. Expected significance formula is inclusive, not per-category

The approach comparison (Section 5.2) reports a single expected significance per approach, computed over the inclusive OS SR. The analysis uses two categories (Baseline + VBF) with different S/B ratios. The comparison should compute per-category significance and combine them to properly reflect the analysis strategy.

### C6. Figure captions in artifact are single sentences

The SELECTION.md Section 10 figure captions are typically one sentence (e.g., "Visible di-tau mass distribution in the Baseline category, showing data (points), stacked MC backgrounds with DY decomposition and QCD template, and signal scaled by x10"). The methodology requires 2-5 sentences per caption.

---

## Strategy Decision Verification

| Decision | Status | Issues |
|----------|--------|--------|
| [D1] Four approaches, now three per [D13] | PASS | Three approaches compared; NN MET regression correctly dropped |
| [D3] W+jets from high-mT | PASS | SF = 0.999 +/- 0.005, mid-mT validation done |
| [D4] QCD from SS with measured OS/SS | PASS | R = 0.979 +/- 0.018, measured from anti-iso CR |
| [D7] Tau ID: Loose | PASS | Implemented correctly |
| [D8] Anti-muon: Tight | PASS | Implemented correctly |
| [D9] MVA vs cut-based comparison | PARTIAL | Comparison done but no alternative architecture (A1) |
| [D10] Baseline + VBF categories | FAIL | VBF thresholds changed from 300/2.5 to 200/2.0 without revision (A4) |
| [D13] NN MET regression dropped | PASS | Properly documented as negative result |

---

## Plot Validation

| Figure | Issue | Severity |
|--------|-------|----------|
| nn_score_baseline.pdf | Missing QCD template; data excess visible | A3 |
| nn_overtraining.pdf | Uses ax.bar instead of mplhep histplot; error bars incorrect | B3 |
| All signal curves | Uses ax.step() instead of mh.histplot | C3 |
| mcol_baseline.pdf, mcol_vbf.pdf | QCD template uses wrong variable (mvis instead of mcol) | B2 |
| mvis_baseline.pdf | Good quality; DY decomposition and QCD visible; data/MC reasonable | OK |
| mvis_vbf.pdf | VBF category shows data systematically below MC; investigate | Note |
| nn_roc.pdf | Clean; train/val/test curves consistent | OK |
| approach_comparison.pdf | Clean horizontal bar chart | OK |

---

## Regression Check

No regression triggers identified. The issues found are within Phase 3 scope and can be fixed locally:
- No data/MC disagreement that traces to Phase 2 object definitions
- No background model failure requiring strategy revision
- The VBF threshold change (A4) is a Strategy consistency issue, not a physics issue requiring upstream rework

---

## Verdict

**FAIL** -- 4 Category A issues must be resolved before advancement. The most critical are A1 (missing alternative architecture), A2 (missing input quality gate), and A3 (missing QCD in NN score plots), all of which are explicitly required by the methodology and Phase 3 CLAUDE.md checklist. A4 (VBF threshold revision) is a process compliance issue. The 6 Category B items should be fixed in the same iteration. After addressing all A and B items, re-review is required.
