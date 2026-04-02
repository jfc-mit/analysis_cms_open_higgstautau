# Phase 3 Plot Validation Report

**Validator:** Plot Validator (automated)
**Date:** 2026-03-24
**Phase:** 3 (Selection)
**Scripts reviewed:** `02_background_estimation.py`, `04_nn_discriminant.py`,
`06_approach_comparison.py`, `07_plots.py`
**Figures reviewed:** 17 (all PNG files in `phase3_selection/outputs/figures/`)

---

## Part 1: Code Linting

### 1.1 Prohibited Calls

| Rule | Status | Details |
|------|--------|---------|
| No `ax.set_title()` | PASS | No occurrences found. |
| No absolute `fontsize=<int>` | PASS | All fontsize uses are relative strings (`"x-small"`). |
| No `plt.colorbar` / `fig.colorbar(im, ax=)` | PASS | No occurrences found. |
| No `tight_layout()` | PASS | No occurrences found. |

### 1.2 Histogram API

| Rule | Status | Details |
|------|--------|---------|
| No `ax.step()` / `ax.bar()` -- use `mh.histplot` | **RED FLAG** | `ax.bar()` is used in all four plotting scripts for stacked histograms. `ax.step()` is used in `07_plots.py:187` for signal overlays. `mh.histplot` is never used anywhere. See finding F1 below. |

### 1.3 Figure Configuration

| Rule | Status | Details |
|------|--------|---------|
| `figsize=(10, 10)` always | PASS | All 7 figure-creation calls use `figsize=(10, 10)`. |
| `mh.style.use("CMS")` | PASS | Set at module level in all 4 plotting scripts. |
| `exp_label` on every figure | PASS | All 7 plotting functions call `mh.label.exp_label()`. Correctly uses `"Open Simulation"` for MC-only NN plots and `"Open Data"` for data/MC plots. |

### 1.4 Ratio Plot Configuration

| Rule | Status | Details |
|------|--------|---------|
| `hspace=0` when `sharex=True` | PASS | All 3 ratio-plot functions (`07_plots.py`, `02_background_estimation.py` x2) use both `sharex=True` and `fig.subplots_adjust(hspace=0)`. |

### 1.5 Save Configuration

| Rule | Status | Details |
|------|--------|---------|
| Save PDF + PNG | PASS | All plotting functions save both `.pdf` and `.png`. |
| `bbox_inches="tight"` | PASS | Used in all 14 `savefig()` calls. |
| `dpi=200` | PASS | Used in all 14 `savefig()` calls. |
| `transparent=True` | PASS | Used in all 14 `savefig()` calls. |
| `plt.close(fig)` after saving | PASS | All plotting functions close the figure after saving. |

---

## Part 2: Visual Validation

### 2.1 Data/MC Comparison Plots (from `07_plots.py`)

#### mvis_baseline.png

| Check | Status | Notes |
|-------|--------|-------|
| Experiment label | PASS | "CMS Open Data, Baseline" and sqrt(s)=8 TeV present and readable. |
| Axis labels | PASS | Y: "Events / 8", X: "m_vis [GeV]". |
| Legend | PASS | Readable, no overlap with data. Two-column layout with x-small font. |
| Data/MC ratio centered ~1.0 | PASS | Ratio generally centered around 1.0 across the spectrum. |
| Physical distribution | PASS | Smooth Z peak structure, no spikes or gaps. |
| Ratio panel connected | PASS | No visible gap; hspace=0 respected. |
| No QCD template in NN score plots | **WARNING** | QCD template is missing from NN score plots (comment in code says "skip QCD for now"). The NN score data/MC comparisons lack this background component, which may explain small data/MC mismodeling. |

#### mvis_vbf.png

| Check | Status | Notes |
|-------|--------|-------|
| Experiment label | PASS | "CMS Open Data, VBF" present. |
| Axis labels | PASS | Correct. |
| Legend | PASS | Readable. |
| Data/MC ratio | PASS | Scattered due to low statistics but centered on 1.0. |
| Physical distribution | PASS | Expected Z peak shape, low stats tails. |
| Ratio panel connected | PASS | |

#### nn_score_baseline.png

| Check | Status | Notes |
|-------|--------|-------|
| Experiment label | PASS | |
| Axis labels | PASS | Y: "Events / 0.05", X: "NN Score". |
| Legend | PASS | |
| Data/MC ratio | **WARNING** | Systematic data excess at low NN scores (0.0-0.15), ratio ~1.2-1.4. Likely due to missing QCD template. |
| Physical distribution | PASS | Smooth, no spikes. |
| Ratio panel connected | PASS | |

#### nn_score_vbf.png

| Check | Status | Notes |
|-------|--------|-------|
| Experiment label | PASS | |
| Axis labels | PASS | |
| Data/MC ratio | **WARNING** | Very large fluctuations in ratio at low NN scores due to low statistics; ratio points drop well below 0.5. Low stats effect, not a plot bug. |
| Physical distribution | PASS | |
| Ratio panel connected | PASS | |

#### mcol_baseline.png

| Check | Status | Notes |
|-------|--------|-------|
| Experiment label | PASS | |
| Axis labels | PASS | Y: "Events / 10", X: "m_col [GeV]". |
| Data/MC ratio | PASS | Generally centered on 1.0, slight deficit at ~60 GeV. |
| Physical distribution | PASS | |
| Ratio panel connected | PASS | |

#### mcol_vbf.png

| Check | Status | Notes |
|-------|--------|-------|
| Experiment label | PASS | |
| Data/MC ratio | PASS | Large uncertainties from low statistics but no systematic bias. |
| Physical distribution | PASS | |
| Ratio panel connected | PASS | |

#### tau_pt_baseline.png

| Check | Status | Notes |
|-------|--------|-------|
| Experiment label | PASS | |
| Axis labels | PASS | |
| Data/MC ratio | PASS | Centered on 1.0. |
| Physical distribution | PASS | Steeply falling pT spectrum as expected. |
| Ratio panel connected | PASS | |

#### mu_pt_baseline.png

| Check | Status | Notes |
|-------|--------|-------|
| Experiment label | PASS | |
| Axis labels | PASS | |
| Data/MC ratio | PASS | |
| Physical distribution | PASS | |
| Ratio panel connected | PASS | |

#### met_pt_baseline.png

| Check | Status | Notes |
|-------|--------|-------|
| Experiment label | PASS | |
| Axis labels | PASS | |
| Data/MC ratio | PASS | |
| Physical distribution | PASS | |
| Ratio panel connected | PASS | |

#### njets_baseline.png

| Check | Status | Notes |
|-------|--------|-------|
| Experiment label | PASS | |
| Axis labels | PASS | |
| Data/MC ratio | **WARNING** | Ratio at Njets=2 is ~0.75, and Njets>=3 bins have very few events making ratio unreliable. The 0-jet and 1-jet bins dominate and show reasonable agreement. |
| Physical distribution | PASS | Steeply falling multiplicity, as expected. |
| Ratio panel connected | PASS | |

#### delta_r_baseline.png

| Check | Status | Notes |
|-------|--------|-------|
| Experiment label | PASS | |
| Axis labels | PASS | |
| Data/MC ratio | PASS | |
| Physical distribution | PASS | Peak at ~3.1 (back-to-back topology) as expected for Z/H decays. |
| Ratio panel connected | PASS | |

### 2.2 Background Estimation Plots (from `02_background_estimation.py`)

#### wjets_validation_midmt.png

| Check | Status | Notes |
|-------|--------|-------|
| Experiment label | PASS | "CMS Open Data" present. |
| Axis labels | PASS | |
| Legend | PASS | Includes SF value in W+jets label. |
| Data/MC ratio | **WARNING** | Shows SF_W=1.00 in the legend, meaning the sideband normalization returned a scale factor near unity. Data/MC agreement is good overall (~1.0), but data exceeds MC consistently, suggesting the W+jets SF may be slightly underestimated or an additional QCD component is missing in this intermediate-mT region. |
| Physical distribution | PASS | |
| Ratio panel connected | PASS | |

#### mt_regions.png

| Check | Status | Notes |
|-------|--------|-------|
| Experiment label | PASS | |
| Axis labels | PASS | Y: "Events / 5 GeV", X: "m_T(mu, E_T^miss) [GeV]". |
| Legend | PASS | Region boundaries clearly marked with colored dashed lines. |
| Data/MC ratio | **WARNING** | Data/MC ratio is systematically >1 in the high-mT region (mT > 70 GeV), reaching ~1.1-1.2. This is the region used to derive the W+jets SF, and the deficit suggests possible issues with the W+jets normalization or missing backgrounds at high mT. |
| Physical distribution | PASS | Log scale, smooth distribution. |
| Ratio panel connected | PASS | |

### 2.3 NN Diagnostic Plots (from `04_nn_discriminant.py`)

#### nn_roc.png

| Check | Status | Notes |
|-------|--------|-------|
| Experiment label | PASS | "CMS Open Simulation" -- correct for MC-only. |
| Axis labels | PASS | Clear FPR/TPR labels. |
| Legend | PASS | AUC values reported: Train=0.8426, Val=0.8325, Test=0.8250. |
| Physical content | PASS | All 3 curves (train/val/test) very close, indicating no significant overtraining. AUC > 0.75 threshold met. |

#### nn_overtraining.png

| Check | Status | Notes |
|-------|--------|-------|
| Experiment label | PASS | "CMS Open Simulation" present. |
| Axis labels | PASS | |
| Legend | PASS | Readable, placed at upper center. |
| Physical content | PASS | Train (filled) and test (points) distributions agree well for both signal and background, confirming no overtraining. |

#### nn_feature_importance.png

| Check | Status | Notes |
|-------|--------|-------|
| Experiment label | PASS | "CMS Open Simulation" present. |
| Axis labels | PASS | Y: feature names readable at x-small, X: "Mean |weight| (first layer)". |
| Legend | N/A | No legend needed for a single-series bar chart. |
| Physical content | PASS | mvis is the most important feature, followed by delta_r and met_pt. Reasonable physics ordering. |

### 2.4 Approach Comparison (from `06_approach_comparison.py`)

#### approach_comparison.png

| Check | Status | Notes |
|-------|--------|-------|
| Experiment label | PASS | "CMS Open Data" present. |
| Axis labels | PASS | X: "Expected Significance [sigma]". |
| Legend | N/A | Labels are on the y-axis (approach names). |
| Physical content | PASS | NN discriminant shows highest expected significance (~1.6 sigma), followed by cut-based m_vis (~0.85) and collinear mass (~0.8). |

---

## Part 3: Summary of Findings

### RED FLAG (Category A)

**F1: `ax.bar()` and `ax.step()` used instead of `mh.histplot()`.**
The plotting specification requires using `mh.histplot` for histogram rendering.
All four plotting scripts (`02_background_estimation.py`, `04_nn_discriminant.py`,
`06_approach_comparison.py`, `07_plots.py`) use raw `ax.bar()` for stacked
histograms and `ax.step()` for signal overlays. `mh.histplot` is never called.

- `02_background_estimation.py`: lines 315, 385 (`ax.bar`)
- `04_nn_discriminant.py`: lines 291, 293 (`ax.bar`)
- `07_plots.py`: line 171 (`ax.bar`), line 187 (`ax.step`)

**Severity assessment:** While the resulting plots are visually acceptable
(the CMS style is applied, axes are labeled, legends are correct, etc.),
the use of raw matplotlib primitives bypasses `mplhep`'s histogram rendering
which provides consistent bar widths, edge handling, and style integration.
The visual output is functionally adequate but violates the spec rule:
"No `ax.step()`/`ax.bar()` for histograms (use `mh.histplot`)."

### WARNINGS (Category B/C)

**F2 (Category B): Missing QCD template in NN score plots.**
The `07_plots.py` script explicitly skips QCD estimation for NN score
distributions (line 302: "skip QCD for now"). This results in a systematic
data excess visible in `nn_score_baseline.png` at low NN scores. The QCD
component is present in all other data/MC comparison plots (mvis, mcol,
kinematic variables). This should be resolved before the final analysis --
either by computing NN scores for SS data to build the QCD template, or
by noting this as a known limitation.

**F3 (Category C): Data/MC normalization in high-mT region.**
The `mt_regions.png` plot shows a ~10-20% data excess over MC prediction
in the high-mT sideband (mT > 70 GeV). Since this region is used to
derive the W+jets normalization scale factor, this suggests incomplete
background modeling or a self-consistency issue. Worth investigating but
may be expected given the simplicity of the background model.

**F4 (Category C): W+jets SF = 1.00 shown in validation plot.**
The `wjets_validation_midmt.png` legend shows "W+jets (SF=1.00)", which
either means the sideband method returned exactly 1.0 or the plot was
made before the SF was applied. The `background_estimation.json` should
be cross-checked to confirm the SF was properly propagated.

**F5 (Category C): Njets ratio at high multiplicity.**
The `njets_baseline.png` ratio panel shows significant Data/MC
disagreement at Njets=2 (~0.75) and higher multiplicities. This is
expected behavior for LO MC samples and is not a plotting error, but
it should be noted in the SELECTION.md artifact as a known modeling
limitation.

---

## Part 4: Global Assessment

| Category | Count | Items |
|----------|-------|-------|
| RED FLAG (A) | 1 | F1: ax.bar/ax.step instead of mh.histplot |
| WARNING (B) | 1 | F2: Missing QCD in NN score plots |
| WARNING (C) | 3 | F3, F4, F5: Background modeling notes |

### Items that PASS

- figsize=(10,10) on all figures
- mh.style.use("CMS") in all scripts
- exp_label on every figure with correct Open Data / Open Simulation distinction
- PDF + PNG saved with bbox_inches="tight", dpi=200, transparent=True
- hspace=0 with sharex=True on all ratio plots
- No set_title(), no tight_layout(), no absolute fontsize, no colorbar
- plt.close(fig) after all saves
- All figures are visually readable with proper axis labels and legends
- Ratio panels properly connected (no visible gaps)
- Data/MC ratios generally centered on 1.0
- Physical distributions show expected shapes (Z peak, falling pT spectra, etc.)
- NN overtraining check passes (train/test agreement)
