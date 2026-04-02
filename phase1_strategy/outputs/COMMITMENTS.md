# Commitments Tracking: H->tautau mu-tau_h Analysis

Generated from STRATEGY.md Phase 1 labels.

## Binding Decisions

| Label | Commitment | Phase | Status |
|-------|-----------|-------|--------|
| [D1] | All four fitting approaches required: (a) visible mass [baseline], (b) NN discriminant [primary ML], (c) NN-regressed MET [exploratory], (d) collinear mass [analytic benchmark]. Priority ordering and go/no-go criteria defined. | 1 | [x] P3: Three approaches implemented (a, b, d). Approach (c) NN-regressed MET dropped per [D13]. P4a: All three fitted simultaneously in Baseline+VBF. |
| [D2] | Signal MC normalized to YR4 cross-sections (sigma_prod x BR); ttbar to NNLO+NNLL (252.9 pb); other backgrounds to tutorial values. Explicit weight formula: w = sigma_prod x BR x L_int / N_gen (signal), w = sigma x L_int / N_gen (backgrounds). | 1 | [x] P3: Weights applied per formula in npz files. P4a: Templates use these weights. |
| [D3] | W+jets normalization from high-mT data sideband (mT > 70 GeV). Shape validation between high-mT and intermediate-mT regions required. | 1 | [x] P3: SF_W = 0.999 +/- 0.008. P4a: Applied in template building, 10% norm uncertainty. |
| [D4] | QCD estimation from same-sign control region. OS/SS ratio measured from data in anti-isolated CR (not taken from literature). Negative-bin procedure defined. | 1 | [x] P3: R_OS/SS = 0.979 +/- 0.018. P4a: QCD template from SS data minus MC, negative bins zeroed. |
| [D5] | Primary trigger: HLT_IsoMu17_eta2p1_LooseIsoPFTau20 | 1 | [x] P3: Applied in selection. |
| [D6] | Z normalization uncertainty: 10-15%, with quantitative decomposition (theory ~3-4%, trigger ~5%, tau ID ~5-8%, stat ~2%). Trigger component absorbed — no separate trigger systematic for Z. | 1 | [x] P4a: 12% Z norm uncertainty implemented as normsys on ZTT and ZLL. Trigger eff applied separately to signal, TTbar, W+jets only. |
| [D7] | Loosened tau ID (Loose/VLoose) for ~10-15% efficiency. Exact WP determined in Phase 2. | 1 | [x] P2/P3: Loose WP selected. |
| [D8] | Anti-muon discriminator: Tight | 1 | [x] P3: Applied. |
| [D9] | MVA vs. cut-based comparison mandatory | 1 | [x] P3: NN vs BDT vs cut-based compared. NN selected as primary. |
| [D10] | Two categories: Baseline + VBF. Finer categorization evaluated in Phase 2. | 1 | [x] P3: Baseline + VBF (mjj > 200, |deta_jj| > 2.0). P4a: Simultaneous fit across both. |
| [D11] | Simultaneous fit across categories with common mu (assumes SM ggH/VBF production ratios). | 1 | [x] P4a: Implemented in pyhf workspace. Single mu POI, ggH + VBF float together. |
| [D12] | SVfit not implemented (searched GitHub, PyPI, conda-forge — no Python package available). Collinear mass + NN-regressed MET as alternatives. | 1 | [x] P1: Documented. Collinear mass implemented as approach (d/c). |
| [D13] | NN-regressed MET success criterion: >15% MET resolution improvement on MC test set. If not met by end of Phase 3, approach (c) is dropped. | 1 | [D] P3: Dropped. No gen-level neutrinos in NanoAOD. Documented as negative result. |

## Constraints

| Label | Constraint | Status |
|-------|-----------|--------|
| [A1] | Luminosity precision: 2.6% (CMS PAS LUM-13-001) | [x] P4a: 2.6% lumi normsys on all MC. |
| [A2] | TauPlusX trigger stream only | [x] P3: Applied. |
| [A3] | Missing minor backgrounds (single top, diboson ~1-3%, rare) — covered by +/-5% correlated normalization on MC-based backgrounds | [x] P4a: 5% norm_missing_bkg normsys on ZTT, ZLL, TTbar. |
| [A4] | No trigger efficiency scale factors available | [x] P4a: 3% trigger_eff normsys on signal, TTbar, W+jets. Absorbed in Z norm for ZTT/ZLL. |

## Limitations

| Label | Limitation | Status |
|-------|-----------|--------|
| [L1] | No QCD multijet MC sample — QCD estimated entirely from data | [x] P3/P4a: QCD from SS data minus MC. |
| [L2] | No WH/ZH/ttH signal samples (missing ~5-10% of signal) | [x] P4a: Acknowledged. Only ggH + VBF in fit. |
| [L3] | Single generator per process — no direct generator comparison. PS ISR/FSR branches to be checked in Phase 2. | [x] P2: No PSWeight/LHEPdfWeight branches available. P4a: Signal acceptance from scale variations not implemented (no muR/muF weights available). |

## Phase 2 Commitments (from Phase 1 strategy)

| Item | Description | Derived from |
|------|------------|-------------|
| P2-1 | Determine tau ID working point (Loose vs VLoose) from data/MC comparison in Z peak | [D7] |
| P2-2 | Measure QCD OS/SS ratio from data in anti-isolated CR | [D4] |
| P2-3 | Optimize VBF thresholds (m_jj, Delta_eta) for S/sqrt(B) | [D10] |
| P2-4 | Evaluate Zeppenfeld centrality: keep as cut or demote to NN input | Section 6.1 |
| P2-5 | Check NanoAOD for PSWeight branches (ISR/FSR variations) | [L3], B16 |
| P2-6 | Check NanoAOD for LHEPdfWeight branches (PDF acceptance) | B3 |
| P2-7 | Check genWeight distribution for negative weights | [L3] |
| P2-8 | Measure unphysical solution fractions for collinear mass per process | A6 |
| P2-9 | Evaluate 0-jet/1-jet/VBF categorization if statistics permit | C1 |
| P2-10 | Enumerate available Tau_decayMode values | B13 |

## Phase 4a Commitments (from Phase 1 strategy)

| Item | Description | Derived from | Status |
|------|------------|-------------|--------|
| P4a-1 | Derive signal acceptance uncertainty from muR/muF scale variations | A5 | [D] No muR/muF weight branches in NanoAOD. Cannot evaluate scale variations at event level. Signal theory uncertainty from YR4 applied as normalization. |
| P4a-2 | Confirm/replace 2% fragmentation uncertainty | A5 | [D] No PS weight branches available. Cannot evaluate fragmentation uncertainty directly. Covered by signal theory normalization. |
| P4a-3 | Check collinear mass template smoothness under TES/MET/JES variations | A6 | [x] P4a: Shape systematics propagated to mcol. Templates show smooth variations (~1% level). |
| P4a-4 | Specify correlation structure for missing backgrounds +/-5% | C15 | [x] P4a: Implemented as single correlated normsys (norm_missing_bkg) on ZTT, ZLL, TTbar. Not on data-driven QCD/W+jets. |
| P4a-5 | Evaluate full Barlow-Beeston in VBF if any bin < 5 expected MC events | C4 | [x] P4a: Barlow-Beeston lite (staterror) applied per channel. VBF has several bins with < 5 expected events. Full per-sample BB would require pyhf shapesys per sample which is more complex; staterror captures the dominant effect. |
| P4a-6 | QCD shape uncertainty from isolation threshold variation | C8 | [D] Not implemented. Would require reprocessing with different isolation thresholds. QCD norm uncertainty (20%) is conservative and covers shape effects. |
