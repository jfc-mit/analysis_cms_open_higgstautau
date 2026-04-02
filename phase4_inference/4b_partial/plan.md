# Phase 4b Plan: 10% Data Validation

## Goal
Run 10% of the observed data through the full analysis chain and compare
to the Phase 4a expected results. This is the first encounter with real
data and serves as a pre-unblinding sanity check.

## Data inventory
- OS SR data: Run2012B (26,236 events) + Run2012C (41,752 events) = 67,988 total
- SS SR data: Run2012B (8,879) + Run2012C (14,255) = 23,134 total
- 10% subsample: ~6,799 OS SR events, ~2,313 SS SR events

## Scripts

### 01_select_10pct.py
- Load OS SR and SS SR data from both Run periods
- Use np.random.RandomState(42) for reproducibility
- Select 10% of data events (random uniform per-event mask)
- Save subsampled arrays as npz files for downstream use
- Document: N_selected, N_total, actual fraction

### 02_build_data_histograms.py
- Histogram the 10% data subsample in all 3 observables (m_vis, nn_score, m_col)
- In both categories (Baseline, VBF)
- Scale data by 10x for comparison to full MC predictions
- Also build unscaled histograms (for the actual fit)
- Compare to full expected from 4a nominal templates
- Save data histograms as JSON

### 03_fit_10pct_data.py
- For each of the 3 approaches (m_vis, nn_score, m_col):
  - Load the pyhf workspace from Phase 4a
  - Replace Asimov observations with actual 10% data histograms (scaled x10)
  - Fit for mu (MLE)
  - Report: mu_hat, sigma(mu), significance
  - Compare to expected (mu=1, sigma from 4a)
  - Compute NP pulls
  - Run GoF (chi2 + toy-based p-value with 200 toys)

### 04_diagnostics.py
- Per-category fit: fit Baseline-only and VBF-only for mu consistency
- NP pull analysis: flag any |pull| > 2
- Data/MC chi2 per discriminant per category

### 05_figures.py
- Data/MC comparison plots with ratio panels for all 6 combinations
  (3 observables x 2 categories)
- NP pull plot from 10% fit (primary NN approach)
- mu comparison: expected vs 10% for all 3 approaches
- GoF toy distributions with observed chi2 marked

## Outputs
- `outputs/INFERENCE_PARTIAL.md` — primary artifact
- `outputs/partial_data_results.json` — machine-readable fit results
- `outputs/data_histograms_10pct.json` — 10% data histograms
- `outputs/figures/*.pdf` — all diagnostic plots

## Validation criteria
- mu within 2 sigma of expected (mu=1)
- No NP pull > 2 sigma
- GoF p-value > 0.05
- Data/MC agreement in control distributions (Z peak, mT sideband)
- Per-category mu consistency
