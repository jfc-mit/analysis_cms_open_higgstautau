# Phase 2 Exploration Plan

## Scripts to write

1. **`src/01_sample_inventory.py`** — Complete inventory of all 9 files:
   tree names, all branch names/types, event counts, schema documentation.
   Also checks for weight branches (genWeight, PSWeight, LHEPdfWeight, etc.).
   Runs on first 1000 events per sample for speed.

2. **`src/02_data_quality.py`** — Data quality assessment:
   check for NaN/inf, empty branches, outlier values, unphysical values
   (negative pT, |eta| > 10, etc.). Compare event counts to expected
   xsec * lumi. Check genWeight distributions. Check MC truth info structure.

3. **`src/03_preselection.py`** — Apply the baseline selection from Strategy §5.2:
   trigger, muon ID, tau ID (at VLoose/Loose/Medium), pair selection (OS, DR>0.5),
   event-level cuts. Produce cutflow tables. Compute yields with xsec normalization.
   Run on full dataset.

4. **`src/04_tau_id_wp_study.py`** — Compare VLoose/Loose/Medium tau isolation WPs:
   data/MC comparison in Z peak region (60-120 GeV visible mass).
   Compute data/MC ratio, chi2/ndf for each WP to determine [D7].

5. **`src/05_variable_distributions.py`** — Signal vs background distributions
   for all discriminating variables. Stacked MC vs data with ratio panels.
   Compute separation power (ROC AUC) for each variable.

6. **`src/06_collinear_mass.py`** — Compute collinear mass, measure unphysical
   solution fractions per process [P2-8]. Verify strategy estimates.

7. **`src/07_vbf_optimization.py`** — VBF category optimization: scan m_jj and
   Delta_eta thresholds for S/sqrt(B). Evaluate Zeppenfeld centrality [P2-3, P2-4].

## Figures to produce (all in phase2_exploration/outputs/figures/)

- `cutflow_yields.pdf/png` — Cutflow table visualization
- `tau_id_wp_*.pdf/png` — Data/MC comparison for VLoose/Loose/Medium at Z peak
- `mvis_*.pdf/png` — Visible mass data/MC stacked
- `mt_mu_met.pdf/png` — Transverse mass
- `met_pt.pdf/png` — MET distribution
- `muon_pt.pdf/png`, `tau_pt.pdf/png` — Lepton pT
- `delta_r.pdf/png`, `delta_phi.pdf/png` — Angular correlations
- `njets.pdf/png`, `nbjets.pdf/png` — Jet multiplicities
- `jet_pt.pdf/png`, `jet_eta.pdf/png` — Jet kinematics
- `pv_npvs.pdf/png` — Pileup distribution
- `tau_decay_mode.pdf/png` — Tau decay mode
- `met_significance.pdf/png` — MET significance
- `separation_power.pdf/png` — Variable ranking by ROC AUC
- `collinear_mass.pdf/png` — Collinear mass distribution
- `vbf_optimization.pdf/png` — VBF S/sqrt(B) scan

## Deliverables

- `phase2_exploration/outputs/EXPLORATION.md` — Primary artifact
- `experiment_log.md` — Updated with all findings
- `phase2_exploration/logs/executor_phase2_20260324.md` — Session log

## Execution order

1. Sample inventory (01) — prototype first 1000 events
2. Data quality (02) — full scan for pathologies
3. Preselection + yields (03) — full dataset, all WPs
4. Tau ID WP study (04) — determine [D7]
5. Variable distributions (05) — all key variables
6. Collinear mass study (06) — [P2-8]
7. VBF optimization (07) — [P2-3, P2-4]
8. PDF build test
9. Write EXPLORATION.md artifact
