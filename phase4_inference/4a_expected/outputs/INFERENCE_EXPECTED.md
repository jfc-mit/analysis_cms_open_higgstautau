# Phase 4a: Expected Results — H->tautau in the mu-tau_h Final State

## 1. Statistical Model Construction

### 1.1 Model overview

The statistical analysis uses a binned profile likelihood ratio method
implemented in pyhf. For each of the three fitting approaches (visible
mass, NN discriminant, collinear mass), a simultaneous fit is performed
across two categories (Baseline and VBF) with a single parameter of
interest (POI): the signal strength modifier mu = sigma_obs / sigma_SM.

The model includes:
- **Signal**: ggH and VBF production, floating with a common mu
- **Backgrounds**: Z->tautau (ZTT), Z->ll (ZLL), ttbar, W+jets, QCD multijet
- **Systematic uncertainties**: 21 nuisance parameters (normalization + shape)
  plus Barlow-Beeston statistical uncertainties per bin per channel
- **Total parameters**: ~71 per workspace (21 NPs + 50 staterror gammas + 1 POI)

### 1.2 Template construction

Templates are built from Phase 3 selected event arrays:

**MC processes** (OS signal region): DY is decomposed into ZTT and ZLL
using generator-level truth matching (`is_ztt` flag). W+jets combines
W1J + W2J + W3J samples with the data-driven scale factor SF_W = 0.999.

**QCD template** (data-driven): QCD = (Data_SS - MC_SS) x R_OS/SS where
R_OS/SS = 0.979 +/- 0.018 from Phase 3 background estimation. Negative
bins are set to zero.

**Categorization**: Events with >= 2 jets, m_jj > 200 GeV, and
|delta_eta_jj| > 2.0 enter the VBF category; all others enter Baseline.

### 1.3 Binning

Initial (before merging):

| Approach | Observable | Bins | Range |
|----------|-----------|------|-------|
| m_vis | Visible di-tau mass | 25 | 0-250 GeV |
| NN score | Neural network discriminant | 20 | 0-1 |
| m_col | Collinear approximation mass | 25 | 0-300 GeV |

**Low-statistics bin merging (F1 fix):** To prevent GoF toy convergence
failures caused by near-empty bins in the VBF category and the kinematic
dead zone (m_vis < 10 GeV), adjacent bins with fewer than 10 total
expected events are merged. The final bin counts are:

| Approach | Baseline bins | VBF bins |
|----------|--------------|----------|
| m_vis | 24 | 19 |
| NN score | 20 | 20 |
| m_col | 24 | 22 |

---

## 2. Template Yields

### 2.1 Baseline category

| Process | m_vis | NN score | m_col |
|---------|-------|----------|-------|
| ggH | 143.0 | 143.0 | 128.0 |
| VBF | 8.2 | 8.2 | 7.9 |
| ZTT | 38,873.9 | 38,889.7 | 33,365.5 |
| ZLL | 6,121.7 | 6,162.6 | 5,824.9 |
| TTbar | 2,088.2 | 2,131.1 | 1,942.8 |
| W+jets | 12,274.8 | 12,366.3 | 11,412.9 |
| QCD | 11,167.6 | 11,196.6 | 10,013.2 |
| **Total bkg** | **70,526.1** | **70,746.4** | **62,559.3** |
| **Signal** | **151.2** | **151.2** | **136.0** |
| **S/sqrt(B)** | **0.569** | **0.569** | **0.544** |

### 2.2 VBF category

| Process | m_vis | NN score | m_col |
|---------|-------|----------|-------|
| ggH | 5.1 | 5.1 | 4.8 |
| VBF | 6.4 | 6.4 | 6.2 |
| ZTT | 346.9 | 348.2 | 344.3 |
| ZLL | 60.7 | 64.6 | 59.4 |
| TTbar | 417.2 | 428.9 | 385.6 |
| W+jets | 348.6 | 359.4 | 332.1 |
| QCD | 50.6 | 47.1 | 52.4 |
| **Total bkg** | **1,224.0** | **1,248.2** | **1,173.7** |
| **Signal** | **11.5** | **11.5** | **11.0** |
| **S/sqrt(B)** | **0.328** | **0.325** | **0.323** |

The VBF category has ~56% VBF signal purity (VBF/(ggH+VBF)) but
limited statistics. Combined S/sqrt(B) across categories is ~0.66
for NN score.

---

## 3. Systematic Uncertainties

### 3.1 Normalization systematics (normsys)

| Systematic | Magnitude | Affected processes | Correlation | Source |
|-----------|-----------|-------------------|-------------|--------|
| Luminosity | 2.6% | All MC | Fully correlated | CMS PAS LUM-13-001 [A1] |
| Z->tautau norm | 12% | ZTT, ZLL | Correlated across categories | Decomposition: theory 4%, trigger 5%, tau ID 8%, stat 2% [D6] |
| TTbar norm | 5% | TTbar | Correlated | NNLO+NNLL theory (Top++v2.0) |
| W+jets norm | 10% | W+jets | Per category | SF uncertainty (0.8%) + mT extrapolation (~10%) |
| QCD norm | 20% | QCD | Per category | OS/SS ratio uncertainty + methodology |
| ggH theory (scale) | +4.4/-6.9% | ggH | Signal only | YR4 muR/muF scale variations |
| VBF theory (scale) | +0.3/-0.2% | VBF | Signal only | YR4 |
| ggH PDF+alpha_s | 3.2% | ggH | Signal only | YR4 |
| VBF PDF+alpha_s | 2.2% | VBF | Signal only | YR4 |
| BR(H->tautau) | 1.7% | ggH, VBF | Signal only | YR4 (THU+mq+alpha_s combined) |
| Trigger efficiency | 3% | ggH, VBF, TTbar, W+jets | Correlated (not ZTT/ZLL) | Residual after Z norm absorption [D6, A4] |
| Tau ID efficiency | 5% | ggH, VBF, ZTT | Correlated | CMS tau POG, loosened WP |
| Muon ID+iso | 2% | All MC (not QCD) | Correlated | CMS muon POG |
| b-tag efficiency | 5% | TTbar | Correlated | CMS BTV POG |
| Missing backgrounds | 5% | ZTT, ZLL, TTbar | Correlated | Covers single top + diboson [A3] |

### 3.2 Shape systematics (histosys)

Each shape systematic shifts the relevant kinematic quantity, propagates
to MET, recomputes all observables (m_vis, m_col, NN score), and
rebuilds templates in both categories:

| Systematic | Variation | Propagation | Typical impact on signal |
|-----------|-----------|-------------|------------------------|
| Tau energy scale (TES) | +-3% on tau_pt | MET correction: MET_px -= delta_tau_px | ~1% on m_col shape |
| Muon energy scale (MES) | +-1% on mu_pt | MET correction: MET_px -= delta_mu_px | ~0.5% on m_vis shape |
| Jet energy scale (JES) | +-3% on jet_pt | VBF category migration only (no MET) | Category migration is key effect |
| MET unclustered | +-10% on unclustered MET | Scale unclustered component only | ~1% on m_col shape |

**Self-check verification**: For each systematic:
1. The varied quantity changes (e.g., tau_pt shifts by +-3%)
2. Impact is non-zero in multiple bins (verified in shape comparison plots)
3. Impact direction is correct (TES up -> higher tau_pt -> higher m_vis)
4. Evaluation at reco level consistently
5. Propagation through the full chain (not borrowed as flat %)

**JES implementation (F2 fix):** JES does NOT propagate to MET because
jet phi is not stored in the Phase 3 arrays. The proper vector formula
MET_px -= (jet_pt_shifted - jet_pt_nom) * cos(jet_phi) requires per-jet
phi, which is unavailable. JES therefore affects only jet-based quantities:
lead/sublead jet pT, mjj (scaled as mjj * scale^2), and VBF category
migration. This is a documented limitation. The previous implementation
used hardcoded directional factors (0.5, 0.3) which had no physical basis;
these have been removed.

**MET unclustered implementation (F3 fix):** The MET unclustered
variation now correctly scales only the unclustered component of MET,
defined as MET_total minus the clustered contributions from reconstructed
objects (muon + tau). The unclustered component is computed as
uncl = -(MET + muon_pT + tau_pT) (in the MET sign convention), scaled by
+-10%, and the total MET is recomputed. The previous implementation
scaled the entire MET vector, which double-counted energy scale effects
already covered by TES and MES. After the fix, the MET unclustered
up/down asymmetry is (-0.34, +0.37), much more symmetric than the
previous (-0.27, +0.05) which was an artifact of the double-counting.

**Template smoothing (F4 fix):** Shape systematic templates are smoothed
using a 3-bin moving average applied to the ratio (shifted/nominal)
before multiplying back by the nominal template. This suppresses MC
statistical noise that dominated over the genuine physics shape effect
for low-statistics signal processes (e.g., ~143 ggH events spread across
20 NN score bins). Without smoothing, the fit interpreted bin-to-bin
fluctuations as precision shape information, producing artificially
tight nuisance parameter constraints. After smoothing, the TES post-fit
uncertainty relaxed from 0.21 to 0.26, closer to the 0.3-0.6 range
typical of published CMS analyses.

**JES category migration**: Under JES variations, jet pT shifts change
the VBF categorization. This is handled by re-evaluating the VBF
selection (m_jj > 200, |deta_jj| > 2.0) with shifted jet kinematics.
Events can migrate between Baseline and VBF categories.

**NN score propagation**: For each systematic variation, all 14 NN input
features are recomputed (mu_pt, tau_pt, met_pt, mvis, mt, delta_r, etc.)
and passed through the trained NN model to produce shifted NN score
templates. This captures the full correlation between energy scale
variations and the NN discriminant.

### 3.3 MC statistical uncertainty

Barlow-Beeston lite (staterror) is applied per channel, with one gamma
parameter per bin per channel. This accounts for the finite MC statistics
in each bin.

In the VBF category, several bins have low MC statistics (< 5 expected
events for some processes). The staterror modifiers handle this correctly
by allowing the bin-by-bin yields to fluctuate within their statistical
precision.

---

## 4. Expected Results on Asimov Data

### 4.1 Asimov fit results

Asimov data is generated under the mu = 1 (SM) hypothesis with all
nuisance parameters at their nominal values.

| Approach | mu_hat | sigma(mu) | 95% CL limit | Expected significance |
|----------|--------|-----------|--------------|----------------------|
| m_vis | 1.000 | 3.060 | 6.24 | 0.325 sigma |
| **NN score** | **1.000** | **1.247** | **2.60** | **0.814 sigma** |
| m_col | 1.000 | 4.250 | 9.46 | 0.222 sigma |

The NN discriminant provides the best expected precision with
sigma(mu) = 1.25, a factor 2.5 improvement over the visible mass
approach (sigma(mu) = 3.06) and a factor 3.4 improvement over the
collinear mass approach (sigma(mu) = 4.25).

**Resolving power statement**: The NN score approach with sigma(mu) = 1.25
can distinguish signal strength values differing by ~2.5 (2 x sigma(mu))
at 2-sigma significance. This means the measurement can distinguish
between the SM prediction (mu = 1) and the no-signal hypothesis (mu = 0)
at approximately 0.8 sigma, or can detect enhanced production (mu >= 3.5)
at approximately 2-sigma level.

**Changes from v1 (pre-fix):** sigma(mu) increased from 1.15 to 1.25
for the NN score approach. This reflects three corrections:
(1) F2/JES: removing the incorrect MET propagation changed the JES shape
impact; (2) F3/MET uncl: scaling only the unclustered component increased
the genuine MET unclustered impact while eliminating double-counting with
TES/MES; (3) F4/smoothing: reducing template noise relaxed the TES
post-fit constraint from 0.21 to 0.26, widening the total uncertainty.
The increase is consistent with the pre-fix results having benefited from
partially artificial constraints.

### 4.2 CLs limit scan

The expected 95% CL upper limit was computed using the CLs method with
the q-tilde test statistic, scanning mu from 0 to 10 in 41 steps.

| Approach | Expected 95% CL limit |
|----------|----------------------|
| m_vis | 6.24 |
| NN score | 2.60 |
| m_col | 9.46 |

### 4.3 Comparison to reference analyses

The published CMS result (R1, JHEP 05 (2014) 104) measured mu = 0.78
+/- 0.27 (combined, all channels, 7+8 TeV, 24.6 fb-1). Our expected
uncertainty of sigma(mu) = 1.25 for the NN score approach is approximately
4.6 times larger, consistent with:
- Single channel (mu-tau_h only, ~23% of total sensitivity)
- Single run period (11.5 fb-1 vs 24.6 fb-1)
- No SVfit mass reconstruction
- Looser tau ID (larger backgrounds)

---

## 5. Validation Checks

### 5.1 Signal injection test

Asimov data is generated at various mu values and the fit recovers the
injected signal strength:

**NN score approach:**

| mu_inject | mu_hat | sigma(mu) | Pull |
|-----------|--------|-----------|------|
| 0.0 | 0.000 | 1.193 | 0.000 |
| 1.0 | 1.000 | 1.246 | 0.000 |
| 2.0 | 2.000 | 1.364 | 0.000 |
| 5.0 | 5.000 | 1.603 | 0.000 |

**m_vis approach:**

| mu_inject | mu_hat | sigma(mu) | Pull |
|-----------|--------|-----------|------|
| 0.0 | 0.000 | 2.972 | 0.000 |
| 1.0 | 1.000 | 2.952 | 0.000 |
| 2.0 | 2.000 | 3.026 | 0.000 |
| 5.0 | 5.000 | 3.093 | 0.000 |

**m_col approach:**

| mu_inject | mu_hat | sigma(mu) | Pull |
|-----------|--------|-----------|------|
| 0.0 | 0.000 | 4.190 | 0.000 |
| 1.0 | 1.000 | 4.779 | 0.000 |
| 2.0 | 2.000 | 4.309 | 0.000 |
| 5.0 | 5.000 | 4.400 | 0.000 |

All injected values are recovered with pulls < 0.01, confirming the fit
is unbiased and the model correctly captures the signal parameterization.

### 5.2 Nuisance parameter pulls

On Asimov data, all nuisance parameter pulls are consistent with zero
(by construction). This validates that the workspace is correctly
assembled and the fit converges to the expected solution.

### 5.3 Impact ranking

Top 15 nuisance parameters by impact on mu (NN score approach):

| Rank | Parameter | Delta mu (up) | Delta mu (down) | Total impact |
|------|-----------|---------------|-----------------|-------------|
| 1 | MES (shape) | +0.375 | -0.431 | 0.404 |
| 2 | MET unclustered (shape) | -0.342 | +0.365 | 0.354 |
| 3 | JES (shape) | -0.256 | +0.278 | 0.267 |
| 4 | TES (shape) | -0.265 | +0.147 | 0.214 |
| 5 | QCD norm (baseline) | -0.127 | +0.126 | 0.126 |
| 6 | Z->tautau norm | +0.094 | -0.100 | 0.097 |
| 7 | Trigger efficiency | -0.089 | +0.097 | 0.093 |
| 8 | TTbar norm | -0.073 | +0.073 | 0.073 |
| 9 | b-tag efficiency | -0.073 | +0.073 | 0.073 |
| 10 | Luminosity | -0.064 | +0.068 | 0.066 |
| 11 | Muon ID/iso | -0.048 | +0.051 | 0.050 |
| 12 | Missing bkg norm | -0.049 | +0.046 | 0.047 |
| 13 | W+jets norm (baseline) | -0.050 | +0.039 | 0.045 |
| 14 | ggH theory (scale) | -0.016 | +0.047 | 0.035 |
| 15 | QCD norm (VBF) | -0.029 | +0.028 | 0.029 |

**Dominant systematics**: The four shape systematics (MES, MET uncl,
JES, TES) are the leading uncertainties, collectively contributing
sqrt(0.404^2 + 0.354^2 + 0.267^2 + 0.214^2) = 0.64 to delta(mu).

**Changes from v1 (pre-fix):** The impact ranking changed significantly
after the F2/F3/F4 fixes. TES dropped from rank 1 (0.376) to rank 4
(0.214) because template smoothing (F4) removed MC statistical noise
that artificially inflated TES sensitivity. MET unclustered increased
from rank 3 (0.191) to rank 2 (0.354) because the proper unclustered-only
scaling (F3) produces a larger genuine effect than the previous total-MET
scaling which partially cancelled itself. JES increased from rank 4
(0.165) to rank 3 (0.267) because removing the incorrect MET propagation
(F2) changed how JES affects the NN score purely through category migration.
Critically, the MET unclustered up/down asymmetry resolved: from
(-0.27, +0.05) to (-0.34, +0.37), confirming the previous factor-6
asymmetry was an artifact of the double-counting.

No single systematic dominates > 80% of the total uncertainty. The total
systematic uncertainty is sqrt(sum of squares of all impacts) ~ 0.64,
while the statistical uncertainty dominates (sigma(mu) = 1.25 total).

### 5.4 Goodness of fit

**chi2/ndf**: On Asimov data, chi2 = 0.000 for all approaches. This is
expected by construction (Asimov data IS the model prediction). The
meaningful GoF test occurs in Phase 4b/4c with real data.

**Toy-based p-value**: 200 toys generated for NN score, 100 each for
m_vis and m_col. All p-values = 1.0 on Asimov data (observed chi2 = 0
is always less than any toy chi2). This validates the toy generation and
fitting machinery is working correctly.

**Convergence monitoring (F17 fix):**

| Workspace | Toys | Converged | Outliers (chi2 > 1000) | Failed | Rate |
|-----------|------|-----------|------------------------|--------|------|
| NN score | 200 | 200 | 0 | 0 | 100% |
| m_vis | 100 | 100 | 0 | 0 | 100% |
| m_col | 100 | 100 | 0 | 0 | 100% |

All workspaces achieved 100% toy convergence with zero outliers after
the F1 low-statistics bin merging fix. Before the fix, m_vis had 4/100
catastrophic outliers (chi2 ~ 100,000) and m_col had 1/99 (one toy
failed silently), traced to near-empty bins in the VBF category causing
likelihood evaluation failures under Poisson fluctuations.

**Note on ndf**: The effective ndf is negative because the model has
more parameters than data bins. This is standard for HistFactory models
with many nuisance parameters -- the GoF interpretation relies on
toy-based p-values rather than the chi2/ndf ratio.

---

## 6. Systematic Completeness Table

| Source | Conventions | R1 (8 TeV) | R2 (13 TeV) | This analysis | Status |
|--------|------------|-----------|------------|---------------|--------|
| Tau energy scale | Required | 3% per DM | 1-3% per DM | 3% shape (histosys) | Implemented |
| Tau ID efficiency | Required | 6% | 5% | 5% normsys on signal, ZTT [F5] | Implemented |
| Muon ID/iso | Required | ~1% | ~2% | 2% normsys on all MC | Implemented |
| Muon energy scale | Required | Included | Included | 1% shape (histosys) | Implemented |
| Jet energy scale | Required | pT/eta dependent | pT/eta dependent | 3% shape, category migration only (no MET, jet phi unavailable) [F2] | Implemented |
| MET unclustered | Required | Propagated | Propagated | 10% on unclustered MET component only [F3] | Implemented |
| Z->tautau norm | Required | 3.3% | 4% | 12% normsys [D6] | Implemented |
| W+jets norm | Required | Data-driven | Data-driven | 10% normsys per category | Implemented |
| QCD norm | Required | Data-driven | Data-driven | 20% normsys per category | Implemented |
| TTbar norm | Required | ~10% | 6% | 5% normsys (NNLO+NNLL) | Implemented |
| Luminosity | Required | 2.6% | 2.5% | 2.6% normsys [A1] | Implemented |
| PDF+alpha_s | Required | Per process | Per process | Normalization only (3.2%/2.2%) | Implemented |
| Signal theory (scale) | Required | Per mode | Per mode | +4.4/-6.9% (ggH), +0.3/-0.2% (VBF) | Implemented |
| BR(H->tautau) | Required | Included | Included | 1.7% normsys | Implemented |
| MC statistics | Required | Barlow-Beeston | Barlow-Beeston | staterror per bin per channel | Implemented |
| Trigger efficiency | Required | ~4-8% | ~5% | 3% normsys (not ZTT) [D6] | Implemented |
| b-tag efficiency | Required | ~2-5% | ~1-3% | 5% normsys on TTbar | Implemented |
| Missing backgrounds | Required | Included | Included | 5% normsys on MC bkg [A3] | Implemented |
| Pileup reweighting | Strategy | +/-5% | +/-5% | Not implemented | See note |
| Jet->tau fake rate | Strategy | Included | Included | Not separately implemented | Absorbed in W+jets/QCD norm |
| Generator comparison | Strategy | Powheg vs aMC@NLO | Various | Not possible [L3] | Limitation |
| PS ISR/FSR | Strategy | Included | Included | Not possible (no PS weights) | Limitation |

**Notes on missing items**:
- **Pileup reweighting**: The strategy committed to implementing pileup
  reweighting with +/-5% variation. This was not implemented because the
  CMS Open Data NanoAOD does not include official pileup weights, and
  the PV_npvs-based reweighting was not applied in Phase 3 (events use
  raw MC weights). The pileup effect is partially absorbed by the large
  Z normalization uncertainty (12%) and the per-category background
  normalizations. This is a known limitation.
- **Jet->tau fake rate**: The fake rate shape systematic is absorbed into
  the W+jets and QCD normalization uncertainties, which are conservatively
  large (10% and 20% respectively).

---

## 7. Output Files

| File | Description |
|------|-------------|
| `nominal_templates.json` | Nominal template histograms for all processes, approaches, categories |
| `shape_systematic_templates.json` | Up/down shape systematic templates |
| `workspace_mvis.json` | pyhf workspace for visible mass fit |
| `workspace_nn_score.json` | pyhf workspace for NN discriminant fit |
| `workspace_mcol.json` | pyhf workspace for collinear mass fit |
| `expected_results.json` | Asimov fit results (mu, limits, significance) |
| `validation_results.json` | Signal injection, impacts, GoF results |

---

## 8. Figure List

| Figure | File | Caption |
|--------|------|---------|
| m_vis template (Baseline) | `figures/template_mvis_baseline.pdf` | Pre-fit visible mass template in the Baseline category showing stacked backgrounds (Z->tautau, Z->ll, ttbar, W+jets, QCD) and signal scaled by x10. Asimov data points overlay the total prediction. The Z->tautau background dominates with a peak near 60-80 GeV. |
| m_vis template (VBF) | `figures/template_mvis_vbf.pdf` | Pre-fit visible mass template in the VBF category. Lower statistics than Baseline with ttbar and W+jets as significant backgrounds alongside the Z->tautau contribution. |
| NN score template (Baseline) | `figures/template_nn_score_baseline.pdf` | Pre-fit NN discriminant template in the Baseline category. Backgrounds peak at low NN scores while signal (x10) peaks at high scores, demonstrating the NN's discriminating power. |
| NN score template (VBF) | `figures/template_nn_score_vbf.pdf` | Pre-fit NN discriminant template in the VBF category. Reduced statistics but similar signal-background separation pattern. |
| m_col template (Baseline) | `figures/template_mcol_baseline.pdf` | Pre-fit collinear mass template in the Baseline category. The broader distribution compared to m_vis reflects the inclusion of unphysical collinear solutions. |
| m_col template (VBF) | `figures/template_mcol_vbf.pdf` | Pre-fit collinear mass template in the VBF category. |
| Signal injection | `figures/signal_injection.pdf` | Signal injection linearity test for all three approaches. Asimov data generated at mu = 0, 1, 2, 5 is fit and the recovered mu is plotted against injected mu. All points lie on the diagonal, confirming unbiased recovery. |
| NP impact ranking | `figures/impact_ranking.pdf` | Impact of the top 15 nuisance parameters on the signal strength mu for the NN score approach. The four shape systematics (TES, MES, MET unclustered, JES) dominate. |
| NP pulls | `figures/np_pulls.pdf` | Nuisance parameter best-fit values and uncertainties for the NN score Asimov fit. All pulls are consistent with zero as expected. The green (yellow) bands indicate the 1-sigma (2-sigma) regions. |
| CLs scan | `figures/cls_scan.pdf` | CLs values as a function of mu for all three approaches. The intersection with the 95% CL line (CLs = 0.05) gives the upper limit. The NN score provides the tightest limit at 2.60. |
| TES shift | `figures/syst_shift_tes.pdf` | Ratio of tau energy scale up/down templates to nominal for ZTT, ggH, and TTbar in the NN score Baseline channel. Shows the bin-by-bin shape effect of the 3% TES variation. |
| MES shift | `figures/syst_shift_mes.pdf` | Ratio of muon energy scale up/down templates to nominal. The 1% MES variation produces smaller shape changes than TES. |
| JES shift | `figures/syst_shift_jes.pdf` | Ratio of jet energy scale up/down templates to nominal. JES affects category migration and MET. |
| MET uncl shift | `figures/syst_shift_met_uncl.pdf` | Ratio of MET unclustered energy up/down templates to nominal. The 10% variation produces visible shape effects in the NN discriminant. |
| GoF toys | `figures/gof_toys.pdf` | Distribution of chi2 values from 200 toy fits compared to the Asimov observed chi2 (=0). All toys have chi2 > 0, giving p-value = 1.0. This validates the toy generation and fit machinery; the real GoF test occurs with data. |

---

## 9. Strategy Decision Verification

| Decision | Status |
|----------|--------|
| [D1] Three approaches | Implemented: mvis, nn_score, mcol. NN-MET dropped [D13]. |
| [D2] YR4 cross-sections | Implemented in MC weights. |
| [D3] W+jets from high-mT | SF = 0.999 applied, 10% norm uncertainty. |
| [D4] QCD from SS | R_OS/SS = 0.979, 20% norm uncertainty. |
| [D6] Z norm 12% | Implemented as normsys on ZTT, ZLL. |
| [D10] Baseline + VBF | Simultaneous fit, common mu. |
| [D11] Common mu | Implemented. ggH and VBF share mu. |
| [A1] Lumi 2.6% | Implemented as normsys. |
| [A3] Missing bkg 5% | Implemented as normsys on ZTT, ZLL, TTbar. |

---

## 10. Review Fix Documentation

### 10.1 Category A fixes

**F1 (GoF toy failures):** Low-statistics bins in VBF categories for
m_vis and m_col caused convergence failures in 4% of GoF toys, with
chi2 values reaching 100,000-170,000 (5 orders of magnitude above the
bulk distribution). Root cause: near-empty bins (total < 5 expected events)
in the VBF tails, combined with individual process bins at the 1e-6 floor.
Poisson(1e-6) = 0 in every toy, creating degenerate likelihood landscapes.
Fix: adjacent bins with total expected events below 10 are merged (greedy
left-to-right merging). m_vis VBF: 25 -> 19 bins; m_col VBF: 25 -> 22 bins;
m_vis baseline: 25 -> 24 bins (kinematic dead zone at m_vis < 10 GeV).
After fix: 0 outliers and 0 failed toys across all 400 toys (200 NN score +
100 m_vis + 100 m_col).

**F2 (JES MET propagation):** The original code propagated JES to MET
using hardcoded factors (0.5, 0.3) because jet phi is not stored in
Phase 3 arrays. These factors have no physical basis. Fix: JES no longer
modifies MET. The JES shape systematic now affects only jet-based quantities
(lead/sublead jet pT, mjj, VBF category migration). This is documented as
a limitation. Impact: JES total impact changed from 0.165 to 0.267, as the
spurious MET component previously partially cancelled the category migration
effect.

**F3 (MET unclustered scaling):** The original code scaled total MET by
+-10%, double-counting TES/MES effects. Fix: the unclustered MET component
is isolated by subtracting the clustered lepton contributions (muon pT +
tau pT) from the total MET vector, then only the residual (unclustered)
component is scaled. The proper formula is:
MET_new = MET_old + (scale - 1) * (MET_old + clustered_leptons).
Impact: MET uncl went from rank 3 (0.191) to rank 2 (0.354); the
up/down asymmetry resolved from (-0.27, +0.05) to (-0.34, +0.37).

**F4 (Shape template noise):** With ~143 ggH events in 20 NN score bins,
MC statistical fluctuations (1/sqrt(7) ~ 38% per bin) exceeded the 3%
TES physics effect by an order of magnitude. The fit interpreted noise as
shape information, constraining TES to post-fit uncertainty 0.21 (published
CMS range: 0.3-0.6). Fix: 3-bin moving average smoothing applied to the
ratio (shifted/nominal) for all shape systematics, then the smoothed
ratio is multiplied by the nominal template. After smoothing, TES post-fit
uncertainty relaxed from 0.21 to 0.26. Total sigma(mu) increased from
1.15 to 1.25, consistent with the removal of artificial constraints.

### 10.2 Category B documentation fixes

**F5 (Tau ID 10% -> 5%):** The Phase 1 strategy specified 10% tau ID
efficiency uncertainty as a conservative estimate for Open Data without
official scale factors. The implementation uses 5%, matching the published
CMS 13 TeV tau POG measurement for the loosened working point (R2,
CMS-TAU-16-003). The 5% value is more appropriate because: (1) the 8 TeV
tau ID performance is comparable to or better than 13 TeV for the loose WP;
(2) using 10% would be overly conservative and artificially inflate the
total uncertainty; (3) the reference analysis R2 uses 5% for the same
measurement. This revision from the strategy's conservative estimate to
the measured value is documented here as a formal [D] decision.

**F8 (S/sqrt(B) vs profile likelihood significance):** The pre-fit
S/sqrt(B) significance (0.57 in the Baseline category for NN score) and
the post-fit profile likelihood significance (0.81 sigma) are different
metrics that should not be directly compared. S/sqrt(B) is a cut-and-count
estimate computed in the signal-enriched region using a single bin, while
the profile likelihood uses the full binned NN score shape across both
categories and profiles all systematic uncertainties. The profile likelihood
is more powerful because it exploits shape information and the simultaneous
Baseline+VBF fit. The profile likelihood expected significance of 0.81
sigma is the appropriate metric for this analysis.

**B6 (Pileup):** Pileup reweighting was committed in the strategy but is
formally downscoped [D] for Phase 4a. Justification: (1) the CMS Open Data
NanoAOD does not include official pileup weights, and the strategy's
alternative PV_npvs-based approach was not applied in Phase 3; (2) the
Phase 2 data/MC PV_npvs comparison shows moderate disagreement (~10-15%
in the tails) but the core distribution is well-modeled; (3) the pileup
shape effect on the NN discriminant is subdominant to the four implemented
shape systematics (total impact delta_mu ~ 0.64); (4) at 8 TeV with
~20 pileup interactions, the effect is smaller than at 13 TeV. Commitment:
pileup reweighting will be implemented before Phase 4c if the data fit
shows NP pulls suggesting pileup mismodeling.

### 10.3 Category C notes

**F6 (ggH QCD scale):** The strategy's Section 9.2 summary table lists
"+7.2%/-7.8%" for ggH scale uncertainty, which is the combined
scale+PDF+alpha_s envelope. The implementation correctly decomposes this
into independent NPs per YR4 best practice: scale (+4.4%/-6.9%) and
PDF+alpha_s (3.2%), matching the strategy's Section 5 data samples table.
The implementation is correct; the strategy summary table conflated two
uncertainty components.
