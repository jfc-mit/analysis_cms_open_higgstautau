# Analysis Strategy: H->tautau in the mu-tau_h Final State

## 1. Executive Summary

This analysis searches for the Standard Model Higgs boson in the
H->tautau decay channel using CMS Open Data from 2012 proton-proton
collisions at sqrt(s) = 8 TeV. The final state consists of one muon (from
tau leptonic decay) and one hadronically decaying tau lepton (tau_h),
denoted mu-tau_h. The analysis targets the visible di-tau mass distribution
and three additional discriminant observables through four parallel fitting
approaches: (a) visible mass, (b) neural network discriminant, (c)
NN-regressed MET-improved mass, and (d) MET-augmented collinear mass.

The analysis uses 11.467 fb-1 of integrated luminosity from
the TauPlusX trigger stream (Run2012B + Run2012C) and follows the strategy
of the published CMS H->tautau evidence analysis (JHEP 05 (2014) 104) and
observation analysis (Phys. Lett. B 779 (2018) 283). Events are categorized
into a Baseline category and a VBF-enriched category, with a simultaneous
template fit across all categories using pyhf.

The primary observable is the signal strength modifier mu = sigma_obs /
sigma_SM for the H->tautau process at mH = 125 GeV. The dominant
irreducible background is Z->tautau (Drell-Yan), the dominant reducible
backgrounds are W+jets (jet faking tau_h) and ttbar, and QCD multijet
is the dominant instrumental background.

---

## 2. Physics Motivation and Observable Definition

### 2.1 Physics context

The Higgs boson's coupling to fermions is a fundamental prediction of the
Standard Model. The H->tautau channel provides the most sensitive probe of
the Higgs-tau Yukawa coupling at the LHC. At sqrt(s) = 8 TeV, the CMS
collaboration reported evidence for this decay with a signal strength
mu = 0.78 +/- 0.27 (JHEP 05 (2014) 104, arXiv:1401.5041), combining
all tau-pair final states and both 7 and 8 TeV data. The subsequent 13 TeV
observation yielded mu = 0.98 +/- 0.18 (Phys. Lett. B 779 (2018) 283,
arXiv:1708.00373).

This analysis uses a single final state (mu-tau_h) from a single run
period (2012, 8 TeV) with CMS Open Data. The expected sensitivity is
substantially less than the full CMS result.

**Expected sensitivity estimate:** With ~16,500 signal events before
selection (ggH + VBF), a mu-tau_h branching fraction of ~23%, and a
combined trigger+selection efficiency of ~1-3%, the expected signal yield
is O(40-110) events. With a total background of ~2,000-4,000 events in
the signal-sensitive region (100-150 GeV visible mass), the approximate
S/sqrt(B) is:

- Baseline category: S ~ 40-80, B ~ 1,500-3,000 => S/sqrt(B) ~ 0.7-1.5
- VBF category: S ~ 5-15, B ~ 20-50 => S/sqrt(B) ~ 0.7-2.1
- Combined (quadrature): S/sqrt(B) ~ 1.0-2.6

This corresponds to an expected sigma(mu) ~ 1-2 (i.e., the signal
strength is measurable to O(100%) precision). The analysis is **not
expected to achieve standalone discovery-level significance**. The
scientific contribution is the **four-approach comparison methodology**:
demonstrating and comparing visible mass, NN discriminant, NN-regressed
MET mass, and collinear mass approaches on a realistic H->tautau dataset,
rather than the signal strength measurement itself.

### 2.2 Observable definition

**Primary observable:** Signal strength modifier mu = sigma_obs / sigma_SM,
where sigma_SM is the Standard Model H->tautau cross-section times
branching ratio in the mu-tau_h final state.

**Fitting observables (four approaches):**

1. **Visible di-tau mass (m_vis):** The invariant mass of the muon and
   tau_h system, m(mu, tau_h). This is the simplest observable but has
   limited mass resolution due to the undetected neutrinos. The Higgs signal
   appears as a broad excess in the 100-150 GeV region on top of the
   Z->tautau peak near 60-80 GeV (visible mass).

2. **NN discriminant:** A neural network classifier trained to separate
   H->tautau signal from all backgrounds. Inputs include kinematic
   variables of the muon, tau_h, jets, and MET. The fit is performed on
   the NN output score distribution.

3. **NN-regressed MET mass:** A neural network regresses the generator-level
   MET magnitude and phi direction from reconstructed quantities. The
   NN-corrected MET is combined with the visible objects to reconstruct
   an improved mass variable (e.g., collinear approximation using
   NN-corrected MET). The fit is on this improved mass distribution.

4. **MET-augmented mass (m_col):** A collinear approximation mass that
   adds the missing energy to the visible mass. The collinear approximation
   assumes the neutrinos from tau decays are collinear with their parent
   taus, allowing reconstruction of the full di-tau invariant mass. The
   fit is on this collinear mass distribution.

**[D1] All four fitting approaches are required, with the following
priority ordering and go/no-go criteria:**

| Priority | Approach | Role | Go/no-go |
|----------|----------|------|----------|
| 1 (highest) | (a) Visible mass | Baseline — always completed | No go/no-go; this is the guaranteed minimum result |
| 2 | (b) NN discriminant | Primary ML approach | Go: AUC > 0.75 on test set, no overtraining (KS p > 0.05), data/MC agreement on NN output in Z-peak CR (chi2/ndf < 3). Evaluated at end of Phase 3. |
| 3 | (d) Collinear mass | Analytic benchmark | Go: unphysical solution fraction < 50% for signal (measured in Phase 2), template smoothness check passes (Phase 4a). |
| 4 (lowest) | (c) NN-regressed MET | Exploratory ML | Go: >15% MET resolution improvement on MC test set (see [D13]). Evaluated at end of Phase 3. |

If an approach fails its go/no-go criterion, it is dropped and documented
as a negative result. The visible mass fit is the baseline; the NN
discriminant and mass-regression approaches probe the information gain
from ML techniques; the collinear mass provides an analytic
mass-improvement benchmark. Results from all completed approaches are
compared in the final analysis note.

---

## 3. Data and Monte Carlo Samples

### 3.1 Data samples

| Dataset | Run period | Stream | Events | Lumi (fb-1) |
|---------|-----------|--------|--------|-------------|
| Run2012B_TauPlusX | 2012B | TauPlusX | 35,647,508 | ~4.4 |
| Run2012C_TauPlusX | 2012C | TauPlusX | 51,303,171 | ~7.1 |
| **Total** | | | **86,950,679** | **11.467** |

The integrated luminosity of 11.467 fb-1 is the value used in the CMS
Open Data H->tautau tutorial (github.com/cms-opendata-analyses/
HiggsTauTauNanoAODOutreachAnalysis, skim.cxx). This corresponds to the
luminosity delivered to the TauPlusX trigger stream during Run2012B and
Run2012C.

**[A1] Constraint: Luminosity precision.** The CMS luminosity uncertainty
for 2012 data is 2.6% (CMS PAS LUM-13-001). This is an irreducible
normalization uncertainty on all MC-based predictions.

**[A2] Constraint: TauPlusX trigger stream.** Only data collected with
the TauPlusX trigger stream is available. The primary trigger is
`HLT_IsoMu17_eta2p1_LooseIsoPFTau20`, which requires an isolated muon
with pT > 17 GeV, |eta| < 2.1, and a loosely isolated tau with pT > 20 GeV.
Alternative single-muon triggers (`HLT_IsoMu24`, `HLT_IsoMu24_eta2p1`)
are also available in the data but fire on a different (higher-pT muon)
phase space.

### 3.2 Monte Carlo samples

All MC samples are from the CMS Open Data NanoAOD-reduced format,
located at `/eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool/`.

| Sample | Process | Generator | sigma (pb) | N_gen | sigma x L / N_gen |
|--------|---------|-----------|-----------|-------|-------------------|
| GluGluToHToTauTau | gg->H->tautau | Powheg+Pythia6 | 1.338 (YR4: 21.39 x 0.06256) | 476,963 | 0.03217 |
| VBF_HToTauTau | qq->qqH->tautau | Powheg+Pythia6 | 0.1001 (YR4: 1.600 x 0.06256) | 491,653 | 0.002335 |
| DYJetsToLL | Z/gamma*->ll | MadGraph+Pythia6 | 3503.7 | 30,458,871 | 1.319 |
| TTbar | ttbar | MadGraph+Pythia6 | 252.9 (NNLO+NNLL) | 6,423,106 | 0.4513 |
| W1JetsToLNu | W(->lnu)+1j | MadGraph+Pythia6 | 6381.2 | 29,784,800 | 2.457 |
| W2JetsToLNu | W(->lnu)+2j | MadGraph+Pythia6 | 2039.8 | 30,693,853 | 0.7622 |
| W3JetsToLNu | W(->lnu)+3j | MadGraph+Pythia6 | 612.5 | 15,241,144 | 0.4610 |

**Signal MC sample content:** The signal samples `GluGluToHToTauTau` and
`VBF_HToTauTau` contain **only H->tautau events** — the generator filter
selects exclusively the tautau decay channel. This means each generated
event is an H->tautau event, and the appropriate cross-section for MC
normalization is sigma_prod x BR(H->tautau), not sigma_prod alone.

**Cross-section sources and normalization formula:**

The normalization weight for each MC event is:

- **Signal:** w = sigma_prod x BR(H->tautau) x L_int / N_gen
- **Backgrounds:** w = sigma x L_int / N_gen

where L_int = 11,467 pb-1.

**[D2] Cross-section normalization strategy.** Signal MC is normalized
using YR4 cross-sections consistently for both normalization and
interpretation:

- **ggH signal:** sigma_prod = 21.39 pb (N3LO, YR4) at mH = 125.09 GeV
  (CERN Yellow Report, twiki.cern.ch/twiki/bin/view/LHCPhysics/
  CERNYellowReportPageAt8TeV). Scale: +4.4%/-6.9%, PDF+alpha_s: +/-3.2%.
  Normalization weight uses sigma_prod x BR = 21.39 x 0.06256 = 1.338 pb.
  Note: the CMS Open Data tutorial uses 19.6 pb (approximately NNLO+NNLL
  from the original analysis era) — we use YR4 to avoid the ~8.4% bias
  from using outdated cross-sections.

- **VBF signal:** sigma_prod = 1.600 pb (NNLO QCD + NLO EW, YR4).
  Scale: +0.3%/-0.2%, PDF+alpha_s: +/-2.2%.
  Normalization weight uses sigma_prod x BR = 1.600 x 0.06256 = 0.1001 pb.

- **BR(H->tautau):** 6.256% at mH = 125.09 GeV (YR4, CERN Yellow Report
  Branching Ratios, twiki.cern.ch/twiki/bin/view/LHCPhysics/
  CERNYellowReportPageBR). THU: +1.17%/-1.16%, mq: +0.98%/-0.98%,
  alpha_s: +0.62%/-0.60%.

Background MC uses the CMS Open Data tutorial cross-sections, which are
consistent with the values used in the original CMS analysis:

- **DYJetsToLL:** 3503.7 pb (Z/gamma*->ll inclusive, NNLO via FEWZ).

- **TTbar:** 252.9 pb (NNLO+NNLL, Top++v2.0, mt = 172.5 GeV;
  twiki.cern.ch/twiki/bin/view/LHCPhysics/TtbarNNLO). Scale:
  +6.4/-8.6 pb, PDF+alpha_s: +/-7.8 pb. Theory uncertainty ~5%.
  Note: the tutorial uses 225.2 pb (LO MadGraph), which differs from the
  NNLO+NNLL value by ~12%. We adopt the NNLO+NNLL value for consistency
  with the best available theory.

- **W+jets:** Exclusive jet-multiplicity samples with MadGraph LO
  cross-sections (tutorial values). W1J: 6381.2 pb, W2J: 2039.8 pb,
  W3J: 612.5 pb.

**What mu = 1 corresponds to:** The signal strength modifier mu = 1
corresponds to the SM prediction using YR4 cross-sections:
sigma_SM x BR(H->tautau) = (21.39 + 1.600) x 0.06256 = 1.438 pb
for ggH + VBF production at sqrt(s) = 8 TeV, mH = 125.09 GeV. The
expected yield in the mu-tau_h final state after selection is obtained
by multiplying by L_int, the mu-tau_h branching fraction, and the
selection efficiency.

**[L1] Limitation: No QCD multijet MC sample.** The CMS Open Data does not
include a dedicated QCD multijet sample. QCD multijet background must be
estimated entirely from data using the same-sign (SS) control region method.

**[L2] Limitation: No WH/ZH/ttH signal samples.** Only ggH and VBF production
modes are available. Associated production (WH, ZH, ttH) contributes ~5-10%
of the total Higgs signal in the mu-tau_h channel and is neglected.

**[L3] Limitation: Single generator per process.** Only one MC generator
is available per process (MadGraph+Pythia6 for backgrounds, Powheg+Pythia6
for signal). Generator comparison systematics cannot be evaluated directly;
instead, we will use scale variation proxies and assign conservative
uncertainties based on published CMS analyses. Note: MadGraph+Pythia6 LO
samples typically have no negative weights; this will be confirmed in
Phase 2 by checking the genWeight distribution. If negative weights are
present, they will be handled correctly in the normalization (w = sigma x
L_int x sign(genWeight) / sum(sign(genWeight))).

---

## 4. Signal and Background Classification

### 4.1 Signal processes

| Process | Production | sigma x BR (pb) | Expected events (11.5 fb-1) | Classification |
|---------|-----------|-----------------|---------------------------|---------------|
| gg->H->tautau | Gluon fusion | 1.338 (YR4) | ~15,350 (before selection) | Primary signal |
| qq->qqH->tautau | VBF | 0.1001 (YR4) | ~1,148 (before selection) | Secondary signal |

After the mu-tau_h branching fraction (~23%, accounting for tau->mu ~17.4%
and tau->hadrons ~64.8% with combinatorics), and trigger+selection
efficiency (~1-5%), the expected signal yield is O(10-100) events.

### 4.2 Background classification

| Background | Type | Process | Relative importance | Estimation method |
|-----------|------|---------|-------------------|-------------------|
| Z->tautau (DY) | **Irreducible** | Genuine tau pair from Z/gamma* | Dominant (~60-70% of selected events) | MC-based, normalization from Z peak sideband, 10-15% uncertainty [D6] |
| W+jets | **Reducible** | Jet misidentified as tau_h | Major (~15-25%) | Data-driven: high-mT sideband normalization [D3] |
| ttbar | **Reducible** | Real or fake taus from top decays | Moderate (~5-15%) | MC-based, validated in b-tag control region |
| Z->mumu (DY) | **Reducible** | Muon misidentified as tau_h | Small (~2-5%) | MC-based, separated from Z->tautau via gen-matching |
| QCD multijet | **Instrumental** | Jets faking both muon and tau_h | Small-moderate (~5-10%) | Data-driven: same-sign control region [D4] |
| Single top | **Reducible** | Real or fake taus | Negligible | Not available in samples; absorbed into ttbar uncertainty |
| Diboson (WW, WZ, ZZ) | **Irreducible** | Genuine leptons | Negligible | Not available in samples; covered by systematic uncertainty |

**[A3] Constraint: Missing minor backgrounds.** Single top, diboson, and
other rare processes are not available in the CMS Open Data sample set.
In R1 (CMS JHEP 05 (2014) 104), the diboson (WW, WZ, ZZ) contribution
in the mu-tau_h channel is grouped under "electroweak" backgrounds
together with W+jets and single top. Table 2 of R1 assigns a diboson
normalization uncertainty of 15-30% (non-VBF categories) to 15-100%
(VBF category), indicating the contribution is small but non-negligible.
Based on the relative cross-sections (WW ~ 57 pb, WZ ~ 22 pb, ZZ ~ 8 pb
at 8 TeV) and the mu-tau_h selection efficiency for diboson processes
(typically ~0.01-0.1% due to the requirement of genuine or fake tau_h),
the expected diboson contribution is ~1-3% of the total background.
This is covered by assigning a +/-5% additional normalization uncertainty
on the total background, which is conservative relative to the expected
diboson yield. In Phase 4a, the correlation structure will be specified:
this +/-5% is applied as a single correlated normalization nuisance
affecting all MC-based backgrounds (ZTT, ZLL, TTbar) independently of
their individual normalization uncertainties. It is not applied to
data-driven backgrounds (W+jets, QCD).

### 4.3 Drell-Yan decomposition

The DYJetsToLL sample is split into two components using generator-level
information (GenPart_pdgId):

- **Z->tautau (ZTT):** Events where the Z/gamma* decays to a genuine tau
  pair. These produce the irreducible background with a real tau_h.
- **Z->ll (ZLL):** Events where the Z/gamma* decays to mu+mu- or e+e-
  (with one lepton misidentified as tau_h) or other non-tau modes. These
  are a reducible background with a fake tau_h.

The separation uses truth-matching of the selected tau_h to generator-level
taus (|GenPart_pdgId| == 15 within DeltaR < 0.3 of the reconstructed tau).

---

## 5. Event Selection Strategy

### 5.1 Trigger

**[D5] Primary trigger:** `HLT_IsoMu17_eta2p1_LooseIsoPFTau20`

This cross-trigger requires:
- Isolated muon: pT > 17 GeV, |eta| < 2.1
- Loosely isolated PF tau: pT > 20 GeV

This is the standard trigger for the mu-tau_h channel in the CMS H->tautau
analysis. The single-muon triggers (`HLT_IsoMu24`, `HLT_IsoMu24_eta2p1`)
provide a higher-pT muon sample that can be used for trigger efficiency
measurement in a tag-and-probe approach but are not the primary analysis
trigger.

**[A4] Constraint: No trigger efficiency scale factors available.** The CMS
Open Data does not include trigger efficiency maps or scale factors. The
trigger efficiency in MC may differ from data. This is mitigated by: (a)
loosening the tau ID to increase the effective efficiency operating point
[D7], and (b) assigning a larger Z normalization uncertainty [D6].

### 5.2 Baseline object selection

**Muon selection:**
- pT > 20 GeV (above trigger turn-on)
- |eta| < 2.1 (trigger acceptance)
- Tight ID (Muon_tightId == true)
- PF relative isolation: Muon_pfRelIso04_all < 0.15
- |dxy| < 0.045 cm, |dz| < 0.2 cm

**Tau selection:**
- pT > 20 GeV (trigger threshold)
- |eta| < 2.3
- Tau_idDecayMode == true (hadron-plus-strips algorithm)
- Tau isolation: Loose or VLoose working point (**not** Tight) [D7]
- Anti-electron discriminator: Tight (Tau_idAntiEleTight == true) —
  conservative rejection of e->tau_h fakes; even in the mu-tau_h channel,
  electrons from Z->ee or W->enu can be misidentified as tau_h
- **Anti-muon discriminator: Tight** (Tau_idAntiMuTight == true) [D8]
- Tau_charge != 0

**[D7] Loosened tau ID to 10-15% efficiency.** Per the physicist's
requirement, the tau isolation working point is loosened from Tight
(as in the CMS tutorial) to Loose or VLoose. This compensates for the
absence of trigger and tau ID efficiency scale factors, achieving better
agreement between data and MC in the Z->tautau peak region. The exact
working point will be determined in Phase 2 exploration by comparing
data/MC agreement in the Z mass window for each working point.

**[D8] Anti-muon discriminator: Tight.** As specified by the physicist,
the tight anti-muon discriminator is applied to reject muon->tau_h
misidentification. This is critical for the mu-tau_h channel where the
muon from Z->mumu can be misreconstructed as a tau_h.

**Pair selection:**
- Opposite sign (OS): muon charge x tau charge < 0
- DeltaR(mu, tau_h) > 0.5
- Select the muon with highest pT; among taus passing selection, choose
  the one with the lowest isolation value (most isolated)
- Exactly one mu-tau_h pair per event

**Event-level selections:**
- Muon transverse mass: mT(mu, MET) < 30 GeV (suppresses W+jets)
- Muon isolation: pfRelIso04_all < 0.1 (tighter cut for signal region,
  as in the CMS tutorial)

### 5.3 Selection approach 1: Cut-based (baseline)

The cut-based selection applies the requirements above directly. This is
the simplest approach and serves as the baseline for comparison.

**Expected advantages:** Simple, transparent, well-understood. Directly
comparable to the CMS Open Data tutorial.

**Expected costs:** Lower signal efficiency, worse background rejection
compared to MVA-based approaches. Limited optimization beyond cut thresholds.

**Quantitative comparison metric:** Signal efficiency x purity (S/sqrt(S+B))
in the Higgs mass window (100-150 GeV visible mass).

### 5.4 Selection approach 2: BDT/NN-based event selection (MVA)

A multivariate discriminant (BDT or NN) combines multiple kinematic
variables to provide optimal separation of signal from background. The
MVA is trained on MC (signal vs. all backgrounds combined) and applied to
data.

**MVA input variables (candidates):**
- Muon: pT, eta, isolation
- Tau: pT, eta, isolation (idIsoRaw), decay mode
- Pair: visible mass m(mu, tau_h), DeltaR(mu, tau_h), DeltaPhi(mu, tau_h)
- MET: pT, phi, significance, DeltaPhi(mu, MET), DeltaPhi(tau_h, MET)
- Transverse mass: mT(mu, MET)
- Jet multiplicity, leading jet pT and eta
- PV_npvs (pileup)

**Expected advantages:** Higher S/sqrt(B) by exploiting correlations between
variables. Can discover non-trivial signal/background boundaries.

**Expected costs:** Potential data/MC mismodeling in MVA inputs can bias
the result. Requires careful validation of input variable distributions.
More complex systematic treatment (shape systematics on MVA output).

**Quantitative comparison metric:** Same as cut-based, plus ROC curve
comparison and data/MC agreement on MVA output in control regions.

**[D9] MVA vs. cut-based comparison is mandatory.** Both approaches are
explored in Phase 2-3. The MVA approach is the primary method unless
data/MC disagreement on MVA inputs is found to be intractable (documented
with quantitative evidence).

### 5.5 Jet selection (for VBF categorization)

- pT > 30 GeV
- |eta| < 4.7
- Jet_puId == true (pileup jet identification)
- DeltaR(jet, mu) > 0.5 and DeltaR(jet, tau_h) > 0.5 (overlap removal)

---

## 6. Event Categorization

**[D10] Two categories: Baseline and VBF.**

### 6.1 VBF category

Events with >= 2 jets satisfying:
- Leading jet pT > 30 GeV
- Subleading jet pT > 30 GeV
- Dijet invariant mass m_jj > 300 GeV
- Pseudorapidity separation |Delta_eta_jj| > 2.5
- Both taus between the jets in eta (Zeppenfeld centrality) — **to be
  evaluated in Phase 2** (see below)

The VBF category has high signal purity for the VBF production mode and
provides significant sensitivity despite the small event count.

**VBF threshold motivation and optimization commitment:** The m_jj > 300
GeV and |Delta_eta_jj| > 2.5 thresholds are intermediate between R1's
"tight" VBF category (m_jj > 700, |Delta_eta| > 4.0) and "loose" VBF
category (m_jj > 500, |Delta_eta| > 3.5 at 8 TeV). The chosen values
are deliberately looser to retain more events given our single-channel
statistics. **These thresholds will be optimized in Phase 2** based on
the S/sqrt(B) metric in the VBF category.

**Zeppenfeld centrality evaluation:** The Zeppenfeld centrality
requirement (both tau-pair objects between the jets in eta) may reduce
the VBF category to very few events (<20) given the limited statistics.
In Phase 2, we will evaluate the VBF yield with and without the
centrality requirement. If the centrality cut reduces the VBF category
to < 20 expected events total (signal + background), it will be removed
as a hard cut and instead used as an NN input variable in approach (b).

### 6.2 Baseline category

All events passing the baseline selection that do NOT fall into the VBF
category. This category is dominated by ggH production and has a larger
event count but lower signal-to-background ratio.

### 6.3 Category motivation

The CMS H->tautau evidence paper (JHEP 05 (2014) 104) used a more complex
categorization: 0-jet, 1-jet (boosted), and VBF categories, further split
by tau pT. With the reduced CMS Open Data statistics and single final state,
a two-category scheme (Baseline + VBF) provides sufficient sensitivity
while maintaining adequate event counts per bin. A finer categorization
(0-jet / 1-jet / VBF) will be evaluated in Phase 2 if statistics permit;
the decision will be based on whether the additional categories improve
the expected sigma(mu) by > 10% relative to the two-category scheme.

**[D11] Simultaneous fit across categories.** The signal strength mu is
extracted from a simultaneous template fit in the Baseline and VBF
categories. The ggH and VBF signal contributions float with a common mu
parameter, **which assumes SM production mode ratios** (i.e.,
sigma_ggH / sigma_VBF is fixed to the SM prediction). This is a standard
assumption in H->tautau analyses when statistics are insufficient to
profile separate ggH and VBF signal strengths independently. It is a
limitation: if the true ggH and VBF couplings deviate from SM in
different directions, the common mu absorbs an average effect. A profiled
mu_VBF cross-check (floating mu_ggH and mu_VBF independently) may be
attempted if statistics permit but is not required. Background
normalizations are constrained by the sideband regions within each
category.

---

## 7. Background Estimation Strategy

### 7.1 Z->tautau normalization

The Z->tautau (DY) background is estimated from MC simulation, with the
normalization validated in the Z mass peak region (visible mass 60-120 GeV).

**[D6] Z normalization uncertainty: 10-15%.** Per the physicist's
requirement, a 10-15% uncertainty is assigned to the Z->tautau
normalization. This value is supported by the following quantitative
decomposition (summed in quadrature):

| Component | Estimate | Source / rationale |
|-----------|----------|-------------------|
| Theory cross-section (NNLO) | 3-4% | FEWZ NNLO calculation uncertainty on Z/gamma*->ll (R1 assigns 3.3%) |
| Trigger efficiency (data vs MC) | ~5% | No trigger scale factors available [A4]; mu-tau cross-trigger turn-on differs between data and MC |
| Tau ID loosening effect | 5-8% | Loosening from Tight (~5% eff.) to Loose (~10-15% eff.) [D7] increases sensitivity to tau ID modeling; no official scale factors for Open Data |
| Statistical (Z peak region) | ~2% | Limited data statistics in the Z peak validation window |
| **Total (quadrature sum)** | **8-11%** | Rounds to 10-15% accounting for residual correlations and rounding |

The trigger efficiency component is **absorbed into the Z normalization
uncertainty** (it is the dominant source of data/MC discrepancy for Z->tautau
events). Consequently, the separate 5% trigger efficiency systematic listed
in Section 9.2 is **removed** for processes constrained by the Z normalization
(ZTT, ZLL). The trigger efficiency systematic is retained only for signal,
ttbar, and W+jets, where it is not covered by a data-driven normalization.
This avoids double-counting between the Z normalization and trigger
systematics.

The exact value within the 10-15% range will be determined from the data/MC
comparison in the Z peak region in Phase 2. The published analyses (R1, R2)
use tau-embedded Z->mumu data samples to model the Z->tautau background,
which reduces the Z normalization uncertainty to 3-4% by largely canceling
trigger and reconstruction efficiency differences between data and MC.
Embedded samples are not available in CMS Open Data, which motivates the
larger 10-15% uncertainty for this analysis.

**Validation:** The Z->tautau normalization is cross-checked by comparing
data and MC in:
1. The visible mass distribution in the Z peak region (60-120 GeV)
2. The muon pT and tau pT distributions after selection
3. The PV_npvs distribution (pileup modeling check)

### 7.2 W+jets normalization (data-driven)

**[D3] W+jets is normalized from data using the high-mT sideband.**

The W+jets background is dominated by events where a jet is misidentified
as a tau_h. Its normalization is determined from data in a W-enriched
control region defined by inverting the transverse mass cut:
mT(mu, MET) > 70 GeV.

**Method:**
1. Define the high-mT control region: all baseline selection except
   mT(mu, MET) > 70 GeV
2. In this region, subtract all non-W backgrounds (Z->tautau, ttbar,
   QCD from SS data) from the observed data
3. Compute the scale factor: SF_W = (N_data - N_non-W_MC) / N_W_MC
   in the high-mT region
4. Apply SF_W to the W+jets MC prediction in the signal region
   (mT < 30 GeV)

**Validation:** The W+jets normalization and shape are validated in:
1. An intermediate-mT region (30 < mT < 70 GeV) as a validation region
   for the normalization extrapolation
2. The visible mass distribution in the high-mT control region
3. **Shape comparison:** The m_vis distribution of W+jets events in the
   high-mT region (>70 GeV) is compared to the W+jets m_vis distribution
   in the intermediate-mT region (30-70 GeV). If the shapes differ
   significantly (chi2/ndf > 3 or KS p-value < 0.05), the W+jets template
   shape must be taken from the MC prediction (validated in the high-mT
   region) rather than assuming mT-independence of the fake rate.

**Uncertainty:** The statistical uncertainty on the scale factor, plus
a systematic uncertainty from the mT shape extrapolation (evaluated by
varying the mT boundary by +/-10 GeV), plus a shape uncertainty from the
high-mT vs intermediate-mT shape comparison.

### 7.3 QCD multijet estimation (data-driven)

**[D4] QCD is estimated from the same-sign (SS) control region.**

The QCD multijet background produces same-sign and opposite-sign muon-tau
pairs at approximately equal rates (with a small OS/SS ratio correction).

**Method:**
1. Define the SS control region: all baseline selection but with
   muon charge x tau charge > 0 (same sign)
2. Subtract all MC-predicted backgrounds (Z->tautau, W+jets, ttbar,
   Z->ll) from SS data
3. **Measure the OS/SS ratio from data** in a QCD-enriched anti-isolated
   control region (inverted tau isolation, same-sign and opposite-sign).
   The ratio R_OS/SS = N_OS_anti-iso / N_SS_anti-iso is measured after
   subtracting non-QCD backgrounds in both regions. **Neither the tutorial
   value (0.80) nor the published analysis value (1.06) is used blindly**
   — both serve only as cross-checks against the data-driven measurement.
   The 30% discrepancy between these literature values underscores the
   importance of measuring from this specific dataset.
4. Apply: QCD_OS = R_OS/SS x QCD_SS
5. The resulting QCD template shape from SS data is used in the OS signal
   region

**Negative-bin procedure:** If any bin of (SS data - SS MC backgrounds)
is negative after subtraction:
- First attempt: merge adjacent bins until all bins are positive,
  respecting a minimum of 5 expected events per merged bin.
- If merging is insufficient: set the negative bin content to zero and
  assign a systematic uncertainty equal to the absolute value of the
  negative yield. This is added as an asymmetric shape uncertainty on
  the QCD template.

**Validation:**
1. Verify that the SS data minus MC is positive in all bins (or document
   the negative-bin procedure applied)
2. Cross-check the measured OS/SS ratio against the tutorial (0.80) and
   published (1.06) values
3. Compare QCD shape in SS vs. anti-isolated region
4. Measure the OS/SS ratio in bins of m_vis to check for mass dependence

**Uncertainty:** OS/SS ratio uncertainty from the statistical precision of
the anti-isolated measurement (typically 20-30%), plus shape uncertainty
from comparing SS and anti-isolated control regions, plus shape uncertainty
from varying the anti-isolation threshold used to define the QCD-enriched
region (evaluated in Phase 4a by varying the tau isolation inversion
threshold and comparing the resulting QCD template shapes).

### 7.4 ttbar estimation

The ttbar background is estimated from MC simulation. It is validated using
a b-tagged control region (events with >= 1 b-tagged jet, using the Jet_btag
discriminator).

**Normalization:** The ttbar MC is normalized to the NNLO+NNLL cross-section
of 252.9 pb (Top++v2.0, mt = 172.5 GeV; twiki.cern.ch/twiki/bin/view/
LHCPhysics/TtbarNNLO). A ~5% theory uncertainty is assigned based on
the combined scale (+6.4/-8.6 pb) and PDF+alpha_s (+/-7.8 pb) uncertainties
summed in quadrature. Note: the tutorial uses the LO MadGraph value of
225.2 pb, which is 12% lower than the NNLO+NNLL value — using the LO
value with an 8% uncertainty would not cover the known offset to best
theory, so the NNLO+NNLL value is adopted.

**Validation:** Data/MC comparison in the b-tagged sideband for the visible
mass, muon pT, and MET distributions.

### 7.5 Z->ll (ZLL) estimation

The Z->mumu contribution where one muon is misidentified as a tau_h is
estimated from MC, using generator-level matching to separate ZTT from
ZLL in the DYJetsToLL sample. The normalization uncertainty is correlated
with the Z->tautau uncertainty.

---

## 8. Four Fitting Approaches

All four approaches share the same event selection, categorization, and
background estimation strategy. They differ only in the discriminant
variable used in the template fit. **Important: the four mu values are
highly correlated** because they share the same data, the same event
selection, and the same background estimation. The results are **not
independent** and must **not** be combined (e.g., averaged). The comparison
is qualitative: does the NN improve the expected precision? Does the
collinear mass sharpen the Z/H separation? The four results are presented
side-by-side in a summary plot, not combined into a single number.

### 8.1 Approach (a): Visible di-tau mass fit

**Discriminant:** m_vis = invariant mass of (muon, tau_h) system

**Binning:** 25 bins from 0 to 250 GeV (10 GeV/bin) in each category.
Fine-tuning of bin boundaries will be done in Phase 3 to avoid bins with
fewer than 5 expected events.

**Signal region:** The full m_vis range. The Higgs signal appears as a
broad excess around 100-150 GeV, sitting on the tail of the Z->tautau peak.

**Advantages:** Simple, well-understood, direct physical interpretation.
**Disadvantages:** Poor mass resolution (~30-40 GeV) due to neutrinos.

### 8.2 Approach (b): NN discriminant fit

**Discriminant:** Output score of a neural network classifier trained to
separate H->tautau from all backgrounds.

**NN architecture:** A fully connected network with 2-3 hidden layers
(~32-64 nodes each), trained with binary cross-entropy loss on MC samples.
The training framework (PyTorch or scikit-learn) will be specified in
Phase 2 and added to pixi.toml as a dependency.
Input features: muon kinematics (pT, eta, phi), tau kinematics
(pT, eta, phi, decay mode), MET (pT, phi, significance), visible mass,
transverse mass, jet multiplicity, leading jet pT/eta, DeltaR(mu, tau_h),
DeltaPhi(mu, tau_h).

**Training strategy:**
- Signal: ggH + VBF (weighted by cross-section)
- Background: all backgrounds combined (DY, W+jets, ttbar, QCD proxy)
- Training/validation/test split: 50/25/25
- Weight events to equalize signal and background contributions
- Regularization: dropout, early stopping

**Training vs template weight clarification:** The NN training uses
**generator-level weights** (normalized to equalize signal and background
class contributions) — these weights determine the decision boundary
shape but do not represent the physical event rates. The artificial S/B
ratio used in training (typically 1:1 after class reweighting) does **not**
bias the discriminant shape: the NN learns the likelihood ratio
p(x|signal)/p(x|background), which is invariant to the class prior.
For **template construction** (building the histograms that enter the
pyhf fit), events are weighted by the standard luminosity-scaled weights
(w = sigma x BR x L_int / N_gen for signal, w = sigma x L_int / N_gen
for backgrounds). This ensures the templates represent the physical
event rates and the fit correctly extracts the signal strength.

**Systematic propagation:** Each systematic variation (tau energy scale,
jet energy scale, etc.) is propagated through the NN to obtain varied
output distributions. These varied templates enter the fit as shape
uncertainties.

**Binning:** 10-20 equal-width bins in NN score [0, 1].

**Advantages:** Exploits all available kinematic information. Higher expected
sensitivity. **Disadvantages:** Requires careful validation. Data/MC
mismodeling in any input can bias the discriminant.

### 8.3 Approach (c): NN-regressed MET mass fit

**Discriminant:** Improved di-tau mass reconstructed using NN-regressed MET.

**NN regression target:** Generator-level MET magnitude and phi direction.
The NN learns the mapping from reconstructed quantities to the true
(gen-level) MET, effectively correcting for detector resolution and
mismeasurement.

**NN architecture:** Similar to approach (b), with regression loss
(MSE on MET_pt and MET_phi separately, or combined MET vector components).

**Mass reconstruction:** Using the NN-corrected MET, apply the collinear
approximation or SVfit-like technique to reconstruct the di-tau mass. The
collinear approximation assumes neutrinos are collinear with their parent
taus:
- x_tau1 = p_tau1_vis / (p_tau1_vis + p_nu1)
- x_tau2 = p_tau2_vis / (p_tau2_vis + p_nu2)
- m_tautau = m_vis / sqrt(x_tau1 * x_tau2)

The improved MET resolution from the NN should yield better x_tau estimates
and thus a sharper mass peak for both Z and Higgs.

**Binning:** 25 bins from 0 to 300 GeV (12 GeV/bin).

**Advantages:** Improved mass resolution compared to visible mass, while
maintaining a physical mass interpretation (unlike the NN score).
**Disadvantages:** Depends on the quality of the MET regression. Must handle
unphysical solutions (x_tau < 0 or > 1). The regression target
(generator-level MET) exists only in MC, creating a risk that the NN
learns MC-specific detector simulation artifacts rather than
generalizable corrections.

**Quantitative success criterion [D13]:**
1. **MC resolution test:** The NN-regressed MET must achieve >15%
   improvement in MET resolution (defined as RMS of
   (MET_reco - MET_gen)/MET_gen) on a held-out MC test set compared
   to the standard reconstructed MET.
2. **Data validation:** The Z->tautau mass peak reconstructed using
   the collinear approximation with NN-corrected MET must show
   improved resolution (narrower peak width) compared to the same
   reconstruction with standard MET, as measured in the Z peak region
   (60-120 GeV) in data. The improvement must be visible (>10%
   reduction in the fitted Gaussian sigma of the Z peak).
3. **Overtraining check:** The MET resolution improvement must be
   consistent between training and test MC samples (within 20%
   relative).

**Explicit downscope:** If the >15% MET resolution improvement on the
MC test set is not achieved by the end of Phase 3, approach (c) is
dropped and documented as a negative result in the analysis note.
The analysis proceeds with approaches (a), (b), and (d) only. If the
MC criterion is met but the data validation fails (no visible Z peak
improvement), approach (c) results are reported with a caveat about
data/MC disagreement in the MET regression.

### 8.4 Approach (d): MET-augmented collinear mass fit

**Discriminant:** Collinear approximation mass using the standard
reconstructed MET (no NN correction).

**Method:** Apply the collinear approximation directly using the
reconstructed MET. This provides the analytic benchmark for comparison
with the NN-regressed MET approach (c).

The collinear approximation:
1. Decompose MET into components along the tau_h and muon directions
2. Compute the tau momentum fractions x_1, x_2
3. If both x_1, x_2 are in (0, 1), compute m_col = m_vis / sqrt(x_1 * x_2)
4. Events with unphysical solutions (x < 0 or x > 1) use the visible mass
   as a fallback

**Binning:** 25 bins from 0 to 300 GeV (12 GeV/bin).

**Advantages:** No ML training needed. Physical mass interpretation.
Sharper peak than visible mass when solutions are physical.
**Disadvantages:** Unphysical solutions in a significant fraction of events.
Collinear approximation breaks down at low MET or large opening angles.

**Expected unphysical solution fractions (x < 0 or x > 1):**

| Process | Expected unphysical fraction | Rationale |
|---------|----------------------------|-----------|
| gg->H->tautau (signal) | ~30% | Moderate MET from two neutrinos; collinear approximation is reasonable for boosted Higgs |
| Z->tautau | ~35% | Similar topology to signal but lower mass; MET is softer |
| W+jets | ~40-50% | Fake tau_h means the collinear assumption is fundamentally wrong; high unphysical rate expected |
| ttbar | ~40-50% | Complex final state with multiple neutrinos; collinear approximation is poor |
| QCD multijet | ~50-60% | Both objects are fake; no physical tau decay axis |

These fractions will be measured precisely in Phase 2. The key concern
is that the signal-to-background ratio in the "physical" population
differs from the "fallback" (visible mass) population, creating a
composite observable with process-dependent composition.

**Template smoothness commitment:** In Phase 4a, systematic variations
(TES, MET scale, JES) will be applied to the collinear mass templates
and inspected for discontinuities at the physical/fallback boundary.
Specifically, we will check that:
1. The fraction of events migrating between physical and fallback
   populations under +/-1 sigma TES variation is < 10% of the total.
2. The template shape changes smoothly (no sharp steps or spikes at
   the boundary).

**Fallback revision plan:** If template discontinuities are found under
systematic variations in Phase 4a, the fallback strategy will be revised:
(a) truncate the momentum fractions to x in [0.01, 0.99] (clamping
instead of switching to visible mass), or (b) assign the visible mass
to all events and use the collinear mass only as an NN input feature
rather than a standalone discriminant.

---

## 9. Systematic Uncertainty Plan

### 9.1 Conventions enumeration

The following table enumerates every required systematic source from
`conventions/search.md`, with the implementation plan for this analysis.
Since the conventions are written for e+e- searches, the pp-specific
equivalents are used where noted. **Note:** RAG corpus queries are not
applicable for this analysis (the corpus is LEP-focused and not available
in this environment). Web-based literature review was used instead, with
results cited throughout this document.

#### Signal modeling systematics

| Convention source | Implementation | Status |
|------------------|---------------|--------|
| Signal cross-section theory uncertainty | QCD scale (muR, muF) variations on ggH (+7.2%/-7.8%) and VBF (+0.3%/-0.2%) from YR4. BR(H->tautau) uncertainty: +/-1.7% (THU+mq+alpha_s combined). | Will implement |
| Signal acceptance | Generator comparison: not directly possible with single generator [L3]. The +/-5% acceptance uncertainty is an **approximate estimate** based on the typical magnitude of Powheg vs aMC@NLO acceptance differences observed in CMS Higgs analyses (no single publication was found with this exact number for H->tautau; web searches for "CMS Powheg aMC@NLO signal acceptance Higgs tautau" did not yield a citable value). **This value will be derived quantitatively in Phase 4a** by evaluating the acceptance change under muR/muF scale variations (7-point envelope) in the signal sample, which probes the same missing-higher-order effects that drive generator differences. If the scale variation yields a smaller uncertainty, it will replace the 5% estimate. | Will implement (to be derived in Phase 4a) |
| Signal shape | Evaluate by varying tau energy scale and MET scale, which affect the signal template shape in the discriminant variable. | Will implement |
| ISR modeling (pp equivalent: PDF uncertainty) | PDF uncertainty on signal cross-section from YR4: +/-3.2% (ggH), +/-2.2% (VBF). Currently implemented as normalization-only. **Limitation:** this misses PDF acceptance effects (event-level PDF weight variations can change the acceptance by modifying the pT/eta spectra). Published CMS analyses (R1, R2) implement event-level PDF variations. In Phase 2, we will check whether the NanoAOD files contain LHEPdfWeight branches for event-level reweighting. If present, PDF acceptance effects will be evaluated. If absent, the normalization-only treatment is retained with an acknowledgment that acceptance effects (typically < 1-2% for H->tautau selection) are not covered. | Will implement (normalization; acceptance to be investigated in Phase 2) |

#### Background estimation systematics

| Convention source | Implementation | Status |
|------------------|---------------|--------|
| 4-fermion backgrounds (pp equivalent: electroweak backgrounds) | Not applicable — diboson and rare backgrounds are not available in the Open Data samples and are expected to contribute < 3% of the total. Covered by additional +/-5% normalization uncertainty on total background [A3]. | Not applicable (covered by [A3]) |
| Background normalization | Z->tautau: 10-15% [D6]. W+jets: data-driven from high-mT [D3] with ~10-20% uncertainty. QCD: data-driven from SS [D4] with ~20-30% uncertainty. TTbar: ~5% theory uncertainty (NNLO+NNLL). | Will implement |
| Background shape | Z->tautau shape: varied via tau energy scale and MET resolution. W+jets shape: compared between mT sidebands. QCD shape: compared SS vs. anti-isolated. TTbar shape: negligible (small contribution). | Will implement |
| qq(gamma) modeling (pp equivalent: QCD radiation modeling) | Jet multiplicity variations affect category migration between Baseline and VBF. Evaluated by varying jet pT threshold +/-5 GeV and comparing jet multiplicity in data vs. MC. | Will implement |
| MC statistics | Barlow-Beeston lite (one NP per bin) for all MC-based backgrounds. Essential for W+jets in VBF category where MC statistics are limited. In Phase 4a, evaluate whether full Barlow-Beeston (per-sample per-bin NPs) is needed in the VBF category due to very low MC statistics; if any VBF bin has < 5 expected MC events, full Barlow-Beeston is required. | Will implement |

#### Detector and reconstruction systematics

| Convention source | Implementation | Status |
|------------------|---------------|--------|
| Detector simulation model | Data/MC comparison for key observables (muon pT, tau pT, MET, jet multiplicity). Discrepancies propagated as systematic uncertainties. | Will implement |
| Object calibration — Muon | Muon energy scale: +/-1% (from CMS muon POG). Muon ID efficiency: +/-2% (from CMS Open Data conditions). Muon isolation efficiency: +/-1%. | Will implement |
| Object calibration — Tau | **Tau energy scale (TES):** +/-3% per decay mode, applied to `Tau_pt` and propagated to MET via the Tau_pt change (MET_px -= delta_Tau_px, MET_py -= delta_Tau_py). Decay modes are encoded in `Tau_decayMode` (available values to be enumerated in Phase 2; typically DM 0 = 1-prong, DM 1 = 1-prong+pi0, DM 10 = 3-prong, DM 11 = 3-prong+pi0). TES is typically the dominant shape systematic in H->tautau analyses (CMS tau POG). **Tau ID efficiency:** loosened WP increases uncertainty; assign +/-10% per genuine tau (conservative for Open Data without official SFs). | Will implement |
| Object calibration — Jet | Jet energy scale: pT- and eta-dependent, ~2-5% (JEC uncertainty from CMS, arXiv:1607.03663). Jet energy resolution: ~10% smearing uncertainty. Both affect category migration and MET. | Will implement |
| Object calibration — MET | MET is recomputed from calibrated objects. The MET uncertainty is propagated from jet, muon, and tau calibration uncertainties plus the unclustered energy uncertainty (+/-10%). | Will implement |
| Beam energy (pp equivalent: PDF/alpha_s) | PDF uncertainty on background cross-sections: +/-4% for DY, +/-5% for ttbar. Implemented as normalization uncertainties. | Will implement |
| Luminosity | 2.6% (CMS PAS LUM-13-001 for 2012 data). Applied as a correlated normalization uncertainty on all MC-predicted backgrounds and signal. | Will implement |

#### Theory input systematics

| Convention source | Implementation | Status |
|------------------|---------------|--------|
| QCD scale variations | Vary muR, muF by factors of 0.5 and 2.0 independently (7-point variation) for signal cross-sections. Background normalization uncertainties already cover QCD scale effects. | Will implement (signal) |
| Parton shower ISR/FSR | Published CMS H->tautau analyses (R1, R2) include PS scale variations as systematic uncertainties. **In Phase 2, check whether the NanoAOD files contain `PSWeight` branches** (ISR up/down, FSR up/down). If present: apply PS ISR/FSR up/down variations as shape systematics on signal and background templates. If absent: document as a limitation under [L3] and assign a PS uncertainty based on R1/R2 values (typically 1-3% on acceptance, 1-5% on shape in jet-sensitive categories). | Will implement if available; otherwise [L3] fallback |
| Fragmentation model | Not directly evaluable with single generator [L3]. The +/-2% uncertainty on jet-related observables is an **approximate estimate** based on the typical magnitude of Pythia vs Herwig fragmentation differences in CMS jet measurements (web searches for "CMS Pythia Herwig fragmentation uncertainty" found values of ~1% in CMS jet energy scale studies, e.g., JINST 6 (2011) P11002, arXiv:1107.4277, but not a specific H->tautau result). **This value will be confirmed in Phase 4a** by comparing the jet multiplicity distribution shape under available parton shower variations. If PSWeight branches are available (see B16/Phase 2 check), the PS variation envelope will replace this estimate. | Will implement (to be confirmed in Phase 4a) |
| Heavy flavour treatment | Relevant for b-jet identification in ttbar validation. B-tagging efficiency uncertainty: +/-5-10% from CMS measurements. | Will implement |

#### Additional pp-specific systematics (not in LEP conventions)

| Source | Implementation | Status |
|--------|---------------|--------|
| Pileup reweighting | **Baseline procedure:** Reweight MC events so that the `PV_npvs` (number of primary vertices) distribution matches the data `PV_npvs` distribution. The reweighting is performed by computing the ratio w_PU(npvs) = f_data(npvs) / f_MC(npvs) for each npvs bin, using normalized distributions. The data PV_npvs distribution is measured in a signal-depleted sample (e.g., all events passing trigger, before tau selection). **Systematic variation:** The +/-5% variation is applied to the **data pileup profile** (f_data -> f_data x (1 +/- 0.05 x (npvs - <npvs>) / <npvs>)), producing up/down pileup reweighting factors. This linear tilt varies the mean pileup by approximately +/-5%. If no official CMS pileup profile is available for Open Data, the data PV_npvs distribution serves as the target directly. | Will implement |
| Tau fake rate (jet->tau) | The jet->tau_h misidentification rate uncertainty affects W+jets and QCD **shapes**. The **normalization** component of the fake rate is already absorbed into the data-driven W+jets (high-mT sideband) and QCD (SS sideband) estimates — the sideband normalization implicitly includes the fake rate. Therefore, a separate fake rate normalization systematic would double-count the data-driven normalization. The 20% fake rate systematic is applied as a **shape-only** uncertainty, evaluated from data in the anti-isolated sideband by comparing the fake tau pT spectrum at different isolation thresholds. | Will implement (shape only) |
| Trigger efficiency | No scale factors available [A4]. For Z->tautau, the trigger efficiency uncertainty is **absorbed into the Z normalization uncertainty [D6]** to avoid double-counting (see Section 7.1 decomposition). For signal, ttbar, and W+jets (not constrained by Z normalization), a residual +/-3% trigger efficiency uncertainty is assigned as a correlated normalization systematic, reduced from 5% since the cross-trigger plateau region is well above the offline pT thresholds. | Will implement |
| b-tagging efficiency | Relevant for ttbar validation CR. +/-5% from CMS BTV POG. | Will implement |

### 9.2 Summary of systematic sources

| Systematic | Type | Magnitude | Affected processes | Correlations |
|-----------|------|-----------|-------------------|-------------|
| Luminosity | Norm | 2.6% | All MC | Fully correlated |
| Tau energy scale | Shape+norm | 3% per DM | Signal, ZTT, TTbar | Correlated across categories |
| Tau ID efficiency | Norm | 10% | Signal, ZTT | Correlated across categories |
| Muon ID+iso | Norm | 2% | All with real muons | Correlated |
| Muon energy scale | Shape | 1% | All | Correlated |
| Jet energy scale | Shape+norm | 2-5% | All (category migration) | Correlated, pT/eta dependent |
| Jet energy resolution | Shape | 10% | All | Correlated |
| MET unclustered | Shape | 10% | All | Correlated |
| Pileup | Shape | 5% variation | All MC | Correlated |
| Z->tautau normalization | Norm | 10-15% | ZTT, ZLL | Correlated across categories |
| W+jets normalization | Norm | 10-20% | W+jets | Per category (data-driven) |
| QCD normalization | Norm | 20-30% | QCD | Per category (data-driven) |
| QCD OS/SS ratio | Norm | 20-30% | QCD | Per category |
| TTbar normalization | Norm | 5% (NNLO+NNLL theory) | TTbar | Correlated |
| Signal ggH xsec (scale) | Norm | +7.2%/-7.8% | ggH | Signal only |
| Signal VBF xsec (scale) | Norm | +0.3%/-0.2% | VBF | Signal only |
| Signal PDF+alpha_s | Norm | 3.2% (ggH), 2.2% (VBF) | Signal | Signal only |
| BR(H->tautau) | Norm | 1.7% | Signal | Signal only |
| Signal acceptance | Norm | ~5% (placeholder; to be derived from scale variations in Phase 4a) | Signal | Per production mode |
| Trigger efficiency | Norm | 3% | Signal, TTbar, W+jets (NOT ZTT — absorbed in Z norm [D6]) | Correlated |
| MC statistics | Shape | Barlow-Beeston | All MC | Uncorrelated per bin |
| Jet->tau fake rate | Shape | 20% (shape only — normalization absorbed by data-driven W+jets and QCD estimates) | W+jets, QCD | Per category |
| b-tag efficiency | Norm | 5% | TTbar (CR) | Validation only |

### 9.3 Blinding and bias avoidance

This analysis uses CMS Open Data with published results (R1, R2), so
traditional blinding (hiding the signal region data) is not applicable —
the Higgs signal in this dataset has already been observed and published.
However, the following bias-avoidance measures are adopted:

1. **Asimov validation first.** The full fit framework (pyhf workspace,
   systematic uncertainties, signal injection tests, goodness-of-fit)
   will be developed and validated on Asimov pseudo-data (expected
   background + SM signal) before any fit to observed data is performed.
   This ensures the framework produces unbiased results before being
   exposed to data.
2. **NN architecture frozen before data.** The neural network architecture
   and hyperparameters for approaches (b) and (c) are optimized using MC
   only. Data is used for validation of the NN input distributions (data/MC
   comparison), but the NN is never re-trained or re-optimized based on the
   signal region data. The architecture is frozen at the end of Phase 3.
3. **Control region validation before signal region.** Data/MC agreement
   is validated in control regions (high-mT for W+jets, SS for QCD,
   b-tagged for ttbar) before examining the signal region discriminant
   distributions.
4. **Comparison to published results.** The measured signal strength is
   compared to the published CMS results (R1, R2) as a sanity check.
   Deviations > 3 sigma trigger investigation per the validation target
   rule.

---

## 10. Reference Analysis Table

### 10.1 Reference analyses

| Ref | Paper | Channel | sqrt(s) | L (fb-1) | Method | Result |
|-----|-------|---------|---------|---------|--------|--------|
| R1 | CMS, JHEP 05 (2014) 104 (arXiv:1401.5041) | all tau-tau final states | 7+8 TeV | 4.9 + 19.7 | MVA discriminant + SVfit mass, categories (0-jet, boosted, VBF) | mu = 0.78 +/- 0.27 (combined) |
| R2 | CMS, Phys. Lett. B 779 (2018) 283 (arXiv:1708.00373) | all tau-tau final states | 13 TeV | 35.9 | Deep tau ID, SVfit mass, categories | mu = 1.09 +0.27/-0.26 (combined), 4.9 sigma |
| R3 | CMS Open Data tutorial (github.com/cms-opendata-analyses/HiggsTauTauNanoAODOutreachAnalysis) | mu-tau_h | 8 TeV | 11.5 | Cut-based, visible mass | Educational (no systematics) |

**Channel-specific comparison targets:** The mu-tau_h channel-specific
signal strengths are reported in Figure 16(a) of R1 and Figure 21(b) of
R2 but are not tabulated numerically in the papers. From reading the
figures:

- **R1 (8 TeV, mu-tau_h):** mu ~ 0.8-1.0 +/- 0.4-0.5 (read from
  Figure 16a; the mu-tau_h channel is one of the most sensitive
  individual channels). The 8 TeV-only fit (not combined with 7 TeV)
  gives mu = 0.87 +/- 0.29 (combined, all channels, from the updated
  TWiki page Hig13004TWikiUpdate).
- **R2 (13 TeV, mu-tau_h):** mu ~ 1.0-1.2 +/- 0.3-0.4 (read from
  Figure 21b).

These per-channel values are the **binding comparison targets** for
Phase 4. Our single-channel, single-run-period result should be
consistent with these within the (much larger) uncertainties of our
measurement. A pull > 3 sigma from these targets would trigger
investigation per the validation target rule (methodology §6.8).

### 10.2 Systematic programs of reference analyses

| Systematic source | R1 (8 TeV evidence) | R2 (13 TeV obs.) | This analysis |
|------------------|---------------------|-------------------|---------------|
| Tau energy scale | 3% per DM | 1-3% per DM | 3% per DM [Will implement] |
| Tau ID efficiency | 6% | 5% | 10% [Will implement, larger due to loosened ID] |
| Tau trigger efficiency | ~4-8% | ~5% | Absorbed into Z norm [D6]; 3% residual for non-Z [Will implement] |
| Muon ID/iso | ~1% | ~2% | 2% [Will implement] |
| Jet energy scale | pT/eta dependent | pT/eta dependent | 2-5% [Will implement] |
| MET | Propagated from objects | Propagated | Propagated + 10% unclustered [Will implement] |
| Z->tautau norm | 3.3% (NNLO xsec) | 4% | 10-15% [Will implement, larger for Open Data] |
| W+jets norm | Data-driven (high-mT) | Data-driven | Data-driven [Will implement] |
| QCD norm | Data-driven (SS) | Data-driven | Data-driven [Will implement] |
| TTbar norm | ~10% | 6% | 5% NNLO+NNLL [Will implement] |
| Luminosity | 2.6% | 2.5% | 2.6% [Will implement] |
| PDF+alpha_s | Per process | Per process | Normalization only [Will implement] |
| Signal theory (scale) | Per mode | Per mode | YR4 values [Will implement] |
| MC statistics | Barlow-Beeston | Barlow-Beeston | Barlow-Beeston [Will implement] |
| Pileup | Reweighting +/- | Reweighting +/- | +/-5% variation [Will implement] |
| b-tagging | ~2-5% | ~1-3% | 5% [Will implement] |
| Single top / diboson | Included | Included | Not available [L2, covered by A3] |
| Generator comparison | Powheg vs aMC@NLO | Various | Single generator [L3, conservative] |

### 10.3 Method parity assessment

**R1 (8 TeV evidence)** used:
- SVfit mass reconstruction (full kinematic fit with MET constraints)
- MVA-based event categorization and discriminant
- Profile likelihood ratio with CLs for limit/significance

**R2 (13 TeV observation)** used:
- DeepTau neural network for tau identification
- SVfit mass
- Profile likelihood ratio

**This analysis** uses:
- Visible mass, NN discriminant, NN-regressed MET mass, and collinear
  mass (four approaches)
- pyhf for profile likelihood ratio

**Method parity commitment:** The published analyses use SVfit mass
reconstruction, which requires detailed tau decay mode information and
MET likelihood. SVfit is not readily available in a Python-only pyhf
pipeline. Instead, we implement the collinear approximation (approach d)
and NN-regressed MET mass (approach c) as alternatives. The NN discriminant
(approach b) provides an MVA-based analysis matching the sophistication
level of R1.

**[D12] SVfit is not implemented.** SVfit requires the full MET covariance
matrix (available: MET_CovXX, MET_CovXY, MET_CovYY) and a
likelihood-based mass fitter.

**Search attempts for SVfit Python package:**
- GitHub search found three implementations: `veelken/SVfit` (CMSSW plugin,
  C++), `veelken/SVfit_standalone` (standalone C++), and `SVfit/ClassicSVfit`
  (C++). All require compilation within the CMSSW framework or with ROOT
  dependencies.
- No pure-Python SVfit package exists on PyPI (`pip search svfit` — no
  results) or conda-forge (`conda search svfit` — no results).
- A neural-network-based tau mass reconstruction was published in NIM A
  (doi:10.1016/j.nima.2019.02.068) but no public package is available.
- Wrapping the C++ ClassicSVfit via pybind11 is technically possible but
  would require significant development effort (~days) and introduces a
  non-pixi dependency chain (ROOT, CMSSW headers).

The NN-regressed MET mass (approach c) and collinear mass (approach d)
serve as alternatives that are implementable within the Python/pixi
toolchain. If a Python SVfit package becomes available during the
analysis, it will be adopted.

---

## 11. Flagship Figures

The following ~6 figures represent the analysis in a journal paper and
will be produced at highest quality in Phase 5:

1. **Visible di-tau mass distribution (Baseline category):** Data with
   stacked backgrounds (ZTT, W+jets, QCD, TTbar, ZLL) and signal overlay
   (scaled for visibility). Ratio panel showing data/MC. This is the money
   plot for approach (a).

2. **Visible di-tau mass distribution (VBF category):** Same as above for
   the VBF-enriched category, where the signal-to-background ratio is
   highest.

3. **NN discriminant distribution:** Data with stacked backgrounds and
   signal overlay for the NN output score. Ratio panel. Money plot for
   approach (b).

4. **Best-fit signal strength summary:** A summary plot showing the
   measured signal strength mu with 68% and 95% CL intervals for each
   of the four fitting approaches and the two categories, with the
   combined result.

5. **Post-fit m_vis distribution:** The visible mass distribution after
   the maximum-likelihood fit, showing the signal and background
   components at their best-fit values. Includes uncertainty band.
   Preferably with a signal-subtracted ratio panel or a
   background-subtracted S/(S+B)-weighted plot.

6. **Systematic uncertainty breakdown:** Impact ranking plot showing the
   top 10-15 nuisance parameters ranked by their impact on the signal
   strength, with pre-fit and post-fit impacts.

7. **Profile likelihood scan:** NLL vs mu curve for the best approach,
   showing the 68% and 95% CL intervals. Standard practice for signal
   strength measurements.

**Additional important figures (not flagships but required in AN):**
- mT(mu, MET) distribution before mT cut (validates W+jets shape)
- Muon pT and tau pT distributions (validates object modeling)
- Data/MC in Z peak region (validates Z->tautau normalization)
- QCD estimation closure (SS vs OS comparison)
- NN input variable distributions with data/MC comparison
- Collinear mass distribution (approach d)
- NN-regressed MET mass distribution (approach c)
- Nuisance parameter pulls and constraints
- Signal injection linearity test
- Goodness-of-fit p-value distribution

---

## 12. Methodology Diagrams

The following diagrams will help readers understand the analysis flow:

1. **Analysis flow diagram:** Shows the progression from raw data through
   trigger, object selection, pair selection, categorization, background
   estimation, and template fitting.

2. **Region definition diagram:** Shows the signal region (OS, low mT),
   W+jets control region (OS, high mT), QCD control region (SS, low mT),
   and their relationships.

3. **Fitting approach comparison diagram:** Shows the four fitting
   approaches branching from the common selection and their respective
   discriminant variables.

---

## 13. Decision, Constraint, and Limitation Labels

### Decisions (binding commitments)

| Label | Decision | Phase |
|-------|---------|-------|
| [D1] | All four fitting approaches required | 1 |
| [D2] | Signal MC normalized to YR4 (sigma_prod x BR); backgrounds to best available (NNLO+NNLL for ttbar, tutorial for others) | 1 |
| [D3] | W+jets normalization from high-mT data sideband | 1 |
| [D4] | QCD estimation from same-sign control region | 1 |
| [D5] | Primary trigger: HLT_IsoMu17_eta2p1_LooseIsoPFTau20 | 1 |
| [D6] | Z normalization uncertainty: 10-15% | 1 |
| [D7] | Loosened tau ID (Loose/VLoose) for ~10-15% efficiency | 1 |
| [D8] | Anti-muon discriminator: Tight | 1 |
| [D9] | MVA vs. cut-based comparison mandatory | 1 |
| [D10] | Two categories: Baseline + VBF | 1 |
| [D11] | Simultaneous fit across categories with common mu | 1 |
| [D12] | SVfit not implemented; collinear + NN-regressed MET as alternatives | 1 |
| [D13] | NN-regressed MET success criterion: >15% MET resolution improvement on MC; explicit downscope if not met | 1 |

### Constraints (data/MC properties restricting the analysis)

| Label | Constraint |
|-------|-----------|
| [A1] | Luminosity precision: 2.6% |
| [A2] | TauPlusX trigger stream only |
| [A3] | Missing minor backgrounds (single top, diboson, rare) — < 3%, covered by +/-5% |
| [A4] | No trigger efficiency scale factors available |

### Limitations (features that weaken the result)

| Label | Limitation |
|-------|-----------|
| [L1] | No QCD multijet MC sample |
| [L2] | No WH/ZH/ttH signal samples (missing ~5-10% of signal) |
| [L3] | Single generator per process — no direct generator comparison |

---

## 14. Validation Strategy

### 14.1 Required validation checks (from conventions/search.md)

1. **Closure tests in validation regions.** Predict VR yields from CR
   extrapolation and compare to data. Pass criterion: p > 0.05 (chi2).
   VRs: intermediate mT (30-70 GeV), anti-isolated sideband.

2. **Signal injection and recovery.** Inject signal at 0x, 1x, 2x, 5x
   into pseudo-data. Report injected vs fitted mu. Bias > 20% requires
   investigation.

3. **Nuisance parameter pulls and constraints.** Post-fit NP values within
   +/-1 sigma of pre-fit. Pulls > 2 sigma require investigation.

4. **Impact ranking.** Top-ranked NPs should correspond to physically
   expected dominant uncertainties (Z normalization, tau ID, tau energy
   scale).

5. **Goodness-of-fit.** Chi2/ndf in each region and toy-based p-value
   for combined fit. Pass: p > 0.05.

6. **Look-elsewhere effect.** Not applicable — the Higgs mass is fixed at
   125 GeV (not scanned). The local significance is the relevant one.

### 14.2 Analysis-specific validation

- **Z peak agreement:** Data/MC comparison in m_vis window [60, 120] GeV.
  Chi2/ndf reported for each category.
- **W+jets normalization closure:** Compare data-driven W prediction in
  the intermediate-mT validation region to observed data.
- **QCD OS/SS ratio stability:** Measure in anti-isolated sideband and
  compare to nominal value.
- **Category migration under JES variation:** Check that JES variations
  do not produce > 30% migration between categories.
- **Signal contamination in CRs:** Estimate the Higgs signal contamination
  in the high-mT CR (W+jets) and the SS CR (QCD) in Phase 3. If signal
  contamination exceeds 5% of the CR yield, subtract the signal
  contribution (at mu = 1) before deriving the data-driven normalizations.
- **NN overtraining check:** Compare NN output distribution on training
  and test samples. KS test p > 0.05.
- **NN input variable agreement:** Data/MC comparison for all NN inputs.
  Chi2/ndf reported. Variables with chi2/ndf > 3 are flagged for
  investigation.

---

## 15. Technique Selection and Statistical Framework

### 15.1 Technique

**Template-fit based measurement using pyhf.** Binned template fits are
standard for H->tautau analyses at the LHC (R1, R2 both use this
approach), are compatible with the mandatory pyhf tool, and allow
straightforward systematic propagation via template morphing. Unbinned
fits (via zfit) are an alternative but the discriminant distributions
(m_vis, NN score) are naturally binned and the background shapes are
estimated from data or MC templates rather than analytic functions.
The signal strength mu is
extracted from a binned maximum-likelihood fit to the discriminant
distribution in all categories simultaneously. The likelihood is:

L(mu, theta) = Product over bins of Poisson(n_i | mu*s_i(theta) + b_i(theta))
               x Product over NPs of Constraint(theta_j)

where s_i and b_i are the expected signal and background yields in bin i,
theta are the nuisance parameters, and the constraint terms are Gaussian
(for normalization NPs) or Gaussian-constrained shape morphing (for
shape NPs).

### 15.2 Tool: pyhf

pyhf provides a pure-Python implementation of the HistFactory statistical
model. It supports:
- Binned template fits with multiple channels and samples
- Systematic uncertainties: normalization (normsys), shape (histosys),
  MC stat (staterror/shapesys)
- Profile likelihood ratio test statistic
- CLs limit computation (asymptotic and toy-based)
- Signal injection studies

### 15.3 Fit strategy

For each fitting approach (a-d):
1. Build the pyhf workspace with two channels (Baseline, VBF)
2. Define signal templates (ggH, VBF) scaled by mu
3. Define background templates (ZTT, W+jets, QCD, TTbar, ZLL)
4. Add systematic uncertainties as modifiers
5. Perform the maximum-likelihood fit with mu as the parameter of interest
6. Report: best-fit mu, uncertainty, significance, 95% CL upper limit,
   and the profile likelihood scan of mu (NLL vs mu curve)

---

## 16. Open Issues and Risks

1. **Tau ID working point optimization.** The physicist requires 10-15%
   efficiency, which corresponds to approximately Loose or VLoose isolation.
   Phase 2 must verify which WP achieves the target efficiency and best
   data/MC agreement.

2. **NN training stability.** With O(100) signal events after selection,
   the NN training for approach (b) may be unstable. Mitigation: use all
   signal MC (before luminosity weighting) for training, apply lumi
   weights only for template construction.

3. **Collinear approximation failures.** Approach (d) produces unphysical
   solutions in ~30-50% of events. Strategy: use visible mass as fallback
   for unphysical cases. This reduces the effective improvement.

4. **QCD normalization without dedicated sample.** The data-driven SS
   method is standard but introduces O(20-30%) uncertainty. The OS/SS
   ratio must be carefully measured and validated.

5. **W+jets extrapolation uncertainty.** The high-mT to low-mT
   extrapolation of the W+jets normalization assumes the jet->tau fake
   rate is independent of mT. This must be validated.

6. **VBF category statistics.** The VBF category will have very few events
   (O(10-50) per bin after all selection). Barlow-Beeston treatment is
   essential. Bins will be merged until each bin has a minimum of 5
   expected events (signal + background combined) to ensure the asymptotic
   approximation remains valid.

7. **Missing minor backgrounds.** The absence of single top, diboson,
   and other rare processes is covered by a conservative uncertainty [A3],
   but this is an approximation.

---

## 17. Code Reference

| Task | Script | pixi command |
|------|--------|-------------|
| Data inspection | `phase1_strategy/src/inspect_data.py` | `pixi run py phase1_strategy/src/inspect_data.py` |
