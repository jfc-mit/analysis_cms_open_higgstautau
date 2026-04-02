# Phase 3 Execution Plan

## Overview
Implement final event selection, background estimation, categorization,
NN discriminant, NN MET regression, and collinear mass for H->tautau
mu-tau_h analysis at 8 TeV.

## Scripts to write

### 1. `src/01_full_selection.py` — Full selection + DY decomposition + VBF categorization
- Re-read ROOT files (need per-jet arrays for mjj/deta_jj, GenPart for DY split)
- Apply full selection chain from Phase 2 (already validated)
- Add DY decomposition: Z->tautau vs Z->ll via GenPart truth matching
- Compute VBF variables: mjj, |deta_jj|, Zeppenfeld centrality
- Categorize events: Baseline vs VBF (mjj>200, |deta_jj|>2.0)
- Save extended npz files with all variables, gen-level info, VBF variables
- Produce cutflow table

### 2. `src/02_background_estimation.py` — W+jets and QCD data-driven
- W+jets: high-mT sideband (mT>70) normalization [D3]
  - Needs re-reading with relaxed mT cut or separate high-mT selection
- QCD: same-sign control region [D4]
  - Needs re-reading with inverted charge requirement
  - Measure OS/SS ratio from anti-isolated CR
- Validate in intermediate mT (30-70 GeV) region
- Produce validation plots

### 3. `src/03_collinear_mass.py` — Collinear mass implementation
- Compute collinear mass from selected events
- Report physical/unphysical fractions per process and category
- Produce mass distribution plots

### 4. `src/04_nn_discriminant.py` — NN classifier training [D1, D9]
- Train NN to separate signal from backgrounds
- Inputs: mu_pt, mu_eta, tau_pt, tau_eta, met_pt, mvis, mt, delta_r,
  delta_phi, njets, lead_jet_pt, lead_jet_eta, nbjets
- Architecture: 2-3 hidden layers, 32-64 nodes, ReLU, dropout
- 50/25/25 split, fixed seed
- Overtraining check (KS test)
- Validation plots: ROC, score distributions, feature importance
- Data/MC agreement on NN output

### 5. `src/05_nn_met_regression.py` — NN MET regression [D1, D13]
- Need gen-level MET from GenPart (derive from neutrinos)
- Train NN to regress gen-level MET from reco quantities
- Success criterion: >15% MET resolution improvement
- If successful: compute improved collinear mass
- If not: document negative result

### 6. `src/06_approach_comparison.py` — Cut-based vs MVA comparison [D9]
- Compare cut-based and MVA-based selection
- Metrics: S/sqrt(B), AUC, expected significance
- Document rationale for final choice

### 7. `src/07_plots.py` — Data/MC comparison plots
- For each category (Baseline, VBF):
  - mvis, NN score, collinear mass distributions
  - Stacked MC with data overlay and ratio panel
- CMS style, all plotting rules

## Figures to produce
- Cutflow comparison bar chart
- W+jets SF validation (intermediate mT)
- QCD OS/SS ratio measurement
- mvis data/MC for Baseline and VBF categories
- NN training curves, ROC, score distributions
- NN feature importance
- NN output data/MC agreement per category
- Collinear mass per category
- MET resolution before/after NN regression
- Cut-based vs MVA comparison (S/sqrt(B))

## Key decisions
- Need ROOT file re-read for: gen-level info, per-jet arrays, SS/high-mT CRs
- Will process in chunks for large samples (DY: 30M events)
- scikit-learn already in pixi.toml for NN (MLPClassifier/MLPRegressor)
- Prototype on 1000 events, then full scale

## Artifact structure
`outputs/SELECTION.md` with sections:
1. Event selection summary
2. Cutflow table (all cuts, all samples, weighted)
3. Background estimation (W+jets SF, QCD OS/SS)
4. Categorization (Baseline/VBF yields)
5. NN discriminant (architecture, training, validation)
6. NN MET regression (result against D13 criterion)
7. Collinear mass (physical fractions, distributions)
8. Approach comparison (cut-based vs MVA)
9. Data/MC agreement plots
10. Self-check
