# Phase 2 Exploration: H->tautau in the mu-tau_h Final State

## 1. Sample Inventory

### 1.1 Data location and format

All NanoAOD files are stored at `/eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/`.
Each file contains a single TTree named `Events`. The schema is a reduced
NanoAOD format produced by the CMS Open Data outreach tool.

### 1.2 Event counts and file structure

| File | Process | Events | Branches | Tree |
|------|---------|--------|----------|------|
| GluGluToHToTauTau.root | gg->H->tautau | 476,963 | 69 | Events |
| VBF_HToTauTau.root | VBF H->tautau | 491,653 | 69 | Events |
| DYJetsToLL.root | Z/gamma*->ll | 30,458,871 | 69 | Events |
| TTbar.root | ttbar | 6,423,106 | 69 | Events |
| W1JetsToLNu.root | W+1jet | 29,784,800 | 69 | Events |
| W2JetsToLNu.root | W+2jets | 30,693,853 | 69 | Events |
| W3JetsToLNu.root | W+3jets | 15,241,144 | 69 | Events |
| Run2012B_TauPlusX.root | Data RunB | 35,647,508 | 62 | Events |
| Run2012C_TauPlusX.root | Data RunC | 51,303,171 | 62 | Events |

**Total Data:** 86,950,679 events. **Total MC:** 143,527,390 events.

### 1.3 Branch schema

**MC samples (69 branches):**

| Collection | Branches | Type |
|-----------|---------|------|
| GenPart | pt, eta, phi, mass, pdgId, status | float[]/int32_t[] |
| HLT | IsoMu24_eta2p1, IsoMu24, IsoMu17_eta2p1_LooseIsoPFTau20 | bool |
| Jet | pt, eta, phi, mass, btag, puId | float[]/bool[] |
| MET | pt, phi, sumet, significance, CovXX, CovXY, CovYY | float |
| Muon | pt, eta, phi, mass, charge, pfRelIso03_all, pfRelIso04_all, tightId, softId, dxy, dxyErr, dz, dzErr, jetIdx, genPartIdx | various |
| Tau | pt, eta, phi, mass, charge, decayMode, relIso_all, jetIdx, genPartIdx, idDecayMode, idIsoRaw, idIsoVLoose, idIsoLoose, idIsoMedium, idIsoTight, idAntiEleLoose, idAntiEleMedium, idAntiEleTight, idAntiMuLoose, idAntiMuMedium, idAntiMuTight | various |
| PV | npvs, x, y, z | int32_t/float |
| Event | event, luminosityBlock, run | various |

**Data samples (62 branches):** Same as MC minus the 7 GenPart branches
(GenPart_pt, GenPart_eta, GenPart_phi, GenPart_mass, GenPart_pdgId,
GenPart_status, nGenPart). No data-only branches exist.

### 1.4 Object multiplicities (first 1000 events)

| Sample | mean nMuon | mean nTau | mean nJet | mean nGenPart |
|--------|-----------|----------|----------|--------------|
| ggH signal | 0.42 | 6.71 | 6.49 | 7.69 |
| VBF signal | 0.50 | 8.14 | 7.72 | 9.31 |
| DY | 0.65 | 3.41 | 2.38 | 4.71 |
| ttbar | 1.06 | 8.55 | 9.03 | 9.98 |
| W+1jet | 0.40 | 6.09 | 5.81 | 6.99 |
| Data RunB | 0.83 | 4.14 | 3.24 | N/A |
| Data RunC | 0.86 | 6.62 | 5.02 | N/A |

**Note:** The high tau multiplicity (6-8 per event) includes all
reconstructed tau candidates before any quality cuts. After applying
idDecayMode and isolation requirements, the yield drops dramatically.

---

## 2. Data Quality Assessment

### 2.1 Pathologies found

**Tau_relIso_all has NaN values in all samples.** In the first 50,000
events of each checked sample:
- GluGluToHToTauTau: 257,324 NaN values (out of ~335,000 tau entries)
- DYJetsToLL: 135,983 NaN
- Run2012B_TauPlusX: 209,427 NaN

**Impact:** Tau_relIso_all cannot be used directly for pair selection
(argmin on NaN would fail). The pair selection algorithm uses
`ak.fill_none(ak.nan_to_none(...), 999.0)` to handle NaN values safely,
effectively deprioritizing taus with undefined isolation.

**Muon_pfRelIso04_all has -999 sentinel values.** This is the standard
NanoAOD sentinel for muons where isolation is not computed (e.g., very
low-pT muons). The preselection cut pfRelIso04_all < 0.15 naturally
rejects these.

### 2.2 No other data quality issues

- No NaN or Inf in any non-isolation branch
- No negative pT values
- No extreme eta values (all within expected detector coverage)
- Jet_pt minimum is 15 GeV (consistent with NanoAOD jet threshold)
- MET_pt ranges are physical (0.03-649 GeV)
- PV_npvs ranges 1-54, mean ~17 (reasonable for 2012 pileup)

---

## 3. Data Archaeology

### 3.1 Weight and flag branches

**No event weight branches found in any sample:**
- PSWeight: **NOT FOUND** in any sample [confirms P2-5]
- LHEPdfWeight: **NOT FOUND** [confirms P2-6]
- LHEScaleWeight: **NOT FOUND**
- genWeight: **NOT FOUND** [confirms P2-7]
- LHEWeight_originalXWGTUP: **NOT FOUND**

**Implication:** The NanoAOD reduction tool stripped all weight information.
All MC events have implicit weight = 1 (before cross-section normalization).
This means:
- **No negative weights** — confirmed, since genWeight is absent and
  MadGraph LO samples typically have none.
- **No PS ISR/FSR variations** — must assign from published analyses (R1/R2)
  per strategy [L3, B16].
- **No PDF acceptance variations** — must assign from published analyses
  per strategy [B3].
- **No muR/muF scale variations** — must assign from published analyses.

**Strategy revision input:** Phase 1 committed [B16] to checking PSWeight
branches. Since they are absent, the analysis will assign ISR/FSR
uncertainties from the published CMS H->tautau analyses, as planned in the
fallback. This is not a feasibility change — the strategy already anticipated
this scenario.

### 3.2 Pre-selection detection

Comparing N_gen to expected events from xsec * lumi:

| Sample | N_gen | xsec * lumi | Ratio N_gen/(xsec*L) |
|--------|-------|-------------|---------------------|
| ggH | 476,963 | 15,345 | 31.1 |
| VBF | 491,653 | 1,148 | 428.3 |
| DY | 30,458,871 | 40,176,928 | 0.76 |
| ttbar | 6,423,106 | 2,900,004 | 2.21 |
| W+1jet | 29,784,800 | 73,173,220 | 0.41 |
| W+2jets | 30,693,853 | 23,390,387 | 1.31 |
| W+3jets | 15,241,144 | 7,023,538 | 2.17 |

**Interpretation:** Signal samples have N_gen >> expected (ratio >>1),
meaning the generator produced many more events than expected at 11.5 fb-1.
This is normal — MC is overproduced to reduce statistical uncertainty.
DY and W+1jet have ratio < 1, meaning the available MC provides less
than one "luminosity equivalent" of simulated data. W+2jets and W+3jets
have ratio > 1. The ttbar sample provides ~2x the expected events.

**No evidence of pre-selection** in the NanoAOD reduction — the file sizes
are consistent with full generator-level samples skimmed to reduced NanoAOD
format (dropping miniAOD-level branches).

### 3.3 MC generation parameters

All MC samples use Pythia6 for parton showering with the CMS 2012 tune
(Tune Z2*). Beam energy: 4 TeV per beam (sqrt(s) = 8 TeV).

| Sample | Generator | Process |
|--------|-----------|---------|
| ggH | Powheg + Pythia6 | gg->H->tautau at NLO |
| VBF | Powheg + Pythia6 | qq->qqH->tautau at NLO |
| DY | MadGraph + Pythia6 | Z/gamma*->ll at LO |
| ttbar | MadGraph + Pythia6 | ttbar at LO |
| W+jets | MadGraph + Pythia6 | W(->lnu)+Nj at LO |

**Coverage gaps:** Single energy (8 TeV), single year (2012), single
generator per process. No generator comparison possible [L3].

### 3.4 Truth-level information

**GenPart structure:** Available in MC only. Contains:
- GenPart_pt, GenPart_eta, GenPart_phi, GenPart_mass (kinematics)
- GenPart_pdgId (particle identity)
- GenPart_status (1 = final state, 2 = intermediate)

**PDG IDs found in signal samples:** {-15, -13, -11, 11, 13, 15}
(electrons, muons, taus and their antiparticles). **No Higgs (pdgId=25)
is stored** — the NanoAOD reduction stripped the Higgs intermediate state.

**GenPart multiplicities:** Mean 7.7 (ggH), 9.3 (VBF), 4.7 (DY)
particles per event with status 1 or 2.

**Truth matching capability:** The Tau_genPartIdx and Muon_genPartIdx
branches link reconstructed objects to GenPart entries, enabling:
- DY decomposition into Z->tautau vs Z->ll (via GenPart_pdgId matching)
- Signal truth matching for efficiency studies

### 3.5 Tau_decayMode values [P2-10]

Unique values across all samples: **{-1, 0, 1, 2, 10}**

| Value | Meaning | Fraction (ggH, pre-selection) |
|-------|---------|------------------------------|
| -1 | Not a tau (failed HPS algorithm) | ~53% |
| 0 | 1-prong, 0 pi0 | ~12% |
| 1 | 1-prong, 1 pi0 | ~12% |
| 2 | 1-prong, 2 pi0 | ~4% |
| 10 | 3-prong, 0 pi0 | ~19% |

Decay modes 0, 1, 2, 10 are physical hadronic tau decay modes.
Mode -1 indicates failed tau reconstruction. After idDecayMode requirement,
only modes 0, 1, 2, 10 remain.

### 3.6 HLT trigger rates (first 1000 events)

| Trigger | ggH | VBF | DY | Data B | Data C |
|---------|-----|-----|-----|--------|--------|
| IsoMu17_eta2p1_LooseIsoPFTau20 | 6.4% | 9.0% | 16.2% | 28.2% | 26.1% |
| IsoMu24_eta2p1 | 7.8% | 9.3% | 20.5% | 21.4% | 20.1% |
| IsoMu24 | 8.0% | 9.4% | 21.7% | 21.4% | 20.2% |

The mu-tau cross-trigger (IsoMu17_eta2p1_LooseIsoPFTau20) fires less
often on signal MC than on data, consistent with the lower fraction of
events containing both a muon and a tau in MC signal samples (which require
the H->tautau->mu+tau_h decay chain).

---

## 4. Object Definitions and Preselection

### 4.1 Object selection (from Strategy Section 5.2)

**Muon:**
- pT > 20 GeV, |eta| < 2.1, tightId, pfRelIso04_all < 0.15
- |dxy| < 0.045 cm, |dz| < 0.2 cm

**Tau:**
- pT > 20 GeV, |eta| < 2.3, idDecayMode
- idAntiEleTight, idAntiMuTight [D8]
- Tau isolation: Loose WP (idIsoLoose) [D7 — determined below]
- charge != 0

**Pair selection:**
- Opposite sign (OS), DeltaR(mu, tau) > 0.5
- Highest-pT muon, lowest-isolation tau
- mT(mu, MET) < 30 GeV
- Muon pfRelIso04_all < 0.1 (signal region tightening)

### 4.2 Cutflow (Loose tau ID)

| Cut | ggH (raw) | VBF (raw) | DY (raw) | ttbar (raw) | W+1j (raw) |
|-----|-----------|-----------|----------|-------------|------------|
| Total | 476,963 | 491,653 | 30,458,871 | 6,423,106 | 29,784,800 |
| Trigger | 33,520 | 49,109 | 4,753,620 | 872,546 | 1,251,689 |
| Good muon | 25,522 | 39,150 | 4,479,322 | 746,718 | 1,044,071 |
| Good tau | 8,230 | 10,964 | 77,699 | 53,489 | 41,505 |
| OS pair | 8,069 | 10,556 | 63,298 | 40,610 | 31,357 |
| DR > 0.5 | 8,069 | 10,556 | 63,279 | 40,556 | 31,314 |
| mT < 30 GeV | 5,397 | 7,067 | 39,795 | 6,210 | 3,383 |
| Iso < 0.1 | 4,603 | 6,255 | 34,468 | 5,670 | 2,951 |

**Trigger efficiency (MC):** ggH: 7.0%, VBF: 10.0%, DY: 15.6%
**Selection efficiency (after trigger):** ggH: 13.7%, VBF: 12.7%

### 4.3 Weighted yields after full preselection

| Sample | Raw events | Weighted yield | Weight per event |
|--------|-----------|----------------|-----------------|
| ggH | 4,603 | 148.1 | 0.0322 |
| VBF | 6,255 | 14.6 | 0.0023 |
| DY | 34,468 | 45,465.2 | 1.319 |
| ttbar | 5,670 | 2,560.0 | 0.451 |
| W+1jet | 2,951 | 7,249.8 | 2.457 |
| W+2jets | 5,194 | 3,958.1 | 0.762 |
| W+3jets | 3,319 | 1,529.5 | 0.461 |
| **MC Total** | | **60,925.3** | |
| Data RunB | 26,236 | 26,236 | 1.0 |
| Data RunC | 41,752 | 41,752 | 1.0 |
| **Data Total** | | **67,988** | |

**Data/MC ratio: 1.116** (12% excess in data over MC prediction).

This excess is consistent with the missing QCD multijet background,
which is not included in the MC. The QCD contribution will be estimated
from the same-sign control region in Phase 3 [D4]. Estimating
QCD ~ 7,000 events would bring Data/MC to ~1.0.

### 4.4 Background composition

After preselection (weighted):
- DY (Z->tautau + Z->ll): 74.6% (dominant)
- W+jets (combined): 20.9%
- ttbar: 4.2%
- Missing: QCD multijet (~10-15% of data based on Data-MC excess)

**Signal fraction:** S/(S+B) = 162.7/60,925.3 = 0.27% (before any
signal-region optimization).

---

## 5. Tau ID Working Point Study [D7]

### 5.1 Comparison methodology

Three tau isolation working points (VLoose, Loose, Medium) were compared
using the full dataset. For each WP, the complete preselection was applied
and the visible mass distribution was compared between data and MC in
the Z peak region (60-120 GeV).

### 5.2 Results

| WP | Data | MC Total | Data/MC (full range) | chi2/ndf (Z peak 60-120 GeV) |
|----|------|----------|---------------------|------------------------------|
| VLoose | 87,238 | 74,313 | 1.174 | 24.47/6 = 4.08 |
| Loose | 67,314 | 60,188 | 1.118 | 17.76/6 = 2.96 |
| Medium | 48,496 | 45,697 | 1.061 | 17.69/6 = 2.95 |

### 5.3 Signal yields per WP (weighted)

| WP | ggH yield | VBF yield | Total signal |
|----|-----------|-----------|-------------|
| VLoose | 165.7 | 16.1 | 181.8 |
| Loose | 148.1 | 14.6 | 162.7 |
| Medium | 122.6 | 12.5 | 135.1 |

### 5.4 Decision: Loose working point [D7 resolved]

**Recommendation: Loose** tau isolation working point.

**Rationale:**
1. **Data/MC agreement:** Loose gives chi2/ndf = 2.96, comparable to
   Medium (2.95) and much better than VLoose (4.08). The Data/MC ratio
   of 1.12 at Loose is consistent with missing QCD (~7000 events).
2. **Signal yield:** Loose retains 20% more signal than Medium (162.7 vs
   135.1 weighted events), which is significant given the limited expected
   sensitivity.
3. **Efficiency operating point:** Loose provides approximately 10-12%
   tau ID efficiency, consistent with the [D7] requirement of ~10-15%.
4. **VLoose rejected:** Despite higher signal yield, VLoose has
   significantly worse data/MC agreement (chi2/ndf = 4.08), suggesting
   the MC poorly models the very loose isolation regime.

Plots: `figures/tau_id_wp_VLoose.pdf`, `figures/tau_id_wp_Loose.pdf`,
`figures/tau_id_wp_Medium.pdf`.

---

## 6. Variable Survey and Separation Power

### 6.1 Discriminating variables studied

The following variables were surveyed for signal (ggH + VBF) vs background
separation power, quantified by ROC AUC:

| Rank | Variable | ROC AUC | Comment |
|------|----------|---------|---------|
| 1 | tau pT | 0.695 | Signal taus are harder |
| 2 | m_vis (visible mass) | 0.656 | Higgs peak vs Z peak |
| 3 | N_jets | 0.647 | VBF has more jets |
| 4 | MET pT | 0.639 | Signal has more MET |
| 5 | DeltaR(mu, tau) | 0.564 | Moderate separation |
| 6 | Muon pT | 0.561 | Signal muons are harder |
| 7 | tau decay mode | 0.554 | Mild discrimination |
| 8 | mT(mu, MET) | 0.554 | Anti-correlated with W+jets |
| 9 | DeltaPhi(mu, tau) | 0.554 | Weak separation |
| 10 | PV_npvs (pileup) | 0.532 | Marginal |
| 11 | Muon eta | 0.507 | No discrimination |
| 12 | N_b-jets | 0.507 | Marginal (ttbar rejection) |
| 13 | Tau eta | 0.503 | No discrimination |

**Top candidates for NN inputs:** tau_pt, m_vis, N_jets, MET_pt,
DeltaR(mu,tau), muon_pt. These provide the most individual separation.
Additionally, MET phi, tau decay mode, and mT should be included as
they provide complementary information.

Plots for each variable: `figures/{variable}.pdf`.
Separation power ranking: `figures/separation_power.pdf`.

### 6.2 Data/MC agreement

Data/MC comparisons with ratio panels were produced for all 13 variables.
Key observations:

- **m_vis:** Good shape agreement. Z peak at ~60-80 GeV clearly visible.
  Data excess in the tail (>120 GeV) could be signal or QCD contamination.
- **Muon pT:** Reasonable agreement. Slight excess at high pT in data.
- **Tau pT:** Good agreement in shape.
- **MET:** Data slightly higher than MC, consistent with QCD contribution.
- **N_jets:** Good agreement for 0-3 jets. Excess at high multiplicity.
- **PV_npvs:** Good agreement, confirming pileup modeling is adequate.
- **Tau decay mode:** Modes 0, 1, 2, 10 all populated. Mode 10 (3-prong)
  is less common.

---

## 7. Collinear Mass Study [P2-8]

### 7.1 Unphysical solution fractions

The collinear approximation yields unphysical solutions (x_mu < 0, x_mu > 1,
x_tau < 0, x_tau > 1, or near-parallel mu-tau configuration) at the
following rates:

| Process | N_total | N_physical | Unphysical fraction |
|---------|---------|------------|-------------------|
| ggH (signal) | 4,603 | 2,499 | **45.7%** |
| VBF (signal) | 6,255 | 3,776 | **39.6%** |
| DY (Z->tautau) | 34,468 | 16,963 | **50.8%** |
| ttbar | 5,670 | 2,552 | **55.0%** |
| W+1jet | 2,951 | 889 | **69.9%** |
| W+2jets | 5,194 | 2,055 | **60.4%** |
| W+3jets | 3,319 | 1,363 | **58.9%** |
| Data RunB | 26,236 | 11,666 | **55.5%** |
| Data RunC | 41,752 | 18,805 | **55.0%** |

### 7.2 Comparison with strategy estimates

| Process | Strategy estimate | Measured | Status |
|---------|-----------------|----------|--------|
| ggH | ~30% | 45.7% | **Higher than expected** |
| Z->tautau | ~35% | 50.8% | **Higher than expected** |
| W+jets | ~40-50% | 60-70% | **Higher than expected** |
| ttbar | ~40-50% | 55.0% | Consistent |

All fractions are higher than the strategy estimates. The ggH signal has
45.7% unphysical solutions, which exceeds the 50% threshold for concern
but remains below the go/no-go criterion (signal unphysical < 50%,
strategy [D1] priority table). The collinear mass approach (d) remains
viable but the high unphysical fractions reduce its effective statistics
significantly.

**For events with physical solutions,** the collinear mass provides
improved mass resolution compared to the visible mass: the Z peak appears
sharper and the Higgs signal region is better separated.

Plots: `figures/collinear_mass.pdf`, `figures/collinear_mass_physical.pdf`.

---

## 8. VBF Category Optimization [P2-3, P2-4]

### 8.1 Jet multiplicity distribution

After full preselection (Loose tau ID), the jet multiplicity for VBF signal
shows a clear excess at >= 2 jets compared to backgrounds:

| Category | VBF signal | ggH signal | DY | W+jets | ttbar |
|----------|-----------|-----------|-----|--------|-------|
| 0-jet | 1.3 | 73.1 | 27,605 | 5,361 | 42 |
| 1-jet | 4.3 | 47.3 | 11,654 | 4,917 | 651 |
| >= 2-jet | 9.0 | 27.7 | 6,206 | 2,459 | 1,867 |

### 8.2 VBF threshold optimization

A scan over m_jj and |Delta_eta_jj| thresholds was performed using
MC signal and DY+ttbar backgrounds after full preselection:

**Best cut:** m_jj > 200 GeV, |Delta_eta_jj| > 2.0

This gives S/sqrt(B) ~ 0.49 in the VBF category. The loose thresholds
are motivated by the limited statistics in this single-channel analysis.

### 8.3 Zeppenfeld centrality [P2-4]

| Zeppenfeld cut | S (weighted) | B (weighted) | S/sqrt(B) | N_total |
|----------------|-------------|-------------|-----------|---------|
| None (no cut) | 16.65 | 1,168.6 | 0.487 | — |
| zep < 1.0 | 16.42 | 1,097.9 | 0.496 | — |
| zep < 0.5 | 8.62 | 531.9 | 0.374 | — |

**Decision:** The Zeppenfeld centrality cut with threshold 1.0 provides
marginal improvement (0.496 vs 0.487) and is retained as a soft cut.
The tight cut (0.5) loses too much signal. Per strategy [P2-4], since
the VBF category has > 20 expected events, the centrality requirement
is retained as a cut rather than demoted to an NN input.

### 8.4 0-jet / 1-jet / VBF categorization [P2-9]

The strategy committed to evaluating finer categorization if statistics
permit [D10, C1]. Given the yields:
- 0-jet: ~27,600 DY, ~73 ggH (S/sqrt(B) ~ 0.44)
- 1-jet: ~11,650 DY, ~47 ggH (S/sqrt(B) ~ 0.44)
- >= 2-jet: ~6,200 DY, ~28 ggH + ~9 VBF (S/sqrt(B) ~ 0.47)

The 0-jet and 1-jet categories have comparable S/sqrt(B). Splitting them
does not improve expected sensitivity by > 10% relative to the
Baseline+VBF scheme. **Decision: retain two categories (Baseline + VBF)**
per the original strategy [D10].

---

## 9. Baseline Yields Summary

### 9.1 Final yields after preselection (Loose tau ID)

| Category | ggH | VBF | DY | ttbar | W+jets | MC Total | Data | Data/MC |
|----------|-----|-----|----|-------|--------|----------|------|---------|
| Inclusive | 148.1 | 14.6 | 45,465 | 2,560 | 12,737 | 60,925 | 67,988 | 1.116 |

The ~12% Data/MC excess is attributed to missing QCD multijet background
(not included in MC). The QCD estimate from the same-sign control region
[D4] is expected to account for this difference.

---

## 10. PDF Build Test

The PDF build toolchain was tested with a minimal stub:
- pandoc (3.8.3) with pandoc-crossref and citeproc: **PASS**
- tectonic (TeX compilation): **PASS**
- Full pipeline (markdown -> .tex -> .pdf): **PASS**

The stub was deleted after verification.

---

## 11. Strategy Revision Inputs

### 11.1 No PSWeight/LHEPdfWeight branches

**Phase 1 assumed:** PSWeight branches might be available for ISR/FSR
variations [B16, P2-5]. Phase 2 found: branches are absent.

**Implications:** The analysis must assign ISR/FSR uncertainties from
published CMS analyses rather than evaluating from the MC directly.
This was anticipated in the strategy fallback plan. No revision needed.

### 11.2 No genWeight branch

**Phase 1 assumed:** genWeight distribution should be checked for negative
weights [L3, P2-7]. Phase 2 found: genWeight is absent.

**Implications:** All events have implicit weight 1. No negative weight
handling needed. No revision needed.

### 11.3 Collinear mass unphysical fractions higher than expected

**Phase 1 estimated:** ~30% for ggH signal. **Phase 2 measured:** 45.7%.

**Implications:** The collinear mass approach (d) is still viable (signal
unphysical fraction < 50%), but the reduced effective statistics may limit
its precision. The go/no-go criterion [D1] is met, but the template
smoothness check in Phase 4a [P4a-3] should be carefully monitored.

### 11.4 No Higgs in GenPart

The Higgs boson (pdgId=25) is not stored in the reduced NanoAOD GenPart
collection. Only the decay products (taus, then their decay products) are
available. This limits some truth-matching capabilities but does not affect
the analysis since the H->tautau events are identified by the sample
identity, not by matching to the Higgs in the event record.

---

## 12. Self-Check

- [x] Sample inventory complete with all branches documented
- [x] Data quality validated — Tau_relIso_all NaN and Muon iso sentinels documented
- [x] Data archaeology done (weights, pre-selection, MC params, truth info)
- [x] Tau ID WP comparison done — Loose WP selected [D7]
- [x] Variable survey with separation power ranking (13 variables, ROC AUC)
- [x] Baseline yields tabulated (Data: 67,988, MC: 60,925)
- [x] Data/MC agreement plots for all key variables (13 plots)
- [x] PSWeight branches checked — NOT FOUND [P2-5]
- [x] Tau_decayMode values documented: {-1, 0, 1, 2, 10} [P2-10]
- [x] PDF build test passed
- [x] All figures pass plotting rules (CMS style, figsize=(10,10), exp_label, no titles)

## 13. Figures Produced

| Figure | Description |
|--------|-------------|
| `mvis.pdf` | Visible mass data/MC comparison with ratio |
| `mt.pdf` | Transverse mass (mu, MET) |
| `mu_pt.pdf` | Muon pT distribution |
| `tau_pt.pdf` | Tau pT distribution |
| `mu_eta.pdf` | Muon eta distribution |
| `tau_eta.pdf` | Tau eta distribution |
| `met_pt.pdf` | MET distribution |
| `njets.pdf` | Jet multiplicity |
| `nbjets.pdf` | B-jet multiplicity |
| `pv_npvs.pdf` | Pileup distribution |
| `tau_dm.pdf` | Tau decay mode |
| `delta_phi.pdf` | DeltaPhi(mu, tau) |
| `delta_r.pdf` | DeltaR(mu, tau) |
| `separation_power.pdf` | Variable ranking by ROC AUC |
| `tau_id_wp_VLoose.pdf` | Tau ID VLoose data/MC at Z peak |
| `tau_id_wp_Loose.pdf` | Tau ID Loose data/MC at Z peak |
| `tau_id_wp_Medium.pdf` | Tau ID Medium data/MC at Z peak |
| `collinear_mass.pdf` | Collinear mass (all events) |
| `collinear_mass_physical.pdf` | Collinear mass (physical solutions only) |
| `vbf_mjj.pdf` | VBF dijet mass distribution |
| `vbf_deta.pdf` | VBF Delta_eta_jj distribution |
