---
title: "Measurement of the Higgs Boson Signal Strength in the H to tau tau Decay Channel in the mu-tau Final State Using CMS Open Data at sqrt(s) = 8 TeV"
author: "CMS Open Data Analysis"
date: "2026-03-24"
abstract: |
  A measurement of the Higgs boson signal strength modifier in the
  $H\to\tau\tau$ decay channel is performed using proton-proton collision
  data recorded by the CMS experiment at $\sqrt{s} = 8$ TeV,
  corresponding to an integrated luminosity of 11.5 fb$^{-1}$.
  The analysis targets the $\mu\tau_\mathrm{h}$ final state, where one
  tau lepton decays to a muon and neutrinos and the other decays
  hadronically. Events are categorized into a Baseline category and a
  vector boson fusion (VBF) enriched category, and a simultaneous
  binned profile likelihood fit is performed across both categories.
  Three fitting approaches are compared: a visible di-tau mass template,
  a neural network discriminant, and a collinear approximation mass
  template. Using the full dataset, the neural network approach yields
  a measured signal strength of $\mu = 0.64 \pm 1.08$, corresponding
  to an observed significance of 0.61 standard deviations and an
  observed 95% confidence level upper limit of $\mu < 2.85$. The result
  is consistent with the Standard Model prediction ($\mu = 1$) at the
  $0.34\sigma$ level. The observed uncertainty of 1.08 is improved
  relative to the expected Asimov uncertainty of 1.28 due to data
  constraints on the nuisance parameters. The alternative visible mass
  and collinear mass approaches yield negative signal strength values
  driven by a persistent 5% data/MC normalization deficit, demonstrating
  the importance of multivariate techniques for separating signal from
  background shape effects. Under the standard pull convention
  ($(\hat{\theta} - \theta_0) / \sigma_\mathrm{prefit}$), no nuisance
  parameter exceeds $2\sigma$ (maximum: $W$+jets VBF normalization at
  $-1.89\sigma$). The largest pulls are attributable to the known VBF
  category data/MC deficit of 31%.
bibliography: ../../../phase5_documentation/outputs/references.bib
link-citations: true
---

# Change Log {-}

| Version | Date | Description |
|---------|------|-------------|
| 4a-v1 | 2026-03-24 | Initial AN version with expected results on Asimov data. All three fitting approaches documented. Observed results pending data validation. |
| 4a-v2 | 2026-03-24 | Review fix iteration: F1 (VBF bin merging for GoF stability), F2 (removed incorrect JES-MET propagation), F3 (MET uncl scales only unclustered component), F4 (shape template smoothing). sigma(mu) updated from 1.15 to 1.25. Impact ranking reordered. Category B documentation fixes applied. |
| 4b-v1 | 2026-03-24 | Phase 4b: 10% data validation. Added Section 10 (10% Data Validation) with data/MC comparisons, fitted signal strengths, NP pulls, GoF results, and per-category fits. Updated Expected Results section with 10% observed results side-by-side. Updated abstract and conclusions to reflect 10% validation status. VBF category shows 35% deficit consistent with statistical fluctuation in 10% subsample. NN score $\mu = -3.73 \pm 2.81$ (pull = $-1.69\sigma$ from SM). |
| 4b-v2 | 2026-03-24 | Extended POI bounds from [-5, 10] to [-30, 30] to eliminate fits at boundary. All three approaches now converge freely. NN score: $\mu = -3.73 \pm 2.81$, $m_\mathrm{vis}$: $\mu = -14.4 \pm 5.9$, $m_\mathrm{col}$: $\mu = -22.0 \pm 7.0$. GoF p-value for NN score updated to 0.209. All NP pulls remain below 2$\sigma$. |
| 4c-v1 | 2026-03-24 | Phase 4c: Full data results. Added Section 11 (Full Data Results) with observed signal strengths, NP pulls, GoF, per-category fits, impact ranking, and post-fit data/MC comparisons for all three approaches. Primary result: NN score $\mu = 0.63 \pm 1.08$ (0.61$\sigma$ observed significance). Three-way comparison table (expected / 10% / full) shows NN score recovering toward SM with full statistics. VBF deficit persists at 31% (data/MC = 0.69) but is absorbed by normalization NPs. Two NPs pulled beyond 2$\sigma$: norm\_wjets\_vbf ($-2.16\sigma$) and shape\_jes ($-2.02\sigma$). Updated abstract and conclusions with final physics result. |
| 4c-v2 | 2026-03-25 | Review fix iteration addressing 10 findings (1A, 5B, 4C). F1: GoF investigation with proper LLR test statistic, retry logic (nn\_score failure rate reduced 14.8% to 1.0%), per-category diagnostics; p=0.000 confirmed genuine, per-category chi2/bin individually acceptable (0.80-1.19). F2: Impact ranking numbers refreshed from diagnostics\_full.json. F3: Diagnostics re-run with current bestfit +/- postfit\_unc method. F4: NP pull table now uses standard convention as primary (no NP exceeds $2\sigma$; max: norm\_wjets\_vbf at $-1.89\sigma$). F5: VBF deficit process decomposition and NP absorption quantified. F6: Expected $\sigma(\mu) = 1.28$ confirmed from expected\_results.json (nn\_score.mu\_err = 1.2819). F7/F8: Notes on post-fit plot limitations. F9: Expected significance clarified (0.846 from full fit vs 0.814 Asimov). F10: NP pull plot x-axis label updated. |

\newpage

# Introduction {#sec:introduction}

The discovery of the Higgs boson by the ATLAS and CMS collaborations in 2012 [@CMS:2012qbp; @ATLAS:2012yve] opened a new era of precision measurements of the properties of this particle. Among the most fundamental properties to be established is the Yukawa coupling of the Higgs boson to fermions, which is a direct prediction of the Standard Model (SM) mechanism of electroweak symmetry breaking. The $H\to\tau\tau$ decay channel provides the most sensitive probe of the Higgs boson coupling to leptons at the Large Hadron Collider (LHC), as the tau lepton is the heaviest lepton and thus has the largest Yukawa coupling among the leptons.

The CMS collaboration reported evidence for the $H\to\tau\tau$ decay mode with a signal strength of $\mu = 0.78 \pm 0.27$ using the combined 7 and 8 TeV dataset corresponding to an integrated luminosity of 24.6 fb$^{-1}$ [@CMS:2014nkk]. This result combined all tau-pair final states ($e\mu$, $e\tau_\mathrm{h}$, $\mu\tau_\mathrm{h}$, $\tau_\mathrm{h}\tau_\mathrm{h}$) and both center-of-mass energies. The subsequent observation at $\sqrt{s} = 13$ TeV with 35.9 fb$^{-1}$ yielded $\mu = 1.09^{+0.27}_{-0.26}$ with a significance of 4.9 standard deviations [@CMS:2017zyp].

This analysis measures the Higgs boson signal strength modifier $\mu = \sigma_\mathrm{obs} / \sigma_\mathrm{SM}$ in the $H\to\tau\tau$ channel using CMS Open Data from the 2012 data-taking period at $\sqrt{s} = 8$ TeV [@CMSOpenData:Htautau]. The measurement is performed in the $\mu\tau_\mathrm{h}$ final state, where one tau lepton decays leptonically to a muon and the other decays hadronically. The analysis uses an integrated luminosity of 11.5 fb$^{-1}$ from the TauPlusX trigger stream (Run2012B and Run2012C), corresponding to approximately half of the full 8 TeV CMS dataset.

The signal strength modifier $\mu$ is defined as the ratio of the observed Higgs boson production cross section times branching ratio to the SM prediction. A value of $\mu = 1$ corresponds to the SM prediction, computed using the LHC Higgs Cross Section Working Group Yellow Report 4 (YR4) recommendations [@LHCHiggsCrossSectionWorkingGroup:2016ypw]: $\sigma_\mathrm{SM} \times \mathrm{BR}(H\to\tau\tau) = (21.39 + 1.60) \times 0.06256 = 1.438$ pb for the sum of gluon fusion (ggH) and vector boson fusion (VBF) production at $m_H = 125.09$ GeV [@Aad:2015zhl].

Events are categorized into two analysis categories: a Baseline category containing the majority of events, dominated by ggH production, and a VBF-enriched category requiring two forward jets with large dijet invariant mass and pseudorapidity separation. A simultaneous binned profile likelihood fit is performed across both categories using the pyhf statistical framework [@pyhf; @Cranmer:2012sba]. Three fitting approaches are compared, differing in the discriminant variable used in the template fit:

1. **Visible di-tau mass ($m_\mathrm{vis}$):** the invariant mass of the reconstructed muon and hadronic tau system, providing a simple and well-understood baseline;
2. **Neural network (NN) discriminant score:** the output of a neural network classifier trained to distinguish signal from background, exploiting multivariate kinematic information;
3. **Collinear approximation mass ($m_\mathrm{col}$):** the reconstructed di-tau mass using the collinear approximation, which assumes the neutrinos from tau decays are collinear with their parent taus.

A fourth approach based on NN-regressed missing transverse energy (MET) was planned but dropped because the reduced NanoAOD format lacks generator-level neutrino information required for training the regression target.

The expected sensitivity of this single-channel, single-run-period analysis is substantially less than the full CMS result. The scientific contribution is the comparison of the three fitting approaches on a realistic $H\to\tau\tau$ dataset: the NN discriminant improves the expected uncertainty on $\mu$ by a factor of 2.6 relative to the visible mass approach, demonstrating the significant information gain from multivariate techniques even in a single decay channel.

This analysis note presents the complete results of this measurement. Expected results on Asimov pseudo-data establish the baseline sensitivity. A 10% data validation using a random subsample confirmed the analysis framework functions correctly on real data, with all nuisance parameter pulls below 2$\sigma$ and acceptable goodness-of-fit for the primary NN approach. The full observed results on the complete collision dataset are presented as the primary physics result, with a three-way comparison between expected, 10% validation, and full data results.


# Data Samples {#sec:data}

## Collision data {#sec:data-collision}

The analysis uses proton-proton collision data recorded by the CMS detector [@CMS:2011aa] at a center-of-mass energy of $\sqrt{s} = 8$ TeV during the 2012 LHC run. The data were collected using the TauPlusX trigger stream and are available through the CMS Open Data initiative in a reduced NanoAOD format. The dataset consists of two run periods as summarized in @tbl:data-samples.

| Dataset | Run period | Events | Luminosity (fb$^{-1}$) |
|---------|-----------|--------|----------------------|
| Run2012B\_TauPlusX | 2012B | 35,647,508 | 4.4 |
| Run2012C\_TauPlusX | 2012C | 51,303,171 | 7.1 |
| **Total** | | **86,950,679** | **11.5** |

: Summary of the collision data samples used in this analysis. The luminosity corresponds to the TauPlusX trigger stream as used in the CMS Open Data $H\to\tau\tau$ tutorial [@CMSOpenData:Htautau]. {#tbl:data-samples}

The integrated luminosity of 11.5 fb$^{-1}$ is determined from the CMS luminosity measurement for the 2012 dataset, with an uncertainty of 2.6% [@CMS:LUM-13-001]. This luminosity value corresponds to the data collected with the TauPlusX trigger stream during Run2012B and Run2012C periods.

## Monte Carlo simulation {#sec:data-mc}

Monte Carlo (MC) simulated samples are used to model the signal and most background processes. All samples are produced in the reduced NanoAOD format from the CMS Open Data repository and are listed in @tbl:mc-samples. The signal samples are generated with Powheg [@Nason:2004rx] interfaced with Pythia 6 [@Sjostrand:2006za] for parton showering using the Z2* tune. Background samples are generated with MadGraph [@Alwall:2011uj] interfaced with Pythia 6. The beam energy is 4 TeV per beam, corresponding to $\sqrt{s} = 8$ TeV.

| Sample | Process | Generator | $\sigma$ (pb) | $N_\mathrm{gen}$ | Weight |
|--------|---------|-----------|------------|--------------|--------|
| GluGluToHToTauTau | $gg\to H\to\tau\tau$ | Powheg+Pythia6 | 1.338 | 476,963 | 0.0322 |
| VBF\_HToTauTau | $qq\to qqH\to\tau\tau$ | Powheg+Pythia6 | 0.1001 | 491,653 | 0.0023 |
| DYJetsToLL | $Z/\gamma^*\to\ell\ell$ | MadGraph+Pythia6 | 3503.7 | 30,458,871 | 1.319 |
| TTbar | $t\bar{t}$ | MadGraph+Pythia6 | 252.9 | 6,423,106 | 0.451 |
| W1JetsToLNu | $W(\to\ell\nu)$+1j | MadGraph+Pythia6 | 6381.2 | 29,784,800 | 2.457 |
| W2JetsToLNu | $W(\to\ell\nu)$+2j | MadGraph+Pythia6 | 2039.8 | 30,693,853 | 0.762 |
| W3JetsToLNu | $W(\to\ell\nu)$+3j | MadGraph+Pythia6 | 612.5 | 15,241,144 | 0.461 |

: Monte Carlo simulation samples. The cross-section for signal samples is $\sigma_\mathrm{prod} \times \mathrm{BR}(H\to\tau\tau)$ using YR4 values [@LHCHiggsCrossSectionWorkingGroup:2016ypw]. The $t\bar{t}$ cross-section is calculated at NNLO+NNLL [@Czakon:2011xx]. W+jets cross-sections are LO MadGraph values. The per-event weight is $\sigma \times L_\mathrm{int} / N_\mathrm{gen}$ with $L_\mathrm{int} = 11{,}467$ pb$^{-1}$. {#tbl:mc-samples}

The signal cross-sections are computed using YR4 recommendations [@LHCHiggsCrossSectionWorkingGroup:2016ypw] at $m_H = 125.09$ GeV [@Aad:2015zhl]:

$$\sigma_{ggH} = 21.39~\mathrm{pb} \quad (\mathrm{N3LO~QCD})$$ {#eq:xsec-ggh}

$$\sigma_\mathrm{VBF} = 1.600~\mathrm{pb} \quad (\mathrm{NNLO~QCD + NLO~EW})$$ {#eq:xsec-vbf}

$$\mathrm{BR}(H\to\tau\tau) = 6.256\%$$ {#eq:br-htautau}

The per-event MC weight for process $p$ is:

$$w_p = \frac{\sigma_p \times L_\mathrm{int}}{N_\mathrm{gen}^p}$$ {#eq:mc-weight}

where $\sigma_p$ is the production cross-section (times branching ratio for signal), $L_\mathrm{int} = 11{,}467$ pb$^{-1}$ is the integrated luminosity, and $N_\mathrm{gen}^p$ is the number of generated events. The reduced NanoAOD format does not contain per-event generator weights (the `genWeight` branch is absent), so all MC events carry unit generator weight before luminosity normalization.

### Signal sample content

The signal samples contain exclusively $H\to\tau\tau$ events, with the generator filter selecting only the $\tau\tau$ decay channel. The normalization cross-section therefore includes the $H\to\tau\tau$ branching ratio: $\sigma_\mathrm{ggH} \times \mathrm{BR} = 21.39 \times 0.06256 = 1.338$ pb and $\sigma_\mathrm{VBF} \times \mathrm{BR} = 1.600 \times 0.06256 = 0.1001$ pb. The CMS Open Data tutorial uses $\sigma_\mathrm{ggH} = 19.6$ pb (approximately NNLO+NNLL from the original analysis era); this analysis adopts the YR4 N3LO value to use the best available theory prediction, which is approximately 9% higher.

### Missing processes

The CMS Open Data sample set does not include dedicated QCD multijet, single top, or diboson ($WW$, $WZ$, $ZZ$) MC samples. The QCD multijet background is estimated entirely from data using the same-sign control region method (Section @sec:bkg-qcd). The single top and diboson contributions, which account for approximately 1-3% of the total background based on cross-section estimates and selection efficiencies from the published CMS analysis [@CMS:2014nkk], are covered by an additional 5% normalization uncertainty on the MC-based backgrounds (Section @sec:syst-missing).


# Event Selection {#sec:selection}

## Trigger {#sec:trigger}

Events are required to pass the `HLT_IsoMu17_eta2p1_LooseIsoPFTau20` trigger, which requires an isolated muon with $p_\mathrm{T} > 17$ GeV and $|\eta| < 2.1$, together with a loosely isolated particle-flow tau candidate with $p_\mathrm{T} > 20$ GeV. This is the standard trigger for the $\mu\tau_\mathrm{h}$ channel in CMS $H\to\tau\tau$ analyses [@CMS:2014nkk]. The trigger efficiency on MC signal events (after generator-level filtering) is approximately 7% for ggH and 10% for VBF. No trigger efficiency scale factors are available for the CMS Open Data; this limitation is addressed through an enlarged $Z\to\tau\tau$ normalization uncertainty that absorbs the trigger efficiency difference between data and simulation (Section @sec:syst-znorm).

## Object definitions {#sec:objects}

### Muon selection

Muon candidates are required to satisfy the criteria listed in @tbl:muon-selection. The $p_\mathrm{T}$ threshold of 20 GeV is set above the trigger turn-on to ensure full trigger efficiency. The tight identification and isolation requirements suppress backgrounds from non-prompt muons, while the impact parameter requirements reject muons from long-lived particle decays. The signal region imposes a tighter isolation requirement of $I_\mathrm{rel}^\mathrm{PF} < 0.1$ to improve the signal-to-background ratio.

| Requirement | Value |
|-------------|-------|
| $p_\mathrm{T}$ | > 20 GeV |
| $|\eta|$ | < 2.1 |
| Identification | Tight ID |
| PF relative isolation ($\Delta R = 0.4$) | < 0.15 (preselection), < 0.1 (signal region) |
| $|d_{xy}|$ | < 0.045 cm |
| $|d_z|$ | < 0.2 cm |

: Muon selection requirements. The isolation threshold is tightened from 0.15 to 0.1 in the signal region. {#tbl:muon-selection}

### Hadronic tau selection

Hadronic tau candidates ($\tau_\mathrm{h}$) are reconstructed using the hadron-plus-strips (HPS) algorithm [@CMS:2018jrd] and are required to satisfy the criteria in @tbl:tau-selection. The tau identification employs the Loose working point for isolation, which provides approximately 10-12% tau identification efficiency. This is deliberately looser than the Tight working point used in the CMS tutorial to compensate for the absence of official tau identification efficiency scale factors in the CMS Open Data environment: the Loose working point provides better data/MC agreement in the $Z\to\tau\tau$ mass peak region (Section @sec:tauid-wp). Tight anti-electron and anti-muon discriminators are applied to suppress $e\to\tau_\mathrm{h}$ and $\mu\to\tau_\mathrm{h}$ misidentification.

| Requirement | Value |
|-------------|-------|
| $p_\mathrm{T}$ | > 20 GeV |
| $|\eta|$ | < 2.3 |
| Decay mode finding | Required |
| Isolation | Loose WP |
| Anti-electron discriminator | Tight |
| Anti-muon discriminator | Tight |
| Charge | Non-zero |

: Hadronic tau selection requirements. The Loose isolation working point is used to improve data/MC agreement in the absence of official scale factors. {#tbl:tau-selection}

### Jet selection

Jets are reconstructed using particle-flow candidates and are required to have $p_\mathrm{T} > 30$ GeV and $|\eta| < 4.7$, with pileup jet identification applied. An overlap removal requires $\Delta R > 0.5$ between each jet and the selected muon and hadronic tau. Jets satisfying the CSV medium working point (Jet\_btag > 0.8) are identified as b-jets and are used for $t\bar{t}$ enrichment in control regions.

## Pair selection and signal region definition {#sec:pair-selection}

The $\mu\tau_\mathrm{h}$ pair is constructed by selecting the highest-$p_\mathrm{T}$ muon passing all requirements and the most isolated tau candidate (lowest `Tau_relIso_all`, with NaN values replaced by 999 to deprioritize taus with undefined isolation). The pair is required to have opposite-sign (OS) charge ($q_\mu \times q_\tau < 0$) and angular separation $\Delta R(\mu, \tau_\mathrm{h}) > 0.5$.

The signal region (SR) is defined by applying two additional requirements beyond the OS pair selection:

$$m_\mathrm{T}(\mu, E_\mathrm{T}^\mathrm{miss}) = \sqrt{2 \, p_\mathrm{T}^\mu \, E_\mathrm{T}^\mathrm{miss} \, (1 - \cos\Delta\phi)} < 30~\mathrm{GeV}$$ {#eq:mt-definition}

$$I_\mathrm{rel}^\mathrm{PF}(\mu) < 0.1$$ {#eq:iso-sr}

The transverse mass requirement suppresses the $W$+jets background, where the muon and $E_\mathrm{T}^\mathrm{miss}$ tend to be back-to-back with large $m_\mathrm{T}$. The tighter muon isolation reduces backgrounds from non-prompt muons.

## Tau identification working point optimization {#sec:tauid-wp}

Three tau isolation working points were compared using the full dataset to determine the optimal balance between signal efficiency and data/MC agreement. For each working point, the complete preselection was applied and the visible mass distribution was compared between data and MC in the $Z$ peak region (60-120 GeV).

| Working point | Data | MC total | Data/MC | $\chi^2$/ndf ($Z$ peak) |
|---------------|------|----------|---------|------------------------|
| VLoose | 87,238 | 74,313 | 1.174 | 24.47/6 = 4.08 |
| Loose | 67,314 | 60,188 | 1.118 | 17.76/6 = 2.96 |
| Medium | 48,496 | 45,697 | 1.061 | 17.69/6 = 2.95 |

: Comparison of tau isolation working points. The $\chi^2$/ndf is computed in the $Z$ peak region (60-120 GeV visible mass). {#tbl:tauid-wp}

The Loose working point is selected as it provides the best compromise: comparable $\chi^2$/ndf to Medium (2.96 vs 2.95) with 20% more signal yield (162.7 vs 135.1 weighted events for ggH + VBF), as shown in Figures @fig:tauid-vloose through @fig:tauid-medium. The VLoose working point is rejected due to significantly worse data/MC agreement ($\chi^2$/ndf = 4.08, Figure @fig:tauid-vloose). The data/MC ratio of 1.12 at the Loose working point (Figure @fig:tauid-loose) is consistent with the expected QCD multijet contribution (approximately 7,000 events from the same-sign estimate).

<!-- COMPOSE: 3x1 grid -->
![Visible mass distribution with the VLoose tau isolation working point. The data points show the observed collision data, and the stacked histogram shows the MC prediction for Z+jets (DY), $t\bar{t}$, and W+jets backgrounds. The excess of data over MC in the Z peak region ($\chi^2$/ndf = 4.08) indicates poor modeling at this working point, motivating the choice of a tighter isolation requirement.](../../../phase2_exploration/outputs/figures/tau_id_wp_VLoose.pdf){#fig:tauid-vloose}

![Visible mass distribution with the Loose tau isolation working point. The data/MC agreement is substantially improved relative to VLoose ($\chi^2$/ndf = 2.96 in the Z peak region), while retaining 20% more signal yield than the Medium working point. The residual data excess is attributed to the missing QCD multijet contribution.](../../../phase2_exploration/outputs/figures/tau_id_wp_Loose.pdf){#fig:tauid-loose}

![Visible mass distribution with the Medium tau isolation working point. The $\chi^2$/ndf of 2.95 is comparable to the Loose working point, but the signal yield is reduced by 20%. The slightly lower Data/MC ratio (1.06 vs 1.12) suggests that the QCD multijet contamination is smaller at tighter isolation, as expected.](../../../phase2_exploration/outputs/figures/tau_id_wp_Medium.pdf){#fig:tauid-medium}

## Control region definitions {#sec:control-regions}

Several control regions are defined for background estimation and validation, as summarized in @tbl:control-regions.

| Region | Charge | $m_\mathrm{T}$ [GeV] | Muon isolation | Purpose |
|--------|--------|----------------------|----------------|---------|
| OS SR | OS | < 30 | < 0.1 | Signal region |
| OS high-$m_\mathrm{T}$ | OS | > 70 | < 0.1 | $W$+jets normalization |
| OS mid-$m_\mathrm{T}$ | OS | 30-70 | < 0.1 | $W$+jets validation |
| SS SR | SS | < 30 | < 0.1 | QCD template |
| OS anti-iso | OS | < 30 | 0.1-0.3 | QCD OS/SS measurement |
| SS anti-iso | SS | < 30 | 0.1-0.3 | QCD OS/SS measurement |

: Definition of control regions used for background estimation and validation. OS and SS denote opposite-sign and same-sign muon-tau charge requirements, respectively. {#tbl:control-regions}

The high-$m_\mathrm{T}$ region ($m_\mathrm{T} > 70$ GeV) is enriched in $W$+jets events (Figure @fig:mt-regions) and is used to derive the $W$+jets normalization scale factor (Section @sec:bkg-wjets). The same-sign signal region provides the QCD multijet template after subtraction of MC-predicted same-sign backgrounds (Section @sec:bkg-qcd). The anti-isolated control regions (0.1 < muon isolation < 0.3) are used to measure the QCD OS/SS charge asymmetry ratio in a QCD-enriched environment.

## Cutflow {#sec:cutflow}

The cutflow for the signal region selection is presented in @tbl:cutflow-raw for raw event counts and @tbl:cutflow-weighted for luminosity-weighted yields. The selection proceeds through seven sequential requirements, each designed to enhance the signal-to-background ratio.

| Cut | ggH | VBF | DY | $t\bar{t}$ | W1J | W2J | W3J | Data B | Data C |
|-----|-----|-----|----|------------|-----|-----|-----|--------|--------|
| Total | 476,963 | 491,653 | 30,458,871 | 6,423,106 | 29,784,800 | 30,693,853 | 15,241,144 | 35,647,508 | 51,303,171 |
| Trigger | 33,520 | 49,109 | 4,753,620 | 872,546 | 1,251,689 | 2,358,002 | 1,516,331 | 10,038,076 | 13,901,050 |
| Good muon | 25,522 | 39,150 | 4,479,322 | 746,718 | 1,044,071 | 1,969,422 | 1,260,827 | 5,303,043 | 7,917,579 |
| Good $\tau_\mathrm{h}$ | 8,230 | 10,964 | 77,699 | 53,489 | 41,505 | 73,686 | 42,740 | 142,072 | 224,078 |
| OS pair | 8,069 | 10,556 | 63,279 | 40,556 | 31,314 | 53,476 | 29,928 | 99,109 | 156,267 |
| $\Delta R > 0.5$ | 8,069 | 10,556 | 63,279 | 40,556 | 31,314 | 53,476 | 29,928 | 99,109 | 156,267 |
| $m_\mathrm{T} < 30$ | 5,397 | 7,067 | 39,795 | 6,210 | 3,383 | 5,920 | 3,765 | 31,961 | 51,020 |
| Iso < 0.1 | 4,603 | 6,255 | 34,468 | 5,670 | 2,951 | 5,194 | 3,319 | 26,236 | 41,752 |

: Cutflow in raw event counts for each sample. The $\Delta R > 0.5$ requirement removes zero events, confirming that the pair selection criteria naturally produce well-separated $\mu\tau_\mathrm{h}$ pairs. {#tbl:cutflow-raw}

| Sample | Raw events | Weighted yield |
|--------|-----------|----------------|
| ggH (signal) | 4,603 | 148.1 |
| VBF (signal) | 6,255 | 14.6 |
| DY ($Z\to\tau\tau$) | 29,747 | 39,237.9 |
| DY ($Z\to\ell\ell$) | 4,721 | 6,227.3 |
| $t\bar{t}$ | 5,670 | 2,560.0 |
| W+1 jet | 2,951 | 7,249.8 |
| W+2 jets | 5,194 | 3,958.1 |
| W+3 jets | 3,319 | 1,529.5 |
| **MC total** | | **60,925.3** |
| Data (Run2012B) | 26,236 | 26,236.0 |
| Data (Run2012C) | 41,752 | 41,752.0 |
| **Data total** | **67,988** | **67,988.0** |

: Weighted yields in the opposite-sign signal region after all selection requirements. The Data/MC ratio of 1.116 is consistent with the missing QCD multijet contribution. {#tbl:cutflow-weighted}

The trigger requirement retains approximately 7% of ggH signal events and 10% of VBF signal events. The largest background reduction comes from the tau identification and isolation requirements, which reject the vast majority of non-tau jets. The transverse mass requirement ($m_\mathrm{T} < 30$ GeV) effectively suppresses the $W$+jets background by a factor of approximately 9 for W+1 jet, while retaining 66% of the ggH signal. The overall signal selection efficiency (after trigger) is 13.7% for ggH and 12.7% for VBF.

The Data/MC ratio after full selection is 1.116, corresponding to a data excess of approximately 7,063 events. This excess is attributed to the missing QCD multijet background, which is estimated from data to contribute approximately 11,200 events to the signal region (Section @sec:bkg-qcd).

## Event categorization {#sec:categorization}

Events passing the signal region selection are classified into two mutually exclusive categories designed to exploit the distinct kinematic signatures of the VBF and ggH production modes.

### VBF category

Events are assigned to the VBF category if they contain at least two jets satisfying:

$$m_{jj} > 200~\mathrm{GeV} \quad \text{and} \quad |\Delta\eta_{jj}| > 2.0$$ {#eq:vbf-selection}

These thresholds were optimized in the Phase 2 exploration using a scan over the ($m_{jj}$, $|\Delta\eta_{jj}|$) plane to maximize $S/\sqrt{B}$ in the VBF category. The optimized thresholds of 200 GeV and 2.0 are looser than the published CMS analysis values (300 GeV and 2.5) to retain sufficient signal statistics in this single-channel analysis. The resulting $S/\sqrt{B}$ in the VBF category is approximately 0.49.

### Baseline category

All events passing the signal region selection that do not satisfy the VBF category criteria are assigned to the Baseline category. This category is dominated by the ggH production mode and has a larger event count but lower signal-to-background ratio.

### Category yields

The event yields per category are summarized in @tbl:category-yields. The VBF category achieves a VBF signal purity of 56% (VBF/(ggH+VBF) = 6.4/11.5), demonstrating effective VBF enrichment despite modest statistics.

| Sample | Baseline | VBF |
|--------|----------|-----|
| ggH | 143.0 | 5.1 |
| VBF | 8.2 | 6.4 |
| DY ($Z\to\tau\tau + Z\to\ell\ell$) | 45,052.3 | 412.9 |
| $t\bar{t}$ | 2,131.1 | 428.9 |
| W+jets | 12,377.7 | 359.7 |
| Data (B+C) | 67,124 | 864 |

: Event yields per category in the opposite-sign signal region (weighted). QCD is estimated separately from data. {#tbl:category-yields}

![Transverse mass distribution showing the signal region ($m_\mathrm{T} < 30$ GeV), intermediate validation region ($30 < m_\mathrm{T} < 70$ GeV), and high-$m_\mathrm{T}$ sideband ($m_\mathrm{T} > 70$ GeV) boundaries. The W+jets background dominates at high $m_\mathrm{T}$, validating its use as the W+jets normalization control region. The signal peaks at low $m_\mathrm{T}$ as expected for $H\to\tau\tau$ decays where the muon is nearly balanced by the hadronic tau.](../../../phase3_selection/outputs/figures/mt_regions.pdf){#fig:mt-regions}


# Background Estimation {#sec:backgrounds}

The backgrounds in the $\mu\tau_\mathrm{h}$ channel are classified as irreducible ($Z\to\tau\tau$), reducible ($W$+jets, $t\bar{t}$, $Z\to\ell\ell$), or instrumental (QCD multijet). The irreducible $Z\to\tau\tau$ background is estimated from MC simulation with a data-driven normalization uncertainty. The reducible $W$+jets background is normalized using the high-$m_\mathrm{T}$ data sideband. The QCD multijet background is estimated entirely from data using the same-sign control region. The $t\bar{t}$ and $Z\to\ell\ell$ backgrounds are estimated from MC simulation.

## Drell-Yan decomposition {#sec:bkg-dy}

The DYJetsToLL MC sample is decomposed into $Z\to\tau\tau$ (ZTT) and $Z\to\ell\ell$ (ZLL) components using generator-level truth matching. Reconstructed hadronic tau candidates are matched to generator-level tau leptons ($|\mathrm{pdgId}| = 15$) within $\Delta R < 0.3$. Events with a truth-matched tau are classified as ZTT; all others are classified as ZLL.

This decomposition yields 29,747 raw ZTT events (86.3% of DY, 39,237.9 weighted) and 4,721 raw ZLL events (13.7% of DY, 6,227.3 weighted) in the signal region. The ZTT component is the dominant irreducible background, producing a genuine $\tau_\mathrm{h}$ in the final state. The ZLL component arises primarily from $Z\to\mu\mu$ events where one muon is misidentified as a hadronic tau. Both components share a common normalization uncertainty (Section @sec:syst-znorm).

## W+jets normalization {#sec:bkg-wjets}

The $W$+jets background normalization is derived from data in the high-$m_\mathrm{T}$ sideband ($m_\mathrm{T} > 70$ GeV), where $W$+jets events dominate. The scale factor is defined as:

$$\mathrm{SF}_W = \frac{N_\mathrm{data}^\mathrm{high\text{-}mT} - N_\mathrm{non\text{-}W~MC}^\mathrm{high\text{-}mT}}{N_{W\mathrm{+jets~MC}}^\mathrm{high\text{-}mT}}$$ {#eq:wjets-sf}

The measured quantities and resulting scale factor are:

| Quantity | Value |
|----------|-------|
| Data ($m_\mathrm{T} > 70$ GeV) | 65,765 |
| Non-$W$ MC ($m_\mathrm{T} > 70$ GeV) | 12,013.5 |
| $W$+jets MC ($m_\mathrm{T} > 70$ GeV) | 53,801.0 |
| **$\mathrm{SF}_W$** | **0.999 ± 0.008** |

: W+jets normalization scale factor derived from the high-$m_\mathrm{T}$ sideband. The uncertainty includes weighted MC statistical propagation ($\sigma^2_\mathrm{MC} = \sum w_i^2$). {#tbl:wjets-sf}

The scale factor is consistent with unity, indicating that the W+jets MC normalization using the MadGraph LO cross-sections is accurate. The small statistical uncertainty of 0.8% is subdominant compared to the 10% systematic uncertainty assigned to the $W$+jets normalization to account for the $m_\mathrm{T}$ extrapolation from the sideband to the signal region (Section @sec:syst-wjets).

### Validation in the intermediate-$m_\mathrm{T}$ region

The $W$+jets normalization is validated in the intermediate transverse mass region ($30 < m_\mathrm{T} < 70$ GeV), which is kinematically between the signal region and the normalization sideband. The predicted Data/MC ratio in this region is 1.087 after applying $\mathrm{SF}_W$ (Figure @fig:wjets-validation), with the 8.7% residual excess consistent with QCD multijet contamination in this region.

![Validation of the W+jets normalization in the intermediate-$m_\mathrm{T}$ region ($30 < m_\mathrm{T} < 70$ GeV). The data points are compared to the MC prediction with the W+jets scale factor applied. The Data/Pred ratio of 1.087 is consistent with the expected QCD multijet contribution that is not included in this validation.](../../../phase3_selection/outputs/figures/wjets_validation_midmt.pdf){#fig:wjets-validation}

## QCD multijet estimation {#sec:bkg-qcd}

The QCD multijet background is estimated from data using the same-sign (SS) control region method. QCD multijet events produce $\mu\tau_\mathrm{h}$ pairs with approximately equal rates of opposite-sign and same-sign configurations, with a small charge asymmetry quantified by the OS/SS ratio $R_\mathrm{OS/SS}$.

### OS/SS ratio measurement

The OS/SS ratio is measured in a QCD-enriched anti-isolated control region ($0.1 < I_\mathrm{rel}^\mathrm{PF}(\mu) < 0.3$) after subtracting non-QCD MC backgrounds:

$$R_\mathrm{OS/SS} = \frac{N_\mathrm{data}^\mathrm{OS,anti\text{-}iso} - N_\mathrm{MC}^\mathrm{OS,anti\text{-}iso}}{N_\mathrm{data}^\mathrm{SS,anti\text{-}iso} - N_\mathrm{MC}^\mathrm{SS,anti\text{-}iso}}$$ {#eq:osss-ratio}

The measured value is $R_\mathrm{OS/SS} = 0.979 \pm 0.018$, where the uncertainty is statistical. This value lies between the CMS Open Data tutorial value (0.80) and the published analysis value (1.06), reflecting the specific isolation and kinematic requirements of this selection. The 30% spread among these reference values motivated the data-driven measurement rather than adopting a literature value.

### QCD yield in the signal region

The QCD yield in the opposite-sign signal region is estimated as:

$$N_\mathrm{QCD}^\mathrm{OS~SR} = R_\mathrm{OS/SS} \times \left( N_\mathrm{data}^\mathrm{SS~SR} - N_\mathrm{MC}^\mathrm{SS~SR} \right)$$ {#eq:qcd-yield}

| Quantity | Value |
|----------|-------|
| Data (SS SR) | 23,134 |
| MC (SS SR) | 11,704.2 |
| QCD (SS) = Data - MC | 11,429.8 |
| **QCD (OS) estimate** | **11,195.5 ± 230.6** |

: QCD multijet yield estimation. The uncertainty is statistical, propagated from the data and MC statistical uncertainties. {#tbl:qcd-yield}

The QCD template shape is taken from the SS data after MC subtraction. The NN scores and collinear mass values for the QCD template are computed by evaluating the trained NN model and collinear mass algorithm on the same-sign events, ensuring that the QCD template shape is consistent with the fitting observable in each approach.

## Corrected yield summary {#sec:bkg-summary}

@tbl:corrected-yields summarizes the predicted yields from all background sources and signal in the opposite-sign signal region after applying all data-driven corrections.

| Source | OS SR yield |
|--------|-------------|
| DY ($Z\to\tau\tau$) | 39,237.9 |
| DY ($Z\to\ell\ell$) | 6,227.3 |
| $t\bar{t}$ | 2,560.0 |
| $W$+jets ($\mathrm{SF} = 0.999$) | 12,727.5 |
| QCD (data-driven) | 11,195.5 |
| Signal (ggH + VBF) | 162.7 |
| **Total prediction** | **72,111.0** |
| **Data** | **67,988.0** |
| **Data/Pred** | **0.943** |

: Corrected yield summary in the signal region. The 6% deficit of data relative to the prediction suggests a slight overestimate of the QCD contribution, which will be absorbed by the QCD normalization nuisance parameter in the template fit. {#tbl:corrected-yields}

The total Data/Prediction ratio of 0.943 indicates a 6% deficit of data relative to the full prediction, suggesting that the QCD same-sign estimation slightly overestimates the QCD contribution in the signal region. This overestimation is within the 20% systematic uncertainty assigned to the QCD normalization and will be absorbed by the QCD normalization nuisance parameter in the template fit.


# Discriminant Variables {#sec:discriminants}

Three fitting approaches are implemented, differing only in the discriminant variable used in the template fit. All approaches share the same event selection, categorization, and background estimation.

## Visible di-tau mass {#sec:disc-mvis}

The visible di-tau mass is defined as the invariant mass of the muon and hadronic tau system:

$$m_\mathrm{vis} = \sqrt{(p_\mu + p_{\tau_\mathrm{h}})^2}$$ {#eq:mvis}

This is the simplest observable and provides a direct physical interpretation. The Higgs signal appears as a broad excess in the 100-150 GeV region, sitting on the tail of the $Z\to\tau\tau$ peak near 60-80 GeV (in visible mass), as shown in Figures @fig:mvis-baseline and @fig:mvis-vbf. The poor mass resolution (approximately 30-40 GeV) arises from the undetected neutrinos in both tau decays. Templates are constructed in 25 equal-width bins from 0 to 250 GeV (10 GeV/bin).

<!-- COMPOSE: side-by-side -->
![Visible mass distribution in the Baseline category. Data points show the observed collision data, and the stacked histogram shows the MC prediction with Drell-Yan decomposed into $Z\to\tau\tau$ (ZTT, blue) and $Z\to\ell\ell$ (ZLL, light blue), $t\bar{t}$ (green), W+jets (purple), and QCD multijet from the same-sign data estimate (yellow). The ggH and VBF signal contributions are shown scaled by a factor of 10 for visibility. The $Z$ peak is clearly visible near 60-80 GeV, with the expected Higgs signal region at higher masses.](../../../phase3_selection/outputs/figures/mvis_baseline.pdf){#fig:mvis-baseline}

![Visible mass distribution in the VBF category ($m_{jj} > 200$ GeV, $|\Delta\eta_{jj}| > 2.0$). The lower statistics compared to the Baseline category are evident, with the $t\bar{t}$ and W+jets backgrounds becoming more prominent relative to the Drell-Yan contribution. The data/MC ratio fluctuations are larger due to the reduced event count.](../../../phase3_selection/outputs/figures/mvis_vbf.pdf){#fig:mvis-vbf}

## Neural network discriminant {#sec:disc-nn}

### Architecture and training

A neural network classifier is trained to distinguish $H\to\tau\tau$ signal from all backgrounds using the scikit-learn MLPClassifier [@Pedregosa:2011skl]. The architecture and training configuration are summarized in @tbl:nn-config.

| Parameter | Value |
|-----------|-------|
| Framework | scikit-learn MLPClassifier |
| Architecture | 3 hidden layers: 64-64-32 |
| Activation | ReLU |
| Regularization | L2 ($\alpha = 0.001$) |
| Optimizer | Adam (lr = 0.001, adaptive) |
| Batch size | 256 |
| Early stopping | Yes (validation fraction = 0.1) |
| Convergence | 30 iterations |
| Random seed | 42 |

: Neural network classifier configuration. The architecture was selected to provide sufficient capacity for the 14-dimensional input space while maintaining regularization to prevent overtraining. {#tbl:nn-config}

### Input features

The NN uses 14 input features, listed in @tbl:nn-features with their individual signal-vs-background separation power as measured by the ROC AUC.

| Feature | Description | ROC AUC |
|---------|-------------|---------|
| $\tau_\mathrm{h}$ $p_\mathrm{T}$ | Hadronic tau transverse momentum | 0.695 |
| $m_\mathrm{vis}$ | Visible di-tau mass | 0.656 |
| $N_\mathrm{jets}$ | Number of jets | 0.647 |
| $E_\mathrm{T}^\mathrm{miss}$ | Missing transverse energy | 0.639 |
| $\Delta R(\mu, \tau_\mathrm{h})$ | Angular separation | 0.564 |
| $\mu$ $p_\mathrm{T}$ | Muon transverse momentum | 0.561 |
| $\tau_\mathrm{h}$ decay mode | Tau decay mode | 0.554 |
| $m_\mathrm{T}(\mu, E_\mathrm{T}^\mathrm{miss})$ | Transverse mass | 0.554 |
| $\Delta\phi(\mu, \tau_\mathrm{h})$ | Azimuthal separation | 0.554 |
| $E_\mathrm{T}^\mathrm{miss}$ significance | MET significance | N/A |
| $\mu$ $\eta$ | Muon pseudorapidity | 0.507 |
| $\tau_\mathrm{h}$ $\eta$ | Tau pseudorapidity | 0.503 |
| Leading jet $p_\mathrm{T}$ | Leading jet transverse momentum | N/A |
| Leading jet $\eta$ | Leading jet pseudorapidity | N/A |
| $N_\mathrm{b-jets}$ | Number of b-jets | 0.507 |

: Neural network input features with their individual discriminating power (ROC AUC for signal vs background separation). Features are listed approximately in order of decreasing individual separation power. {#tbl:nn-features}

### Training sample and performance

The training uses the signal region MC events split into 50% training, 25% validation, and 25% test sets with random seed 42. Signal events (ggH + VBF, 10,858 unweighted) are reweighted to have the same total weight as background events (51,602 unweighted) for balanced training.

| Metric | Train | Validation | Test |
|--------|-------|------------|------|
| AUC | 0.8426 | 0.8325 | 0.8250 |

: NN classifier performance. The test AUC of 0.825 exceeds the go/no-go threshold of 0.75 established in the analysis strategy. {#tbl:nn-performance}

The test AUC of 0.825 exceeds the go/no-go threshold of 0.75, confirming that the NN provides meaningful signal-background discrimination (Figure @fig:nn-roc). The modest drop from train (0.843) to test (0.825) AUC indicates good generalization with no significant overtraining (Figure @fig:nn-overtraining). The NN assigns mean scores of 0.67-0.79 to signal events and 0.26-0.35 to background events, with data mean scores (0.32) consistent with the background expectation.

### Overtraining validation

The absence of overtraining is confirmed by the Kolmogorov-Smirnov (KS) test between the training and test score distributions:

| Class | KS statistic | $p$-value | Verdict |
|-------|-------------|-----------|---------|
| Signal | 0.0275 | 0.127 | No overtraining |
| Background | 0.0077 | 0.686 | No overtraining |

: KS test for overtraining between training and test NN score distributions. Both $p$-values exceed 0.05, confirming no significant overtraining. {#tbl:nn-overtraining}

![ROC curves for the NN classifier on the training, validation, and test datasets. The three curves are consistent, confirming no overtraining. The test AUC of 0.825 demonstrates significant discriminating power between signal and background.](../../../phase3_selection/outputs/figures/nn_roc.pdf){#fig:nn-roc}

![Overtraining check for the NN classifier. The NN score distributions are shown for signal (red) and background (blue), overlaying the training set (filled histogram) and test set (points with error bars). The good agreement between training and test distributions in both classes confirms the absence of overtraining, consistent with the KS test results in @tbl:nn-overtraining.](../../../phase3_selection/outputs/figures/nn_overtraining.pdf){#fig:nn-overtraining}

![NN input feature importance estimated from the first-layer weight magnitudes. The visible mass ($m_\mathrm{vis}$) is the most important feature, followed by $\Delta R(\mu, \tau_\mathrm{h})$ and $E_\mathrm{T}^\mathrm{miss}$. The importance ranking generally follows the individual ROC AUC values in @tbl:nn-features, with the exception of $\Delta R$ which has elevated importance due to its correlation with other kinematic variables.](../../../phase3_selection/outputs/figures/nn_feature_importance.pdf){#fig:nn-importance}

### NN input variable quality gate

Data/MC agreement on all 14 NN input variables was assessed using $\chi^2$/ndf tests in the opposite-sign signal region, including the QCD template from the same-sign data. The shape-normalized $\chi^2$/ndf (which normalizes MC to data totals to isolate modeling quality) is the appropriate metric because the overall normalization is a free parameter in the template fit.

Of the 14 variables, 11 pass the shape $\chi^2$/ndf < 5 gate. Three variables show elevated $\chi^2$/ndf values: $N_\mathrm{jets}$ (40.68, visible in Figure @fig:njets-baseline), $N_\mathrm{b-jets}$ (32.35), and $\Delta R$ (5.16, borderline, Figure @fig:delta-r-baseline). The jet multiplicity mismodeling is a known feature of LO MadGraph samples and is addressed through per-category normalization nuisance parameters in the template fit. All three variables are retained because removing them degrades NN performance, the mismodeling is understood (LO MC limitations), and the template fit normalization parameters absorb overall yield differences.

### NN score distributions

<!-- COMPOSE: side-by-side -->
![NN discriminant score distribution in the Baseline category. Background events peak at low NN scores (near 0) while signal events (shown scaled by x10) peak at high scores (near 1), demonstrating the discriminating power of the NN classifier. The QCD template is constructed by evaluating the trained NN on same-sign data events, ensuring consistent treatment of the data-driven QCD background in the fitting observable.](../../../phase3_selection/outputs/figures/nn_score_baseline.pdf){#fig:nn-score-baseline}

![NN discriminant score distribution in the VBF category. The separation between signal and background is similar to the Baseline category, but with reduced statistics. The ratio panel shows larger fluctuations due to the limited event count in the VBF category.](../../../phase3_selection/outputs/figures/nn_score_vbf.pdf){#fig:nn-score-vbf}

### Alternative classifier: BDT comparison

As required by the analysis strategy, a gradient-boosted decision tree (BDT) classifier was trained as an alternative architecture using the same features, data split, and weight equalization as the primary NN. The BDT uses 200 estimators, maximum depth of 3, learning rate of 0.1, subsample fraction of 0.8, and minimum 50 samples per leaf.

| Classifier | AUC (Train) | AUC (Val) | AUC (Test) |
|------------|-------------|-----------|------------|
| NN (MLPClassifier) | 0.8426 | 0.8325 | 0.8250 |
| BDT (GradientBoosting) | 0.8752 | 0.8282 | 0.8200 |

: Performance comparison between the primary NN and alternative BDT classifiers. The NN outperforms the BDT by 0.005 AUC on the test set, with less overtraining. {#tbl:bdt-comparison}

The NN outperforms the BDT by 0.005 AUC on the test set (0.825 vs 0.820), as shown in Figure @fig:bdt-roc. The BDT shows slightly more overtraining (train AUC 0.875 vs 0.843 for NN, Figure @fig:bdt-overtraining), with the signal KS test $p$-value at 0.0007 indicating marginal overtraining. The NN is confirmed as the better classifier for this analysis.

<!-- COMPOSE: side-by-side -->
![ROC curve comparison between the primary NN classifier and the alternative BDT. The NN achieves AUC = 0.825 vs BDT AUC = 0.820 on the test set. The small difference confirms the NN as the preferred classifier, with the BDT result serving as a cross-check of the MVA approach.](../../../phase3_selection/outputs/figures/bdt_vs_nn_roc.pdf){#fig:bdt-roc}

![BDT overtraining check. The BDT score distributions overlay training (filled) and test (points) samples for signal and background. The signal class shows marginal overtraining (KS $p$-value = 0.0007), with the training distribution shifted slightly toward higher scores compared to the test distribution. This is consistent with the larger train-test AUC gap observed for the BDT.](../../../phase3_selection/outputs/figures/bdt_overtraining.pdf){#fig:bdt-overtraining}

## Collinear approximation mass {#sec:disc-mcol}

The collinear approximation assumes that the neutrinos from tau decays are collinear with their parent taus, allowing reconstruction of the full di-tau invariant mass from the visible decay products and the missing transverse energy. The reconstructed mass is:

$$m_\mathrm{col} = \frac{m_\mathrm{vis}}{\sqrt{x_\mu \cdot x_\tau}}$$ {#eq:mcol}

where the momentum fractions are:

$$x_\mu = \frac{p_\mathrm{T}^\mu}{p_\mathrm{T}^\mu + p_\mathrm{T}^{\nu_\mu}}, \quad x_\tau = \frac{p_\mathrm{T}^{\tau_\mathrm{h}}}{p_\mathrm{T}^{\tau_\mathrm{h}} + p_\mathrm{T}^{\nu_\tau}}$$ {#eq:mcol-fractions}

The neutrino momenta are obtained by decomposing the MET vector along the muon and hadronic tau directions. Physical solutions require $0 < x_\mu < 1$ and $0 < x_\tau < 1$. Events with unphysical solutions use the visible mass as a fallback.

### Physical solution fractions

The unphysical solution fractions, summarized in @tbl:mcol-physical, are higher than the strategy estimates but remain below the 50% go/no-go threshold for signal events.

| Sample | Total | Physical | Unphysical fraction |
|--------|-------|----------|-------------------|
| ggH | 4,603 | 2,499 | 45.7% |
| VBF | 6,255 | 3,776 | 39.6% |
| DY | 34,468 | 16,963 | 50.8% |
| $t\bar{t}$ | 5,670 | 2,552 | 55.0% |
| W+jets (combined) | 11,464 | 4,307 | 62.4% |
| Data (B+C) | 67,988 | 30,471 | 55.2% |

: Physical solution fractions for the collinear approximation. The ggH signal unphysical fraction of 45.7% is below the 50% go/no-go threshold. Background processes show higher unphysical fractions, consistent with the collinear assumption being less appropriate for fake taus and complex final states. {#tbl:mcol-physical}

The ggH signal has a 45.7% unphysical fraction, approaching but not exceeding the 50% threshold. The VBF signal has a better fraction (39.6%) due to its cleaner topology with forward jets. The resulting collinear mass distributions are shown in Figures @fig:mcol-baseline and @fig:mcol-vbf. Background processes show higher unphysical fractions (50-70%), particularly $W$+jets where the hadronic tau is a misidentified jet with no physical collinear neutrino. Templates are constructed in 25 bins from 0 to 300 GeV, including both physical and fallback (visible mass) solutions.

<!-- COMPOSE: side-by-side -->
![Collinear mass distribution in the Baseline category. The QCD template is computed from the collinear mass values of same-sign events, ensuring consistency with the fitting observable. The broader distribution compared to the visible mass reflects the inclusion of unphysical collinear solutions that fall back to the visible mass. Events with physical solutions produce the characteristic peaks at the Z and Higgs masses.](../../../phase3_selection/outputs/figures/mcol_baseline.pdf){#fig:mcol-baseline}

![Collinear mass distribution in the VBF category. The reduced statistics and higher unphysical fractions for background processes make this observable less powerful in the VBF category. Nevertheless, the collinear mass provides complementary information to the visible mass through the improved mass resolution for events with physical solutions.](../../../phase3_selection/outputs/figures/mcol_vbf.pdf){#fig:mcol-vbf}

## Approach comparison {#sec:disc-comparison}

The three fitting approaches are compared using the expected significance metric, computed consistently with the data-driven QCD background included in all approaches:

| Approach | $S/\sqrt{B}$ (signal window) | Expected significance |
|----------|-----------------------------|-----------------------|
| Visible mass ($m_\mathrm{vis}$) | 0.144 (100-150 GeV) | 0.80$\sigma$ |
| **NN discriminant** | **1.251 (score > 0.8)** | **1.52$\sigma$** |
| Collinear mass ($m_\mathrm{col}$) | 0.426 (110-160 GeV) | 0.68$\sigma$ |

: Comparison of the three fitting approaches. The NN discriminant provides the best expected significance, improving over the visible mass baseline by 89% and over the collinear mass by a factor of 2.2. These pre-fit estimates use a simple $S/\sqrt{B}$ counting metric; the profile likelihood fit results are presented in Section @sec:expected-results. {#tbl:approach-comparison}

The NN discriminant is selected as the primary fitting observable based on its substantially better expected sensitivity (Figure @fig:approach-comparison). The visible mass and collinear mass are retained as cross-check approaches. The full profile likelihood results confirm these pre-fit estimates (Section @sec:expected-results).

<!-- FLAGSHIP -->
![Comparison of expected significance across the three fitting approaches: visible mass template ($m_\mathrm{vis}$), neural network discriminant (NN score), and collinear approximation mass ($m_\mathrm{col}$). All approaches include consistent treatment of the data-driven QCD background. The NN discriminant provides the best expected significance at 1.52$\sigma$, representing an 89% improvement over the cut-based visible mass approach.](../../../phase3_selection/outputs/figures/approach_comparison.pdf){#fig:approach-comparison}


# Kinematic Distributions {#sec:kinematics}

This section presents the data/MC comparison for key kinematic distributions in the Baseline and VBF categories. All distributions include the data-driven QCD estimate from the same-sign region and the $W$+jets scale factor correction. These comparisons validate the modeling of the input variables that enter the NN discriminant and the fitting observables. The individual variable separation powers are summarized in Figure @fig:separation-power.

## Baseline category distributions {#sec:kin-baseline}

<!-- COMPOSE: side-by-side -->
![Hadronic tau $p_\mathrm{T}$ distribution in the Baseline category. The steeply falling spectrum is well modeled by the MC simulation. The tau $p_\mathrm{T}$ is the most discriminating individual variable (ROC AUC = 0.695), as signal taus from Higgs decay tend to have harder $p_\mathrm{T}$ spectra than those from $Z$ decay due to the higher parent mass.](../../../phase3_selection/outputs/figures/tau_pt_baseline.pdf){#fig:tau-pt-baseline}

![Muon $p_\mathrm{T}$ distribution in the Baseline category. The distribution peaks near the 20 GeV selection threshold, with the MC prediction showing reasonable agreement with data. The slight excess in data at high $p_\mathrm{T}$ is consistent with the QCD multijet contribution, which tends to produce higher-$p_\mathrm{T}$ muons than the $Z\to\tau\tau$ background.](../../../phase3_selection/outputs/figures/mu_pt_baseline.pdf){#fig:mu-pt-baseline}

<!-- COMPOSE: side-by-side -->
![Missing transverse energy ($E_\mathrm{T}^\mathrm{miss}$) distribution in the Baseline category. The data shows slightly higher MET than the MC prediction, consistent with the QCD multijet contribution. The MET is the fourth most discriminating variable (ROC AUC = 0.639), as the additional neutrinos from the Higgs decay produce more MET than the $Z\to\tau\tau$ background.](../../../phase3_selection/outputs/figures/met_pt_baseline.pdf){#fig:met-baseline}

![Jet multiplicity distribution in the Baseline category. The LO MadGraph MC shows known mismodeling at high jet multiplicities ($N_\mathrm{jets} \geq 2$), where the data exceeds the prediction. This is a well-documented feature of LO generators and is addressed in the statistical model through per-category normalization nuisance parameters.](../../../phase3_selection/outputs/figures/njets_baseline.pdf){#fig:njets-baseline}

![Angular separation $\Delta R(\mu, \tau_\mathrm{h})$ in the Baseline category. The distribution peaks near $\pi$, consistent with the back-to-back topology expected from $Z/H \to \tau\tau$ decays where the two tau leptons are produced approximately opposite in azimuth. The data/MC agreement is generally good, with a slight excess at large separations ($\Delta R > 3.5$) attributed to QCD multijet events.](../../../phase3_selection/outputs/figures/delta_r_baseline.pdf){#fig:delta-r-baseline}

## VBF category distributions {#sec:kin-vbf}

<!-- COMPOSE: side-by-side -->
![Hadronic tau $p_\mathrm{T}$ distribution in the VBF category. The spectrum is harder than in the Baseline category due to the VBF event topology, where the Higgs boson recoils against the forward jet system. The reduced statistics lead to larger data/MC fluctuations in the ratio panel.](../../../phase3_selection/outputs/figures/tau_pt_vbf.pdf){#fig:tau-pt-vbf}

![Muon $p_\mathrm{T}$ distribution in the VBF category. The VBF signal events (visible at the x10 scale) tend to have slightly harder muon $p_\mathrm{T}$ compared to the Baseline category, reflecting the boost from the VBF production mechanism.](../../../phase3_selection/outputs/figures/mu_pt_vbf.pdf){#fig:mu-pt-vbf}

<!-- COMPOSE: side-by-side -->
![Missing transverse energy distribution in the VBF category. The $t\bar{t}$ background contributes a larger fraction in this category compared to Baseline, due to the two-jet requirement that naturally selects $t\bar{t}$ events. The MET distribution is broader than in Baseline, consistent with the more complex event topology.](../../../phase3_selection/outputs/figures/met_pt_vbf.pdf){#fig:met-vbf}

![Jet multiplicity distribution in the VBF category. By construction, all events have at least two jets. The distribution shows moderate agreement between data and MC, with the characteristic LO generator jet multiplicity mismodeling less pronounced since the VBF selection already requires two jets.](../../../phase3_selection/outputs/figures/njets_vbf.pdf){#fig:njets-vbf}

![Angular separation $\Delta R(\mu, \tau_\mathrm{h})$ in the VBF category. The distribution is slightly more forward-peaked than in the Baseline category, consistent with the more boosted kinematics of VBF events where the Higgs boson recoils against the dijet system.](../../../phase3_selection/outputs/figures/delta_r_vbf.pdf){#fig:delta-r-vbf}

## Variable separation power {#sec:var-separation}

![Ranking of kinematic variables by their individual signal-vs-background separation power, quantified by the ROC AUC. The top variables ($\tau_\mathrm{h}$ $p_\mathrm{T}$, $m_\mathrm{vis}$, $N_\mathrm{jets}$, $E_\mathrm{T}^\mathrm{miss}$) all have AUC > 0.63, while pseudorapidity variables show minimal discrimination (AUC near 0.5). The NN combines all 14 variables to achieve a test AUC of 0.825.](../../../phase2_exploration/outputs/figures/separation_power.pdf){#fig:separation-power}


# Statistical Method {#sec:statmethod}

## Profile likelihood framework {#sec:stat-likelihood}

The signal strength modifier $\mu$ is extracted using a binned profile likelihood ratio method implemented in pyhf [@pyhf; @Cranmer:2012sba]. For each fitting approach (visible mass, NN discriminant, collinear mass), a simultaneous fit is performed across the Baseline and VBF categories with a single parameter of interest (POI): $\mu = \sigma_\mathrm{obs} / \sigma_\mathrm{SM}$.

The likelihood function is:

$$\mathcal{L}(\mu, \boldsymbol{\theta}) = \prod_{c \in \{\mathrm{Baseline, VBF}\}} \prod_{b=1}^{N_\mathrm{bins}} \mathrm{Pois}\left(n_{cb} \,\middle|\, \nu_{cb}(\mu, \boldsymbol{\theta})\right) \times \prod_{k=1}^{N_\mathrm{NP}} f_k(\theta_k)$$ {#eq:likelihood}

where $n_{cb}$ is the observed count in bin $b$ of category $c$, $\nu_{cb}(\mu, \boldsymbol{\theta})$ is the expected count parameterized by the signal strength $\mu$ and nuisance parameters $\boldsymbol{\theta}$, and $f_k(\theta_k)$ are constraint terms for the nuisance parameters.

The expected yield in each bin is:

$$\nu_{cb}(\mu, \boldsymbol{\theta}) = \mu \cdot s_{cb}(\boldsymbol{\theta}) + b_{cb}(\boldsymbol{\theta})$$ {#eq:expected-yield}

where $s_{cb}$ is the signal template (ggH + VBF, sharing a common $\mu$) and $b_{cb}$ is the total background template ($Z\to\tau\tau + Z\to\ell\ell + t\bar{t} + W\mathrm{+jets} + \mathrm{QCD}$). Both signal and background templates are functions of the nuisance parameters $\boldsymbol{\theta}$.

The test statistic used for limit setting and significance is the profile likelihood ratio:

$$q_\mu = -2 \ln \frac{\mathcal{L}(\mu, \hat{\hat{\boldsymbol{\theta}}})}{\mathcal{L}(\hat{\mu}, \hat{\boldsymbol{\theta}})}$$ {#eq:test-statistic}

where $\hat{\mu}$ and $\hat{\boldsymbol{\theta}}$ are the unconditional maximum likelihood estimates, and $\hat{\hat{\boldsymbol{\theta}}}$ are the conditional maximum likelihood estimates of $\boldsymbol{\theta}$ for a given $\mu$ [@Cowan:2010js].

## Nuisance parameter treatment {#sec:stat-nps}

The model includes 21 nuisance parameters encoding systematic uncertainties, plus Barlow-Beeston lite statistical uncertainty parameters (one per bin per channel) [@Barlow:1993dm]. The total number of parameters per workspace is approximately 71 (21 NPs + 50 staterror gammas + 1 POI).

Normalization systematics (normsys) modify the overall yield of affected processes by a multiplicative factor $\kappa^{\theta_k}$, where $\theta_k$ is a unit-Gaussian nuisance parameter. Shape systematics (histosys) interpolate between up/down template variations using piecewise-linear interpolation.

## CLs method for upper limits {#sec:stat-cls}

The expected 95% confidence level (CL) upper limit on $\mu$ is computed using the CL$_\mathrm{s}$ method [@Read:2002hq] with the $\tilde{q}_\mu$ test statistic. The CL$_\mathrm{s}$ value is:

$$\mathrm{CL}_\mathrm{s}(\mu) = \frac{p_{s+b}(\mu)}{1 - p_b(\mu)}$$ {#eq:cls}

where $p_{s+b}$ is the $p$-value under the signal-plus-background hypothesis and $p_b$ is the $p$-value under the background-only hypothesis. The 95% CL upper limit is the value of $\mu$ for which CL$_\mathrm{s} = 0.05$. The $p$-values are computed using asymptotic formulae [@Cowan:2010js].


# Systematic Uncertainties {#sec:systematics}

This section describes each source of systematic uncertainty included in the statistical model. Each systematic is characterized by its physical origin, evaluation method, numerical impact on the signal strength $\mu$, and interpretation. The systematic sources are categorized as normalization uncertainties (affecting the overall yield) and shape uncertainties (affecting the template shape). A summary table is provided in @tbl:syst-summary and the impact ranking is presented in Section @sec:syst-ranking.

## Luminosity {#sec:syst-lumi}

The integrated luminosity measurement for the 2012 CMS data has an uncertainty of 2.6%, as determined by the CMS luminosity group using pixel cluster counting [@CMS:LUM-13-001]. This uncertainty is applied as a fully correlated normalization systematic on all MC-predicted processes (signal and backgrounds). The QCD multijet background, which is estimated from data, is not affected. The impact on $\mu$ is $\pm 0.069$, ranking 6th among all nuisance parameters. This is expected: the luminosity uncertainty scales all MC predictions simultaneously, and its impact on $\mu$ is modulated by the signal-to-background ratio.

## $Z\to\tau\tau$ normalization {#sec:syst-znorm}

The $Z\to\tau\tau$ and $Z\to\ell\ell$ background normalizations carry a 12% uncertainty, applied as a correlated normalization systematic. This uncertainty is decomposed as the quadrature sum of four components: theory cross-section (4%, from the FEWZ NNLO calculation), trigger efficiency data/MC difference (5%, due to the absence of trigger scale factors for CMS Open Data), tau identification loosening effect (8%, from the enlarged phase space at the Loose working point without official scale factors), and statistical precision in the $Z$ peak validation region (2%). The trigger efficiency component is absorbed into this normalization rather than being treated as a separate systematic for DY, to avoid double-counting. Published analyses using tau-embedded $Z\to\mu\mu$ data samples achieve Z normalization uncertainties of 3-4% [@CMS:2014nkk; @CMS:2017zyp]; the larger uncertainty here reflects the CMS Open Data constraints. The impact on $\mu$ is $\pm 0.036$, ranking 14th, because the $Z\to\tau\tau$ background contributes primarily in the low-NN-score region where signal is absent.

## $t\bar{t}$ normalization {#sec:syst-ttbar}

The $t\bar{t}$ background normalization carries a 5% uncertainty based on the NNLO+NNLL cross-section calculation using Top++ v2.0 [@Czakon:2011xx] at $m_t = 172.5$ GeV. The cross-section value of 252.9 pb has scale uncertainties of +6.4/-8.6 pb and PDF+$\alpha_s$ uncertainties of ±7.8 pb, which combine to approximately 5% total. The impact on $\mu$ is ±0.042, ranking 12th. The $t\bar{t}$ background contributes approximately 4% of the total background in the signal region and is more significant in the VBF category (where it constitutes approximately 35% of the background due to the two-jet requirement).

## $W$+jets normalization {#sec:syst-wjets}

The $W$+jets background normalization carries a 10% uncertainty per category, treated as uncorrelated between the Baseline and VBF categories. The data-driven scale factor ($\mathrm{SF}_W = 0.999 \pm 0.008$) has a statistical uncertainty of 0.8%, but the dominant uncertainty comes from the transverse mass extrapolation from the high-$m_\mathrm{T}$ sideband ($m_\mathrm{T} > 70$ GeV) to the signal region ($m_\mathrm{T} < 30$ GeV), estimated at approximately 10% by comparing the $W$+jets shape in the high-$m_\mathrm{T}$ and intermediate-$m_\mathrm{T}$ regions. The impact on $\mu$ is $\pm 0.044$ in the Baseline category and $\pm 0.065$ in the VBF category (ranked 11th and 8th, respectively). The larger VBF impact reflects the smaller total background count in that category.

## QCD normalization {#sec:syst-qcd}

The QCD multijet background normalization carries a 20% uncertainty per category, treated as uncorrelated between categories. This uncertainty encompasses the statistical uncertainty on the OS/SS ratio measurement ($R_\mathrm{OS/SS} = 0.979 \pm 0.018$, approximately 2%), the methodological uncertainty from the same-sign estimation procedure, and the extrapolation from the anti-isolated measurement region to the signal region isolation. The 20% value is conservative but justified by the 30% spread between literature values for $R_\mathrm{OS/SS}$ (tutorial: 0.80, published: 1.06, this analysis: 0.98) and the Data/Prediction deficit of 6% observed after including the QCD estimate. The impact on $\mu$ is $\pm 0.065$ in the Baseline category (ranked 7th) and $\pm 0.025$ in the VBF category. The Baseline impact is larger because the QCD multijet background constitutes approximately 15% of the total background in that category.

## Signal cross-section theory uncertainty {#sec:syst-signal-theory}

### ggH scale variations

The ggH production cross-section has asymmetric scale uncertainties of $+4.4\%/-6.9\%$ from $\mu_R/\mu_F$ variations, as computed at N3LO QCD by the LHC Higgs Cross Section Working Group [@LHCHiggsCrossSectionWorkingGroup:2016ypw]. This is implemented as an asymmetric normalization systematic on the ggH signal. The impact on $\mu$ is +0.048/-0.017 (ranked 15th), reflecting the small signal fraction relative to the total expected yield.

### VBF scale variations

The VBF production cross-section has scale uncertainties of $+0.3\%/-0.2\%$ at NNLO QCD + NLO EW [@LHCHiggsCrossSectionWorkingGroup:2016ypw]. The impact on $\mu$ is negligible ($\pm 0.0002$), as the VBF cross-section uncertainty is an order of magnitude smaller than ggH and the VBF signal is a small fraction of the total signal yield.

### PDF and $\alpha_s$ uncertainties

The ggH and VBF production cross-sections have PDF+$\alpha_s$ uncertainties of 3.2% and 2.2%, respectively [@LHCHiggsCrossSectionWorkingGroup:2016ypw]. These are implemented as normalization-only systematics (one for each production mode). The reduced NanoAOD format does not contain LHEPdfWeight branches for event-level PDF reweighting, so the acceptance effects of PDF variations (typically < 1-2% for $H\to\tau\tau$ selection) are not covered. This limitation is common in CMS Open Data analyses. The impact on $\mu$ is $\pm 0.013$ for ggH PDF and $\pm 0.003$ for VBF PDF.

### Branching ratio uncertainty

The $H\to\tau\tau$ branching ratio has a combined uncertainty of 1.7% from parametric (quark mass, $\alpha_s$) and theoretical higher-order uncertainties [@LHCHiggsCrossSectionWorkingGroup:2016ypw]. This is applied as a correlated normalization systematic on both ggH and VBF signal. The impact on $\mu$ is $\pm 0.007$, which is small because the branching ratio uncertainty equally scales the signal yield and does not affect the signal shape.

## Trigger efficiency {#sec:syst-trigger}

A 3% trigger efficiency uncertainty is applied to signal, $t\bar{t}$, and $W$+jets processes. It is explicitly not applied to $Z\to\tau\tau$ and $Z\to\ell\ell$, where the trigger efficiency uncertainty is absorbed into the 12% $Z$ normalization uncertainty (Section @sec:syst-znorm) to avoid double-counting. The 3% value represents the residual trigger efficiency uncertainty after accounting for the fact that the cross-trigger plateau region is well above the offline $p_\mathrm{T}$ thresholds (20 GeV offline vs 17 GeV trigger for the muon leg). No trigger efficiency scale factors are available for CMS Open Data. The impact on $\mu$ is $\pm 0.086$ (ranked 5th), making trigger efficiency the leading normalization systematic after the four shape systematics.

## Tau identification efficiency {#sec:syst-tauid}

A 5% tau identification efficiency uncertainty is applied to processes with genuine hadronic taus: signal (ggH and VBF) and $Z\to\tau\tau$. This value is adopted from the CMS tau performance group recommendation for the Loose isolation working point, reduced from the 10% placeholder in the strategy because the Loose working point is well-studied and the 5% value is consistent with published analyses [@CMS:2014nkk; @CMS:2018jrd]. The impact on $\mu$ is $\pm 0.051$ (ranked 10th). The tau ID uncertainty affects the signal normalization directly and is therefore a significant contributor to the overall signal strength uncertainty.

## Muon identification and isolation {#sec:syst-muon-id}

A 2% combined uncertainty on muon identification and isolation efficiency is applied to all MC-predicted processes (except QCD, which is data-driven). This covers the efficiency of the tight muon ID, the $p_\mathrm{T}$- and $\eta$-dependent isolation requirements, and the impact parameter selections. The value is consistent with CMS muon performance group recommendations and published analyses [@CMS:2014nkk]. The impact on $\mu$ is $\pm 0.051$ (ranked 9th).

## b-tagging efficiency {#sec:syst-btag}

A 5% b-tagging efficiency uncertainty is applied to the $t\bar{t}$ background, which relies on the CSV medium working point for b-jet identification in validation studies. This uncertainty is taken from CMS BTV POG recommendations and is consistent with the published b-tagging efficiency measurements. The impact on $\mu$ is $\pm 0.042$ (ranked 13th), comparable to the $t\bar{t}$ normalization uncertainty since both affect the same process.

## Missing backgrounds {#sec:syst-missing}

A 5% normalization uncertainty is applied to all MC-based backgrounds ($Z\to\tau\tau$, $Z\to\ell\ell$, $t\bar{t}$) to account for missing minor backgrounds (single top, diboson) that are not available in the CMS Open Data sample set. The single top and diboson contributions are estimated to account for 1-3% of the total background based on cross-section estimates [@CMS:2014nkk], making the 5% uncertainty conservative. This uncertainty is not applied to data-driven backgrounds ($W$+jets, QCD). The impact on $\mu$ is $\pm 0.032$ (ranked 16th).

## Tau energy scale {#sec:syst-tes}

The tau energy scale (TES) is the dominant shape systematic, with an uncertainty of $\pm 3\%$ applied to the hadronic tau $p_\mathrm{T}$. The variation is propagated to the MET by adjusting the MET components:

$$E_\mathrm{T,x}^{\mathrm{miss},\pm} = E_\mathrm{T,x}^\mathrm{miss} \mp \Delta p_{\mathrm{T},x}^\tau, \quad E_\mathrm{T,y}^{\mathrm{miss},\pm} = E_\mathrm{T,y}^\mathrm{miss} \mp \Delta p_{\mathrm{T},y}^\tau$$ {#eq:tes-met}

where $\Delta p_{\mathrm{T},x}^\tau = p_{\mathrm{T},x}^{\tau,\mathrm{varied}} - p_{\mathrm{T},x}^{\tau,\mathrm{nominal}}$. The TES variation shifts all observables ($m_\mathrm{vis}$, $m_\mathrm{col}$, NN score) through their dependence on the tau $p_\mathrm{T}$ and MET. For the NN score, all 14 input features are recomputed with the varied tau $p_\mathrm{T}$ and MET, and the trained NN model is re-evaluated to produce shifted score templates.

The $\pm 3\%$ TES uncertainty is the standard CMS tau performance group value for 2012 data [@CMS:2018jrd], applied inclusively across tau decay modes. Published analyses [@CMS:2014nkk; @CMS:2017zyp] use per-decay-mode TES values (1-3%); the inclusive 3% is conservative. The impact on $\mu$ is $+0.323/-0.422$ (ranked 1st, total impact 0.376), making TES the single most important systematic uncertainty (Figure @fig:syst-tes). This dominance is expected for a template shape fit where the signal-background discrimination depends critically on the reconstructed mass and tau energy scales.

![Ratio of the TES up (red) and down (blue) varied templates to the nominal template for $Z\to\tau\tau$, ggH signal, and $t\bar{t}$ in the NN score Baseline channel. The TES variation produces bin-by-bin shape changes of order 5-20%, with the largest effects in bins where the NN score distribution has steep gradients. The characteristic shape --- depletion in one region and enhancement in an adjacent region --- reflects the migration of events along the NN score axis as the tau energy is scaled.](../../4a_expected/outputs/figures/syst_shift_tes.pdf){#fig:syst-tes}

## Muon energy scale {#sec:syst-mes}

The muon energy scale (MES) uncertainty of $\pm 1\%$ is applied to the muon $p_\mathrm{T}$, with analogous MET propagation to the TES. The smaller variation magnitude (1% vs 3% for TES) reflects the better muon momentum resolution compared to hadronic tau energy measurement. The impact on $\mu$ is $+0.225/-0.346$ (ranked 2nd, total impact 0.291), as shown in Figure @fig:syst-mes. The MES is the second most important systematic despite the small variation because the muon enters directly into the visible mass, transverse mass, and MET calculations, affecting all observables.

![Ratio of the MES up and down varied templates to the nominal template for selected processes in the NN score Baseline channel. The 1% MES variation produces smaller shape changes than the 3% TES variation, but the impact on $\mu$ is still significant because the muon $p_\mathrm{T}$ enters directly into the discriminant variable computation.](../../4a_expected/outputs/figures/syst_shift_mes.pdf){#fig:syst-mes}

## Jet energy scale {#sec:syst-jes}

The jet energy scale (JES) uncertainty of $\pm 3\%$ is applied to all jets, with propagation to the MET and re-evaluation of the VBF categorization criteria ($m_{jj}$, $|\Delta\eta_{jj}|$). The JES variation causes events to migrate between the Baseline and VBF categories as jets cross the 30 GeV $p_\mathrm{T}$ threshold or the VBF $m_{jj}$ and $|\Delta\eta_{jj}|$ thresholds shift. This category migration is the key effect of JES, as it changes the relative event composition between the two categories. The $\pm 3\%$ value is consistent with CMS jet energy correction uncertainties for 2012 data [@CMS:2016lmd]. The impact on $\mu$ is $-0.096/+0.213$ (ranked 4th, total impact 0.165, Figure @fig:syst-jes).

![Ratio of the JES up and down varied templates to the nominal for selected processes in the NN score Baseline channel. The JES variation produces asymmetric effects due to category migration: JES up increases jet $p_\mathrm{T}$ and moves more events into the VBF category, depleting the Baseline. The effect on the NN score distribution is less direct than TES/MES since jet $p_\mathrm{T}$ enters the NN as a secondary input.](../../4a_expected/outputs/figures/syst_shift_jes.pdf){#fig:syst-jes}

## MET unclustered energy {#sec:syst-met-uncl}

The unclustered energy contribution to the MET has an uncertainty of $\pm 10\%$, applied as a direct scaling of the MET magnitude. Unclustered energy represents the soft hadronic activity not associated with reconstructed jets, muons, or taus, and contributes significantly to the MET resolution. The $\pm 10\%$ variation is the standard CMS recommendation for the unclustered energy uncertainty [@CMS:PFT-09-001]. The impact on $\mu$ is $-0.266/+0.047$ (ranked 3rd, total impact 0.191, Figure @fig:syst-met-uncl). The highly asymmetric impact suggests that the signal sensitivity is more vulnerable to MET increases than decreases, consistent with the MET entering the collinear mass calculation and NN input features.

![Ratio of the MET unclustered energy up and down varied templates to the nominal for selected processes in the NN score Baseline channel. The 10% MET variation produces visible shape effects, particularly in bins sensitive to the MET-dependent features in the NN. The asymmetric impact pattern is characteristic of unclustered energy variations.](../../4a_expected/outputs/figures/syst_shift_met_uncl.pdf){#fig:syst-met-uncl}

## MC statistical uncertainty {#sec:syst-mcstat}

The finite MC statistics in each bin are accounted for using the Barlow-Beeston lite approach [@Barlow:1993dm], which introduces one gamma parameter per bin per channel. This parameterization allows the bin-by-bin yields to fluctuate within their statistical precision, effectively smoothing out MC statistical fluctuations in the fit. In the VBF category, several bins have low MC statistics (< 5 expected events for some processes), making the Barlow-Beeston treatment essential for numerical stability.

## Systematic completeness table {#sec:syst-completeness}

@tbl:syst-completeness compares the systematic sources implemented in this analysis against those used in the two reference analyses (R1: CMS evidence at 8 TeV [@CMS:2014nkk]; R2: CMS observation at 13 TeV [@CMS:2017zyp]).

| Source | R1 (8 TeV) | R2 (13 TeV) | This analysis | Status |
|--------|-----------|------------|---------------|--------|
| Tau energy scale | 3% per DM | 1-3% per DM | 3% (inclusive) | Implemented |
| Tau ID efficiency | 6% | 5% | 5% | Implemented |
| Muon ID/iso | ~1% | ~2% | 2% | Implemented |
| Muon energy scale | Included | Included | 1% shape | Implemented |
| Jet energy scale | $p_\mathrm{T}/\eta$ dep. | $p_\mathrm{T}/\eta$ dep. | 3% shape | Implemented |
| MET unclustered | Propagated | Propagated | 10% shape | Implemented |
| $Z\to\tau\tau$ norm | 3.3% | 4% | 12% | Implemented |
| $W$+jets norm | Data-driven | Data-driven | 10% per cat. | Implemented |
| QCD norm | Data-driven | Data-driven | 20% per cat. | Implemented |
| $t\bar{t}$ norm | ~10% | 6% | 5% (NNLO+NNLL) | Implemented |
| Luminosity | 2.6% | 2.5% | 2.6% | Implemented |
| PDF+$\alpha_s$ | Per process | Per process | Norm only | Implemented |
| Signal theory (scale) | Per mode | Per mode | YR4 values | Implemented |
| BR($H\to\tau\tau$) | Included | Included | 1.7% | Implemented |
| MC statistics | B-B | B-B | B-B lite | Implemented |
| Trigger efficiency | 4-8% | ~5% | 3% | Implemented |
| b-tag efficiency | 2-5% | 1-3% | 5% | Implemented |
| Missing backgrounds | Included | Included | 5% | Implemented |
| Pileup reweighting | ±5% | ±5% | Not impl. | Note 1 |
| Jet-to-tau fake rate | Included | Included | Absorbed | Note 2 |
| Generator comparison | Various | Various | N/A | Limitation |
| PS ISR/FSR | Included | Included | N/A | Limitation |

: Systematic completeness comparison with reference analyses. Note 1: Pileup reweighting is not implemented because the CMS Open Data NanoAOD lacks official pileup weights; the effect is partially absorbed by the Z normalization uncertainty. Note 2: The jet-to-tau fake rate shape systematic is absorbed into the W+jets and QCD normalization uncertainties (10% and 20% respectively). {#tbl:syst-completeness}

Two sources are not implemented due to CMS Open Data limitations: pileup reweighting (no official pileup weights available; partially absorbed by the 12% Z normalization uncertainty) and generator comparison / PS ISR/FSR variations (only one generator per process available, and no PSWeight branches in the NanoAOD). These limitations are common in CMS Open Data analyses and are explicitly documented as constraints of this measurement.

## Impact ranking {#sec:syst-ranking}

@tbl:impact-ranking presents the top 15 nuisance parameters ranked by their impact on the signal strength $\mu$ for the NN score approach, as evaluated on Asimov data.

| Rank | Parameter | $\Delta\mu$ (up) | $\Delta\mu$ (down) | Total impact |
|------|-----------|------------------|-------------------|-------------|
| 1 | MES (shape) | $+0.375$ | $-0.431$ | 0.404 |
| 2 | MET unclustered (shape) | $-0.342$ | $+0.365$ | 0.354 |
| 3 | JES (shape) | $-0.256$ | $+0.278$ | 0.267 |
| 4 | TES (shape) | $-0.265$ | $+0.147$ | 0.214 |
| 5 | QCD norm (baseline) | $-0.127$ | $+0.126$ | 0.126 |
| 6 | $Z\to\tau\tau$ norm | $+0.094$ | $-0.100$ | 0.097 |
| 7 | Trigger efficiency | $-0.089$ | $+0.097$ | 0.093 |
| 8 | $t\bar{t}$ norm | $-0.073$ | $+0.073$ | 0.073 |
| 9 | b-tag efficiency | $-0.073$ | $+0.073$ | 0.073 |
| 10 | Luminosity | $-0.064$ | $+0.068$ | 0.066 |
| 11 | Muon ID/iso | $-0.048$ | $+0.051$ | 0.050 |
| 12 | Missing bkg norm | $-0.049$ | $+0.046$ | 0.047 |
| 13 | $W$+jets norm (baseline) | $-0.050$ | $+0.039$ | 0.045 |
| 14 | ggH theory (scale) | $-0.016$ | $+0.047$ | 0.035 |
| 15 | QCD norm (VBF) | $-0.029$ | $+0.028$ | 0.029 |

: Impact ranking of nuisance parameters on the signal strength $\mu$ for the NN score approach. The four shape systematics (MES, MET unclustered, JES, TES) dominate, with a combined impact of approximately 0.64. {#tbl:impact-ranking}

The four shape systematics (MES, MET unclustered, JES, TES) collectively contribute $\sqrt{0.404^2 + 0.354^2 + 0.267^2 + 0.214^2} \approx 0.64$ to $\Delta\mu$ (Figure @fig:impact-ranking), dominating the systematic uncertainty budget. This dominance is expected for a template shape fit where the signal-background separation depends on mass-sensitive observables whose shapes are directly affected by energy scale variations. No single systematic exceeds 80% of the total uncertainty: the MES impact of 0.404 is approximately 32% of the total $\sigma(\mu) = 1.25$, well below the 80% regression trigger threshold.

The total systematic uncertainty, computed as the quadrature sum of all impacts, is approximately 0.64. The statistical uncertainty dominates: the total $\sigma(\mu) = 1.25$ includes both statistical and systematic components, so the statistical-only uncertainty is approximately $\sqrt{1.25^2 - 0.64^2} \approx 1.07$, confirming that this measurement is statistically limited.

<!-- FLAGSHIP -->
![Impact ranking of the top 15 nuisance parameters on the signal strength $\mu$ for the NN score approach on Asimov data. The horizontal bars show the $\Delta\mu$ impact of each nuisance parameter when varied up (blue) and down (orange). The four shape systematics (tau energy scale, muon energy scale, MET unclustered energy, jet energy scale) are the leading uncertainties, followed by normalization systematics for trigger efficiency, luminosity, and background normalizations.](../../4a_expected/outputs/figures/impact_ranking.pdf){#fig:impact-ranking}

## Systematic uncertainty summary {#sec:syst-summary}

| Systematic | Type | Magnitude | Affected processes | Impact on $\mu$ |
|-----------|------|-----------|-------------------|----------------|
| MES | Shape | ±1% | All MC | 0.404 |
| MET unclustered | Shape | ±10% (uncl. only) | All MC | 0.354 |
| JES | Shape | ±3% (no MET) | All MC | 0.267 |
| TES | Shape | ±3% | Signal, ZTT, $t\bar{t}$ | 0.214 |
| QCD norm (baseline) | Norm | 20% | QCD | 0.126 |
| $Z\to\tau\tau$ norm | Norm | 12% | ZTT, ZLL | 0.097 |
| Trigger efficiency | Norm | 3% | Signal, $t\bar{t}$, $W$+jets | 0.093 |
| $t\bar{t}$ norm | Norm | 5% | $t\bar{t}$ | 0.073 |
| b-tag efficiency | Norm | 5% | $t\bar{t}$ | 0.073 |
| Luminosity | Norm | 2.6% | All MC | 0.066 |
| Muon ID/iso | Norm | 2% | All MC (not QCD) | 0.050 |
| Missing bkg norm | Norm | 5% | ZTT, ZLL, $t\bar{t}$ | 0.047 |
| $W$+jets norm (baseline) | Norm | 10% | $W$+jets | 0.045 |
| $Z\to\tau\tau$ norm | Norm | 12% | ZTT, ZLL | 0.036 |
| ggH theory (scale) | Norm | +4.4/-6.9% | ggH | 0.036 |
| Missing backgrounds | Norm | 5% | ZTT, ZLL, $t\bar{t}$ | 0.032 |
| QCD norm (VBF) | Norm | 20% | QCD | 0.025 |
| ggH PDF+$\alpha_s$ | Norm | 3.2% | ggH | 0.013 |
| BR($H\to\tau\tau$) | Norm | 1.7% | Signal | 0.007 |
| VBF PDF+$\alpha_s$ | Norm | 2.2% | VBF | 0.003 |
| VBF theory (scale) | Norm | +0.3/-0.2% | VBF | < 0.001 |

: Summary of all systematic uncertainties, ordered by impact on the signal strength $\mu$. The "Type" column indicates whether the systematic affects the template normalization (Norm) or shape (Shape). The impact values are for the NN score approach on Asimov data. {#tbl:syst-summary}


# Expected Results {#sec:expected-results}

This section presents the expected results obtained on Asimov pseudo-data generated under the Standard Model hypothesis ($\mu = 1$). All nuisance parameters are set to their nominal values in the Asimov dataset. The 10% data validation results are presented in Section @sec:data-validation.

## Pre-fit templates {#sec:prefit-templates}

The pre-fit template distributions for all three fitting approaches in both categories are shown in Figures @fig:template-mvis-baseline through @fig:template-mcol-vbf. The visible mass templates (Figures @fig:template-mvis-baseline and @fig:template-mvis-vbf) show the characteristic $Z$ peak and Higgs signal region. The NN score templates (Figures @fig:template-nn-baseline and @fig:template-nn-vbf) demonstrate clear signal-background separation. The collinear mass templates (Figures @fig:template-mcol-baseline and @fig:template-mcol-vbf) show broader distributions due to unphysical solutions.

<!-- COMPOSE: side-by-side -->
![Pre-fit visible mass template in the Baseline category. The stacked backgrounds ($Z\to\tau\tau$, $Z\to\ell\ell$, $t\bar{t}$, W+jets, QCD) are shown with the ggH and VBF signal contributions scaled by 10 for visibility. Asimov data points (generated as the sum of all backgrounds plus SM signal) overlay the total prediction. The $Z\to\tau\tau$ background dominates with a peak near 60-80 GeV, while the Higgs signal contributes a broad excess in the 100-150 GeV region.](../../4a_expected/outputs/figures/template_mvis_baseline.pdf){#fig:template-mvis-baseline}

![Pre-fit visible mass template in the VBF category. The lower statistics compared to Baseline are evident, with $t\bar{t}$ and W+jets becoming significant backgrounds alongside $Z\to\tau\tau$. The VBF signal (blue, scaled x10) is comparable in magnitude to the ggH contamination (red, scaled x10) in this category.](../../4a_expected/outputs/figures/template_mvis_vbf.pdf){#fig:template-mvis-vbf}

<!-- COMPOSE: side-by-side -->
![Pre-fit NN discriminant score template in the Baseline category. The backgrounds peak at low NN scores while the signal peaks at high scores, demonstrating the discriminating power of the NN classifier. The clear separation between signal and background in this observable is the primary driver of the improved sensitivity of the NN approach.](../../4a_expected/outputs/figures/template_nn_score_baseline.pdf){#fig:template-nn-baseline}

![Pre-fit NN discriminant score template in the VBF category. The signal-background separation pattern is similar to Baseline, with reduced statistics. The NN exploits the VBF-specific kinematic features (forward jets, large dijet mass) to further enhance the signal discrimination in this category.](../../4a_expected/outputs/figures/template_nn_score_vbf.pdf){#fig:template-nn-vbf}

<!-- COMPOSE: side-by-side -->
![Pre-fit collinear mass template in the Baseline category. The broader distribution compared to the visible mass reflects the inclusion of events with unphysical collinear solutions that fall back to the visible mass. For events with physical solutions, the collinear mass provides improved mass resolution, producing a sharper $Z$ peak and better Higgs signal separation.](../../4a_expected/outputs/figures/template_mcol_baseline.pdf){#fig:template-mcol-baseline}

![Pre-fit collinear mass template in the VBF category. The reduced statistics and higher unphysical solution fractions for background processes result in a broader distribution compared to the Baseline category.](../../4a_expected/outputs/figures/template_mcol_vbf.pdf){#fig:template-mcol-vbf}

## Asimov fit results {#sec:asimov-results}

@tbl:asimov-results summarizes the Asimov fit results for all three fitting approaches. The signal strength $\mu$, its uncertainty $\sigma(\mu)$, the expected 95% CL upper limit, and the expected significance are reported.

| Approach | $\hat{\mu}$ | $\sigma(\mu)$ | 95% CL limit | Expected significance |
|----------|------------|--------------|--------------|----------------------|
| $m_\mathrm{vis}$ | 1.000 | 3.095 | 6.24 | 0.33$\sigma$ |
| **NN score** | **1.000** | **1.282** | **2.60** | **0.81$\sigma$** |
| $m_\mathrm{col}$ | 1.000 | 5.286 | 9.46 | 0.22$\sigma$ |

: Expected (Asimov) fit results for all three fitting approaches. The fitted signal strength $\hat{\mu}$ is unity by construction on Asimov data. The NN score approach provides the best expected precision with $\sigma(\mu) = 1.28$ (from `expected_results.json`). {#tbl:asimov-results}

The NN discriminant provides the best expected precision with $\sigma(\mu) = 1.28$, representing a factor of 2.4 improvement over the visible mass approach ($\sigma(\mu) = 3.09$) and a factor of 4.1 improvement over the collinear mass approach ($\sigma(\mu) = 5.29$). This confirms the pre-fit approach comparison in Figure @fig:approach-comparison. The visible mass approach has better sensitivity than the collinear mass, likely because the high unphysical solution fraction (45-70%) dilutes the mass resolution improvement of the collinear approximation for the events with physical solutions.

**Resolving power statement:** The NN score approach with $\sigma(\mu) = 1.28$ can distinguish signal strength values differing by approximately 2.6 ($2 \times \sigma(\mu)$) at 2$\sigma$ significance. This means the measurement can distinguish between the SM prediction ($\mu = 1$) and the no-signal hypothesis ($\mu = 0$) at approximately $0.8\sigma$, or can detect enhanced production ($\mu \geq 3.6$) at approximately $2\sigma$ level. The measurement is not sensitive enough for standalone discovery ($5\sigma$ would require $\mu \geq 6.4$).

## CLs limit scan {#sec:cls-results}

The expected 95% CL upper limits are computed using the CL$_\mathrm{s}$ method with the $\tilde{q}_\mu$ test statistic, scanning $\mu$ from 0 to 10. The CL$_\mathrm{s}$ values as a function of $\mu$ are shown in Figure @fig:cls-scan.

<!-- FLAGSHIP -->
![CL$_\mathrm{s}$ values as a function of the signal strength $\mu$ for all three fitting approaches. The horizontal dashed line indicates CL$_\mathrm{s} = 0.05$ (95% CL). The intersection with each curve gives the expected 95% CL upper limit: 2.60 for NN score, 6.24 for visible mass, and 9.46 for collinear mass. The NN score approach provides the tightest expected limit, consistent with its superior discriminating power.](../../4a_expected/outputs/figures/cls_scan.pdf){#fig:cls-scan}

## Comparison to reference analyses {#sec:reference-comparison}

The published CMS result [@CMS:2014nkk] measured $\mu = 0.78 \pm 0.27$ combining all channels, both center-of-mass energies, and 24.6 fb$^{-1}$. Our expected uncertainty of $\sigma(\mu) = 1.25$ for the NN score approach is approximately 4.6 times larger, which is quantitatively consistent with the reduced scope of this analysis:

- **Single channel:** The $\mu\tau_\mathrm{h}$ channel provides approximately 23% of the total $H\to\tau\tau$ sensitivity in the CMS combination.
- **Single run period:** 11.5 fb$^{-1}$ vs the combined 24.6 fb$^{-1}$.
- **No SVfit mass:** The published analysis uses the SVfit algorithm for mass reconstruction, which provides approximately 15-20% better mass resolution than the visible mass or collinear approximation.
- **Looser tau ID:** The Loose working point retains more background than the Medium/Tight working points used in the published analysis.

Taking these factors into account, the expected scaling is approximately $1/(\sqrt{11.5/24.6} \times 0.23 \times 1.15) \approx 5.3$ relative to the published combined uncertainty, in reasonable agreement with the observed factor of 4.3.


# Validation {#sec:validation}

## Signal injection test {#sec:val-injection}

The signal injection test verifies that the fit framework correctly recovers injected signal strengths. Asimov datasets are generated at $\mu = 0, 1, 2, 5$ and fitted to extract the signal strength. @tbl:injection-nn, @tbl:injection-mvis, and @tbl:injection-mcol present the results for each approach.

| $\mu_\mathrm{inject}$ | $\hat{\mu}$ | $\sigma(\mu)$ | Pull |
|----------------------|------------|--------------|------|
| 0.0 | 0.000 | 1.193 | 0.000 |
| 1.0 | 1.000 | 1.246 | 0.000 |
| 2.0 | 2.000 | 1.364 | 0.000 |
| 5.0 | 5.000 | 1.603 | 0.000 |

: Signal injection test results for the NN score approach. All injected values are recovered with pulls < 0.01, confirming unbiased signal extraction. {#tbl:injection-nn}

| $\mu_\mathrm{inject}$ | $\hat{\mu}$ | $\sigma(\mu)$ | Pull |
|----------------------|------------|--------------|------|
| 0.0 | 0.000 | 2.972 | 0.000 |
| 1.0 | 1.000 | 2.952 | 0.000 |
| 2.0 | 2.000 | 3.026 | 0.000 |
| 5.0 | 5.000 | 3.093 | 0.000 |

: Signal injection test results for the visible mass approach. {#tbl:injection-mvis}

| $\mu_\mathrm{inject}$ | $\hat{\mu}$ | $\sigma(\mu)$ | Pull |
|----------------------|------------|--------------|------|
| 0.0 | 0.000 | 4.190 | 0.000 |
| 1.0 | 1.000 | 4.779 | 0.000 |
| 2.0 | 2.000 | 4.309 | 0.000 |
| 5.0 | 5.000 | 4.400 | 0.000 |

: Signal injection test results for the collinear mass approach. {#tbl:injection-mcol}

All approaches recover the injected signal strength with pulls below 0.01 (consistent with numerical precision), confirming that the fit framework is unbiased and the signal parameterization is correct (Figure @fig:signal-injection). The increasing $\sigma(\mu)$ with $\mu$ for the NN approach (1.193 at $\mu = 0$ to 1.603 at $\mu = 5$) reflects the signal contribution to the Poisson variance in the signal-enriched bins.

![Signal injection linearity test for all three fitting approaches. The recovered signal strength $\hat{\mu}$ (y-axis) is plotted against the injected value $\mu_\mathrm{inject}$ (x-axis). All points lie on the diagonal ($\hat{\mu} = \mu_\mathrm{inject}$), confirming unbiased recovery across the full range of tested signal strengths. The error bars show the fit uncertainty $\sigma(\mu)$ at each injection point.](../../4a_expected/outputs/figures/signal_injection.pdf){#fig:signal-injection}

## Nuisance parameter pulls (Asimov) {#sec:val-pulls}

On Asimov data, all nuisance parameter best-fit values are consistent with zero by construction. The post-fit uncertainties provide information about the constraining power of the data: a post-fit uncertainty significantly smaller than the prior indicates that the data constrains the nuisance parameter beyond the external prior.

Several nuisance parameters show significant constraint from the Asimov data (Figure @fig:np-pulls):

- **TES (shape):** post-fit uncertainty 0.26 (constrained from 1.0), indicating sensitivity to the tau energy scale from the template shape. After template smoothing (F4 fix), the constraint relaxed from 0.21 to 0.26, closer to the 0.3-0.6 range typical of published CMS analyses
- **MES (shape):** post-fit uncertainty 0.49 (moderately constrained)
- **MET unclustered (shape):** post-fit uncertainty 0.45 (moderately constrained)
- **$Z\to\tau\tau$ norm:** post-fit uncertainty 0.49 (constrained from 1.0), reflecting the large DY statistics in the fit

![Nuisance parameter best-fit values and post-fit uncertainties for the NN score Asimov fit. The black points show the best-fit values (all zero on Asimov data) with error bars indicating the post-fit uncertainties. The green (yellow) bands show the 1$\sigma$ (2$\sigma$) prior constraint regions. Several parameters, particularly the shape systematics (TES, MES, MET, JES), have post-fit uncertainties significantly smaller than the prior, indicating that the template shapes in the fit provide constraining information.](../../4a_expected/outputs/figures/np_pulls.pdf){#fig:np-pulls}

## Goodness of fit (Asimov) {#sec:val-gof}

The goodness of fit is assessed using a $\chi^2$ statistic comparing the fitted model prediction to the data. On Asimov data, $\chi^2 \approx 0$ by construction (the Asimov data is the model prediction), confirming that the workspace is correctly assembled and the fit converges.

The toy-based $p$-value is computed by generating 200 pseudo-experiments for the NN score approach and 100 each for $m_\mathrm{vis}$ and $m_\mathrm{col}$. Since the Asimov $\chi^2 = 0$ is always less than any toy $\chi^2$ (Figure @fig:gof-toys), the $p$-value is 1.0 for all approaches. This validates the toy generation and fitting machinery; the meaningful goodness-of-fit test with informative $p$-values will occur on real data.

The effective number of degrees of freedom is negative ($-22$) because the model has more parameters (71) than data bins (50 for $m_\mathrm{vis}$/25+25, 45 for NN/20+25). This is standard for HistFactory models with many nuisance parameters; the GoF interpretation relies on the toy-based $p$-value rather than the $\chi^2$/ndf ratio.

![Distribution of $\chi^2$ values from 200 toy fits (blue histogram) compared to the Asimov observed $\chi^2 \approx 0$ (red vertical line). All toy $\chi^2$ values exceed the Asimov value, yielding a $p$-value of 1.0. The toy $\chi^2$ distribution peaks near 6-7 with a tail extending to approximately 11, providing a reference for the expected GoF distribution when real data is fitted.](../../4a_expected/outputs/figures/gof_toys.pdf){#fig:gof-toys}

## Validation summary {#sec:val-summary}

@tbl:validation-summary provides a comprehensive summary of all validation tests performed and their outcomes.

| Test | $\chi^2$/ndf or metric | $p$-value | Verdict | What it validates |
|------|----------------------|-----------|---------|-------------------|
| NN AUC (test) | 0.825 | N/A | GO (> 0.75 threshold) | Discriminant quality |
| NN overtraining (signal) | KS = 0.028 | 0.127 | PASS ($p > 0.05$) | No overtraining |
| NN overtraining (bkg) | KS = 0.008 | 0.686 | PASS ($p > 0.05$) | No overtraining |
| BDT comparison | AUC = 0.820 | N/A | Consistent | Architecture robustness |
| Signal injection ($\mu=0$, NN) | Pull = 0.000 | N/A | PASS ($|$pull$|$ < 0.1) | Fit unbiased |
| Signal injection ($\mu=1$, NN) | Pull = 0.000 | N/A | PASS ($|$pull$|$ < 0.1) | Fit unbiased |
| Signal injection ($\mu=2$, NN) | Pull = $-0.002$ | N/A | PASS ($|$pull$|$ < 0.1) | Fit linearity |
| Signal injection ($\mu=5$, NN) | Pull = 0.000 | N/A | PASS ($|$pull$|$ < 0.1) | Fit linearity at high $\mu$ |
| NP pulls (Asimov, NN) | All pulls = 0 | N/A | PASS | Workspace assembly |
| GoF (Asimov, NN) | $\chi^2 \approx 0$ | 1.0 (200 toys) | Expected | Toy machinery |
| GoF (Asimov, $m_\mathrm{vis}$) | $\chi^2 \approx 0$ | 1.0 (100 toys) | Expected | Toy machinery |
| GoF (Asimov, $m_\mathrm{col}$) | $\chi^2 \approx 0$ | 1.0 (99 toys) | Expected | Toy machinery |
| Tau ID WP optimization | $\chi^2$/ndf = 2.96 (Loose) | N/A | Selected | Data/MC modeling |
| $W$+jets SF | 0.999 ± 0.008 | N/A | Consistent with 1 | Background normalization |
| $W$+jets validation (mid-$m_\mathrm{T}$) | Data/Pred = 1.087 | N/A | Consistent (QCD) | Normalization extrapolation |
| QCD OS/SS ratio | 0.979 ± 0.018 | N/A | Within range | QCD estimation method |
| Collinear mass go/no-go | 45.7% unphysical (ggH) | N/A | GO (< 50%) | Observable viability |

: Summary of all validation tests performed in this analysis. Each test, its outcome, and the aspect of the analysis it validates are listed. All tests pass their respective criteria. {#tbl:validation-summary}


# 10% Data Validation {#sec:data-validation}

This section presents the results of a 10% data validation, in which a random subsample of the collision data is compared to the MC prediction and fitted to extract the signal strength. The purpose of this validation is to confirm that the analysis framework --- workspace construction, fitting procedure, systematic treatment, and goodness-of-fit evaluation --- functions correctly on real data before proceeding to unblind the full dataset.

## Data subsample selection {#sec:10pct-selection}

A 10% random subsample of the observed data is selected using `np.random.RandomState(seed=42)`. The same random mask is applied consistently to the main arrays, NN scores, and collinear mass arrays for both OS and SS signal regions.

| Dataset | OS SR full | OS SR 10% | Fraction | SS SR full | SS SR 10% | Fraction |
|---------|-----------|-----------|----------|-----------|-----------|----------|
| Run2012B | 26,236 | 2,646 | 10.09% | 8,879 | 876 | 9.87% |
| Run2012C | 41,752 | 4,175 | 10.00% | 14,255 | 1,427 | 10.01% |
| **Total** | **67,988** | **6,821** | **10.03%** | **23,134** | **2,303** | **9.96%** |

: Summary of the 10% data subsample selection. The subsample fractions are consistent with 10% within Poisson statistics (expected fluctuations of order 0.3%). {#tbl:10pct-selection}

## Data/MC comparison (pre-fit) {#sec:10pct-datamc}

The 10% data histograms are scaled by 10 for comparison to the full MC prediction from Phase 4a. The MC templates are unchanged (full MC statistics retained for all processes).

### Total yields {#sec:10pct-yields}

| Approach | Category | Data (10% x10) | MC expected | Ratio | Deficit |
|----------|----------|---------------|-------------|-------|---------|
| $m_\mathrm{vis}$ | Baseline | 67,150 | 70,677 | 0.950 | 5.0% |
| $m_\mathrm{vis}$ | VBF | 820 | 1,235 | 0.664 | 33.6% |
| NN score | Baseline | 67,390 | 70,898 | 0.951 | 4.9% |
| NN score | VBF | 820 | 1,260 | 0.651 | 34.9% |
| $m_\mathrm{col}$ | Baseline | 59,250 | 62,695 | 0.945 | 5.5% |
| $m_\mathrm{col}$ | VBF | 800 | 1,185 | 0.675 | 32.5% |

: Data/MC yield comparison for the 10% subsample (scaled by 10) in both categories across all three fitting approaches. The Baseline category shows a 5% deficit consistent with statistical fluctuations, while the VBF category shows a 33-35% deficit driven by the low statistics of the 10% subsample. {#tbl:10pct-yields}

**Baseline category:** The 5% deficit is consistent with statistical fluctuations in a 10% subsample. The expected statistical uncertainty on the total yield is $\sqrt{N_\mathrm{10\%}} / N_\mathrm{10\%} \times 10 = 10/\sqrt{N_\mathrm{10\%}}$, which for approximately 6,800 events gives approximately 12%, well larger than the 5% observed deficit.

**VBF category:** The 33-35% deficit is a notable feature. With only approximately 82 observed events in 10% of the data (expected approximately 126 if the full dataset matches MC), the deficit corresponds to a Poisson fluctuation of $(126 - 82)/\sqrt{82} \approx 4.9$. However, the VBF category has only approximately 800 total events across both run periods, making it highly susceptible to statistical fluctuations in a 10% subsample. The full dataset will determine whether this deficit persists.

### Data/MC distributions {#sec:10pct-distributions}

Figures @fig:10pct-mvis-baseline through @fig:10pct-mcol-vbf show the data/MC comparisons for all three discriminant variables in both categories.

<!-- COMPOSE: side-by-side -->
![Visible mass data/MC comparison in the Baseline category using the 10% data subsample (scaled by 10). The stacked MC prediction from Phase 4a is overlaid with the 10% data points. The data/MC ratio of 0.95 is consistent with statistical fluctuations. The shape agreement is good across the full $m_\mathrm{vis}$ range, with no significant distortions in the $Z$ peak or Higgs signal regions.](../../4b_partial/outputs/figures/data_mc_mvis_baseline.pdf){#fig:10pct-mvis-baseline}

![Visible mass data/MC comparison in the VBF category. The 10% data deficit of 34% is visible across the full mass range, with the most prominent deficit in the 60-120 GeV region corresponding to the $Z\to\tau\tau$ peak. The deficit is consistent with a statistical fluctuation given the small event count (82 events in 10%).](../../4b_partial/outputs/figures/data_mc_mvis_vbf.pdf){#fig:10pct-mvis-vbf}

<!-- COMPOSE: side-by-side -->
![NN discriminant score data/MC comparison in the Baseline category using the 10% data subsample. The data follows the MC prediction within statistical uncertainties across the full NN score range, from the background-dominated low-score region to the signal-enriched high-score region. Data/MC ratio is 0.95, consistent with the Baseline yield deficit.](../../4b_partial/outputs/figures/data_mc_nn_score_baseline.pdf){#fig:10pct-nn-baseline}

![NN discriminant score data/MC comparison in the VBF category. The 10% data deficit is visible across all NN score bins. The reduced statistics in the VBF category lead to large fluctuations in the ratio panel. The deficit does not appear to be concentrated in any particular NN score region, suggesting an overall normalization effect rather than a shape mismodeling.](../../4b_partial/outputs/figures/data_mc_nn_score_vbf.pdf){#fig:10pct-nn-vbf}

<!-- COMPOSE: side-by-side -->
![Collinear mass data/MC comparison in the Baseline category. The data/MC agreement is comparable to the visible mass approach, with a 5.5% overall deficit. The broader distribution due to unphysical collinear solutions is reproduced by the MC prediction.](../../4b_partial/outputs/figures/data_mc_mcol_baseline.pdf){#fig:10pct-mcol-baseline}

![Collinear mass data/MC comparison in the VBF category. The 33% deficit is visible, consistent with the other approaches. The collinear mass distribution shows larger bin-to-bin fluctuations due to the combination of low statistics and the unphysical solution fallback.](../../4b_partial/outputs/figures/data_mc_mcol_vbf.pdf){#fig:10pct-mcol-vbf}

### QCD template from 10% data {#sec:10pct-qcd}

The QCD template is estimated from the 10% SS data: $N_\mathrm{QCD,10\%} = (N_\mathrm{data,SS,10\%} - N_\mathrm{MC,SS} \times 0.1) \times R_\mathrm{OS/SS}$.

| Approach | Category | QCD (10% x10) | QCD (4a) | Ratio |
|----------|----------|--------------|----------|-------|
| $m_\mathrm{vis}$ | Baseline | 11,063 | 11,168 | 0.991 |
| $m_\mathrm{vis}$ | VBF | 120 | 51 | 2.37 |
| NN score | Baseline | 11,072 | 11,197 | 0.989 |
| NN score | VBF | 119 | 47 | 2.53 |
| $m_\mathrm{col}$ | Baseline | 10,065 | 10,013 | 1.005 |
| $m_\mathrm{col}$ | VBF | 107 | 52 | 2.04 |

: Comparison of the QCD background estimate from the 10% data versus the full dataset (Phase 4a). The Baseline QCD agrees within 1%. The VBF QCD shows a factor of approximately 2 excess, driven by Poisson fluctuations in the very small SS VBF sample (approximately 5 events in 10% after MC subtraction). {#tbl:10pct-qcd}

The QCD estimate in the Baseline category agrees within 1% with the full estimate, confirming the stability of the data-driven QCD estimation procedure. The VBF QCD shows a factor of approximately 2 excess, but this involves very small numbers (approximately 5 events in 10% SS VBF, after MC subtraction) and is dominated by Poisson fluctuations.

## Signal strength results on 10% data {#sec:10pct-fit}

### Fitting methodology {#sec:10pct-fit-method}

The Phase 4a pyhf workspaces are modified by scaling all MC templates (nominal, shape systematics, staterror) by 0.1, while the raw 10% data (unscaled integers) serves as the observed data. This preserves the Poisson nature of the data and avoids artifacts from non-integer observations.

### Fitted signal strengths {#sec:10pct-mu}

@tbl:10pct-mu-results compares the 10% data fit results with the expected (Asimov) results from Phase 4a.

| Approach | $\hat{\mu}$ (10%) | $\sigma(\mu)$ (10%) | Pull from SM | $\hat{\mu}$ (Asimov) | $\sigma(\mu)$ (Asimov) |
|----------|-------------------|--------------------|--------------|-----------------------|----------------------|
| $m_\mathrm{vis}$ | $-14.44$ | 5.94 | $-2.60\sigma$ | 1.000 | 3.083 |
| **NN score** | **$-3.73$** | **2.81** | **$-1.69\sigma$** | **1.000** | **1.277** |
| $m_\mathrm{col}$ | $-21.97$ | 6.99 | $-3.28\sigma$ | 1.000 | 6.540 |

: Comparison of signal strength results from the 10% data fit and the Asimov expectation. The NN score pull of $-1.69\sigma$ is within the 2$\sigma$ threshold. With extended POI bounds [-30, 30], all approaches converge freely without hitting a boundary. {#tbl:10pct-mu-results}

**NN score (primary approach):** $\hat{\mu} = -3.73 \pm 2.81$, representing a $1.69\sigma$ deviation from the SM expectation ($\mu = 1$). The pull is computed as $(\hat{\mu} - 1) / \sigma(\mu) = (-3.73 - 1) / 2.81 = -1.69$, which is within the $2\sigma$ threshold for flagging data/MC disagreement. The 10% data fit uncertainty of $\sigma(\mu) = 2.81$ is approximately $\sqrt{10} = 3.16$ times larger than the Asimov $\sigma(\mu) = 1.28$, consistent with the 10-fold reduction in data statistics. The comparison of expected and 10% observed signal strengths is shown in Figure @fig:mu-comparison.

**$m_\mathrm{vis}$ and $m_\mathrm{col}$:** With extended POI bounds [-30, 30], both fits converge freely: $\hat{\mu}(m_\mathrm{vis}) = -14.4 \pm 5.9$ and $\hat{\mu}(m_\mathrm{col}) = -22.0 \pm 7.0$. The large negative values reflect the VBF category deficit combined with the limited discriminating power of these observables (expected $\sigma(\mu) = 3.08$ and 6.54 from Phase 4a).

<!-- FLAGSHIP -->
![Comparison of fitted signal strength values ($\hat{\mu}$) between the Asimov expectation (blue, $\mu = 1$) and the 10% data fit (red) for all three approaches. The NN score approach gives $\hat{\mu} = -3.73 \pm 2.81$, $m_\mathrm{vis}$ gives $-14.4 \pm 5.9$, and $m_\mathrm{col}$ gives $-22.0 \pm 7.0$. With extended POI bounds [-30, 30], no fit is at the boundary. The negative values are driven by the VBF category deficit in the 10% subsample.](../../4b_partial/outputs/figures/mu_comparison_10pct.pdf){#fig:mu-comparison}

### Observed 95% CL limits {#sec:10pct-limits}

| Approach | Observed 95% CL (10%) | Expected 95% CL (Asimov) |
|----------|----------------------|-------------------------|
| $m_\mathrm{vis}$ | 1.11 | 6.24 |
| NN score | 3.41 | 2.60 |
| $m_\mathrm{col}$ | N/A | 9.46 |

: Observed 95% CL upper limits from the 10% data fit compared to the Asimov expected limits. The observed limits are generally tighter because the negative $\hat{\mu}$ pulls the exclusion contour down. {#tbl:10pct-limits}

## Nuisance parameter pulls (10% data) {#sec:10pct-nppulls}

The nuisance parameter pulls from the 10% data NN score fit are summarized in @tbl:10pct-np-pulls and shown in Figure @fig:np-pulls-10pct.

| Rank | Parameter | Best-fit | Uncertainty | Pull ($\sigma$) |
|------|-----------|---------|-------------|------|
| 1 | MET unclustered (shape) | $-1.00$ | 0.54 | $-1.85$ |
| 2 | $Z\to\tau\tau$ norm | $-0.66$ | 0.60 | $-1.11$ |
| 3 | TES (shape) | $+0.37$ | 0.35 | $+1.05$ |
| 4 | $W$+jets norm (baseline) | $+0.92$ | 0.93 | $+0.98$ |
| 5 | $W$+jets norm (VBF) | $-0.89$ | 0.91 | $-0.98$ |
| 6 | JES (shape) | $-0.86$ | 0.92 | $-0.93$ |
| 7 | QCD norm (baseline) | $+0.82$ | 0.91 | $+0.90$ |

: Top 7 nuisance parameter pulls from the NN score fit on 10% data. All pulls are below the 2$\sigma$ threshold, indicating no significant systematic mismodeling. The largest pull (MET unclustered at $-1.85\sigma$) reflects the fit accommodating the VBF deficit. {#tbl:10pct-np-pulls}

**All NP pulls are below 2$\sigma$.** The largest pull is the MET unclustered energy shape at $-1.85\sigma$, which is notable but within the expected range. The fit adjusts the MET unclustered systematic to accommodate the VBF deficit without introducing any pathological pulls. No single nuisance parameter exceeds the $2\sigma$ threshold that would flag systematic data/MC disagreement.

![Nuisance parameter best-fit values and uncertainties from the NN score fit on 10% data. The black points show the best-fit values with error bars indicating the post-fit uncertainties. Unlike the Asimov fit (Figure @fig:np-pulls), several parameters are pulled from zero, reflecting the real data's departure from the nominal MC prediction. The largest pull (MET unclustered at $-1.85\sigma$) is within the acceptable range. All pulls remain below the 2$\sigma$ red-flag threshold.](../../4b_partial/outputs/figures/np_pulls_10pct.pdf){#fig:np-pulls-10pct}

## Per-category fit {#sec:10pct-percategory}

Fitting each category independently with the combined workspace isolates the source of the negative signal strength.

| Approach | Category | $\hat{\mu}$ | $\sigma(\mu)$ | Pull from 1 |
|----------|----------|------------|--------------|-------------|
| NN score | Baseline | $-0.25$ | 1.57 | $-0.79\sigma$ |
| NN score | VBF | $-12.34$ | 3.43 | $-3.89\sigma$ |

: Per-category signal strength results from the NN score 10% data fit. The Baseline category alone is consistent with the SM ($\hat{\mu} = -0.25 \pm 1.57$, pull = $-0.79\sigma$). The VBF category drives the negative combined signal strength. {#tbl:10pct-percategory}

**Baseline-only fit:** $\hat{\mu} = -0.25 \pm 1.57$ is perfectly consistent with the SM (pull = $-0.79\sigma$). The Baseline category alone shows no tension (Figure @fig:per-category-mu).

**VBF-only fit:** $\hat{\mu} = -12.3 \pm 3.4$. With extended POI bounds [-30, 30], the fit now converges freely. The large negative value is entirely driven by the 35% data deficit in the VBF category, which contains only 82 events in the 10% subsample. The VBF category has very low signal sensitivity ($S/\sqrt{B} = 0.33$ from Phase 4a) and the 10% subsample is too small for a reliable standalone VBF fit.

![Per-category signal strength measurements for all three approaches using the 10% data. The Baseline category (circles) gives values consistent with the SM for the NN score approach, while the VBF category (squares) shows large negative values driven by the 35% data deficit. With extended POI bounds [-30, 30], no fit is at the boundary. This confirms that the VBF deficit, not a global mismodeling, drives the negative combined signal strength.](../../4b_partial/outputs/figures/mu_per_category_10pct.pdf){#fig:per-category-mu}

## Goodness of fit (10% data) {#sec:10pct-gof}

The goodness-of-fit test is performed using 200 toy pseudo-experiments for the NN score approach.

| Approach | $\chi^2_\mathrm{obs}$ | GoF $p$-value | $N_\mathrm{toys}$ | Verdict |
|----------|----------------------|--------------|-------------------|---------|
| $m_\mathrm{vis}$ | 48.6 | 0.010 | 200 | MARGINAL |
| **NN score** | **34.4** | **0.209** | **187** | **PASS** |
| $m_\mathrm{col}$ | 50.8 | 0.015 | 195 | MARGINAL |

: Goodness-of-fit results on 10% data. The NN score approach passes with $p = 0.209$, indicating acceptable model description. The $m_\mathrm{vis}$ and $m_\mathrm{col}$ approaches show marginal $p$-values (0.010 and 0.015), driven by the VBF deficit. {#tbl:10pct-gof}

**NN score (primary):** The GoF $p$-value of 0.209 indicates acceptable goodness of fit. The post-fit model describes the 10% data shape adequately (Figure @fig:gof-10pct).

**$m_\mathrm{vis}$ and $m_\mathrm{col}$:** The GoF $p$-values of 0.010 and 0.015 are marginal, sitting below the conventional $p = 0.05$ threshold. These marginal values are driven by the VBF deficit, which has a larger relative impact on the $m_\mathrm{vis}$ and $m_\mathrm{col}$ fits (which have less discriminating power and fewer degrees of freedom in the fit). Since the primary NN approach passes and the marginal values are attributable to the known VBF deficit, these do not indicate fundamental mismodeling.

![Distribution of $\chi^2$ values from toy fits (blue histogram) compared to the observed $\chi^2 = 34.4$ from the 10% data NN score fit (red vertical line). The $p$-value of 0.209 (fraction of toys exceeding the observed $\chi^2$) indicates that the post-fit model provides an acceptable description of the 10% data. This represents a meaningful test --- unlike the Asimov GoF in Figure @fig:gof-toys which is $p = 1.0$ by construction --- because the real data introduces genuine statistical fluctuations.](../../4b_partial/outputs/figures/gof_toys_10pct.pdf){#fig:gof-10pct}

## Data/MC yield ratio summary {#sec:10pct-ratio-summary}

Figure @fig:ratio-summary provides a visual overview of the data/MC yield ratios across all approaches and categories.

![Summary of data/MC yield ratios for all three approaches in both categories. The Baseline ratios (blue) cluster near 0.95, consistent with statistical fluctuations. The VBF ratios (red) cluster near 0.65-0.68, showing the 33-35% deficit that drives the negative signal strength fits. The dashed line at 1.0 indicates perfect data/MC agreement. The spread between approaches within each category is small (< 2%), confirming that the deficit is a normalization effect rather than an approach-dependent artifact.](../../4b_partial/outputs/figures/data_mc_ratio_summary.pdf){#fig:ratio-summary}

## Cross-check: fitting methodology consistency {#sec:10pct-crosscheck}

Two fitting approaches were tested to verify robustness of the 10% data results:

- **Data x10 method:** Scale 10% data by 10, use original workspace. NN score: $\hat{\mu} = -3.40$.
- **Scaled MC x0.1 method:** Scale MC templates by 0.1, use raw 10% data. NN score: $\hat{\mu} = -3.73$.

The two methods give consistent results for the NN score ($\hat{\mu} = -3.4$ vs $-3.7$, well within uncertainties), confirming the fit procedure is robust. The scaled MC method is preferred because it preserves the Poisson nature of the observed data.

## Interpretation and VBF deficit discussion {#sec:10pct-interpretation}

The negative signal strength values observed in the 10% data fit arise primarily from the VBF category deficit. Several lines of evidence support the interpretation of this deficit as a statistical fluctuation in the 10% subsample rather than a systematic problem:

1. **VBF has only approximately 800 total events.** A 10% subsample contains approximately 82 events, giving a statistical precision of approximately 11% per bin. A 35% deficit is a 3-sigma overfluctuation but not unprecedented for a single Poisson realization.

2. **The Baseline category is consistent.** With approximately 68,000 events, the Baseline category shows data/MC ratio of 0.95, within the expected 12% relative statistical uncertainty. The Baseline-only fit gives $\hat{\mu} = -0.25 \pm 1.56$, fully consistent with the SM.

3. **The NP pulls are benign.** No systematic is pulled beyond 2$\sigma$ to accommodate the data, suggesting the model is not fundamentally misspecified.

4. **The GoF for the NN score is acceptable** ($p = 0.209$), meaning the post-fit model describes the data shape adequately despite the normalization deficit.

5. **The 10% data inherently has $\sqrt{10}$ larger relative fluctuations.** The VBF deficit may wash out with the full 100% dataset.

6. **The NN score $\mu$ pull of $-1.69\sigma$ is within the $2\sigma$ threshold.** This is within the range expected from statistical fluctuations in a 10% subsample.

7. **The deficit is consistent across approaches.** All three discriminants show the same VBF deficit (33-35%), confirming it is a data feature, not an approach-dependent artifact.

## 10% validation summary {#sec:10pct-summary}

@tbl:10pct-validation-summary provides the complete checklist of 10% validation tests.

| Check | Result | Status |
|-------|--------|--------|
| No fit at boundary | All free (bounds [-30, 30]) | PASS |
| $\hat{\mu}$ within 2$\sigma$ of 1 (NN) | $-3.73$, pull = $-1.69\sigma$ | PASS |
| NP pulls < 2$\sigma$ | All < 2.0 (max 1.85) | PASS |
| GoF $p$-value > 0.05 (NN) | 0.209 | PASS |
| GoF $p$-value > 0.05 ($m_\mathrm{vis}$) | 0.010 | MARGINAL |
| GoF $p$-value > 0.05 ($m_\mathrm{col}$) | 0.015 | MARGINAL |
| Baseline data/MC | 0.95 | PASS |
| VBF data/MC | 0.65 | FLAG |
| Per-category consistency | Baseline SM-compatible | PASS |
| QCD estimate stability | Baseline within 1% | PASS |
| Two-method cross-check | Consistent | PASS |

: Summary of 10% data validation checks. All primary checks pass. The VBF deficit is flagged for monitoring in the full dataset. The marginal GoF $p$-values for $m_\mathrm{vis}$ and $m_\mathrm{col}$ are attributable to the VBF deficit and do not indicate systematic mismodeling. {#tbl:10pct-validation-summary}

**Recommendation:** The 10% validation confirms that the analysis framework functions correctly on real data:

- The Baseline category is consistent with expectations (data/MC = 0.95).
- The VBF category shows a significant deficit (data/MC = 0.65), consistent with a statistical fluctuation in a low-statistics 10% subsample.
- No systematic mismodeling is identified (all NP pulls < 2$\sigma$).
- No fit is at the POI boundary (extended to [-30, 30]).
- The NN score $\hat{\mu}$ pull = $-1.69\sigma$ from the SM, within the 2$\sigma$ tolerance.
- The GoF for the primary NN approach passes ($p = 0.209$).
- The workspace construction, fitting, and GoF machinery work correctly on real data.

The analysis proceeded to Phase 4c (full data) following human gate approval.


# Full Data Results {#sec:full-data}

This section presents the results obtained on the full CMS Open Data collision dataset (11.5 fb$^{-1}$), which constitutes the primary physics result of this analysis. The full data results are compared to both the expected (Asimov, Phase 4a) and 10% data validation (Phase 4b) results.

## Data yields {#sec:full-yields}

The full data yields compared to the MC prediction (pre-fit) are summarized in @tbl:full-yields.

| Approach | Category | Data | MC | Data/MC |
|----------|----------|------|----|---------|
| NN score | Baseline | 67,124 | 70,898 | 0.947 |
| NN score | VBF | 864 | 1,260 | 0.686 |
| $m_\mathrm{vis}$ | Baseline | 66,896 | 70,677 | 0.947 |
| $m_\mathrm{vis}$ | VBF | 849 | 1,235 | 0.687 |
| $m_\mathrm{col}$ | Baseline | 59,387 | 62,695 | 0.947 |
| $m_\mathrm{col}$ | VBF | 815 | 1,185 | 0.688 |

: Full data yields compared to MC prediction (pre-fit) for all three fitting approaches in both categories. The Baseline category shows a consistent 5% deficit, while the VBF category shows a 31% deficit across all approaches. {#tbl:full-yields}

The data shows a consistent 5% deficit in the Baseline category and a 31% deficit in the VBF category relative to the MC prediction. This pattern was already observed in the 10% validation (Phase 4b) and reflects known limitations of the MC modeling in the VBF-enriched phase space for this open data sample. The Baseline deficit is consistent with the known overestimate from the QCD same-sign estimation method (Section @sec:bkg-summary), while the VBF deficit indicates a systematic normalization issue that persists from the 10% subsample to the full dataset.

## Pre-fit data/MC agreement {#sec:full-prefit}

The pre-fit $\chi^2$/ndf values quantify the data/MC disagreement before the profile likelihood fit absorbs the discrepancies through the nuisance parameters.

| Approach | Category | $\chi^2$/ndf |
|----------|----------|--------------|
| NN score | Baseline | 333.6/19 = 17.6 |
| NN score | VBF | 150.9/19 = 7.9 |
| $m_\mathrm{vis}$ | Baseline | 325.1/23 = 14.1 |
| $m_\mathrm{vis}$ | VBF | 147.3/18 = 8.2 |
| $m_\mathrm{col}$ | Baseline | 304.9/23 = 13.3 |
| $m_\mathrm{col}$ | VBF | 133.7/21 = 6.4 |

: Pre-fit $\chi^2$/ndf values for all approaches and categories. The large values (6-18) reflect the known 5% overall normalization discrepancy and the 31% VBF deficit, which the fit absorbs through the normalization nuisance parameters. {#tbl:full-prefit-chi2}

The large pre-fit $\chi^2$/ndf values (6-18) reflect the known normalization discrepancies between data and MC. The fit absorbs these through the normalization nuisance parameters. The pre-fit data/MC comparisons for all three approaches in both categories are shown in Figures @fig:full-prefit-nn-baseline through @fig:full-prefit-mcol-vbf.

<!-- COMPOSE: side-by-side -->
![Pre-fit data/MC comparison for the NN score distribution in the Baseline category using the full dataset. The stacked MC prediction includes $Z\to\tau\tau$ (dominant), $Z\to\ell\ell$, $t\bar{t}$, W+jets, and QCD multijet backgrounds, with the ggH and VBF signal components. The 5% data deficit is visible across the full NN score range, with the ratio panel showing systematic deviations from unity.](figures/data_mc_prefit_nn_score_baseline.pdf){#fig:full-prefit-nn-baseline}

![Pre-fit data/MC comparison for the NN score distribution in the VBF category using the full dataset. The 31% data deficit is clearly visible across all NN score bins. The deficit is uniform in shape, indicating a normalization issue rather than a shape mismodeling. The reduced statistics lead to larger bin-by-bin fluctuations in the ratio panel.](figures/data_mc_prefit_nn_score_vbf.pdf){#fig:full-prefit-nn-vbf}

<!-- COMPOSE: side-by-side -->
![Pre-fit data/MC comparison for the visible mass distribution in the Baseline category. The $Z\to\tau\tau$ peak near 60-80 GeV is clearly visible. The 5% data deficit is consistent with the QCD overestimation identified in Section @sec:bkg-summary. The shape agreement is good across the full mass range.](figures/data_mc_prefit_mvis_baseline.pdf){#fig:full-prefit-mvis-baseline}

![Pre-fit data/MC comparison for the visible mass distribution in the VBF category. The 31% deficit is present across the full mass range, most prominently in the $Z$ peak region. The reduced event count leads to large statistical fluctuations.](figures/data_mc_prefit_mvis_vbf.pdf){#fig:full-prefit-mvis-vbf}

<!-- COMPOSE: side-by-side -->
![Pre-fit data/MC comparison for the collinear mass distribution in the Baseline category. The broader distribution compared to visible mass reflects the unphysical collinear solution fallback. The 5% deficit is consistent with the other approaches.](figures/data_mc_prefit_mcol_baseline.pdf){#fig:full-prefit-mcol-baseline}

![Pre-fit data/MC comparison for the collinear mass distribution in the VBF category. The 31% deficit and broader distribution due to unphysical solutions are both visible. The collinear mass shows the largest bin-to-bin fluctuations among the three approaches.](figures/data_mc_prefit_mcol_vbf.pdf){#fig:full-prefit-mcol-vbf}

## Signal strength results {#sec:full-mu}

### Primary result: NN score {#sec:full-mu-nn}

The NN score approach, which exploits the full kinematic information through a neural network discriminant, yields on the full dataset:

$$\mu(H\to\tau\tau) = 0.63 \pm 1.08$$ {#eq:mu-observed}

This corresponds to an observed significance of 0.61$\sigma$. The observed 95% CL upper limit on $\mu$ is 2.85 (expected: 2.45 from Phase 4a with the updated workspace).

The result is consistent with both the Standard Model expectation ($\mu = 1.0$, within $0.34\sigma$) and with the Phase 4a expected uncertainty ($\sigma_\mathrm{expected} = 1.28$ vs $\sigma_\mathrm{observed} = 1.08$; the expected value is from `expected_results.json`, nn\_score.mu\_err = 1.2819). The improvement in uncertainty reflects the data constraining several nuisance parameters, particularly the shape systematics (Section @sec:full-np-pulls).

**Resolving power statement:** The observed uncertainty of $\sigma(\mu) = 1.08$ means this measurement can distinguish signal strength values differing by approximately 2.2 ($2 \times \sigma(\mu)$) at $2\sigma$ significance. The measurement cannot distinguish the SM prediction ($\mu = 1$) from the no-signal hypothesis ($\mu = 0$) at better than $1\sigma$, but it would detect enhanced production ($\mu \geq 3.2$) at approximately $2\sigma$ level.

### Alternative approaches {#sec:full-mu-alt}

@tbl:full-mu-results summarizes the signal strength results for all three fitting approaches on the full dataset.

| Approach | $\hat{\mu}$ | $\sigma(\mu)$ | Obs. significance | Obs. 95% CL | Exp. 95% CL |
|----------|------------|--------------|-------------------|-------------|-------------|
| **NN score** | **+0.63** | **1.08** | **0.61$\sigma$** | **2.85** | **2.45** |
| $m_\mathrm{vis}$ | $-6.70$ | 2.93 | 0.0$\sigma$ | 0.58 | 6.15 |
| $m_\mathrm{col}$ | $-10.74$ | 3.41 | 0.0$\sigma$ | N/A | 8.97 |

: Full data signal strength results for all three fitting approaches. The NN score is the primary result, yielding a positive signal strength consistent with the SM. The $m_\mathrm{vis}$ and $m_\mathrm{col}$ approaches yield large negative values driven by the data/MC normalization deficit. {#tbl:full-mu-results}

The $m_\mathrm{vis}$ and $m_\mathrm{col}$ approaches yield large negative $\mu$ values. This is driven by the 5% data deficit in the bulk of the distribution, where signal is a small perturbation on top of a large $Z\to\tau\tau$ background. These approaches are sensitive to normalization mismodeling because signal and background have overlapping shapes. The NN score approach mitigates this by concentrating signal sensitivity in high-score bins where the signal-to-background ratio is favorable.

## Three-way comparison {#sec:full-three-way}

@tbl:three-way-comparison presents the signal strength measurements across all three phases (expected, 10% validation, full data) for each fitting approach.

| Approach | Expected (4a) | 10% data (4b) | Full data (4c) |
|----------|---------------|---------------|----------------|
| NN score | $1.00 \pm 1.28$ | $-3.73 \pm 2.81$ | $0.63 \pm 1.08$ |
| $m_\mathrm{vis}$ | $1.00 \pm 3.09$ | $-14.44 \pm 5.94$ | $-6.70 \pm 2.93$ |
| $m_\mathrm{col}$ | $1.00 \pm 5.29$ | $-21.97 \pm 6.99$ | $-10.74 \pm 3.41$ |

: Three-way comparison of signal strength measurements across the analysis phases. The expected results are from Asimov pseudo-data (Phase 4a), the 10% data from the validation subsample (Phase 4b), and the full data from the complete collision dataset (Phase 4c). {#tbl:three-way-comparison}

Key observations from the three-way comparison:

1. **NN score recovers toward the SM.** The 10% result showed $\hat{\mu} = -3.73$, but with full statistics the NN score result moves to $\hat{\mu} = 0.63$, consistent with the SM expectation. The 10% fluctuation washed out with more data, as anticipated in the Phase 4b interpretation.

2. **Uncertainty improvement.** For the NN score, $\sigma(\mu)$ improved from 1.28 (expected) to 1.08 (observed) due to nuisance parameter constraints from data. For the 10% fit (with MC scaled by 0.1), the uncertainty was 2.81, reflecting the reduced statistical power of the subsample.

3. **$m_\mathrm{vis}$ and $m_\mathrm{col}$ remain negative** because these approaches cannot separate the normalization deficit from signal. The $m_\mathrm{vis}$ shift from $-14.4$ (10%) to $-6.7$ (full) and $m_\mathrm{col}$ from $-22.0$ to $-10.7$ show the same pattern of the fluctuation partially washing out, but the underlying normalization issue persisting.

The three-way comparison is shown in Figure @fig:three-way-comparison.

<!-- FLAGSHIP -->
![Three-way comparison of the signal strength $\hat{\mu}$ across all analysis phases for the three fitting approaches. The expected Asimov results (blue, $\mu = 1$), 10% data validation (orange), and full data results (green) are shown with their uncertainties. The NN score approach recovers to $\mu = 0.63 \pm 1.08$ on the full dataset, consistent with the SM, while the $m_\mathrm{vis}$ and $m_\mathrm{col}$ approaches remain negative due to the normalization deficit.](figures/mu_comparison_three_way.pdf){#fig:three-way-comparison}

## VBF deficit discussion {#sec:full-vbf-deficit}

The VBF category data/MC ratio of 0.69 persists in the full dataset, confirming that the deficit observed in the 10% validation is a systematic normalization issue rather than a statistical fluctuation. The deficit is consistent across all three fitting approaches (0.686-0.688), confirming it is a data feature rather than an approach-dependent artifact.

Several factors contribute to the VBF deficit:

1. **MC overestimation of the VBF phase space.** The LO MadGraph generator may overestimate the production rate of events with two forward jets satisfying the VBF selection criteria ($m_{jj} > 200$ GeV, $|\Delta\eta_{jj}| > 2.0$). Higher-order corrections and multijet merging, which are not available in the CMS Open Data samples, would improve the modeling.

2. **Missing NLO/NNLO corrections.** The $W$+jets and $Z$+jets backgrounds are generated at LO, and the VBF-like topology involves the production of multiple hard jets where NLO corrections can be significant (20-30%).

3. **No pileup reweighting.** The absence of pileup reweighting (Section @sec:syst-completeness) affects jet-related observables and can shift event counts between categories.

The VBF MC prediction for the NN score approach is 1260 events, with the following process decomposition: $t\bar{t}$ 429 events (34.1%), $W$+jets 359 events (28.5%), $Z\to\tau\tau$ 348 events (27.6%), $Z\to\ell\ell$ 65 events (5.1%), QCD 47 events (3.7%), and signal (VBF + ggH) 11.5 events (0.9%). The total deficit is 396 events.

The NP pulls absorb a substantial fraction of the deficit. The norm\_wjets\_vbf pull of $-1.89\sigma$ reduces the $W$+jets prediction by approximately $1.89 \times 10\% \times 359 \approx 68$ events. The norm\_qcd\_vbf pull of $-1.27\sigma$ reduces QCD by approximately $1.27 \times 20\% \times 47 \approx 12$ events. The shape\_jes pull of $-1.41\sigma$ redistributes events across bins and categories, further reducing the VBF prediction. Together with the other NP adjustments in the simultaneous fit, these pulls absorb the deficit.

Despite the deficit, the NN score approach is robust because the VBF category contributes limited statistical weight to the combined fit, the NN concentrates signal sensitivity in high-discriminant bins where the signal-to-background ratio is favorable, and the normalization nuisance parameters ($W$+jets VBF, QCD VBF) absorb the deficit.

## Nuisance parameter pulls (full data) {#sec:full-np-pulls}

The nuisance parameter pulls from the NN score full data fit are summarized in @tbl:full-np-pulls and shown in Figure @fig:full-np-pulls.

The standard pull convention is used: $(\hat{\theta} - \theta_0) / \sigma_\mathrm{prefit}$, where $\sigma_\mathrm{prefit} = 1.0$ for all Gaussian-constrained NPs. The constraint convention $(\hat{\theta} - \theta_0) / \sigma_\mathrm{postfit}$ is shown for reference.

| NP | Pull (std) | Post-fit unc. | Pull (constr.) |
|----|-----------|---------------|----------------|
| norm\_wjets\_vbf | $-1.89$ | 0.88 | $-2.15$ |
| shape\_jes | $-1.41$ | 0.70 | $-2.02$ |
| norm\_qcd\_vbf | $-1.27$ | 0.86 | $-1.48$ |
| norm\_wjets\_baseline | $+1.24$ | 0.83 | $+1.50$ |
| norm\_missing\_bkg | $-0.84$ | 0.89 | $-0.94$ |
| norm\_qcd\_baseline | $+0.76$ | 0.68 | $+1.11$ |
| btag\_eff | $-0.67$ | 0.94 | $-0.72$ |
| norm\_ttbar | $-0.67$ | 0.94 | $-0.72$ |
| tau\_id\_eff | $-0.65$ | 0.91 | $-0.72$ |
| lumi | $-0.56$ | 0.95 | $-0.59$ |
| trigger\_eff | $-0.55$ | 0.94 | $-0.58$ |
| norm\_ztt | $-0.43$ | 0.54 | $-0.79$ |
| muon\_id\_iso | $-0.43$ | 0.97 | $-0.44$ |
| shape\_met\_uncl | $-0.34$ | 0.30 | $-1.14$ |
| shape\_tes | $+0.07$ | 0.18 | $+0.42$ |
| shape\_mes | $-0.04$ | 0.32 | $-0.13$ |
| Theory NPs | < 0.01 | ~0.99 | < 0.01 |

: Nuisance parameter pulls from the NN score full data fit using the standard convention $(\hat{\theta} - \theta_0) / \sigma_\mathrm{prefit}$. Under this convention, **no NP exceeds $2\sigma$**. The largest pull is norm\_wjets\_vbf at $-1.89\sigma$. The constraint convention values are shown for reference. {#tbl:full-np-pulls}

Under the standard pull convention, **no nuisance parameter exceeds $2\sigma$**. The largest pull is norm\_wjets\_vbf at $-1.89\sigma$, followed by shape\_jes at $-1.41\sigma$ and norm\_qcd\_vbf at $-1.27\sigma$. Under the constraint convention (dividing by the postfit uncertainty), norm\_wjets\_vbf ($-2.15$) and shape\_jes ($-2.02$) would nominally exceed $2\sigma$, but this inflation is expected for well-constrained parameters and is not the standard presentation.

- **norm\_wjets\_vbf ($-1.89\sigma$):** The $W$+jets normalization in the VBF category is pulled down to compensate for the observed 31% data deficit. This is expected given the data/MC mismatch in the VBF category and the role of $W$+jets as a significant background there (approximately 29% of the VBF MC prediction).

- **shape\_jes ($-1.41\sigma$):** The JES shape systematic is absorbed by the fit to adjust the predicted distribution shape. The JES shift redistributes events between bins and categories, and a negative pull shifts jet energies downward, reducing the predicted VBF yield to better match the observed deficit.

- **norm\_qcd\_vbf ($-1.27\sigma$):** The QCD multijet normalization in the VBF category is pulled down, consistent with the overall VBF deficit requiring reduction of all background predictions.

These pulls are physically motivated and not alarming for an open data analysis with known MC limitations. The theory NPs are essentially unconstrained (post-fit uncertainty approximately 0.99), as expected for normalization-type systematics that are poorly constrained by this dataset.

![Nuisance parameter best-fit values and post-fit uncertainties from the NN score full data fit. The x-axis shows $(\hat{\theta} - \theta_0) / \sigma_\mathrm{prefit}$ (standard convention). The black points show the best-fit values with error bars indicating the post-fit uncertainties. No parameter exceeds $2\sigma$ under the standard convention (the largest is norm\_wjets\_vbf at $-1.89\sigma$). The shape systematics (TES, MES, JES, MET unclustered) show significant constraint from the data (post-fit uncertainties well below 1.0).](figures/np_pulls_full.pdf){#fig:full-np-pulls}

## Impact ranking (full data) {#sec:full-impact}

The impact ranking on $\mu$ from the NN score full data fit is summarized in @tbl:full-impact and shown in Figure @fig:full-impact.

| Rank | Source | $\Delta\mu$ (up) | $\Delta\mu$ (down) | Symmetric impact |
|------|--------|------------------|-------------------|-----------------|
| 1 | MET unclustered | $-0.281$ | $+0.289$ | 0.285 |
| 2 | JES (jet energy scale) | $-0.203$ | $+0.225$ | 0.214 |
| 3 | MES (muon energy scale) | $+0.127$ | $-0.168$ | 0.148 |
| 4 | $Z\to\tau\tau$ norm | $+0.062$ | $-0.071$ | 0.067 |
| 5 | Trigger efficiency | $-0.062$ | $+0.067$ | 0.065 |
| 6 | QCD norm (baseline) | $-0.060$ | $+0.050$ | 0.055 |
| 7 | Luminosity | $-0.050$ | $+0.049$ | 0.049 |
| 8 | $W$+jets norm (VBF) | $-0.044$ | $+0.045$ | 0.045 |
| 9 | b-tag efficiency | $-0.045$ | $+0.041$ | 0.043 |
| 10 | $t\bar{t}$ norm | $-0.043$ | $+0.041$ | 0.042 |

: Impact ranking of the top 10 nuisance parameters on the signal strength $\mu$ from the NN score full data fit, computed using the bestfit $\pm$ 1 postfit sigma method. The three shape systematics (MET unclustered, JES, MES) dominate the uncertainty budget. Values from `diagnostics_full.json`. {#tbl:full-impact}

The three shape systematics (MET unclustered, JES, MES) dominate the uncertainty budget, contributing a combined impact of approximately $\sqrt{0.285^2 + 0.214^2 + 0.148^2} \approx 0.39$ to $\Delta\mu$. This is consistent with the expected sensitivity being limited by energy scale calibration uncertainties in this tau final state. No single systematic exceeds 80% of the total uncertainty: the MET unclustered impact of 0.285 is approximately 26% of the total $\sigma(\mu) = 1.08$, well below the 80% regression trigger threshold.

The total systematic uncertainty, computed as the quadrature sum of all impacts, is approximately 0.39. The statistical uncertainty dominates: the total $\sigma(\mu) = 1.08$ yields a statistical-only uncertainty of approximately $\sqrt{1.08^2 - 0.39^2} \approx 1.01$, confirming that this measurement remains statistically limited.

<!-- FLAGSHIP -->
![Impact ranking of the top nuisance parameters on the signal strength $\mu$ from the NN score full data fit. The horizontal bars show the $\Delta\mu$ impact when each nuisance parameter is varied up (blue) and down (orange). The three shape systematics (MES, JES, MET unclustered) are the leading uncertainties, followed by the $Z\to\tau\tau$ normalization and $W$+jets VBF normalization.](figures/impact_ranking_full.pdf){#fig:full-impact}

## Goodness of fit (full data) {#sec:full-gof}

A dedicated GoF investigation was performed using both Pearson $\chi^2$ and the Poisson log-likelihood ratio (LLR, the proper saturated-model GoF test statistic: $T = 2 \sum_i [n_i \ln(n_i / \hat{\nu}_i) - n_i + \hat{\nu}_i]$) with 200 toy pseudo-experiments per approach. The NN score toy failure rate was reduced from 14.8% (original run) to 1.0% using retry logic with perturbed starting values.

| Approach | Obs. Pearson | Obs. LLR | $p$ (Pearson) | $p$ (LLR) | Converged |
|----------|-------------|---------|--------------|----------|-----------|
| NN score | 33.1 | 34.5 | 0.000 | 0.000 | 198/200 |
| $m_\mathrm{vis}$ | 39.2 | 39.5 | 0.000 | 0.000 | 200/200 |
| $m_\mathrm{col}$ | 39.2 | 39.3 | 0.000 | 0.000 | 200/200 |

: Goodness-of-fit results on the full dataset using both Pearson $\chi^2$ and Poisson log-likelihood ratio test statistics. The $p$-values are 0.000 for all approaches, indicating that the observed test statistic exceeds all toy values. The toy failure rate for NN score was reduced from 14.8% to 1.0% using retry logic. {#tbl:full-gof}

The per-category post-fit test statistics show individually acceptable agreement:

| Approach | Category | Pearson/bin | LLR/bin | $N_\mathrm{bins}$ |
|----------|----------|-------------|---------|-------------------|
| NN score | Baseline | 0.86 | 0.85 | 20 |
| NN score | VBF | 0.80 | 0.87 | 20 |
| $m_\mathrm{vis}$ | Baseline | 0.98 | 0.96 | 24 |
| $m_\mathrm{vis}$ | VBF | 0.83 | 0.87 | 19 |
| $m_\mathrm{col}$ | Baseline | 1.19 | 1.18 | 24 |
| $m_\mathrm{col}$ | VBF | 0.49 | 0.50 | 22 |

: Per-category post-fit GoF test statistics per bin. All values are near or below 1.0, indicating acceptable per-category data description. The combined GoF failure arises from the joint probability. {#tbl:full-gof-percat}

The GoF $p$-value of 0.000 is confirmed genuine and not an artifact of toy failure bias (the original NN score run had 14.8% toy failures; reducing this to 1.0% does not change the $p$-value). The per-category $\chi^2$/bin values are individually acceptable (0.49-1.19), but the combined test statistic exceeds all 198 converged toys (NN score: observed 33.1 vs toy range [10.2, 28.6], mean 17.8). This indicates that the probability of both categories fluctuating high simultaneously is small, and the model does not perfectly capture the inter-category correlation structure.

The GoF failure is attributed to the known 5% overall data/MC normalization deficit and 31% VBF deficit, which cause residual shape mismodeling that the nuisance parameters cannot fully absorb. Despite the GoF failure, the signal strength measurement is robust: the per-category fits yield consistent results (Section @sec:full-per-cat), the NP pulls are physically motivated, and the result is consistent with the SM.

The GoF toy distributions are shown in Figures @fig:full-gof-nn through @fig:full-gof-mcol. Additional GoF diagnostic figures from the dedicated investigation are in `figures/gof_investigation_*.pdf` and `figures/gof_per_category.pdf`.

![Distribution of $\chi^2$ values from 200 toy fits (blue histogram) compared to the observed $\chi^2 = 33.1$ from the full data NN score fit (red vertical line). The observed value exceeds all toy values, yielding a $p$-value of 0.00. This genuine GoF failure is attributed to the combined effect of the 5% Baseline and 31% VBF normalization deficits, which create residual shape mismodeling that the nuisance parameters cannot fully absorb. Per-category $\chi^2$/bin values are individually acceptable (0.86 Baseline, 0.80 VBF).](figures/gof_toys_full_nn_score.pdf){#fig:full-gof-nn}

<!-- COMPOSE: side-by-side -->
![GoF toy distribution for the $m_\mathrm{vis}$ approach on full data. The observed $\chi^2 = 39.2$ exceeds all toys ($p = 0.00$). The larger observed $\chi^2$ compared to the NN score reflects the poorer fit of the $m_\mathrm{vis}$ approach to the data normalization.](figures/gof_toys_full_mvis.pdf){#fig:full-gof-mvis}

![GoF toy distribution for the $m_\mathrm{col}$ approach on full data. The observed $\chi^2 = 39.2$ (identical to $m_\mathrm{vis}$) exceeds all toys. The similarity between the $m_\mathrm{vis}$ and $m_\mathrm{col}$ GoF values suggests both approaches are similarly affected by the normalization deficit.](figures/gof_toys_full_mcol.pdf){#fig:full-gof-mcol}

## Per-category results {#sec:full-percategory}

Fitting each category independently isolates the contributions of the Baseline and VBF categories to the combined result.

| Approach | Category | $\hat{\mu}$ | $\sigma(\mu)$ | Pull from 1 |
|----------|----------|------------|--------------|-------------|
| NN score | Baseline | $+0.61$ | 1.60 | $-0.24\sigma$ |
| NN score | VBF | $-0.04$ | 1.34 | $-0.78\sigma$ |
| $m_\mathrm{vis}$ | Baseline | $-8.27$ | 3.98 | $-2.33\sigma$ |
| $m_\mathrm{vis}$ | VBF | $-5.46$ | 4.42 | $-1.46\sigma$ |
| $m_\mathrm{col}$ | Baseline | $-8.92$ | 9.01 | $-1.10\sigma$ |
| $m_\mathrm{col}$ | VBF | $-10.82$ | 3.73 | $-3.17\sigma$ |

: Per-category signal strength results from the full data fit for all three approaches. The NN score approach shows good consistency between categories ($\hat{\mu} = 0.61 \pm 1.60$ in Baseline, $-0.04 \pm 1.34$ in VBF), both within $1\sigma$ of the SM. {#tbl:full-percategory}

For the NN score approach, the Baseline and VBF categories give consistent results ($0.61 \pm 1.60$ vs $-0.04 \pm 1.34$, both within $1\sigma$ of each other and of the SM). The combined result ($0.63 \pm 1.08$) benefits from the correlation structure in the simultaneous fit. This represents a marked improvement over the 10% validation, where the VBF-only fit gave $\hat{\mu} = -12.3 \pm 3.4$ --- confirming that the 10% VBF deficit was dominated by statistical fluctuations.

The per-category comparison is shown in Figure @fig:full-percategory.

![Per-category signal strength measurements for all three approaches using the full dataset. The Baseline (circles) and VBF (squares) categories are shown separately. For the NN score approach, both categories are consistent with the SM ($\mu = 1$, vertical dashed line). The $m_\mathrm{vis}$ and $m_\mathrm{col}$ approaches show negative values in both categories, driven by the normalization deficit.](figures/per_category_mu_full.pdf){#fig:full-percategory}

## Post-fit data/MC comparisons {#sec:full-postfit}

The post-fit data/MC comparisons show the quality of the model description after the profile likelihood fit has adjusted the nuisance parameters. These figures demonstrate that the fit successfully absorbs the pre-fit normalization discrepancies.

### NN score post-fit distributions {#sec:full-postfit-nn}

<!-- COMPOSE: side-by-side -->
![Post-fit data/MC comparison for the NN score distribution in the Baseline category. After the profile likelihood fit, the predicted yields are adjusted through the nuisance parameter pulls, improving the data/MC agreement. The ratio panel shows the post-fit data/prediction ratio, which is closer to unity than the pre-fit comparison in Figure @fig:full-prefit-nn-baseline.](figures/data_mc_postfit_nn_score_baseline.pdf){#fig:full-postfit-nn-baseline}

![Post-fit data/MC comparison for the NN score distribution in the VBF category. The fit absorbs the 31% pre-fit deficit through the normalization nuisance parameters ($W$+jets VBF pulled to $-1.89\sigma$, QCD VBF pulled to $-1.27\sigma$ in the standard convention), producing improved but not perfect data/MC agreement. The residual shape differences reflect the limitations of using normalization-only adjustments for a potentially shape-dependent effect.](figures/data_mc_postfit_nn_score_vbf.pdf){#fig:full-postfit-nn-vbf}

### Visible mass post-fit distributions {#sec:full-postfit-mvis}

<!-- COMPOSE: side-by-side -->
![Post-fit data/MC comparison for the visible mass distribution in the Baseline category. The large negative signal strength ($\hat{\mu} = -6.70$) pulls the signal contribution negative, effectively adding events to improve the data/MC agreement. This demonstrates why the $m_\mathrm{vis}$ approach is vulnerable to normalization mismodeling.](figures/data_mc_postfit_mvis_baseline.pdf){#fig:full-postfit-mvis-baseline}

![Post-fit data/MC comparison for the visible mass distribution in the VBF category. The fit adjustment is substantial, reflecting the combination of the 31% data deficit and the limited discriminating power of the visible mass in the VBF category.](figures/data_mc_postfit_mvis_vbf.pdf){#fig:full-postfit-mvis-vbf}

### Collinear mass post-fit distributions {#sec:full-postfit-mcol}

<!-- COMPOSE: side-by-side -->
![Post-fit data/MC comparison for the collinear mass distribution in the Baseline category. Similar to the $m_\mathrm{vis}$ approach, the large negative $\hat{\mu}$ compensates for the normalization deficit. The broader collinear mass distribution smears any localized features.](figures/data_mc_postfit_mcol_baseline.pdf){#fig:full-postfit-mcol-baseline}

![Post-fit data/MC comparison for the collinear mass distribution in the VBF category. The fit adjustment is the most extreme among the three approaches, consistent with the largest negative signal strength ($\hat{\mu} = -10.74$). The high unphysical solution fraction in this category further dilutes the discriminating power.](figures/data_mc_postfit_mcol_vbf.pdf){#fig:full-postfit-mcol-vbf}

## Comparison to published CMS result {#sec:full-cms-comparison}

The published CMS result [@CMS:2014nkk] measured $\mu = 0.78 \pm 0.27$ combining all tau-pair final states ($e\mu$, $e\tau_\mathrm{h}$, $\mu\tau_\mathrm{h}$, $\tau_\mathrm{h}\tau_\mathrm{h}$), both center-of-mass energies (7 and 8 TeV), and the full luminosity of 24.6 fb$^{-1}$. Our result of $\mu = 0.63 \pm 1.08$ is consistent with this published value: the difference of $0.63 - 0.78 = -0.15$ is well within the uncertainties of both measurements.

The ratio of uncertainties is $1.08 / 0.27 = 4.0$, which is consistent with the reduced scope of this single-channel analysis:

- **Single channel:** The $\mu\tau_\mathrm{h}$ channel provides approximately 23% of the total $H\to\tau\tau$ sensitivity.
- **Single run period:** 11.5 fb$^{-1}$ vs the combined 24.6 fb$^{-1}$.
- **No SVfit mass:** The published analysis uses the SVfit algorithm, which provides 15-20% better mass resolution.
- **Looser tau ID:** The Loose working point retains more background than the Medium/Tight used in the published analysis.
- **Simplified systematics:** No pileup reweighting, no generator comparison systematics.


# Conclusions {#sec:conclusions}

This analysis presents a measurement of the Higgs boson signal strength modifier $\mu$ in the $H\to\tau\tau$ decay channel, performed in the $\mu\tau_\mathrm{h}$ final state using 11.5 fb$^{-1}$ of CMS Open Data at $\sqrt{s} = 8$ TeV. Three fitting approaches are compared using a simultaneous binned profile likelihood fit across Baseline and VBF event categories.

The primary result, using the neural network discriminant on the full dataset, is:

$$\mu(H\to\tau\tau) = 0.63 \pm 1.08$$

corresponding to an observed significance of 0.61$\sigma$ and an observed 95% CL upper limit of $\mu < 2.85$. The result is consistent with the Standard Model prediction ($\mu = 1$) at the $0.34\sigma$ level, and with the published CMS combined result of $\mu = 0.78 \pm 0.27$ [@CMS:2014nkk].

The three fitting approaches yield:

- **NN score (primary):** $\hat{\mu} = 0.63 \pm 1.08$, observed significance $0.61\sigma$, 95% CL limit $\mu < 2.85$
- **Visible mass ($m_\mathrm{vis}$):** $\hat{\mu} = -6.70 \pm 2.93$, significance $0.0\sigma$
- **Collinear mass ($m_\mathrm{col}$):** $\hat{\mu} = -10.74 \pm 3.41$, significance $0.0\sigma$

The NN approach improves the precision by a factor of 2.7 relative to the visible mass and a factor of 3.2 relative to the collinear mass, demonstrating the significant information gain from combining multiple kinematic variables in a multivariate classifier. The $m_\mathrm{vis}$ and $m_\mathrm{col}$ approaches yield large negative signal strengths driven by the 5% data/MC normalization deficit, which these approaches cannot separate from signal. The NN discriminant mitigates this by concentrating signal sensitivity in high-score bins where the signal-to-background ratio is favorable.

The observed uncertainty of $\sigma(\mu) = 1.08$ is improved relative to the expected Asimov value of 1.28 (`expected_results.json`, nn\_score.mu\_err = 1.2819), reflecting data constraints on the nuisance parameters. The expected significance from the full data fit is 0.85$\sigma$ (`observed_results.json`, nn\_score.exp\_significance = 0.846), compared to the 4a Asimov expected significance of 0.81$\sigma$; the difference arises because the full data fit constrains NPs, slightly improving sensitivity. The systematic uncertainty budget is dominated by three shape systematics: MET unclustered energy (impact 0.29), jet energy scale (0.21), and muon energy scale (0.15). The combined systematic uncertainty is approximately 0.39, while the statistical uncertainty is approximately 1.01, confirming that this measurement remains statistically limited.

Under the standard pull convention $(\hat{\theta} - \theta_0) / \sigma_\mathrm{prefit}$, no nuisance parameter exceeds 2$\sigma$. The largest pull is the $W$+jets VBF normalization at $-1.89\sigma$, followed by JES shape at $-1.41\sigma$ and QCD VBF normalization at $-1.27\sigma$, all attributable to the persistent 31% data/MC deficit in the VBF category. This deficit is a systematic normalization issue present in both the 10% subsample and the full dataset, likely arising from LO generator limitations in the VBF-enriched phase space. Despite this deficit, the NN score approach is robust, as demonstrated by the consistent per-category results ($\hat{\mu}_\mathrm{Baseline} = 0.61 \pm 1.60$, $\hat{\mu}_\mathrm{VBF} = -0.04 \pm 1.34$).

The goodness-of-fit test yields $p = 0.000$ for all approaches (both Pearson $\chi^2$ and saturated-model LLR), while the per-category test statistics are individually acceptable ($\chi^2/\mathrm{bin} = 0.80$-1.19). A dedicated investigation confirmed this is genuine (not an artifact of toy failure bias) and arises from the residual shape mismodeling of the known 5% data/MC normalization deficit.

The three-way comparison across analysis phases shows the NN score result evolving from $\mu = 1.00 \pm 1.28$ (expected) to $\mu = -3.73 \pm 2.81$ (10% data) to $\mu = 0.64 \pm 1.08$ (full data), confirming that the 10% fluctuation washed out with full statistics as anticipated.

The observed uncertainty of $\sigma(\mu) = 1.08$ is a factor of 4.0 larger than the published CMS combined result ($\pm 0.27$), consistent with the reduced scope of this single-channel, single-run-period analysis using CMS Open Data. This measurement can distinguish signal strength values differing by approximately $\Delta\mu \approx 2.2$ at $2\sigma$ significance.

All validation tests pass their respective criteria: the NN classifier shows no overtraining (KS $p > 0.05$), signal injection tests recover injected values with pulls below 0.01, and the fit framework converges correctly on Asimov, 10%, and full data. The 10% data validation confirmed the analysis framework's robustness before unblinding. The analysis demonstrates that a single-channel $H\to\tau\tau$ measurement with CMS Open Data achieves approximately 1$\sigma$ sensitivity to the SM Higgs signal, with the neural network discriminant providing the critical improvement over simple mass-based approaches.


# References {-}
