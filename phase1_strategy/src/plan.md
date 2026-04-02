# Phase 1 Executor Plan

## Objective
Produce STRATEGY.md for H->tautau analysis in the mu-tau_h final state using CMS Open Data at 8 TeV.

## Literature and web queries performed
1. CMS H->tautau 8 TeV evidence paper (JHEP 05 (2014) 104, arXiv:1401.5041)
2. CMS H->tautau 13 TeV observation paper (Phys. Lett. B 779 (2018) 283, arXiv:1708.00373)
3. LHC Higgs Cross Section Working Group (CERN Yellow Report) at 8 TeV
4. CMS luminosity for 2012 data
5. CMS Open Data H->tautau tutorial (HiggsTauTauNanoAODOutreachAnalysis)
6. Higgs branching ratios (YR4)
7. ttbar cross-section at NNLO+NNLL

## Key numbers verified from web
- ggH cross-section at 8 TeV: 21.39 pb (N3LO, YR4) / 19.27 pb (NNLO+NNLL, older)
  Tutorial uses: 19.6 pb (approximate older value)
- VBF cross-section at 8 TeV: 1.600 pb (YR4) / Tutorial: 1.55 pb
- BR(H->tautau) at mH=125.09 GeV: 6.256% (YR4)
- ttbar at 8 TeV: 252.9 pb (NNLO+NNLL, Top++v2.0) / Tutorial: 225.2 pb
- DYJetsToLL: 3503.7 pb (NNLO) - from tutorial
- W+jets: W1J=6381.2, W2J=2039.8, W3J=612.5 pb - from tutorial
- Integrated luminosity: 11.467 fb-1 (Run2012B + Run2012C, TauPlusX)
- CMS H->tautau evidence: mu = 0.78 +/- 0.27 (8 TeV, all channels)
- CMS H->tautau observation: mu = 0.98 +/- 0.18 (13 TeV)

## Data inspection results
- All expected branches present in NanoAOD files
- All 9 files accessible on EOS
- Event counts match expectations

## Scripts to write
1. `inspect_data.py` (DONE) - data inspection
2. No additional scripts needed for Phase 1 (strategy is a document phase)

## STRATEGY.md structure
1. Executive Summary
2. Physics Motivation and Observable Definition
3. Data and MC Samples (inventory table)
4. Signal and Background Classification
5. Event Selection Strategy (>=2 approaches)
6. Category Definitions (Baseline + VBF)
7. Background Estimation Strategy
8. Four Fitting Approaches
9. Systematic Uncertainty Plan (conventions enumeration)
10. Reference Analysis Table
11. Flagship Figures (~6)
12. Methodology Diagrams
13. Decision/Constraint/Limitation Labels
14. Validation Strategy
15. Open Issues and Risks

## Timeline estimate
- Plan: done
- Literature review: done
- Data inspection: done
- STRATEGY.md writing: ~30 minutes
- Self-check: ~5 minutes
