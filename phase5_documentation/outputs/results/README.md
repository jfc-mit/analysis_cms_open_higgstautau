# Machine-Readable Results

This directory contains symlinks to the Phase 4c machine-readable output files.

## Contents

| File | Description |
|------|-------------|
| `observed_results.json` | Full data fit results for all three approaches (mu_hat, mu_err, significance, limits, NP pulls, GoF, per-category fits, CLs scans) |
| `diagnostics_full.json` | Full data diagnostics: pre-fit chi2, per-category fits, impact ranking for all 21 NPs, VBF process decomposition |
| `gof_investigation.json` | Dedicated GoF investigation with 200 toys per approach using both Pearson chi2 and LLR test statistics, per-category decomposition |
| `data_histograms_full.json` | Full data histograms for all three approaches in both categories (bin edges, data counts, MC predictions per process) |

## Primary result

The primary result is the NN score signal strength from `observed_results.json`:
- mu_hat = 0.6346 (rounds to 0.63)
- mu_err = 1.08
- Observed significance: 0.61 sigma
- Observed 95% CL upper limit: mu < 2.85

## Symlink targets

All files are symlinks to `phase4_inference/4c_observed/outputs/`. The original files are produced by the Phase 4c statistical analysis scripts.
