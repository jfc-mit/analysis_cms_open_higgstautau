# Phase 2 Plot Validation Report

**Validator:** Plot Validator (code linter + visual inspection)
**Date:** 2026-03-24
**Phase:** 2 (Exploration)
**Scripts reviewed:** 4 plotting scripts (`04_tau_id_wp_study.py`, `05_variable_distributions.py`, `06_collinear_mass.py`, `07_vbf_optimization.py`)
**Figures reviewed:** 21 PNG files in `phase2_exploration/outputs/figures/`

---

## Part 1: Code Linting

### Global checks (all plotting scripts)

| Check | Status | Notes |
|-------|--------|-------|
| `mh.style.use("CMS")` present | PASS | All 4 scripts set CMS style |
| `figsize=(10, 10)` always | PASS | All figures use `(10, 10)` |
| No `ax.set_title()` | PASS | No title calls found |
| No hardcoded `fontsize=N` | PASS | All use `fontsize="x-small"` |
| `bbox_inches="tight"` at save | PASS | All 7 savefig locations use it |
| Both PDF and PNG saved | PASS | All scripts save both formats |
| `dpi=200` | PASS | All save with `dpi=200` |
| `transparent=True` | PASS | All save with transparency |
| `plt.close()` after saving | PASS | All scripts close figures |
| No `plt.colorbar()` / `fig.colorbar()` | PASS | No colorbar calls |
| No `tight_layout()` | PASS | None found |
| `sharex=True` with `hspace=0` | PASS | All 4 ratio-plot locations pair them correctly |
| `exp_label()` on every figure | PASS | All 7 figure-creation sites include `exp_label` |
| `exp_label` NOT on ratio panel | PASS | All calls pass `ax=ax_main` or `ax=ax` (main/single panel) |
| No `.view()[:] =` trap | PASS | No `.view()` assignment found |
| No `data=False` combined with `llabel=` | PASS | No `data=False` found |
| Open Data labeling correct | PASS | Data plots use `llabel="Open Data"`, simulation-only plots use `llabel="Open Simulation"` |

### Per-script findings

#### `04_tau_id_wp_study.py`

| Line | Finding | Category | Details |
|------|---------|----------|---------|
| 299 | `ax_main.text(...)` used instead of `mh.label.add_text()` | **WARNING (B)** | Uses `ax_main.text(0.95, 0.70, ...)` to annotate chi2 info. Should use `mh.label.add_text()` for consistency with mplhep. The text uses `fontsize="x-small"` which is acceptable, and the content (WP name + chi2/ndf) is informational annotation rather than a label. Borderline. |
| 257 | `ax_main.errorbar(...)` used for data instead of `mh.histplot(..., histtype="errorbar")` | **WARNING (C)** | Data points are plotted with raw `ax.errorbar()` instead of `mh.histplot(h, histtype="errorbar", ...)`. The errors are computed as `sqrt(N)` on data counts which is correct for raw event counts (not derived quantities). Functional but not idiomatic. |

#### `05_variable_distributions.py`

| Line | Finding | Category | Details |
|------|---------|----------|---------|
| 151-158 | `ax_main.errorbar(...)` used for data | **WARNING (C)** | Same as 04: raw errorbar for data points instead of `mh.histplot`. Errors are `sqrt(N)` on raw event counts, which is correct. |
| 312 | `ax.barh(...)` used for separation power chart | **RED FLAG (A)** | Uses `ax.barh()` for the ROC AUC bar chart. The spec requires `mh.histplot()` for all binned data, and explicitly prohibits `ax.bar()`. However, this is a horizontal bar chart for ranked variable importance, not a histogram of event data. This is a borderline case -- `mh.histplot` does not natively produce horizontal bar charts for ranking displays. Still, the prohibition on `ax.bar()` is explicit. |
| 312 | Variable names as y-tick labels in separation_power plot | **RED FLAG (A)** | The y-axis labels show code variable names: `tau_pt`, `mvis`, `njets`, `met_pt`, `delta_r`, `mu_pt`, `tau_dm`, `mt`, `delta_phi`, `pv_npvs`, `mu_eta`, `nbjets`, `tau_eta`. These must be publication-quality names (e.g., `$p_T^{\tau_h}$`, `$m_\mathrm{vis}$`, `$N_\mathrm{jets}$`, etc.). Visible on the rendered figure. |
| -- | No `mpl_magic(ax)` call | **WARNING (B)** | None of the distribution plots call `mpl_magic(ax)` for y-axis rescaling. The legends use `fontsize="x-small"` and `ncol=2`, and visually the legends do not overlap with data in most cases, but this is not guaranteed for all distributions. |

#### `06_collinear_mass.py`

| Line | Finding | Category | Details |
|------|---------|----------|---------|
| 225 | `ax_main.errorbar(...)` used for data | **WARNING (C)** | Same pattern. Errors are `sqrt(N)` on raw counts -- correct. |
| 290 | Same for physical-only plot | **WARNING (C)** | Same pattern. |
| -- | No `mpl_magic(ax)` call | **WARNING (B)** | Same as 05. |

#### `07_vbf_optimization.py`

| Line | Finding | Category | Details |
|------|---------|----------|---------|
| -- | No `mpl_magic(ax)` call | **WARNING (B)** | Neither the mjj nor deta plots call `mpl_magic()`. |

### Consistency checks

| Check | Status | Notes |
|-------|--------|-------|
| All figures in outputs/figures/ exist | PASS | 21 PNG + 21 PDF files present |
| No duplicate filenames | PASS | All unique |
| `check_inventory.py` uses bare `print()` | **WARNING (C)** | 10 bare `print()` statements. Should use `logging`. Not a plotting issue but noted. |

---

## Part 2: Visual Validation

### Figure-by-figure assessment

#### 1. `collinear_mass.png`

- **Experiment label:** PASS -- "CMS Open Data" and luminosity label present and readable.
- **Axis labels:** PASS -- "$m_\mathrm{col}(\mu, \tau_h)$ [GeV]" on x-axis, "Events / 10 GeV" on y-axis.
- **Legend:** PASS -- Readable, positioned in upper-center/right, no overlap with data peak.
- **Data/MC ratio:** PASS -- Ratio panel centered around 1.0, reasonable agreement in bulk.
- **Physics check:** PASS -- Distribution peaks around 70-80 GeV as expected, reasonable tail. Log scale appropriate.
- **Ratio panel gap:** PASS -- No visible gap between main and ratio panels.
- **Error bars:** PASS -- Reasonable magnitude, growing in tail as expected for lower statistics.
- **Verdict: PASS**

#### 2. `collinear_mass_physical.png`

- **Experiment label:** PASS -- Present and readable.
- **Axis labels:** PASS -- Includes "(physical solutions only)" annotation in x-label.
- **Legend:** PASS -- No overlap.
- **Data/MC ratio:** PASS -- Centered around 1.0.
- **Physics check:** PASS -- Physical solutions have cleaner peak structure.
- **Ratio panel gap:** PASS -- No gap.
- **Verdict: PASS**

#### 3. `delta_phi.png`

- **Experiment label:** PASS.
- **Axis labels:** PASS -- "$|\Delta\phi(\mu, \tau_h)|$" on x-axis.
- **Legend:** PASS -- Upper-left, no overlap with data. Data peaks strongly at high delta-phi (back-to-back topology) which is physically expected.
- **Data/MC ratio:** **WARNING (B)** -- Ratio points are systematically above 1.0 across the full range (~1.1-1.2), indicating a ~10-20% data excess over MC. This is not a plotting error but a physics observation that should be noted in the exploration artifact.
- **Ratio panel gap:** PASS.
- **Physics check:** PASS -- Back-to-back topology expected for Z/H decay products.
- **Verdict: PASS (physics note)**

#### 4. `delta_r.png`

- **Experiment label:** PASS.
- **Axis labels:** PASS -- "$\Delta R(\mu, \tau_h)$" on x-axis.
- **Legend:** PASS -- No overlap.
- **Data/MC ratio:** **WARNING (B)** -- Same systematic excess as delta_phi.
- **Physics check:** PASS -- Peaks around 3.0 (back-to-back topology), with DR > 0.5 cut visible.
- **Ratio panel gap:** PASS.
- **Verdict: PASS (physics note)**

#### 5. `met_pt.png`

- **Experiment label:** PASS.
- **Axis labels:** PASS -- "$E_T^\mathrm{miss}$ [GeV]" on x-axis, proper units.
- **Legend:** PASS -- No overlap.
- **Data/MC ratio:** PASS -- Ratio near 1.0 in bulk, larger fluctuations in tail (expected with fewer events).
- **Physics check:** PASS -- Steeply falling MET distribution, physical.
- **Ratio panel gap:** PASS.
- **Verdict: PASS**

#### 6. `mt.png`

- **Experiment label:** PASS.
- **Axis labels:** PASS -- "$m_T(\mu, E_T^\mathrm{miss})$ [GeV]".
- **Legend:** **WARNING (B)** -- Legend overlaps slightly with data points in the lower-left. The legend is placed in the lower-left of the main panel where data and MC histograms are present. Not severe but could be improved by moving legend or using `mpl_magic`.
- **Data/MC ratio:** **WARNING (B)** -- Ratio systematically above 1.0 (~1.1-1.2) across the mT range, consistent with the overall data/MC normalization excess.
- **Physics check:** PASS -- Flat/gently falling mT distribution below 30 GeV as expected with the mT < 30 cut.
- **Ratio panel gap:** PASS.
- **Verdict: PASS (legend placement note)**

#### 7. `mu_eta.png`

- **Experiment label:** PASS.
- **Axis labels:** PASS -- "$\eta^\mu$" on x-axis.
- **Legend:** **WARNING (B)** -- Legend overlaps with data/MC distributions. Placed in lower-left where the signal overlay and data points are present.
- **Data/MC ratio:** **WARNING (B)** -- Ratio systematically ~1.1-1.2 across eta range.
- **Physics check:** PASS -- Expected peaked distribution at central eta with acceptance edge at |eta| = 2.1.
- **Ratio panel gap:** PASS.
- **Verdict: PASS (legend placement note)**

#### 8. `mu_pt.png`

- **Experiment label:** PASS.
- **Axis labels:** PASS -- "$p_T^\mu$ [GeV]".
- **Legend:** PASS -- Upper-right, no overlap with log-scale data.
- **Data/MC ratio:** PASS -- Near 1.0 in bulk, growing uncertainty at high pT.
- **Physics check:** PASS -- Steeply falling pT, threshold at 20 GeV visible.
- **Ratio panel gap:** PASS.
- **Verdict: PASS**

#### 9. `mvis.png`

- **Experiment label:** PASS.
- **Axis labels:** PASS -- "$m_\mathrm{vis}(\mu, \tau_h)$ [GeV]".
- **Legend:** PASS -- No overlap.
- **Data/MC ratio:** PASS -- Reasonable agreement, ratio centered around 1.0 in Z peak region.
- **Physics check:** PASS -- Clear Z peak at ~70-80 GeV (visible mass), physical.
- **Ratio panel gap:** PASS.
- **Verdict: PASS**

#### 10. `nbjets.png`

- **Experiment label:** PASS.
- **Axis labels:** PASS -- "$N_{b-\mathrm{jets}}$" on x-axis.
- **Legend:** PASS -- No overlap.
- **Data/MC ratio:** PASS -- Limited ratio points due to discrete variable. 0-jet bin agreement reasonable.
- **Physics check:** PASS -- Dominated by 0-bjets bin, with ttbar contribution visible at higher multiplicities.
- **Ratio panel gap:** PASS.
- **Verdict: PASS**

#### 11. `njets.png`

- **Experiment label:** PASS.
- **Axis labels:** PASS -- "$N_\mathrm{jets}$" on x-axis.
- **Legend:** PASS -- No overlap.
- **Data/MC ratio:** PASS -- Reasonable agreement at low multiplicities.
- **Physics check:** PASS -- Expected falling multiplicity.
- **Ratio panel gap:** PASS.
- **Verdict: PASS**

#### 12. `pv_npvs.png`

- **Experiment label:** PASS.
- **Axis labels:** PASS -- "$N_\mathrm{PV}$".
- **Legend:** PASS -- No overlap.
- **Data/MC ratio:** **WARNING (B)** -- Clear pileup mismodeling visible: data/MC ratio varies significantly across NPV range. Low-NPV bins have ratio < 1, mid-NPV bins have ratio ~1, high-NPV bins show data excess. This is expected for Run 2012 data without pileup reweighting but should be documented as a known issue for Phase 3.
- **Physics check:** PASS -- Physical pileup distribution.
- **Ratio panel gap:** PASS.
- **Verdict: PASS (pileup reweighting needed)**

#### 13. `separation_power.png`

- **Experiment label:** PASS -- "CMS Open Simulation" correctly used.
- **Axis labels:** PASS -- "ROC AUC (Signal vs Background)" on x-axis.
- **Y-axis tick labels:** **RED FLAG (A)** -- Code variable names used as labels: `tau_pt`, `mvis`, `njets`, `met_pt`, `delta_r`, `mu_pt`, `tau_dm`, `mt`, `delta_phi`, `pv_npvs`, `mu_eta`, `nbjets`, `tau_eta`. These MUST be publication-quality names. Example: `tau_pt` should be `$p_T^{\tau_h}$`, `mvis` should be `$m_\mathrm{vis}$`, etc. Visible on the rendered figure.
- **Legend:** N/A -- No legend needed (single series).
- **Physics check:** PASS -- Ranking is plausible: tau pT and mvis most discriminating.
- **Verdict: FAIL -- code variable names visible**

#### 14. `tau_dm.png`

- **Experiment label:** PASS.
- **Axis labels:** PASS -- "$\tau_h$ decay mode".
- **Legend:** PASS -- No overlap.
- **Data/MC ratio:** PASS -- Limited ratio points. Mode 0 and 1 agree reasonably.
- **Physics check:** PASS -- Decay modes 0, 1, 10 dominate as expected (1-prong, 1-prong+pi0, 3-prong).
- **Ratio panel gap:** PASS.
- **Verdict: PASS**

#### 15. `tau_eta.png`

- **Experiment label:** PASS.
- **Axis labels:** PASS -- "$\eta^{\tau_h}$".
- **Legend:** **WARNING (B)** -- Legend overlaps with data/MC distributions in the lower-left region.
- **Data/MC ratio:** **WARNING (B)** -- Systematic excess ~1.1-1.2.
- **Physics check:** PASS -- Expected distribution with acceptance edges at |eta| = 2.3.
- **Ratio panel gap:** PASS.
- **Verdict: PASS (legend placement note)**

#### 16. `tau_id_wp_Loose.png`

- **Experiment label:** PASS.
- **Axis labels:** PASS -- "$m_\mathrm{vis}(\mu, \tau_h)$ [GeV]".
- **Legend:** PASS -- Upper-right, no overlap.
- **Text annotation:** PASS -- Chi2 info box positioned in right side of plot, readable, no overlap with data.
- **Data/MC ratio:** PASS -- Ratio near 1.0 in Z peak, reasonable tails.
- **Physics check:** PASS -- Clear Z peak. Data/MC = 1.070 in Z window is reasonable.
- **Ratio panel gap:** PASS.
- **Verdict: PASS**

#### 17. `tau_id_wp_Medium.png`

- **Experiment label:** PASS.
- **Axis labels:** PASS.
- **Legend:** PASS.
- **Text annotation:** PASS -- Data/MC = 1.030 in Z window. Chi2/ndf = 2.95.
- **Data/MC ratio:** PASS.
- **Physics check:** PASS.
- **Ratio panel gap:** PASS.
- **Verdict: PASS**

#### 18. `tau_id_wp_VLoose.png`

- **Experiment label:** PASS.
- **Axis labels:** PASS.
- **Legend:** PASS.
- **Text annotation:** PASS -- Data/MC = 1.114 in Z window. Chi2/ndf = 4.08 (worst of the three WPs, as expected for the loosest WP).
- **Data/MC ratio:** PASS.
- **Physics check:** PASS.
- **Ratio panel gap:** PASS.
- **Verdict: PASS**

#### 19. `tau_pt.png`

- **Experiment label:** PASS.
- **Axis labels:** PASS -- "$p_T^{\tau_h}$ [GeV]".
- **Legend:** PASS -- Upper-right, no overlap.
- **Data/MC ratio:** PASS -- Good agreement in bulk, growing uncertainty at high pT.
- **Physics check:** PASS -- Steeply falling pT spectrum starting at 20 GeV threshold.
- **Ratio panel gap:** PASS.
- **Verdict: PASS**

#### 20. `vbf_deta.png`

- **Experiment label:** PASS -- "CMS Open Simulation" correctly used.
- **Axis labels:** PASS -- "$|\Delta\eta_{jj}|$" on x-axis, "Normalized" on y-axis.
- **Legend:** PASS -- Upper-right, no overlap.
- **Physics check:** PASS -- VBF has characteristically wider deta distribution than backgrounds, as expected.
- **Verdict: PASS**

#### 21. `vbf_mjj.png`

- **Experiment label:** PASS -- "CMS Open Simulation" correctly used.
- **Axis labels:** PASS -- "$m_{jj}$ [GeV]" on x-axis, "Normalized" on y-axis.
- **Legend:** PASS -- No overlap.
- **Physics check:** PASS -- VBF has higher mjj tail than backgrounds, as expected.
- **Verdict: PASS**

---

## Summary

### RED FLAGS (Category A -- automatic, arbiter may NOT downgrade)

1. **`05_variable_distributions.py` line 312 + `separation_power.png`:** Code variable names (`tau_pt`, `mvis`, `njets`, etc.) used as y-axis tick labels in the separation power bar chart. These are visible on the rendered figure and MUST be replaced with publication-quality LaTeX names. This affects both the code (line 312-315 in `05_variable_distributions.py` where `vars_sorted` is built from the `variable` column of the `VARIABLES` list, which stores code-level branch names) and the rendered figure.

   **Suggested fix:** In `05_variable_distributions.py`, create a display-name mapping from internal variable names to LaTeX labels (e.g., `{"tau_pt": r"$p_T^{\tau_h}$", "mvis": r"$m_\mathrm{vis}$", ...}`) and use it for `ax.set_yticklabels()`.

2. **`05_variable_distributions.py` line 312:** `ax.barh()` used instead of `mh.histplot()`. The spec prohibits `ax.bar()` (and by extension `ax.barh()`). However, this is a variable-ranking chart, not a histogram of event counts. `mh.histplot` cannot produce horizontal bar charts for ranked data. **Recommendation:** This is a borderline case. If the arbiter considers this a strict rule, the plot should be redesigned (e.g., as a horizontal `mh.histplot` with custom bins per variable). Alternatively, `ax.barh()` may be acceptable for non-histogram displays. The RED FLAG classification is mechanical; the arbiter may exercise judgment here.

### WARNINGS (Category B/C)

| # | Script/Figure | Finding | Category |
|---|--------------|---------|----------|
| 1 | `04_tau_id_wp_study.py:299` | `ax_main.text()` used instead of `mh.label.add_text()` | B |
| 2 | `05_variable_distributions.py` (all plots) | No `mpl_magic(ax)` call for y-axis rescaling / legend-data collision avoidance | B |
| 3 | `06_collinear_mass.py` (all plots) | No `mpl_magic(ax)` call | B |
| 4 | `07_vbf_optimization.py` (all plots) | No `mpl_magic(ax)` call | B |
| 5 | `mt.png`, `mu_eta.png`, `tau_eta.png` | Legend overlaps slightly with data/MC distributions | B |
| 6 | `delta_phi.png`, `delta_r.png`, `mu_eta.png`, `tau_eta.png`, `mt.png`, `pv_npvs.png` | Data/MC ratio systematically above 1.0 (~10-20% data excess) | B (physics, not plotting) |
| 7 | `04_tau_id_wp_study.py`, `05_variable_distributions.py`, `06_collinear_mass.py` | Data points plotted with `ax.errorbar()` instead of `mh.histplot(histtype="errorbar")` | C |
| 8 | `check_inventory.py` | Bare `print()` statements (10 occurrences) | C |

### Items with no issues

- All ratio plots have `hspace=0` with `sharex=True` -- no visible gaps
- All figures have experiment labels present and readable
- All figures save both PDF and PNG with correct settings
- No `set_title()` calls anywhere
- No absolute font sizes
- No colorbar violations
- No `data=False` + `llabel` stacking bug
- No derived-quantity error bar trap (all error bars are sqrt(N) on raw event counts)
- All signal overlays are clearly labeled with "x50" scaling factor
- Open Data / Open Simulation labels correctly distinguish data vs MC-only plots
- Physics distributions look reasonable -- Z peak visible, expected kinematic shapes

### Recommendations for fix agent

1. **Must fix (A):** Replace code variable names in `separation_power.png` with LaTeX labels.
2. **Should fix (B):** Add `mpl_magic(ax)` calls to all distribution plots to avoid legend-data overlap, or reposition legends where overlap occurs (mt, mu_eta, tau_eta).
3. **Nice to fix (C):** Switch data point plotting from `ax.errorbar()` to `mh.histplot(histtype="errorbar")` for consistency.
