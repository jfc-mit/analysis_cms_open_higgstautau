# Phase 4c Plan: Full Data Results

## Overview
Run the FULL dataset through the signal strength extraction and compare
to both Phase 4a (expected/Asimov) and Phase 4b (10% data) results.

## Scripts

### 01_build_full_data_histograms.py
- Load ALL data events from phase3 outputs (both Run2012B and Run2012C)
- No subsampling -- use 100% of data
- Histogram in all 3 discriminants (m_vis, NN score, m_col) x 2 categories (Baseline, VBF)
- Build QCD template from full SS data (data_SS - MC_SS) * R_OS/SS
- Use the SAME merged binning as Phase 4a workspaces
- Apply W+jets SF from phase3

### 02_fit_full_data.py
- For each of the 3 approaches (mvis, nn_score, mcol):
  - Load the pyhf workspace from Phase 4a (already has [-30,30] POI bounds)
  - Replace Asimov observations with actual full data
  - MLE fit for mu -> report mu_hat, sigma(mu)
  - Compute NP pulls
  - GoF: chi2/ndf AND toy-based p-value (200 toys)
  - Observed significance (q0 test)
  - CLs 95% upper limit scan
- Compare to BOTH expected (4a) AND 10% (4b)

### 03_diagnostics.py
- Per-category fit (Baseline-only, VBF-only) for each approach
- Pre-fit data/MC chi2 per discriminant per category
- Impact ranking: rank NPs by their impact on mu

### 04_figures.py
- Data/MC pre-fit comparison (6 plots: 3 approaches x 2 categories)
- Post-fit data/MC comparison (6 plots)
- NP pulls from full data fit (NN score primary)
- mu comparison: Expected vs 10% vs Full for all approaches (THREE-WAY)
- Impact ranking plot
- GoF toy distributions with observed chi2

### 05_write_artifact.py
- Not a script; INFERENCE_OBSERVED.md written manually based on results

## Artifacts
- `outputs/observed_results.json` — full fit results
- `outputs/diagnostics_full.json` — per-category fits, pre-fit chi2
- `outputs/data_histograms_full.json` — full data histograms
- `outputs/figures/*.{pdf,png}` — all diagnostic plots
- `outputs/INFERENCE_OBSERVED.md` — primary artifact

## Key Comparisons
| Quantity | Expected (4a) | 10% (4b) | Full (4c) |
|----------|---------------|-----------|-----------|
| mu (NN)  | 1.0 +/- 1.25 | from 4b   | TBD       |
| mu (mvis)| 1.0 +/- 3.09 | from 4b   | TBD       |
| mu (mcol)| 1.0 +/- 3.72 | from 4b   | TBD       |
