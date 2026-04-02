# Phase 2 Executor Session Log — 2026-03-24

## Session overview
- Started: 2026-03-24 02:45 UTC
- Model: Claude Opus 4.6 (1M context)
- Task: Phase 2 Exploration for H->tautau mu-tau_h analysis

## Scripts produced
1. `src/01_sample_inventory.py` — complete NanoAOD file inspection
2. `src/02_data_quality.py` — data quality validation
3. `src/03_preselection.py` — full event selection with Loose tau ID
4. `src/04_tau_id_wp_study.py` — VLoose/Loose/Medium comparison
5. `src/05_variable_distributions.py` — 13-variable survey with ROC AUC
6. `src/06_collinear_mass.py` — collinear mass computation and validation
7. `src/07_vbf_optimization.py` — VBF threshold and centrality optimization

## Key decisions made
- [D7] resolved: Loose tau ID WP selected (chi2/ndf = 2.96, 20% more signal than Medium)
- VBF thresholds: m_jj > 200 GeV, |Delta_eta_jj| > 2.0 (looser than strategy for statistics)
- Zeppenfeld centrality retained with threshold 1.0
- Two-category scheme (Baseline + VBF) confirmed [D10]

## Issues encountered
- `vector.MomentumObject4D` does not accept numpy arrays — switched to manual 4-vector math
- `Tau_relIso_all` has widespread NaN — handled with ak.nan_to_none + fill_none(999)
- VBF script had double-escaped LaTeX in label — fixed
- Large dataset processing (~230M events) took ~40 min for preselection

## Figures produced: 21
- 13 data/MC comparison plots with ratio panels
- 3 tau ID WP comparison plots
- 2 collinear mass plots (all + physical-only)
- 2 VBF distribution plots (mjj, deta_jj)
- 1 separation power ranking bar chart

## Artifacts
- EXPLORATION.md: 13 sections, all self-check items passed
- experiment_log.md: updated with all Phase 2 findings
- cutflow_loose.json: machine-readable cutflow data
- sample_inventory.json: complete branch-level inventory
