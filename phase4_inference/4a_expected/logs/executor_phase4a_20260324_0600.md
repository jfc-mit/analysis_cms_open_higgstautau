# Phase 4a Executor Session Log

**Started**: 2026-03-24 05:57
**Completed**: 2026-03-24 06:35

## Plan

1. Build nominal templates (3 approaches x 2 categories x 7 processes)
2. Build shape systematic templates (TES, MES, JES, MET unclustered)
3. Construct pyhf workspaces (simultaneous Baseline+VBF)
4. Compute expected results on Asimov data
5. Run validation checks (signal injection, impact ranking, GoF)
6. Generate figures

## Execution

### Step 1: Nominal templates (01_build_templates.py)
- Loaded Phase 3 npz arrays
- DY decomposed via is_ztt flag: ZTT = 39,238 weighted, ZLL = 6,227 weighted
- W+jets combined with SF = 0.999
- QCD from SS data minus MC, R_OS/SS = 0.979
- Templates built for mvis (25 bins, 0-250), nn_score (20 bins, 0-1), mcol (25 bins, 0-300)
- S/sqrt(B) = 0.57 (Baseline), 0.33 (VBF) for NN score

### Step 2: Shape systematics (02_shape_systematics.py)
- TES: +-3% on tau_pt, propagated to MET, recomputed mvis/mcol/NN
- MES: +-1% on mu_pt, propagated to MET
- JES: +-3% on jet_pt, category migration, MET
- MET unclustered: +-10% on MET
- Verified non-zero impacts in shape comparison
- QCD template also shifted (MC SS changes under systematics)

### Step 3: pyhf workspaces (03_build_workspace.py)
- 3 workspaces (mvis, nn_score, mcol), each with 2 channels (baseline, vbf)
- 21 NPs + ~50 staterror gammas + 1 POI = ~71 parameters
- All workspaces validated by pyhf schema checker

### Step 4: Expected results (04_expected_results.py)
- Asimov fits recover mu = 1.000 for all approaches
- NN score: sigma(mu) = 1.145, limit = 2.36, significance = 0.892 sigma
- m_vis: sigma(mu) = 2.993, limit = 6.20, significance = 0.326 sigma
- m_col: sigma(mu) = 3.722, limit = 7.81, significance = 0.262 sigma
- CLs scan: 41 points from mu = 0 to 10

### Step 5: Validation (05_validation.py)
- Signal injection: mu = 0, 1, 2, 5 all recovered with pulls < 0.01
- Impact ranking: TES dominates (0.376), then MES (0.291), MET uncl (0.191), JES (0.165)
- GoF: chi2 = 0 on Asimov (expected), p-value = 1.0 (validated toy machinery)

### Step 6: Figures (06_figures.py)
- 16 figures total: 6 template stacks, 4 syst shifts, signal injection, impact ranking, NP pulls, CLs scan, GoF toys

## Key Findings

1. NN score provides 2.6x better precision than m_vis (sigma_mu = 1.15 vs 2.99)
2. Shape systematics (TES, MES, MET, JES) dominate the systematic budget
3. Statistical uncertainty still dominates overall (systatic ~0.56, total 1.15)
4. VBF category adds modest sensitivity due to limited statistics
5. Model passes all validation checks on Asimov data

## Files Produced

- 7 JSON output files (templates, workspaces, results, validation)
- 16 figures (PDF + PNG)
- INFERENCE_EXPECTED.md artifact
- Updated COMMITMENTS.md
- Updated experiment_log.md
