# Phase 4a Plan: Expected Results

## Scripts

### 01_build_templates.py
Build nominal templates for all 3 fitting approaches x 2 categories.
- Load Phase 3 npz arrays (OS SR for MC, SS SR for QCD template)
- DY decomposition: ZTT / ZLL using `is_ztt` flag
- W+jets: combine W1J+W2J+W3J with SF = 0.999
- QCD: (Data_SS - MC_SS) x OS/SS ratio = 0.979; use per-bin template
- Build histograms: m_vis (25 bins, 0-250), NN score (20 bins, 0-1), m_col (25 bins, 0-300)
- Apply VBF categorization (mjj > 200 & |deta_jj| > 2.0)
- Ensure min 5 events/bin via merging
- Save nominal templates to JSON

### 02_shape_systematics.py
Build shifted templates for shape systematics.
- TES +-3%: shift tau_pt, recompute MET, mvis, m_col; re-evaluate NN
- MES +-1%: shift mu_pt, recompute MET, mvis, m_col; re-evaluate NN
- JES +-3%: shift jet_pt, recompute VBF categorization (migration!), re-evaluate NN
- MET unclustered +-10%: shift MET, recompute m_col; re-evaluate NN
- For each variation: rebuild all templates in both categories
- QCD shape from SS with same shifts applied
- Save up/down template pairs

### 03_build_workspace.py
Construct pyhf workspaces (3 approaches x 2 categories simultaneous).
- Signal: ggH + VBF with mu as POI (normsys for theory uncertainties)
- Backgrounds: ZTT, ZLL, W+jets, QCD, TTbar
- Normalization systematics as normsys modifiers
- Shape systematics as histosys modifiers
- Barlow-Beeston (staterror) per bin
- Save workspace JSON files

### 04_expected_results.py
Asimov fits and results.
- Generate Asimov dataset (mu=1)
- Maximum likelihood fit -> best-fit mu + uncertainty
- Expected 95% CL upper limit (CLs)
- Expected significance
- Save results JSON

### 05_validation.py
Validation checks.
- Signal injection: mu = 0, 1, 2, 5 -> recover injected mu
- Nuisance parameter pulls on Asimov (all ~0)
- Impact ranking: top 15 NPs
- Goodness-of-fit: chi2/ndf + toy-based p-value
- Save validation results + figures

### 06_figures.py
Generate all Phase 4a figures.
- Pre/post-fit template stacks (3 approaches x 2 categories)
- NP pull/constraint plot
- Impact ranking plot
- Signal injection linearity
- Systematic shift comparison plots (per-systematic)
- GoF toy distribution

## Outputs
- pyhf workspace JSON (3 per approach: baseline, VBF, combined)
- expected_results.json
- signal_injection.json
- impact_ranking.json
- gof_results.json
- ~20 figures in outputs/figures/
- INFERENCE_EXPECTED.md artifact

## Systematics Implementation

### Normalization-only (normsys):
- Luminosity: 2.6% on all MC
- ZTT norm: 12% (decomposed: theory 4%, trigger 5%, tau ID 8%, stat 2%)
- ZLL norm: 12% (correlated with ZTT)
- TTbar norm: 5%
- W+jets norm: from SF uncertainty (0.8% stat + 10% shape extrapolation -> ~10%)
- QCD norm: 20% (OS/SS ratio uncertainty + methodology)
- ggH theory (scale): +4.4/-6.9%
- VBF theory (scale): +0.3/-0.2%
- ggH PDF+alphas: 3.2%
- VBF PDF+alphas: 2.2%
- BR(H->tautau): 1.7%
- Trigger eff: 3% on signal, TTbar, W+jets (NOT ZTT/ZLL)
- Tau ID eff: 5% on events with genuine taus (signal, ZTT)
- Muon ID+iso: 2% on all MC
- b-tag eff: 5% on TTbar

### Shape (histosys):
- TES: +-3% on tau_pt -> propagate to MET, mvis, m_col, NN
- MES: +-1% on mu_pt -> propagate to MET, mvis, m_col, NN
- JES: +-3% on jet_pt -> category migration + MET + NN
- MET unclustered: +-10% on MET -> m_col, NN

### Statistical (staterror):
- Barlow-Beeston per bin per channel
