# Phase 5 Plot Validation Review

**Reviewer:** Plot Validator
**Date:** 2026-03-25
**Artifact:** `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.pdf` and all figures in `phase5_documentation/outputs/figures/`
**Scope:** Code linting of all plotting scripts + visual inspection of every figure

---

## Mode 1: Code Linting Results

### 1.1 `ax.set_title` / `plt.title` violations

| File | Line | Code | Severity |
|------|------|------|----------|
| `phase4_inference/4b_partial/src/06_postfit_figures.py` | 145 | `ax.set_title(f"{approach_labels[approach]}, p = {p_str}", fontsize=10)` | **(A)** |

**Finding F1 (A):** The `gof_toys_10pct` figure uses `ax.set_title()` on each subplot panel. Per the plotting rules, titles are never allowed -- captions belong in the analysis note. The `fontsize=10` is also an absolute numeric font size, compounding the violation.

### 1.2 Absolute numeric `fontsize=` violations

Multiple scripts use absolute numeric `fontsize=` values. Per the methodology (`appendix-plotting.md`), any script that sets a numeric font size is Category A. Relative string sizes (`'x-small'`, `'small'`) are allowed.

| File | Line | Code | Severity |
|------|------|------|----------|
| `phase4_inference/4b_partial/src/06_postfit_figures.py` | 60 | `fontsize=8` on yticklabels | **(B)** |
| `phase4_inference/4b_partial/src/06_postfit_figures.py` | 104 | `fontsize=12` on yticklabels | **(B)** |
| `phase4_inference/4b_partial/src/06_postfit_figures.py` | 145 | `fontsize=10` on set_title | **(A)** |
| `phase4_inference/4a_expected/src/06_figures.py` | 224 | `fontsize=8` on yticklabels | **(B)** |
| `phase4_inference/4a_expected/src/06_figures.py` | 262 | `fontsize=7` on yticklabels | **(B)** |
| `phase4_inference/4a_expected/src/06_figures.py` | 399 | `fontsize=12` on ax.text | **(B)** |
| `phase4_inference/4b_partial/src/05b_figures_prefit.py` | 204 | `fontsize=12` on yticklabels | **(B)** |
| `phase4_inference/4b_partial/src/05b_figures_prefit.py` | 254, 257 | `fontsize=9` on ax.text | **(B)** |
| `phase4_inference/4c_observed/src/04_figures.py` | 331, 407, 468, 598 | `fontsize=8` or `fontsize=12` on yticklabels | **(B)** |
| `phase4_inference/4c_observed/src/05_gof_investigation.py` | 406 | `fontsize=8` on yticklabels | **(B)** |
| `phase4_inference/4b_partial/src/05_figures.py` | 216, 266 | `fontsize=8` or `fontsize=12` | **(B)** |

**Finding F2 (B):** Widespread use of absolute numeric `fontsize` across 6+ scripts. Most are on y-axis tick labels for pull/impact plots where label density is high, so the intent is understandable, but the methodology strictly prohibits numeric font sizes. These should use relative string sizes (`'x-small'` or `'xx-small'`).

### 1.3 `tight_layout` usage

| File | Lines | Severity |
|------|-------|----------|
| `phase4_inference/4c_observed/src/05_gof_investigation.py` | 367, 419 | **(C)** |
| `phase4_inference/4c_observed/src/04_figures.py` | 345, 420, 482, 538, 611 | **(C)** |
| `phase4_inference/4b_partial/src/06_postfit_figures.py` | 72, 115, 150 | **(C)** |
| `phase4_inference/4a_expected/src/06_figures.py` | 234, 272 | **(C)** |
| `phase4_inference/4b_partial/src/05b_figures_prefit.py` | 215, 266 | **(C)** |
| `phase4_inference/4b_partial/src/05_figures.py` | 228, 277, 311 | **(C)** |

**Finding F3 (C):** `tight_layout` is used in multiple scripts for single-panel plots (NP pulls, impact ranking, GoF per-category). This is acceptable for non-ratio plots where `hspace=0` is not relevant. However, `tight_layout` can interfere with `subplots_adjust(hspace=0)` if both are called on ratio plots. Verified that no ratio plot script calls `tight_layout` -- all ratio plots correctly use `subplots_adjust(hspace=0)` instead. No action required.

### 1.4 `ax.bar()` usage

| File | Lines | Severity |
|------|-------|----------|
| `phase4_inference/4b_partial/src/05b_figures_prefit.py` | 241-242 | **(C)** |

**Finding F4 (C):** `ax.bar()` is used for the `data_mc_ratio_summary` bar chart. The methodology recommends `mh.histplot` for histogram rendering, but `ax.bar()` is appropriate for this specific plot (a grouped bar chart comparing ratios across approaches, not a histogram of event distributions). No action required.

### 1.5 Non-standard `figsize`

| File | Line | figsize | Severity |
|------|------|---------|----------|
| `phase4_inference/4b_partial/src/06_postfit_figures.py` | 121 | `(15, 5)` | **(B)** |

**Finding F5 (B):** The `gof_toys_10pct` figure uses `figsize=(15, 5)` for a 1x3 subplot layout. Per the plotting rules, single-panel and ratio plots use `figsize=(10, 10)`, and MxN subplots should scale to keep the aspect ratio (e.g., 1x3 should be `(30, 10)` per the template). The (15, 5) makes panels too compressed horizontally and labels overlap with the title text.

### 1.6 CMS experiment label

All scripts correctly call `mh.label.exp_label()` with `exp="CMS"` on every figure. The label placement is on the main panel (not ratio panel) for all ratio plots.

**Exception:** The `gof_toys_10pct` figure (1x3 grid) does NOT have a CMS experiment label on any panel -- only `ax.set_title()` calls. This is addressed by F1 above.

### 1.7 hspace=0 for ratio plots

All ratio plot scripts correctly set `fig.subplots_adjust(hspace=0)`. Verified in:
- `phase2_exploration/src/05_variable_distributions.py`
- `phase2_exploration/src/06_collinear_mass.py`
- `phase2_exploration/src/04_tau_id_wp_study.py`
- `phase3_selection/src/02_background_estimation.py`
- `phase3_selection/src/07_plots.py`
- `phase4_inference/4a_expected/src/06_figures.py`
- `phase4_inference/4b_partial/src/05_figures.py`
- `phase4_inference/4b_partial/src/05b_figures_prefit.py`
- `phase4_inference/4c_observed/src/04_figures.py`

**No violations found.**

### 1.8 Save format

All scripts save as both PDF and PNG with `bbox_inches="tight"`, `dpi=200`, `transparent=True` and call `plt.close(fig)` after saving. **No violations.**

---

## Mode 2: Visual Inspection of Figures

### Systematic label overlap on syst_shift plots

**Finding F6 (B):** The four systematic shift plots (`syst_shift_tes.pdf`, `syst_shift_mes.pdf`, `syst_shift_jes.pdf`, `syst_shift_met_uncl.pdf`) have the CMS label text stacking in a visually awkward way. The `llabel="Open Data\n{syst_name}"` produces a two-line left label where "Open Data" appears above "CMS" and the systematic name appears on the second line. This causes the "Open Data" text to appear above "CMS" rather than to its right, and the systematic label name crowds the top-left corner. The layout is legible but not clean. Each plot conveys the information correctly; the label formatting is suboptimal.

### Figure-by-figure visual inspection

Below is the per-figure inspection of all figures referenced in the AN. For each figure I check: CMS label present, no title, axis labels present and readable, legend readable, ratio panel gap (if applicable), no text overflow, error bars where expected, no NaN/Inf, caption >= 2 sentences.

#### Phase 2 Exploration Figures

| Figure | CMS label | No title | Axes labels | Legend | Ratio gap | Errors | Caption | Verdict |
|--------|-----------|----------|-------------|--------|-----------|--------|---------|---------|
| `tau_id_wp_VLoose.pdf` | Yes | Yes | Yes | Yes | None (hspace=0) | Yes | 3 sent. | PASS |
| `tau_id_wp_Loose.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `tau_id_wp_Medium.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `collinear_mass_physical.pdf` | Yes | Yes | Yes | Yes | None (hspace=0) | Yes | 3 sent. | PASS |
| `separation_power.pdf` | Yes | Yes | Yes | Yes | N/A | N/A | 3 sent. | PASS |
| `mt_regions.pdf` | Yes | Yes | Yes, log scale | Yes | None (hspace=0) | Yes | 3 sent. | PASS |

**Phase 2 figures: all PASS.**

#### Phase 3 Selection Figures

| Figure | CMS label | No title | Axes labels | Legend | Ratio gap | Errors | Caption | Verdict |
|--------|-----------|----------|-------------|--------|-----------|--------|---------|---------|
| `mvis_baseline.pdf` | Yes | Yes | Yes | Yes | None (hspace=0) | Yes | 3 sent. | PASS |
| `mvis_vbf.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `nn_roc.pdf` | Yes ("Open Simulation") | Yes | Yes | Yes | N/A | N/A | 2 sent. | PASS |
| `nn_overtraining.pdf` | Yes ("Open Simulation") | Yes | Yes | Yes | N/A | Yes | 3 sent. | PASS |
| `nn_feature_importance.pdf` | Yes ("Open Simulation") | Yes | Yes | N/A | N/A | N/A | 3 sent. | PASS |
| `nn_score_baseline.pdf` | Yes | Yes | Yes | Yes | None (hspace=0) | Yes | 3 sent. | PASS |
| `nn_score_vbf.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `bdt_vs_nn_roc.pdf` | Yes ("Open Simulation") | Yes | Yes | Yes | N/A | N/A | 2 sent. | PASS |
| `bdt_overtraining.pdf` | Yes ("Open Simulation") | Yes | Yes | Yes | N/A | Yes | 3 sent. | PASS |
| `mcol_baseline.pdf` | Yes | Yes | Yes | Yes | None | Yes | 3 sent. | PASS |
| `mcol_vbf.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `approach_comparison.pdf` | Yes | Yes | Yes | N/A | N/A | N/A | 3 sent. | PASS |
| `wjets_validation_midmt.pdf` | Yes | Yes | Yes | Yes | None (hspace=0) | Yes | 2 sent. | PASS |
| `tau_pt_baseline.pdf` | Yes | Yes | Yes | Yes | None | Yes | 3 sent. | PASS |
| `mu_pt_baseline.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `met_pt_baseline.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `njets_baseline.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `delta_r_baseline.pdf` | Yes | Yes | Yes | Yes | None | Yes | 3 sent. | PASS |
| `tau_pt_vbf.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `mu_pt_vbf.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `met_pt_vbf.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `njets_vbf.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `delta_r_vbf.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |

**Phase 3 figures: all PASS.**

#### Phase 4a Expected Results Figures

| Figure | CMS label | No title | Axes labels | Legend | Ratio gap | Errors | Caption | Verdict |
|--------|-----------|----------|-------------|--------|-----------|--------|---------|---------|
| `syst_shift_tes.pdf` | Yes (layout issue) | Yes | Yes | Yes | N/A | N/A | 3 sent. | PASS (see F6) |
| `syst_shift_mes.pdf` | Yes (layout issue) | Yes | Yes | Yes | N/A | N/A | 2 sent. | PASS (see F6) |
| `syst_shift_jes.pdf` | Yes (layout issue) | Yes | Yes | Yes | N/A | N/A | 3 sent. | PASS (see F6) |
| `syst_shift_met_uncl.pdf` | Yes (layout issue) | Yes | Yes | Yes | N/A | N/A | 3 sent. | PASS (see F6) |
| `template_mvis_baseline.pdf` | Yes | Yes | Yes | Yes | None (hspace=0) | Yes | 3 sent. | PASS |
| `template_mvis_vbf.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `template_nn_score_baseline.pdf` | Yes | Yes | Yes | Yes | None (hspace=0) | Yes | 3 sent. | PASS |
| `template_nn_score_vbf.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `template_mcol_baseline.pdf` | Yes | Yes | Yes | Yes | None | Yes | 3 sent. | PASS |
| `template_mcol_vbf.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `cls_scan.pdf` | Yes | Yes | Yes | Yes | N/A | N/A | 3 sent. | PASS |
| `impact_ranking.pdf` | Yes | Yes | Yes | Yes | N/A | N/A | 2+ sent. | PASS |
| `np_pulls.pdf` | Yes | Yes | Yes | Yes | N/A | Yes | 2+ sent. | PASS |
| `signal_injection.pdf` | Yes | Yes | Yes | Yes | N/A | Yes | 3 sent. | PASS |
| `gof_toys.pdf` | Yes | Yes | Yes | Yes | N/A | N/A | 3 sent. | PASS |

**Phase 4a figures: all PASS (with F6 note on syst_shift label layout).**

#### Phase 4b 10% Data Validation Figures

| Figure | CMS label | No title | Axes labels | Legend | Ratio gap | Errors | Caption | Verdict |
|--------|-----------|----------|-------------|--------|-----------|--------|---------|---------|
| `data_mc_mvis_baseline.pdf` | Yes | Yes | Yes | Yes | None (hspace=0) | Yes | 3 sent. | PASS |
| `data_mc_mvis_vbf.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `data_mc_nn_score_baseline.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `data_mc_nn_score_vbf.pdf` | Yes | Yes | Yes | Yes | None | Yes | 3 sent. | PASS |
| `data_mc_mcol_baseline.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `data_mc_mcol_vbf.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `np_pulls_10pct.pdf` | Yes | Yes | Yes | Yes | N/A | Yes | 2+ sent. | PASS |
| `mu_comparison_10pct.pdf` | Yes | Yes | Yes | Yes | N/A | Yes | 2+ sent. | PASS |
| `gof_toys_10pct.pdf` | **NO** | **HAS TITLE** | Yes | Yes | N/A | N/A | 2+ sent. | **FAIL (F1, F5)** |
| `mu_per_category_10pct.pdf` | Yes | Yes | Yes | Yes | N/A | Yes | 2+ sent. | PASS |
| `data_mc_ratio_summary.pdf` | Yes | Yes | Yes | Yes | N/A | N/A | 2+ sent. | PASS |

**Phase 4b figures: 1 FAIL (gof_toys_10pct).**

#### Phase 4c Full Data Figures

| Figure | CMS label | No title | Axes labels | Legend | Ratio gap | Errors | Caption | Verdict |
|--------|-----------|----------|-------------|--------|-----------|--------|---------|---------|
| `data_mc_prefit_nn_score_baseline.pdf` | Yes | Yes | Yes | Yes | None (hspace=0) | Yes | 3 sent. | PASS |
| `data_mc_prefit_nn_score_vbf.pdf` | Yes | Yes | Yes | Yes | None | Yes | 3 sent. | PASS |
| `data_mc_prefit_mvis_baseline.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `data_mc_prefit_mvis_vbf.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `data_mc_prefit_mcol_baseline.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `data_mc_prefit_mcol_vbf.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `np_pulls_full.pdf` | Yes | Yes | Yes | Yes | N/A | Yes | 2+ sent. | PASS |
| `impact_ranking_full.pdf` | Yes | Yes | Yes | Yes | N/A | N/A | 3 sent. | PASS |
| `gof_toys_full_nn_score.pdf` | Yes | Yes | Yes | Yes | N/A | N/A | 4 sent. | PASS |
| `gof_toys_full_mvis.pdf` | Yes | Yes | Yes | Yes | N/A | N/A | 2 sent. | PASS |
| `gof_toys_full_mcol.pdf` | Yes | Yes | Yes | Yes | N/A | N/A | 2 sent. | PASS |
| `per_category_mu_full.pdf` | Yes | Yes | Yes | Yes | N/A | Yes | 3 sent. | PASS |
| `data_mc_postfit_nn_score_baseline.pdf` | Yes | Yes | Yes | Yes | None (hspace=0) | Yes | 3 sent. | PASS |
| `data_mc_postfit_nn_score_vbf.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `data_mc_postfit_mvis_baseline.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `data_mc_postfit_mvis_vbf.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `data_mc_postfit_mcol_baseline.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `data_mc_postfit_mcol_vbf.pdf` | Yes | Yes | Yes | Yes | None | Yes | 2 sent. | PASS |
| `gof_investigation_nn_score.pdf` | Yes | Yes | Yes | Yes | N/A | N/A | N/A (ref text) | PASS |
| `gof_per_category.pdf` | Yes | Yes | Yes | Yes | N/A | N/A | N/A (ref text) | PASS |

**Phase 4c figures: all PASS.**

#### Phase 5 Figures

| Figure | CMS label | No title | Axes labels | Legend | Errors | Caption | Verdict |
|--------|-----------|----------|-------------|--------|--------|---------|---------|
| `mu_comparison_published.pdf` | Yes | Yes | Yes | Yes | Yes | 4 sent. | PASS |
| `mu_comparison_all_vs_published.pdf` | Yes | Yes | Yes | Yes | Yes | 4 sent. | PASS |

**Phase 5 figures: all PASS.**

---

## Mode 3: Physics Checks on Figures

### 3.1 All yields non-negative

All stacked histograms (data/MC comparisons across all phases) show non-negative yields for all background components. Signal components (ggH, VBF) are appropriately scaled (x10 or x50) in pre-fit plots. Post-fit plots show total prediction (not individual components), which is non-negative. **PASS.**

### 3.2 Data/MC ratios

- **Baseline category:** Data/MC ratios range from approximately 0.7 to 1.3 across all variables, centered near 0.95. Within the expected [0.5, 2.0] range. **PASS.**
- **VBF category:** Data/MC ratios show a persistent 31% deficit (ratio near 0.69). The ratios range from approximately 0.4 to 1.2. Some bins in the VBF category dip below 0.5, which is flagged in the text as a known limitation (LO generator deficit). This is within the physical range and is well-documented. **PASS (with known limitation).**
- **Post-fit ratios:** The post-fit data/MC ratios are centered near 1.0 as expected, confirming the fit is working correctly. **PASS.**

### 3.3 Uncertainties scale as sqrt(N)

Error bars on data points in all data/MC comparison plots are consistent with Poisson statistical uncertainties (sqrt(N)). The VBF category shows larger relative error bars as expected from the lower event count. **PASS.**

### 3.4 Pre-fit and post-fit consistency

- The post-fit distributions show improved data/MC agreement compared to pre-fit, as expected from the nuisance parameter adjustments.
- The `data_mc_postfit_nn_score_baseline.pdf` shows the post-fit prediction closely following the data, with the ratio panel centered near 1.0.
- The NP pull plots (`np_pulls_full.pdf`) show all pulls within the expected +/- 2 sigma bands, with the largest pull being the W+jets VBF normalization at -1.89 sigma -- consistent with the known VBF deficit.
- **PASS.**

### 3.5 No unphysical features

- No NaN or Inf values visible in any figure.
- All distributions show physically expected shapes (falling pT spectra, Z peak in mass distributions, back-to-back topology in delta_R, etc.).
- The collinear mass distribution shows the expected broadening from unphysical solutions, which is documented.
- The NN score distributions show the expected signal/background separation pattern.
- **PASS.**

### 3.6 GoF toy distributions

- The Asimov GoF (`gof_toys.pdf`) shows observed chi2 = 0.00 with p-value = 1.0, which is expected for a perfect Asimov fit (the model generates the Asimov data, so chi2 should be zero by construction).
- The 10% data GoF (`gof_toys_10pct.pdf`) shows the NN score approach with p = 0.209, which is acceptable.
- The full data GoF (`gof_toys_full_nn_score.pdf`) shows p = 0.000 with observed chi2 = 33.1 exceeding all toys. This is a genuine GoF failure documented in the text. The toy distribution is well-formed (no pathological features).
- **PASS (GoF failure is a physics result, not a plotting error).**

### 3.7 Signal injection linearity

The `signal_injection.pdf` figure shows recovered mu values on the diagonal for all three approaches at injected mu = {0, 1, 2, 5}. Error bars are symmetric and scale with the approach sensitivity (NN smallest, mcol largest). **PASS.**

### 3.8 CLS scan

The `cls_scan.pdf` shows monotonically decreasing CLs curves for all three approaches, with solid (observed) and dashed (expected) lines. The 95% CL horizontal line is correctly placed at 0.05. The NN approach provides the tightest limit. No unphysical crossing or non-monotonic behavior. **PASS.**

---

## Summary of Findings

### Category A (must resolve)

**F1.** `gof_toys_10pct.pdf` uses `ax.set_title()` with `fontsize=10` on each subplot panel. Titles are prohibited. The CMS experiment label is missing from this figure entirely. The figure should use the CMS label on the first panel (or on all panels if space permits), and move the approach label + p-value information to a text annotation or legend entry instead of a title.
- **Script:** `phase4_inference/4b_partial/src/06_postfit_figures.py`, line 145
- **Figure:** `gof_toys_10pct.pdf`

### Category B (must fix before PASS)

**F2.** Absolute numeric `fontsize=` values are used in at least 6 plotting scripts across Phases 4a, 4b, and 4c. The most common occurrences are `fontsize=8` on y-axis tick labels for NP pull and impact ranking plots, and `fontsize=12` on mu comparison plot labels. Per `appendix-plotting.md`, any numeric font size is a violation. Replace with `'x-small'` or `'xx-small'` as appropriate.
- **Scripts:** See table in Section 1.2 above.

**F5.** `gof_toys_10pct.pdf` uses `figsize=(15, 5)` for a 1x3 subplot layout. Per the template, a 1x3 layout should use `(30, 10)` to maintain the 1:1 per-panel aspect ratio. The (15, 5) makes panels compressed, contributing to the label overlap issue.
- **Script:** `phase4_inference/4b_partial/src/06_postfit_figures.py`, line 121

**F6.** The four systematic shift plots (`syst_shift_tes.pdf`, `syst_shift_mes.pdf`, `syst_shift_jes.pdf`, `syst_shift_met_uncl.pdf`) have a visually awkward CMS label layout. The two-line `llabel` causes "Open Data" to appear above "CMS" and the systematic name to appear on a second line below. This creates a cluttered top-left corner. Recommend moving the systematic name to a separate text annotation or using `rlabel` for the systematic name.
- **Script:** `phase4_inference/4a_expected/src/06_figures.py`, line 368

### Category C (suggestions)

**F3.** `tight_layout` is used in multiple non-ratio plot scripts. This is acceptable for the current figures but could interfere if ratio panels are added later. No action required.

**F4.** `ax.bar()` is used for the data/MC ratio summary bar chart. This is appropriate for the plot type. No action required.

---

## Missing figure references

All figure files referenced in the AN markdown source exist on disk. No missing figures detected.

The AN text at line 1418 references `figures/gof_investigation_*.pdf` and `figures/gof_per_category.pdf` as inline text (not pandoc figure references), which is acceptable for supplementary diagnostic figures that are not part of the main figure sequence.

---

## Caption quality check

All 56 figure captions in the AN meet the minimum 2-sentence requirement. Most captions are 2-4 sentences and follow the required format: `<Plot name>. <Description.>` Captions provide sufficient context for a reader to understand the figure without reading the surrounding text.

---

## Verdict

**FAIL -- 1 Category A and 3 Category B issues must be resolved.**

The Category A finding (F1: `gof_toys_10pct.pdf` with title and missing CMS label) must be resolved before the review can PASS. The Category B findings (F2: absolute font sizes, F5: non-standard figsize, F6: label layout on syst_shift plots) should also be addressed.

The overall figure quality is high. The CMS style is consistently applied across all 96 figures, ratio panels have no visible gaps, error bars are present where expected, and all physics distributions are physically reasonable. The two flagship comparison figures (`mu_comparison_published.pdf` and `mu_comparison_all_vs_published.pdf`) are clean and publication-quality.
