# Phase 1 Constructive Review: H->tautau Strategy

**Reviewer role:** Constructive reviewer
**Date:** 2026-03-24
**Artifact reviewed:** `phase1_strategy/outputs/STRATEGY.md`
**Supporting documents:** `experiment_log.md`, `conventions/search.md`, `prompt.md`

---

## Overall Assessment

The strategy document is thorough and well-organized, covering all required
deliverables: physics motivation, sample inventory, selection approaches,
systematic plan with conventions enumeration, reference analysis table, and
flagship figures. The four-approach fitting strategy is ambitious and, if
executed well, provides genuine physics insight into information recovery
in the H->tautau channel. However, there are several issues ranging from
a potentially misleading sensitivity framing to practical concerns about
the four-approach workload and some methodological gaps. A journal referee
would return this strategy for clarification on several points before
proceeding.

---

## Category A Issues (Must Resolve)

### A1. Sensitivity framing is misleading

The executive summary says the analysis "searches for the Standard Model
Higgs boson" and the observable is the "signal strength modifier mu."
Section 2.1 acknowledges "expected sensitivity is substantially less than
the full CMS result" but never quantifies this. A back-of-envelope
estimate is essential:

- Expected signal after selection: O(10-100) events (stated in Section 4.1).
- Dominant background (Z->tautau): ~60-70% of a much larger selected sample.
- The published full combination (all channels, 7+8 TeV, 24.6 fb-1) achieved
  mu = 0.78 +/- 0.27. This single channel (mu-tau_h only) at a fraction of
  the luminosity (11.5 fb-1 at 8 TeV alone) with inflated systematic
  uncertainties (10-15% Z normalization vs. 3.3% in R1) will have expected
  uncertainty on mu of order 1-2 or larger.

The strategy must include a quantitative expected sensitivity estimate --
even a rough one based on S/sqrt(B) in the signal mass window. Without
this, later phases cannot evaluate whether the analysis has resolving
power or whether the four approaches can be meaningfully compared.
An analysis with sigma(mu) >> 1 cannot discriminate between physics
models; it can only set a weak upper limit. This must be stated honestly.

**Recommendation:** Add a section "Expected Sensitivity" with:
(1) an S/sqrt(B) estimate per category per approach, (2) a rough expected
uncertainty on mu from a simplified likelihood, and (3) an explicit
statement of what "success" looks like for this analysis (e.g., "We expect
to set an observed upper limit of mu < X at 95% CL and demonstrate the
relative sensitivity gains from ML approaches").

### A2. Cross-section values used for MC normalization are not internally consistent

Section 3.2 states the ggH cross-section is 19.6 pb and the VBF
cross-section is 1.55 pb. These are the inclusive production cross-sections,
NOT sigma x BR. But the table shows sigma x BR values in the discussion
(~1.23 pb and ~0.097 pb in Section 4.1), and the normalization weight
formula is w = sigma x L / N_gen.

The critical question: do the tutorial skim files already include the
BR(H->tautau) in the generated sample (i.e., are these fully-hadronized
H->tautau events, such that sigma = sigma_production is the correct
normalization because ALL generated events decay to tautau)? Or is the
sample inclusive Higgs decays, requiring sigma x BR?

The experiment log says "sigma x BR(H->tautau) implicitly in the
generator filter" (line 139 of STRATEGY.md), but this deserves explicit
verification. If the signal MC is exclusively H->tautau events (which it
almost certainly is, given the sample name "GluGluToHToTauTau"), then the
generator-level cross-section for normalization should be
sigma_production x BR(H->tautau), not sigma_production alone.

Using sigma_production = 19.6 pb without BR would overpredict the signal
by a factor of ~16. Using sigma_production x BR = 19.6 x 0.06256 = 1.23 pb
is correct if the sample is filtered to tautau only.

**This must be unambiguously resolved.** If the tutorial skim already
applies the correct weight (sigma = sigma_prod for a BR-filtered sample),
document this explicitly. If not, the normalization is wrong by an order
of magnitude.

### A3. The `conventions/search.md` file is written for e+e- (LEP) searches, not pp collisions

The strategy correctly notes (Section 9.1) that "the conventions are
written for e+e- searches" and maps to pp equivalents. However, this
mapping is incomplete and in some cases inappropriate:

- The "4-fermion backgrounds" row is mapped to "electroweak backgrounds"
  with a "Not applicable" status, but at the LHC, diboson production
  (WW, WZ, ZZ) IS a relevant background for H->tautau, contributing at
  the percent level. The dismissal is correct for this Open Data exercise
  (samples unavailable), but the mapping itself is wrong -- these are not
  "not applicable," they are "not available."
- The "ISR modeling -> PDF uncertainty" mapping loses the ISR physics:
  at the LHC, initial-state radiation (additional jets from ISR/FSR)
  directly affects category migration between Baseline and VBF.
  The strategy covers jet multiplicity variations (QCD radiation modeling
  row), but the explicit ISR jet modeling systematic is not called out
  as a separate source. The published CMS analysis includes
  parton shower (PS) ISR/FSR variations as shape systematics.
- The "beam energy -> PDF/alpha_s" mapping conflates two distinct physics
  effects: beam energy uncertainty (negligible at the LHC) and PDF
  uncertainty (significant). These should not be treated as equivalent.

**Recommendation:** Acknowledge that the conventions file is LEP-oriented
and that the mapping to pp is approximate. Add a dedicated "pp-specific
systematics" subsection that includes: (1) PS ISR/FSR scale variations
(if event weights are available; if not, document this as a limitation),
(2) underlying event modeling, (3) PDF uncertainty as its own category
(not mapped from "beam energy").

---

## Category B Issues (Should Address)

### B1. The four-approach strategy is over-specified for the available sensitivity

With O(10-100) signal events and sigma(mu) likely >> 1, the four fitting
approaches will produce results whose statistical uncertainties overlap
heavily. Comparing mu from four approaches when each has sigma(mu) ~ 2
tells you almost nothing about the relative merits of the approaches.

This is not a reason to abandon the multi-approach strategy (it IS the
physics question posed in the prompt), but the strategy should:
(a) acknowledge this quantitatively, (b) define what constitutes a
meaningful comparison even in the low-sensitivity regime (e.g., expected
limit comparison, Asimov significance comparison, not just observed mu),
and (c) prioritize the approaches so that if Phase 3/4 time runs short,
the most informative subset is completed first.

The strategy currently treats all four approaches with equal weight [D1].
A journal referee would ask: "If you can only publish two, which two?"

### B2. The QCD OS/SS ratio has two conflicting values

Section 7.3 states the OS/SS ratio is "~0.80 (as in the CMS tutorial)
or ~1.06 (as in the published CMS analysis)." These differ by 30% and
are on opposite sides of 1.0 -- one says OS < SS and the other says
OS > SS. This is not a minor discrepancy; it changes the sign of the
QCD normalization correction.

The strategy must commit to one value (or measure it from data) and
explain the discrepancy. The CMS tutorial value of 0.80 applied to
OS = R x SS data means the QCD in OS is LESS than in SS, which is
unusual for QCD dijet events (the OS/SS ratio for QCD is typically
slightly above 1 due to color flow effects). The tutorial may be
using SS/OS = 0.80 (i.e., the QCD OS is 1/0.80 = 1.25 times the SS),
or the labeling may be inverted.

**Recommendation:** Measure the OS/SS ratio from data in an anti-isolated
control region as the primary method. Use neither the tutorial nor
the published value blindly. Document the measurement procedure in the
strategy.

### B3. W+jets extrapolation from high-mT to low-mT assumes mT-independence of the fake rate

Section 7.2 defines the W+jets normalization from mT > 70 GeV and
extrapolates to mT < 30 GeV. The strategy acknowledges this in the
open issues (Section 16, item 5) but does not specify a validation
procedure beyond varying the mT boundary by +/-10 GeV.

The jet->tau_h fake rate depends on the event kinematics, and events
at high mT (genuine W+jets, on-shell W with high MET) have different
jet kinematics than events at low mT (off-shell W, lower MET, more
QCD-like). The W+jets shape in m_vis could differ substantially between
these regions.

**Recommendation:** Add an explicit validation requirement: compare the
W+jets MC m_vis shape in the high-mT and low-mT regions. If they differ
by more than a chi2/ndf threshold, the shape must be taken from the
low-mT MC prediction (not extrapolated from high-mT data), with only
the normalization determined from the high-mT sideband.

### B4. Z->tautau normalization uncertainty of 10-15% is large but unmotivated quantitatively

The strategy assigns 10-15% to cover "missing trigger turn-on effects
and the larger tau efficiency scale factors from the loosened tau ID [D7]."
This is reasonable directionally, but:

- The published analysis (R1) uses 3.3%. Going to 10-15% is a factor
  of 3-5 increase.
- The dominant background (Z->tautau, 60-70% of events) with a 10-15%
  normalization uncertainty means sigma(mu) has a floor from this
  systematic alone that is substantial.
- The Z normalization will likely be the dominant systematic. Per the
  methodology spec, "every systematic variation must be motivated by a
  measurement or published uncertainty."

Rather than pre-assigning 10-15%, the strategy should commit to MEASURING
the data/MC discrepancy in the Z peak region and using that measured
discrepancy (plus its statistical uncertainty) as the normalization
correction and uncertainty. If the measured data/MC ratio in the Z peak
is 0.95 +/- 0.05, then the uncertainty is 5%, not 10-15%.

**Recommendation:** Replace the fixed 10-15% with a measurement-driven
approach: "The Z->tautau normalization scale factor and its uncertainty
will be determined from the data/MC ratio in the Z peak region
(60-120 GeV visible mass). The uncertainty includes both the statistical
precision of this measurement and a systematic component from the
choice of mass window. If the measured uncertainty is less than 10%,
we do not inflate it to 10% -- we use the measured value."

### B5. Missing parton shower / underlying event systematics

The systematic plan does not include parton shower (PS) scale variations
(ISR/FSR), which are standard at the LHC and were included in both
reference analyses (R1, R2). With only MadGraph+Pythia6 available and
no alternative generators [L3], PS weights may not be stored in the
NanoAOD. If PS weights are available, they should be used. If not, this
should be documented as a limitation with a conservative uncertainty
assigned based on R1/R2 values.

**Recommendation:** Check whether the NanoAOD files contain PS weight
branches (e.g., `PSWeight`). If present, include PS ISR/FSR up/down
variations. If absent, add this to [L3] and assign a PS uncertainty
based on the published CMS analysis values.

### B6. No embedding or data-driven Z->tautau estimation considered

The published CMS analysis (R1, R2) uses an embedding technique for
Z->tautau estimation: Z->mumu events in data are selected, the muons
are replaced with simulated tau decays, producing a data-driven Z->tautau
template that inherits data conditions (pileup, trigger, detector response).
This is the gold standard for Z->tautau modeling at CMS.

The strategy does not mention embedding at all. While CMS Open Data may
not include embedded samples, the strategy should at least acknowledge
this technique's existence in the reference analyses and explain why
it is not used (presumably: no embedded samples available in Open Data).
This is relevant because the 10-15% Z normalization uncertainty is
largely compensating for the lack of embedding.

### B7. The "missing minor backgrounds" uncertainty [A3] is additive, not multiplicative

Section 4.2 assigns "+/-5% additional normalization uncertainty on the
total background" to cover single top, diboson, and rare processes.
But this is applied ON TOP of the individual background uncertainties,
meaning the total uncertainty is inflated beyond what the missing
backgrounds warrant. If the missing backgrounds are < 3%, a 5% envelope
is already conservative. But is this 5% correlated with or independent
of the individual background normalization uncertainties? This must be
specified, otherwise the fit will double-count.

---

## Category C Issues (Suggestions)

### C1. Consider a third category: boosted (1-jet, high pT Higgs)

The published CMS analysis (R1) uses three categories: 0-jet, 1-jet
(boosted), and VBF. The strategy collapses 0-jet and 1-jet into
"Baseline." A 1-jet boosted category (e.g., requiring one jet with
pT > 30 GeV and tau-pair pT > 100 GeV) would improve the
signal-to-background ratio for ggH production at the cost of splitting
statistics. Given the already marginal sensitivity, this may not help,
but the strategy should at least evaluate whether it is worth attempting
(e.g., estimate S/sqrt(B) in a potential boosted category).

### C2. Specify the NN training framework

The strategy mentions "a fully connected network with 2-3 hidden layers"
but does not specify the software framework (PyTorch, TensorFlow, scikit-learn).
Since the analysis uses pixi, the framework should be declared early
so it can be added to `pixi.toml`. Recommend PyTorch or scikit-learn
(MLPClassifier) for simplicity.

### C3. Define the collinear mass fallback strategy more precisely

Section 8.4 says "events with unphysical solutions use the visible mass
as a fallback." This creates a bimodal distribution where some events
have collinear mass and others have visible mass, potentially washing out
the mass resolution improvement. An alternative: use a hybrid variable
that smoothly transitions, or report the fraction of events with physical
solutions as a function of the true di-tau mass to understand where the
approximation works.

### C4. Consider the signal contamination in control regions

The high-mT control region for W+jets normalization (mT > 70 GeV) may
contain some Higgs signal (signal events where the muon is not from
the W decay of the tau chain but has high mT by fluctuation). Similarly,
the SS control region for QCD may contain some signal (sign-flipped events
are rare but nonzero). The strategy should estimate the signal
contamination in each CR and decide whether it needs to be subtracted.

### C5. Specify the pileup reweighting procedure

Section 9.1 mentions "vary pileup profile by +/-5% to assess impact"
but does not describe the baseline pileup reweighting procedure. The
MC must first be reweighted to match the data pileup profile (using
PV_npvs or the true number of interactions). The +/-5% variation is
on the data pileup profile used for reweighting. Clarify this.

### C6. The experiment log should include the literature review findings in more detail

The experiment log entries are good (timestamps, clear decisions) but
the literature review (entry at 01:52) only lists numbers without
context. For audit purposes, it would be helpful to note which specific
sections of the published papers informed which strategy decisions.

---

## Honest Framing Check

**Is the analysis telling the truth about what it can measure?**

Partially. The strategy acknowledges "expected sensitivity is substantially
less than the full CMS result" (Section 2.1) but never quantifies this.
The mu-tau_h channel alone at 8 TeV, with only 11.5 fb-1, without
embedding, without SVfit, with a loosened tau ID, and with inflated
systematics, is unlikely to achieve better than sigma(mu) ~ 1.5-2.
This means the analysis cannot make a statistically significant
observation of H->tautau; at best it can set an upper limit of
mu < ~3-4 at 95% CL.

This is not a problem per se -- the analysis prompt explicitly asks for
this exercise, and the four-approach comparison is genuinely interesting
even with low sensitivity. But the strategy must be honest about this
from the start. A reader who sees "searches for the Higgs boson" without
a sensitivity estimate might expect a result that this analysis cannot
deliver.

**The four-approach comparison:** This IS the interesting physics
question. Even with sigma(mu) ~ 2, comparing expected limits across
approaches (visible mass vs. NN vs. collinear mass vs. NN-regressed
MET mass) quantifies the information gain from each technique.
The strategy should reframe the analysis goal as: "We measure the signal
strength mu using four approaches and compare their sensitivities,
demonstrating the information recovery from ML techniques in a
realistic H->tautau analysis environment."

---

## Specific Findings on Strategy Components

### Categorization criteria
Well-justified. The VBF cuts (m_jj > 300, |Delta_eta_jj| > 2.5,
Zeppenfeld centrality) are standard and appropriate. The decision to
use two categories rather than three (collapsing 0-jet and 1-jet) is
reasonable given the statistics.

### W+jets data-driven normalization
The method is sound in principle (high-mT sideband, subtract non-W,
apply scale factor). See B3 for the shape extrapolation concern. The
validation in an intermediate-mT region (30-70 GeV) is appropriate.

### QCD same-sign estimation
Standard method. The OS/SS ratio ambiguity (B2) must be resolved.
The validation plan (positive bins, anti-isolated cross-check) is
appropriate. The shape uncertainty from comparing SS vs. anti-isolated
regions is a good practice.

### Systematic plan completeness
The conventions enumeration is thorough given the LEP-oriented
conventions file. The pp-specific additions (pileup, fake rate, trigger,
b-tagging) are appropriate. Missing: PS ISR/FSR (B5), embedding
acknowledgment (B6).

---

## Summary Verdict

The strategy is comprehensive and ambitious. The four-approach design
addresses a genuine physics question about information recovery. However,
three Category A issues must be resolved before proceeding:

1. **A1:** Add a quantitative sensitivity estimate and reframe the analysis
   goal honestly.
2. **A2:** Unambiguously resolve the signal cross-section normalization
   (sigma vs. sigma x BR).
3. **A3:** Acknowledge the LEP/pp conventions mismatch and complete the
   pp-specific systematic mapping.

The Category B issues (B1-B7) should be addressed to strengthen the
analysis; B2 (OS/SS ratio conflict) and B4 (Z normalization measurement
vs. assumption) are particularly important.

**Recommendation: ITERATE** -- resolve the A issues and address B2 and B4
before advancing to Phase 2.
