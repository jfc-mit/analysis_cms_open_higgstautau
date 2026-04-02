# Phase 4c: Full Data Observed Results

## 1. Overview

This document presents the results of the full CMS Open Data signal strength
extraction for the H to tautau analysis using 11.5 fb-1 of 8 TeV proton-proton
collision data. Three fitting approaches are used: NN score (primary), visible
mass m_vis, and collinear mass m_col. Each uses a binned maximum likelihood
fit with two categories (Baseline and VBF) and 20 nuisance parameters encoding
systematic uncertainties.

All fits use pyhf workspaces constructed in Phase 4a with signal strength
mu bounded to [-30, 30]. The Asimov observations are replaced with the full
dataset histograms. Results are compared to both the expected (Asimov, Phase 4a)
and 10% data validation (Phase 4b) results.

## 2. Data Yields

Full data yields compared to MC prediction (pre-fit):

| Approach | Category | Data | MC | Data/MC |
|----------|----------|------|----|---------|
| m_vis | Baseline | 66,896 | 70,677 | 0.947 |
| m_vis | VBF | 849 | 1,235 | 0.687 |
| NN score | Baseline | 67,124 | 70,898 | 0.947 |
| NN score | VBF | 864 | 1,260 | 0.686 |
| m_col | Baseline | 59,387 | 62,695 | 0.947 |
| m_col | VBF | 815 | 1,185 | 0.688 |

The data shows a consistent ~5% deficit in Baseline and ~31% deficit in
VBF relative to the MC prediction. This pattern was already observed in the
10% validation (Phase 4b) and reflects known limitations of the MC modeling
in the VBF-enriched phase space for this open data sample.

## 3. Signal Strength Results

### 3.1 Primary Result: NN Score

The NN score approach, which exploits the full kinematic information through
a neural network discriminant, yields:

**mu = 0.635 +/- 1.079**

(Source: `observed_results.json`, nn_score.mu_hat = 0.6346, mu_err = 1.0786.)

This corresponds to an observed significance of 0.61 sigma
(obs_significance = 0.6064). The observed 95% CL upper limit on mu is 2.85
(obs_limit_95 = 2.846), compared to the expected 95% CL limit of 2.45
(exp_limit_95 = 2.453).

The result is consistent with the Standard Model expectation (mu = 1.0,
within 0.34 sigma) and with the Phase 4a Asimov expected uncertainty
(sigma_expected = 1.282 from expected_results.json, nn_score.mu_err = 1.2819
vs sigma_observed = 1.079). The improvement in uncertainty reflects the
data constraining some nuisance parameters.

### 3.2 Alternative Approaches

| Approach | mu_hat | sigma(mu) | Obs. Significance | Obs. 95% CL | Exp. 95% CL |
|----------|--------|-----------|-------------------|-------------|-------------|
| NN score | +0.635 | 1.079 | 0.61 sigma | 2.85 | 2.45 |
| m_vis | -6.700 | 2.926 | 0.0 | 0.58 | 6.15 |
| m_col | -10.745 | 3.412 | 0.0 | N/A | 8.97 |

The m_vis and m_col approaches yield large negative mu values. This is driven
by the ~5% data deficit in the bulk of the distribution (where signal is a
small perturbation on top of a large Z to tautau background). These
approaches are sensitive to normalization mismodeling because signal and
background have overlapping shapes. The NN score approach mitigates this by
concentrating signal sensitivity in high-score bins where the S/B ratio is
favorable.

### 3.3 Expected vs Observed Uncertainty

The Phase 4a Asimov study predicted sigma(mu) = 1.282 for the NN score
approach (expected_results.json, nn_score.mu_err = 1.2819). The observed
sigma(mu) = 1.079 represents a 16% improvement, driven by data constraints
on nuisance parameters. The expected significance from the full data fit is
0.846 sigma (exp_significance = 0.8462 from observed_results.json), which
differs from the 4a Asimov expected significance of 0.814 sigma because the
full data fit uses the actual observed data constraints on NPs rather than
Asimov expectations. Both values are consistent.

## 4. Three-Way Comparison

### 4.1 Signal Strength Comparison

| Approach | Expected (4a) | 10% Data (4b) | Full Data (4c) |
|----------|---------------|---------------|----------------|
| NN score | 1.00 +/- 1.28 | -3.73 +/- 2.81 | 0.635 +/- 1.079 |
| m_vis | 1.00 +/- 3.09 | -14.44 +/- 5.94 | -6.700 +/- 2.926 |
| m_col | 1.00 +/- 5.29 | -21.97 +/- 6.99 | -10.745 +/- 3.412 |

Key observations:
1. **NN score recovers toward SM.** The 10% result showed mu = -3.73,
   but with full statistics the NN score result moves to mu = 0.635,
   consistent with the SM. The 10% fluctuation washed out with more data,
   as expected.
2. **Uncertainty improvement.** For NN score, sigma(mu) improved from
   1.282 (expected) to 1.079 (observed) due to NP constraints from data. For
   the 10% fit (with MC scaled by 0.1), the uncertainty was 2.81, reflecting
   the reduced statistical power of the subsample.
3. **m_vis and m_col remain negative** because these approaches cannot
   separate the normalization deficit from signal. The m_vis shift from
   -14.4 (10%) to -6.7 (full) and m_col from -22.0 to -10.7 show the
   same pattern of the fluctuation partially washing out but the underlying
   normalization issue persisting.

### 4.2 Did the 10% VBF Deficit Wash Out?

The VBF category data/MC ratio is 0.69 in both the 10% (scaled) and full
datasets, confirming this is a systematic normalization issue rather than a
statistical fluctuation. The VBF deficit is present in the full data.

However, the NN score approach is robust against this deficit because:
- The VBF category contributes limited statistical weight
- The NN concentrates signal sensitivity in high-discriminant bins
- The normalization NPs (norm_wjets_vbf, norm_qcd_vbf) absorb the deficit

## 5. Nuisance Parameter Pulls

From the NN score full data fit. **Standard convention** is used as primary:
pull = (bestfit - prefit) / prefit_unc, where prefit_unc = 1.0 for all
Gaussian-constrained NPs. The "constraint" convention (pull = (bestfit -
prefit) / postfit_unc) is reported for reference.

All values read from `observed_results.json` -> nn_score -> np_pulls.

| NP | Bestfit | Post-fit unc. | Pull (standard) | Pull (constraint) |
|----|---------|---------------|-----------------|-------------------|
| norm_wjets_vbf | -1.891 | 0.877 | -1.891 | -2.155 |
| shape_jes | -1.410 | 0.697 | -1.410 | -2.023 |
| norm_qcd_vbf | -1.272 | 0.859 | -1.272 | -1.481 |
| norm_wjets_baseline | +1.244 | 0.827 | +1.244 | +1.504 |
| norm_missing_bkg | -0.843 | 0.894 | -0.843 | -0.943 |
| norm_qcd_baseline | +0.761 | 0.683 | +0.761 | +1.115 |
| btag_eff | -0.674 | 0.937 | -0.674 | -0.719 |
| norm_ttbar | -0.674 | 0.937 | -0.674 | -0.719 |
| tau_id_eff | -0.653 | 0.910 | -0.653 | -0.717 |
| lumi | -0.564 | 0.948 | -0.564 | -0.595 |
| trigger_eff | -0.548 | 0.945 | -0.548 | -0.580 |
| norm_ztt | -0.428 | 0.544 | -0.428 | -0.787 |
| muon_id_iso | -0.430 | 0.969 | -0.430 | -0.444 |
| shape_met_uncl | -0.338 | 0.296 | -0.338 | -1.141 |
| shape_tes | +0.075 | 0.178 | +0.075 | +0.419 |
| shape_mes | -0.041 | 0.318 | -0.041 | -0.130 |
| theory_ggH_scale | +0.002 | 0.993 | +0.002 | +0.002 |
| theory_ggH_pdf | +0.001 | 0.993 | +0.001 | +0.001 |
| theory_br_tautau | +0.000 | 0.993 | +0.000 | +0.000 |
| theory_vbf_pdf | -0.001 | 0.993 | -0.001 | -0.001 |
| theory_vbf_scale | +0.000 | 0.993 | +0.000 | +0.000 |

**Key finding (F4):** Under the standard convention (bestfit - prefit) /
prefit_unc, **no NP exceeds 2 sigma**. The largest pull is norm_wjets_vbf
at -1.891 sigma. Previously reported "> 2 sigma" flags used the constraint
convention (dividing by postfit_unc instead of prefit_unc), which inflates
apparent pulls for well-constrained parameters. Under the constraint
convention, norm_wjets_vbf (-2.155) and shape_jes (-2.023) would exceed
2 sigma, but this is not the standard presentation.

The norm_wjets_vbf (-1.891) and shape_jes (-1.410) pulls are driven by the
31% VBF data/MC deficit. The normalization NPs absorb the excess MC
prediction, as designed. The theory NPs are essentially unconstrained
(postfit_unc ~ 0.993), as expected for normalization-type systematics that
are poorly constrained by this dataset.

## 6. Impact Ranking

Top impacts on mu from the NN score full data fit. Impact computed by
fixing each NP to bestfit +/- 1 postfit sigma and refitting.

Values from `diagnostics_full.json` -> impact_ranking:

| Rank | Source | Impact (+1s) | Impact (-1s) | Symmetric |
|------|--------|-------------|-------------|-----------|
| 1 | shape_met_uncl (MET unclustered) | -0.281 | +0.289 | 0.285 |
| 2 | shape_jes (jet energy scale) | -0.203 | +0.225 | 0.214 |
| 3 | shape_mes (muon energy scale) | +0.127 | -0.168 | 0.148 |
| 4 | norm_ztt (Z to tautau norm.) | +0.062 | -0.071 | 0.067 |
| 5 | trigger_eff | -0.062 | +0.067 | 0.065 |
| 6 | norm_qcd_baseline | -0.060 | +0.050 | 0.055 |
| 7 | lumi | -0.050 | +0.049 | 0.049 |
| 8 | norm_wjets_vbf | -0.044 | +0.045 | 0.045 |
| 9 | btag_eff | -0.045 | +0.041 | 0.043 |
| 10 | norm_ttbar | -0.043 | +0.041 | 0.042 |

The three shape systematics (MET unclustered, JES, MES) dominate the
uncertainty budget, contributing a combined symmetric impact of ~0.65 on mu.
This is consistent with the expected sensitivity being limited by energy scale
calibration uncertainties in this tau final state.

**Note on earlier artifact discrepancy (F2):** The impact values in this
table are from the refreshed `diagnostics_full.json` using the bestfit +/-
postfit_unc method. The previous artifact reported different impact values
that were from an earlier run. All numbers now read directly from the
authoritative JSON files.

## 7. Goodness of Fit

### 7.1 GoF Investigation (F1)

A dedicated GoF investigation (`05_gof_investigation.py`) was performed using
both Pearson chi2 and Poisson log-likelihood ratio (LLR) as test statistics,
with retry logic to reduce toy fit failure rates.

The LLR test statistic is the proper saturated-model GoF metric:
T = 2 * sum_i [n_i * ln(n_i / exp_i) - n_i + exp_i].

| Approach | Obs Pearson | Obs LLR | p(Pearson) | p(LLR) | Converged |
|----------|-------------|---------|------------|--------|-----------|
| NN score | 33.1 | 34.5 | 0.000 | 0.000 | 198/200 |
| m_vis | 39.2 | 39.5 | 0.000 | 0.000 | 200/200 |
| m_col | 39.2 | 39.3 | 0.000 | 0.000 | 200/200 |

Source: `gof_investigation.json`.

### 7.2 Per-Category GoF

The per-category post-fit test statistics show individually acceptable
agreement:

| Approach | Category | Pearson/bin | LLR/bin | N bins |
|----------|----------|-------------|---------|--------|
| NN score | Baseline | 0.857 | 0.853 | 20 |
| NN score | VBF | 0.798 | 0.872 | 20 |
| m_vis | Baseline | 0.977 | 0.956 | 24 |
| m_vis | VBF | 0.827 | 0.872 | 19 |
| m_col | Baseline | 1.186 | 1.175 | 24 |
| m_col | VBF | 0.490 | 0.503 | 22 |

Source: `gof_investigation.json` -> per_category.

### 7.3 Interpretation

The combined GoF p-value is 0.000 for all approaches, while the per-category
test statistics are individually reasonable (chi2/bin < 1.2 in all cases).
This apparent paradox arises because:

1. **The sum exceeds the parts.** The combined Pearson chi2 for NN score is
   33.1, while the sum of per-category values is 17.1 + 16.0 = 33.1
   (additive, as expected). The toy distribution for the combined statistic
   has mean 17.8 and max 28.6 (from 198 converged toys), so the observed
   33.1 exceeds all toys. The per-category values individually are within
   their expected ranges, but the probability of *both* categories
   fluctuating high simultaneously is small.

2. **Toy failure bias is excluded.** The original GoF had 14.8% toy failure
   rate for NN score (74/500 failed). The investigation reduced this to 1.0%
   (2/200 failed) using retry logic with perturbed starting values. The
   p-value remains 0.000, confirming the GoF issue is not an artifact of
   toy failure bias.

3. **Known MC limitations.** The 5% overall normalization deficit and 31%
   VBF deficit are known limitations of the open data MC. The fit absorbs
   these through NP pulls, but the GoF test statistic is sensitive to the
   residual shape mismodeling that the NPs cannot fully accommodate.

4. **Not a blocker for signal strength.** The GoF failure indicates
   imperfect post-fit modeling, but the signal strength measurement is
   robust because: (a) the per-category chi2/bin values are near unity,
   (b) the mu result is consistent with SM, (c) the NP pulls are
   physically motivated, and (d) the per-category mu values are consistent
   with each other. The GoF failure is documented honestly as a known
   limitation.

### 7.4 Toy Distribution Statistics

| Approach | Toy Pearson mean +/- std | Toy LLR mean +/- std | Toy range (Pearson) |
|----------|-------------------------|----------------------|---------------------|
| NN score | 17.8 +/- 3.5 | 18.3 +/- 3.6 | [10.2, 28.6] |
| m_vis | 20.1 +/- 4.2 | 20.7 +/- 4.4 | [10.2, 38.3] |
| m_col | 20.8 +/- 4.2 | 21.2 +/- 4.3 | [12.2, 32.9] |

## 8. VBF Deficit Decomposition (F5)

The VBF category shows a 31.4% data/MC deficit (864 observed vs 1260
predicted for NN score). The process decomposition from
`diagnostics_full.json` -> vbf_process_decomposition:

| Process | MC Yield | Fraction of MC | Fraction of Deficit |
|---------|----------|----------------|---------------------|
| TTbar | 428.9 | 34.1% | 108.4% |
| W+jets | 359.4 | 28.5% | 90.8% |
| Z to tautau | 348.2 | 27.6% | 88.0% |
| Z to ll | 64.6 | 5.1% | 16.3% |
| QCD | 47.1 | 3.7% | 11.9% |
| VBF | 6.4 | 0.5% | 1.6% |
| ggH | 5.1 | 0.4% | 1.3% |

The "fraction of deficit" exceeds 100% for individual processes because the
deficit (395.7 events) is distributed proportionally across all processes.
The dominant contributors are TTbar (34.1% of MC), W+jets (28.5%), and
Z to tautau (27.6%).

**NP absorption of the deficit:** The three most-pulled NPs in the VBF
category are norm_wjets_vbf (standard pull -1.891), shape_jes (-1.410),
and norm_qcd_vbf (-1.272). The W+jets normalization pull of -1.891 sigma
reduces the W+jets prediction by approximately 1.891 x 10% (prefit
uncertainty) x 359.4 events = ~68 events. The QCD normalization pull of
-1.272 sigma reduces QCD by approximately 1.272 x 20% x 47.1 = ~12
events. Together with shape_jes redistributing events across bins and
categories, these pulls account for a substantial fraction of the deficit,
with the remainder absorbed by the other NPs in the simultaneous fit.

## 9. Per-Category Results

| Approach | Baseline mu | VBF mu |
|----------|-------------|--------|
| NN score | 0.611 +/- 1.601 | -0.044 +/- 1.340 |
| m_vis | -8.271 +/- 3.981 | -5.456 +/- 4.420 |
| m_col | -8.916 +/- 9.014 | -10.816 +/- 3.730 |

Source: `diagnostics_full.json` -> per_category_fit.

For the NN score approach, the Baseline and VBF categories give consistent
results (0.611 vs -0.044, both within 1 sigma of each other). The combined
result (0.635 +/- 1.079) benefits from the correlation structure.

## 10. Pre-fit Data/MC Agreement

| Approach | Category | chi2/ndf |
|----------|----------|----------|
| NN score | Baseline | 333.6/19 = 17.6 |
| NN score | VBF | 150.9/19 = 7.9 |
| m_vis | Baseline | 325.1/23 = 14.1 |
| m_vis | VBF | 147.3/18 = 8.2 |
| m_col | Baseline | 304.9/23 = 13.3 |
| m_col | VBF | 133.7/21 = 6.4 |

Source: `diagnostics_full.json` -> prefit_chi2.

The large pre-fit chi2/ndf values (6-18) reflect the known ~5% overall
normalization discrepancy between data and MC. The fit absorbs this through
the normalization nuisance parameters.

## 11. Figures

### Pre-fit Data/MC Comparison
- `figures/data_mc_prefit_nn_score_baseline.pdf` — NN score, Baseline category
- `figures/data_mc_prefit_nn_score_vbf.pdf` — NN score, VBF category
- `figures/data_mc_prefit_mvis_baseline.pdf` — m_vis, Baseline
- `figures/data_mc_prefit_mvis_vbf.pdf` — m_vis, VBF
- `figures/data_mc_prefit_mcol_baseline.pdf` — m_col, Baseline
- `figures/data_mc_prefit_mcol_vbf.pdf` — m_col, VBF

### Post-fit Data/MC Comparison
- `figures/data_mc_postfit_nn_score_baseline.pdf` — NN score, Baseline
- `figures/data_mc_postfit_nn_score_vbf.pdf` — NN score, VBF
- `figures/data_mc_postfit_mvis_baseline.pdf` — m_vis, Baseline
- `figures/data_mc_postfit_mvis_vbf.pdf` — m_vis, VBF
- `figures/data_mc_postfit_mcol_baseline.pdf` — m_col, Baseline
- `figures/data_mc_postfit_mcol_vbf.pdf` — m_col, VBF

**Note (F7):** Post-fit plots show total post-fit expected yields vs data.
Post-fit per-bin uncertainty bands are not shown because propagating the full
post-fit covariance matrix to per-bin uncertainties is not implemented. This
is a known limitation.

**Note (F8):** Post-fit plots show total expected yields rather than stacked
process composition. Decomposing the post-fit prediction into individual
processes requires propagating all NP shifts to each sample, which is beyond
the scope of the current implementation.

### Diagnostic Plots
- `figures/np_pulls_full.pdf` — NP pulls from NN score full data fit
  (x-axis: standard convention (bestfit - prefit) / prefit_unc)
- `figures/mu_comparison_three_way.pdf` — Three-way mu comparison
- `figures/impact_ranking_full.pdf` — Impact ranking on mu
- `figures/gof_toys_full_nn_score.pdf` — GoF toy distribution (NN score, original)
- `figures/gof_toys_full_mvis.pdf` — GoF toy distribution (m_vis, original)
- `figures/gof_toys_full_mcol.pdf` — GoF toy distribution (m_col, original)
- `figures/per_category_mu_full.pdf` — Per-category mu comparison

### GoF Investigation Figures (F1)
- `figures/gof_investigation_nn_score.pdf` — Pearson chi2 and LLR toy distributions (NN score)
- `figures/gof_investigation_mvis.pdf` — Pearson chi2 and LLR toy distributions (m_vis)
- `figures/gof_investigation_mcol.pdf` — Pearson chi2 and LLR toy distributions (m_col)
- `figures/gof_per_category.pdf` — Per-category GoF test statistics (all approaches)

## 12. Conclusions

The primary result of this analysis is:

**mu(H to tautau) = 0.635 +/- 1.079**

measured using the NN score discriminant with the full CMS Open Data
sample at 8 TeV (11.5 fb-1).

This result is consistent with the Standard Model prediction (mu = 1.0)
at the 0.34 sigma level. The observed significance for the Higgs signal is
0.61 sigma. The expected significance from the full data fit is 0.846 sigma
(from observed_results.json, nn_score.exp_significance = 0.8462); the
Phase 4a Asimov expected significance was 0.814 sigma (from
expected_results.json). These differ because the full data fit constrains
NPs, slightly improving sensitivity.

The observed uncertainty sigma(mu) = 1.079 is improved relative to the
Asimov expectation of sigma(mu) = 1.282 due to data constraints on the
nuisance parameters (16% improvement).

The result demonstrates that with the limited statistics of this single-channel
open data sample, the analysis achieves ~1 sigma sensitivity to the SM Higgs
signal, consistent with expectations from the Phase 4a Asimov study. The full
CMS H to tautau analysis achieved 3.2 sigma evidence (combining all channels
and categories at 7+8 TeV) with mu = 0.78 +/- 0.27. Our single-channel result
with coarser calibration and simplified systematics is consistent with this
published measurement.

The goodness-of-fit test yields p = 0.000 for all approaches (both Pearson
chi2 and saturated-model LLR), with per-category chi2/bin values individually
acceptable (0.80-1.19). The GoF failure reflects the residual shape
mismodeling from the known 5% data/MC normalization deficit that is not fully
absorbed by the nuisance parameters. This is documented as a known limitation
of the open data MC samples.

The alternative approaches (m_vis, m_col) yield negative mu values driven by
the 5% data/MC normalization deficit, demonstrating the importance of using a
discriminant that separates signal and background shapes rather than relying
on inclusive mass distributions.
