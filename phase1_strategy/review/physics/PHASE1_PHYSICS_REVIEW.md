# Phase 1 Physics Review: H->tautau Strategy (mu-tau_h, 8 TeV Open Data)

**Reviewer role:** Senior collaboration member, physics approval perspective
**Artifact reviewed:** `phase1_strategy/outputs/STRATEGY.md`
**Date:** 2026-03-24

---

## Overall Assessment

The strategy is thorough and well-structured. It correctly identifies the dominant backgrounds, proposes standard data-driven estimation methods for the reducible and instrumental backgrounds, and lays out four fitting approaches that provide a sensible comparison of analysis techniques. The reference analysis table is useful and the systematic plan is extensive.

However, several issues range from significant physics concerns to areas where the strategy is vague or internally inconsistent. A number of the systematic uncertainties appear inflated without clear motivation, which would mask the true sensitivity of the measurement and allow almost any result to be declared "consistent with the Standard Model." The strategy also has structural gaps in the treatment of the NN-based approaches that must be resolved before execution.

**Verdict: ITERATE.** The strategy cannot be approved as-is. The Category A items below must be addressed before proceeding to Phase 2.

---

## Findings

### (A) Must Resolve

#### A1. Over-specified systematic model risks making the measurement meaningless

The systematic plan lists 22+ nuisance parameters for a measurement with O(50-100) signal events in a single final state at 8 TeV with ~11.5 fb-1. For comparison, the full CMS evidence paper (R1, JHEP 05 (2014) 104) used a similar number of systematics but had ~20x the data (all final states, both 7 and 8 TeV, 24.8 fb-1). Several of the uncertainties here are substantially inflated relative to the reference analyses:

- **Tau ID efficiency: 10% vs. 6% (R1) and 5% (R2).** The justification is "loosened ID without official SFs," but loosening the ID working point does not automatically double the uncertainty. The uncertainty should be derived from the data/MC comparison in the Z peak region, not assigned a priori as a round number.
- **Z->tautau normalization: 10-15% vs. 3.3% (R1) and 4% (R2).** This is 3-4x the reference value. The stated justification ("missing trigger turn-on effects and larger tau efficiency scale factors") conflates multiple effects. If the Z normalization is a free parameter in the fit constrained by the Z peak sideband, then the uncertainty comes from the sideband fit, not from an a priori guess. And if it is not floated in the fit, a 15% prior on the dominant background will wash out almost any signal.
- **Trigger efficiency: 5%.** This is on top of the Z normalization uncertainty, which is already claimed to cover the trigger effects. This is double-counting.
- **Missing backgrounds: +/-5% on total background.** This covers processes contributing <3%, so a 5% blanket uncertainty is conservative by nearly 2x. Fine as a placeholder, but should not survive Phase 4.

The cumulative effect is a systematic uncertainty budget that will dominate the total uncertainty and render the signal strength measurement uninformative. The strategy must commit to deriving systematic uncertainties from data wherever possible (Z peak fit, mT sideband, SS region) rather than assigning round-number priors. If the derived uncertainties happen to be large, so be it -- but starting from inflated priors and then declaring "consistent with SM within uncertainties" is not a measurement.

**Required action:** (1) State explicitly which systematic uncertainties will be constrained by data in the fit vs. assigned as external priors. (2) Remove the double-counting between trigger efficiency and Z normalization. (3) Commit to deriving the Z normalization uncertainty from the Z peak data/MC comparison rather than assigning 10-15% a priori. (4) Commit to deriving the tau ID uncertainty from data rather than assigning 10% a priori.

#### A2. The NN-regressed MET approach (c) has no fallback for training failure

Approach (c) trains a neural network to regress generator-level MET from reconstructed quantities. This is a significantly harder regression task than the classification in approach (b). The strategy provides no:

- **Quantitative success criterion:** What MET resolution improvement constitutes "success" for the regression? If the NN-corrected MET has the same resolution as the uncorrected MET, approach (c) degenerates to approach (d). There must be a pre-defined metric (e.g., >20% improvement in MET resolution on the test set) below which approach (c) is abandoned.
- **Training sample strategy:** The regression target is generator-level MET. This is only available in MC. The MC MET resolution may not match data. How will the NN-corrected MET be validated in data?
- **Failure mode analysis:** If the NN learns MC-specific artifacts (e.g., detector simulation quirks not present in data), the "improved" mass variable will have data/MC mismodeling built in from the start. This is a qualitatively different risk from approach (b) where the NN is at least trained on the same features that will be validated.

**Required action:** Define a quantitative success criterion for approach (c), a validation plan in data (e.g., Z->tautau mass peak resolution as a benchmark), and an explicit downscope decision: if the criterion is not met, approach (c) is dropped and documented as a failed alternative.

#### A3. Cross-section values used for signal normalization are inconsistent

Section 3.2 states that MC samples are normalized using the CMS Open Data tutorial cross-sections, but signal interpretation uses YR4 values. Specifically:

- ggH: tutorial uses 19.6 pb, YR4 gives 21.39 pb -- a 9% difference.
- VBF: tutorial uses 1.55 pb, YR4 gives 1.600 pb -- a 3% difference.

Decision [D2] says "tutorial cross-sections for normalization, YR4 for signal interpretation." This is contradictory. The signal strength mu = sigma_obs / sigma_SM depends on what sigma_SM is. If the signal MC is weighted with the tutorial cross-section (19.6 pb) but the signal strength is defined relative to the YR4 cross-section (21.39 pb), then mu = 1 does not correspond to the Standard Model prediction in the fit -- it corresponds to 19.6/21.39 = 0.916 of the SM. The result would be biased by 8.4%.

**Required action:** Use a single, consistent set of cross-sections. If the YR4 values are the reference, normalize the signal MC to the YR4 cross-sections. Document the choice and ensure mu = 1 corresponds to the SM prediction by construction.

#### A4. The OS/SS ratio for QCD estimation is poorly constrained

Section 7.3 gives three different values for the QCD OS/SS ratio: ~0.80 (CMS tutorial), ~1.06 (published CMS analysis), and leaves the choice to Phase 2. These differ by >30%, which is not a rounding difference -- they reflect fundamentally different QCD compositions (the tutorial applies a simpler selection that may have a different fake composition).

More importantly, the strategy does not address the sign of the QCD background. If QCD_SS = N_data_SS - N_MC_SS is negative in some bins (acknowledged as a validation check in Section 7.3), the method breaks down. The strategy needs to state what happens when the SS subtraction goes negative: bin merging? Setting to zero? Using a smoothed template?

**Required action:** (1) Commit to measuring the OS/SS ratio in a QCD-enriched control region (anti-isolated sideband) rather than using a literature value. (2) Define the procedure for bins where QCD_SS < 0 after MC subtraction.

#### A5. The collinear mass fallback strategy biases approach (d)

Section 8.4 states that events with unphysical collinear approximation solutions (x < 0 or x > 1, which is 30-50% of events) use the visible mass as a fallback. This means approach (d) is not actually a collinear mass fit -- it is a mixture of collinear mass and visible mass, with the mixture fraction being signal/background-dependent (the fraction of unphysical solutions differs for signal and background).

This creates a composite observable with properties that are not straightforward to interpret. The shape systematics (tau energy scale, MET scale) will affect not only the mass values but also which events fall into the "physical" vs. "fallback" bins, creating a discontinuous systematic response.

**Required action:** (1) Document the expected fraction of unphysical solutions separately for signal and each background. (2) Consider alternatives to the visible mass fallback: truncating x to [epsilon, 1-epsilon], or using a different mass variable (e.g., the transverse mass) for unphysical events. (3) If the visible mass fallback is retained, demonstrate that the systematic variations produce smooth template changes (no discontinuities at the physical/unphysical boundary).

---

### (B) Should Address

#### B1. No expected sensitivity estimate

The strategy identifies the expected signal yield as "O(10-100) events" (Section 4.1) but provides no estimate of the expected signal strength uncertainty or significance. This is a fundamental gap. Without a rough expected sensitivity, there is no way to judge whether the analysis is feasible or whether the systematic budget is appropriate.

A back-of-the-envelope calculation: with ~60% of selected events being Z->tautau, ~20% W+jets, ~10% QCD, ~5% ttbar, and the signal at ~1% of the background level, S/sqrt(B) in the full m_vis spectrum is O(1). With categorization and an optimized NN discriminant, this might improve to O(1-2). So the expected uncertainty on mu is likely O(1), meaning the measurement can constrain mu to within +/-1 at best.

This should be stated explicitly. If the expected precision is O(1) on mu, then the measurement is a ~1-sigma level exercise and the four-approach comparison is the actual scientific contribution, not the signal strength value itself.

**Required action:** Provide a rough expected sensitivity estimate (S/sqrt(B) or expected sigma(mu)) for at least the visible mass approach. This calibrates expectations and informs the systematic budget -- if sigma(mu) ~ 1, then sub-5% systematics are irrelevant and the effort should focus on the dominant uncertainties.

#### B2. NN training on MC with signal weight equalization is non-standard

Section 8.2 states the NN is trained with "weight events to equalize signal and background contributions." This is a common practice but interacts poorly with the fact that signal MC is generated without luminosity weighting. If the training uses unweighted events (all signal events with weight 1, all background events with weight 1 rescaled to match), the NN learns the generator-level kinematic distributions, not the luminosity-weighted distributions.

This is actually fine for a classifier -- you want to learn the kinematic differences, not the rate differences. But the strategy should be explicit about this and clarify that the luminosity weighting is applied only when constructing the templates (not during NN training).

Additionally, using all signal MC before luminosity weighting means the NN training set has O(500k) signal events but the actual expected signal in data is O(50-100). This is not itself a problem, but the strategy should note that the NN is trained in a regime where signal kinematics are well-sampled but the signal/background ratio in the training is artificial.

**Required action:** Clarify the NN training weight scheme: (1) training uses generator-level weights (not luminosity-scaled), (2) template construction uses luminosity-scaled weights. Note the artificial S/B ratio in training and confirm this does not bias the discriminant.

#### B3. VBF category jet pT threshold inconsistency

Section 5.5 defines jet selection as pT > 30 GeV. Section 6.1 defines VBF as "Leading jet pT > 30 GeV, Subleading jet pT > 30 GeV." The CMS evidence paper (R1) used asymmetric cuts: leading jet pT > 30 GeV, subleading jet pT > 30 GeV, but with category-dependent thresholds. At 8 TeV with limited statistics, a symmetric 30 GeV threshold may be appropriate, but the strategy should note that this was a deliberate choice and not simply a default.

More importantly, the VBF selection requires m_jj > 300 GeV and |Delta_eta_jj| > 2.5. The CMS evidence paper used m_jj > 500 GeV and |Delta_eta_jj| > 3.5 for their "tight VBF" category, and m_jj > 200 GeV for their "loose VBF" category. The choice of 300 GeV and 2.5 is intermediate and should be motivated: is this optimized for S/sqrt(B), or is it a compromise between purity and statistics?

**Required action:** Motivate the VBF selection thresholds (m_jj > 300, |Delta_eta| > 2.5) relative to the reference analysis values. State whether these will be optimized in Phase 2/3 or are fixed.

#### B4. Zeppenfeld centrality requirement may kill VBF statistics

Section 6.1 requires "Both taus between the jets in eta (Zeppenfeld centrality)." With the limited statistics of a single final state in Open Data, this additional requirement on top of m_jj and Delta_eta_jj may reduce the VBF category to O(single digits) of events, making the category statistically useless.

The CMS evidence paper used centrality as one input to the MVA, not as a hard cut. Applying it as a cut is more restrictive and should be justified by showing it improves S/sqrt(B) despite the statistical penalty.

**Required action:** Estimate the VBF category yield with and without the Zeppenfeld centrality requirement. If the yield drops below ~20 events, remove the requirement or use it only as an NN input.

#### B5. W+jets extrapolation assumes mT-independence of fake rate

The W+jets data-driven method (Section 7.2) extrapolates from mT > 70 GeV to mT < 30 GeV. The implicit assumption is that the visible mass shape of W+jets events is the same in the high-mT and low-mT regions. This is not guaranteed: the jet-to-tau fake rate may depend on the event topology, which correlates with mT.

The strategy mentions a systematic from varying the mT boundary by +/-10 GeV, but this tests the stability of the normalization, not the shape. A shape comparison between the high-mT and intermediate-mT (30-70 GeV) regions would be more informative.

**Required action:** Add a shape validation: compare the W+jets m_vis distribution in the high-mT (>70 GeV) and intermediate-mT (30-70 GeV) regions. If they differ significantly, the W+jets shape must be taken from the low-mT region (e.g., using the SS high-mT sideband after QCD subtraction, or applying mT-dependent corrections).

#### B6. Single mu parameter for ggH and VBF conflates production modes

Decision [D11] states: "The ggH and VBF signal contributions float with a common mu parameter." This is a strong assumption. The Higgs coupling to gluons (via the top loop) and the Higgs coupling to W/Z (via VBF) test different aspects of the Standard Model. If there were a new physics contribution modifying the gluon fusion cross-section but not VBF (or vice versa), a common mu would average over the discrepancy.

For a measurement with O(1) expected precision on mu, floating separate mu_ggH and mu_VBF is probably not feasible (the VBF category alone has very few events). But the strategy should acknowledge this limitation explicitly and state that the measurement assumes SM production mode ratios.

**Required action:** Add a statement that the common mu assumes SM ggH/VBF production ratios. Consider adding a cross-check where mu_VBF is profiled (floated freely) while measuring mu_ggH, to test the stability of the result.

#### B7. No discussion of blinding strategy

The strategy makes no mention of whether the analysis will be blinded or not. For a measurement on Open Data that has already been analyzed by CMS, blinding in the traditional sense (hiding the signal region) may not be necessary. But the strategy should state this explicitly, including:

- Whether the fitters will be validated on Asimov data before looking at the observed fit.
- Whether the NN will be developed without looking at data in the signal-enriched region of the discriminant.
- Whether the result from the CMS evidence paper (mu = 0.78 +/- 0.27 for the full combination) constitutes a known answer that could bias analyst choices.

**Required action:** Add a blinding/bias-avoidance section. At minimum, commit to validating the fit framework on Asimov data before running on observed data.

---

### (C) Suggestions

#### C1. Consider a 0-jet / 1-jet split of the Baseline category

The CMS evidence paper used 0-jet, 1-jet (boosted), and VBF categories. Even a simple 0-jet vs. >=1 jet split of the Baseline category would improve sensitivity because the jet multiplicity is correlated with the signal production mode and the background composition. This is a low-cost improvement that may be worth exploring in Phase 2.

#### C2. The NN input variable list should include Delta_phi(mu, MET)

The angular correlation between the muon and MET is a powerful discriminant against W+jets (where the muon and MET are back-to-back) and is not currently listed among the NN inputs. Consider adding Delta_phi(mu, MET) and Delta_phi(tau, MET).

#### C3. The B(H->tautau) value should be checked at execution time

Section 3.2 quotes BR(H->tautau) = 6.256% from the Yellow Report. This is correct for mH = 125.09 GeV. Ensure this value is used consistently (not rounded to 6.3% or 6.25%) and that the mH assumption is documented.

#### C4. Barlow-Beeston lite vs. full in the VBF category

Section 9.2 specifies Barlow-Beeston lite (one NP per bin) for MC statistics. In the VBF category, where MC statistics may be comparable to data statistics, the full Barlow-Beeston treatment (one NP per bin per sample) may be needed. The strategy should flag this as something to evaluate in Phase 4.

#### C5. Consider reporting the profile likelihood scan of mu

In addition to the best-fit mu and confidence interval, the profile likelihood scan (2*Delta_NLL vs. mu) is a standard plot that shows the full shape of the likelihood. This is especially informative when the expected precision is O(1), as the likelihood may be non-Gaussian.

#### C6. Document the expected correlation between approaches

The four fitting approaches share the same events, selection, and background estimation. Their results will be highly correlated. The strategy should note that the four mu values are not independent measurements and should not be combined. The comparison is informative about the relative power of each discriminant, not about the signal strength itself.

---

## Summary Table

| ID | Category | Finding |
|----|----------|---------|
| A1 | **(A) Must resolve** | Over-specified systematic model with inflated priors risks uninformative measurement; double-counting between trigger and Z norm |
| A2 | **(A) Must resolve** | NN-regressed MET approach has no quantitative success criterion or failure mode plan |
| A3 | **(A) Must resolve** | Inconsistent signal cross-sections between MC normalization and signal interpretation (8.4% bias) |
| A4 | **(A) Must resolve** | QCD OS/SS ratio poorly constrained (0.80 vs 1.06); no procedure for negative bins |
| A5 | **(A) Must resolve** | Collinear mass fallback creates composite observable with discontinuous systematic response |
| B1 | **(B) Should address** | No expected sensitivity estimate; cannot judge feasibility or systematic budget appropriateness |
| B2 | **(B) Should address** | NN training weight scheme needs clarification (generator vs. luminosity weights) |
| B3 | **(B) Should address** | VBF selection thresholds (m_jj > 300, Delta_eta > 2.5) not motivated relative to reference |
| B4 | **(B) Should address** | Zeppenfeld centrality as hard cut may reduce VBF to single-digit events |
| B5 | **(B) Should address** | W+jets extrapolation needs shape validation, not just normalization stability |
| B6 | **(B) Should address** | Common mu for ggH and VBF assumes SM production ratios without stating it |
| B7 | **(B) Should address** | No blinding or bias-avoidance strategy discussed |
| C1 | **(C) Suggestion** | Consider 0-jet / >=1-jet split of Baseline category |
| C2 | **(C) Suggestion** | Add Delta_phi(mu, MET) and Delta_phi(tau, MET) to NN inputs |
| C3 | **(C) Suggestion** | Verify BR(H->tautau) = 6.256% is used consistently |
| C4 | **(C) Suggestion** | Evaluate full Barlow-Beeston in VBF category |
| C5 | **(C) Suggestion** | Report profile likelihood scan of mu |
| C6 | **(C) Suggestion** | Document that four approaches are correlated and should not be combined |

---

## Verdict

**ITERATE.** Five Category A findings must be resolved before this strategy can be approved. The most critical is A1 (systematic over-specification): if the uncertainty budget is set by a priori round numbers rather than data-driven constraints, the measurement will be uninformative by construction. The signal cross-section inconsistency (A3) is a straightforward fix. The NN regression success criterion (A2), QCD OS/SS procedure (A4), and collinear mass fallback (A5) require modest additions to the strategy text. The Category B findings should be addressed in the revision but are not individually blocking.
