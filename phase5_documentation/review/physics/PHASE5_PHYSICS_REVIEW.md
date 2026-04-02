# Phase 5 Physics Review: CMS H->tautau Signal Strength Measurement

**Reviewer:** Senior collaboration member (ARC/L2 convener level)
**Date:** 2026-03-25
**Document:** ANALYSIS_NOTE_5_v1.pdf (70 pages)
**Analysis:** Measurement of mu(H->tautau) in the mu-tau_h final state, CMS Open Data at sqrt(s) = 8 TeV, 11.5 fb^{-1}

---

## Executive Summary

This is a well-documented, thorough analysis note that measures the Higgs boson signal strength mu = 0.64 +/- 1.08 in the H->tautau->mu-tau_h channel using CMS Open Data. The result is consistent with the SM (0.34 sigma from mu=1) and with the published CMS measurement (pull = -0.13 sigma). The analysis demonstrates genuine physics content: the three-way comparison of fitting approaches (NN vs visible mass vs collinear mass) provides a compelling demonstration of the power of multivariate techniques. The note is comprehensive at ~70 pages, well-structured, and readable.

However, there are several physics issues that require attention before I would sign off.

---

## 1. Physics Correctness

### 1.1 Primary result: mu = 0.64 +/- 1.08

**(C) The result is sensible.** The central value is positive and consistent with the SM. The uncertainty of 1.08 is approximately 4x the published CMS combined result (0.27), which is quantitatively reasonable given that this is a single channel (~23% of the total sensitivity) with half the luminosity, no SVfit, and a looser tau ID. The scaling argument in Section 9.7 (factor ~4-5) is well-constructed.

### 1.2 Negative signal strengths for m_vis and m_col

**(B) The large negative mu values for the alternative approaches need more careful physics discussion.** The m_vis approach gives mu = -6.70 and m_col gives mu = -10.74. The note attributes this to the "5% data/MC normalization deficit," but a 5% normalization deficit producing mu = -6.7 (a 7.7-sigma shift from the SM) requires more quantitative explanation. Specifically:

- What is the expected shift in mu from a pure 5% normalization offset, given the signal-to-background ratio? For S/B ~ 0.003 (162/60,925), a 5% background normalization shift would shift mu by approximately -0.05 * B / S ~ -0.05 * 60,925 / 162 ~ -18.8 in units of signal events divided by signal template. This rough estimate is actually consistent with the observed values. The note should include this back-of-envelope calculation to make the reader understand that even a small normalization offset produces enormous mu shifts when S/B is tiny and the discriminant cannot separate signal shape from background normalization.

### 1.3 Cross-section values

**(C) Minor.** The note uses the YR4 N3LO ggH cross-section (21.39 pb) rather than the original analysis-era NNLO+NNLL value (19.6 pb used in the CMS tutorial). This is a valid choice (use the best available prediction), and the 9% difference is documented. However, this means the mu measurement is defined with respect to a different theory prediction than the published CMS result. This should be mentioned explicitly when comparing mu values, as it shifts the expected mu by approximately -0.08 relative to the CMS-era definition. The pull between measurements would shift slightly. This is a minor effect given the large uncertainties but should be stated for completeness.

---

## 2. Statistical Method

### 2.1 Profile likelihood framework

**(C) Sound.** The binned profile likelihood with pyhf is standard and well-established. The use of HistFactory with normsys/histosys modifiers is appropriate. The Barlow-Beeston lite treatment for MC statistics is correct. The 21 nuisance parameters plus ~50 gamma parameters for a 50-bin fit (25 per category, 2 categories) is reasonable.

### 2.2 Signal injection tests

**(B) The signal injection tests on Asimov data are trivially satisfied and do not constitute a meaningful validation.** All pulls are identically 0.000, which is expected by construction: Asimov data IS the model prediction, so the model always perfectly recovers the injected value. A meaningful signal injection test would inject signal into toy pseudo-experiments drawn from the background-only model, fit each toy, and verify that the distribution of recovered mu values is centered at the injected value with the expected spread. Alternatively, inject signal into the 10% or full data by adding simulated signal events. The current test only verifies that the minimizer works, not that the model is unbiased in the presence of statistical fluctuations. This should be downgraded from "validation" to "workspace sanity check" in the note.

### 2.3 POI range

**(C)** The extended POI range [-30, 30] is appropriate for the alternative approaches and ensures the fit is not hitting a boundary.

### 2.4 Nuisance parameter constraints

**(B) Several NPs show surprisingly strong constraints from data, which warrants discussion of whether these constraints are physical or reflect template artifacts.** The TES post-fit uncertainty is 0.18 (from 1.0) on full data -- this means the data constrains the TES to 18% of the prior uncertainty. Published CMS analyses with the full dataset and all channels typically achieve TES constraints of 0.3-0.6. A constraint to 0.18 in a single channel with half the luminosity is suspiciously tight and may indicate that the fit is exploiting template features (e.g., sharp bin-to-bin variations from limited MC statistics) rather than genuine physical sensitivity. The MES constraint to 0.32 and MET unclustered to 0.30 are similarly aggressive. The note mentions this for TES in Section 8.12 ("constraint relaxed from 0.21 to 0.26 after template smoothing") but the full-data value of 0.18 is even tighter. This should be investigated further -- if template artifacts are driving the constraint, the postfit uncertainties on mu are underestimated.

---

## 3. Goodness of Fit

### 3.1 GoF p = 0.000

**(A) The GoF failure is a serious concern that is not adequately resolved.** The combined GoF p-value is exactly 0.000 for all three approaches, meaning the observed test statistic exceeds ALL 200 toys. This is not a marginal failure -- it is a definitive statement that the model does not describe the data.

The note argues that the per-category chi2/bin values (0.80-1.19) are "individually acceptable," but this misses the point. The combined GoF failure means the model cannot simultaneously describe both categories. This is not surprising given the 31% VBF deficit, but it does mean the uncertainty on mu is unreliable: the profile likelihood uncertainty assumes the model is correct, and the GoF tells us it is not.

**What is needed:** An explicit statement that the GoF failure means the quoted uncertainty may not have correct coverage. A profile likelihood uncertainty is only guaranteed to have nominal coverage when the model describes the data. The note should quantify this: what is the expected impact on the uncertainty if the VBF deficit is due to a systematic effect not captured by the model? One way to assess this: fit the Baseline category alone (where the per-category GoF is acceptable) and compare the resulting mu and uncertainty to the combined fit. If the Baseline-only result has similar precision, the combined result is robust despite the GoF failure. The per-category results in Table 21 actually show this (Baseline: 0.61 +/- 1.60 vs combined 0.63 +/- 1.08), but the improvement from 1.60 to 1.08 comes from the VBF category -- the same category with the GoF problem. This should be discussed explicitly.

### 3.2 Toy generation

**(B) The original toy failure rate of 14.8% for the NN score approach is concerning.** The note states this was reduced to 1.0% using "retry logic with perturbed starting values." A 14.8% failure rate suggests numerical instability in the fit, likely from low-MC-statistics bins in the VBF category. The retry logic may produce a biased subsample of toys (the failed toys may represent legitimately different fit minima). The note should verify that the toy chi2 distribution from the 426 converged toys (out of 500 in the original run) is consistent with the 198 converged toys (out of 200 in the retry run). A KS test between the two distributions would be informative.

---

## 4. Systematic Uncertainties

### 4.1 Systematic program completeness

**(C) Adequate for an Open Data analysis.** The systematic completeness table (Table 11) is a strong element of the note. It honestly compares against two reference analyses and documents what is missing and why. The missing systematics (pileup reweighting, generator comparison, ISR/FSR) are genuine limitations of the CMS Open Data format.

### 4.2 Discrepancy between Asimov and full-data impact rankings

**(B) The dramatic reshuffling of the impact ranking between Asimov (Table 10) and full data (Table 17) is insufficiently discussed.** Key changes:

- TES drops from #4 Asimov (impact 0.214) to ~#15 full data (impact 0.025) -- a factor of 8.5 reduction
- MES drops from #1 Asimov (0.404) to #3 full data (0.148) -- a factor of 2.7 reduction
- MET unclustered stays at #1-2 but drops from 0.354 to 0.285

The TES reduction is the most dramatic. On Asimov data, TES is constrained to 0.26; on full data, it is constrained to 0.18. This extreme constraint (TES is known to within 0.54% of its nominal value) drives the impact reduction. But is this constraint physical? A 3% TES uncertainty constrained to 0.18 means the effective TES uncertainty is 0.54%, which is far more precise than the CMS tau performance group measurement. This could indicate that the fit is using sharp template features to constrain TES, and that the constraint would relax with smoother templates or more MC statistics.

The note should present an explicit comparison: run the fit with the TES and MES NPs fixed at their postfit values and report the change in mu and its uncertainty. If mu does not change significantly, the constraints are benign. If mu shifts, the constraints are compensating for a model deficiency.

### 4.3 Normalization systematics

**(B) The Z->tautau normalization uncertainty of 12% is large but justified.** The decomposition (4% theory + 5% trigger + 8% tau ID + 2% stat in quadrature) is clearly documented. However, a 12% uncertainty on the dominant background is unusual for a CMS Htautau analysis (published analyses achieve 3-4% using tau-embedded samples). This significantly impacts the sensitivity. The note correctly attributes this to Open Data limitations.

### 4.4 JES implementation

**(B) The JES systematic is described as "+/- 3% on all jets" which is a significant simplification.** Published CMS analyses use p_T- and eta-dependent JES uncertainties decomposed into ~25 independent sources. A flat 3% may overestimate the JES uncertainty in some regions and underestimate it in others. More importantly, the JES should include MET propagation (adjusting MET when jets are shifted). The note states JES is applied "with propagation to the MET and re-evaluation of the VBF categorization criteria" (Section 7.11), which is correct. However, Table 13 lists JES as "Shape, +/-3% (no MET)" -- this contradicts the text. Clarify whether the JES variation includes MET propagation or not.

### 4.5 norm_wjets_baseline impact = 0.0

**(B) A nuisance parameter with zero impact on mu despite a pull of +1.24 sigma is suspicious.** From the JSON diagnostics, norm_wjets_baseline has impact_up = 0.0 and impact_down = 0.0, with bestfit = +1.24 and postfit_unc = 0.83. A NP that is pulled by 1.24 sigma but has zero impact on mu suggests either: (a) the impact calculation has a numerical issue, or (b) the W+jets normalization in the Baseline category is perfectly degenerate with other NPs. Either way, this should be investigated and explained in the note. A zero-impact NP with a significant pull is a red flag for the impact ranking methodology.

---

## 5. Validation

### 5.1 10% data validation

**(C) Well-executed.** The 10% validation procedure is thorough, the VBF deficit is properly flagged, and the interpretation that it reflects statistical fluctuations in a small subsample is reasonable (the deficit persists in the full data, but the 10% interpretation at the time was valid).

### 5.2 NN overtraining

**(C) Adequate.** The KS test p-values (0.127 signal, 0.686 background) confirm no significant overtraining. The BDT comparison is a useful cross-check.

### 5.3 Validation summary table

**(C) Excellent.** Table 8 is comprehensive and well-organized. The full-data GoF is honestly flagged rather than hidden.

---

## 6. Comparison to Published CMS Result

### 6.1 Pull calculation

**(C) Correct.** The pull of -0.13 sigma between this measurement (0.63 +/- 1.08) and the published CMS result (0.78 +/- 0.27) is correctly computed, treating the uncertainties as uncorrelated. In reality, there are correlated systematics (luminosity, theory cross-sections) between the two measurements, but given the dominant statistical uncertainty, the effect on the pull is negligible.

### 6.2 Comparison scope

**(B) The comparison is slightly misleading because the published CMS result uses a different signal hypothesis.** The published mu = 0.78 +/- 0.27 is from the full combination of all channels and both center-of-mass energies. The mu_tau_h channel at 8 TeV contributes a fraction of this. A fairer comparison would be to the published per-channel result for mu_tau_h at 8 TeV only, if available from the paper. The CMS evidence paper (JHEP 05 (2014) 104) does break down the result by channel and energy -- the per-channel 8 TeV mu_tau_h result would be the appropriate comparison target, not the full combination. The note should cite whether such a breakdown is available and use it.

---

## 7. Figure Quality

### 7.1 General assessment

**(C) The figure set is comprehensive.** 192 figure files (96 PDF+PNG pairs) cover the full analysis story: tau ID optimization, kinematic distributions, NN training diagnostics, templates, pre/post-fit comparisons, systematic shift shapes, NP pulls, impact rankings, GoF, and comparison to published results. The figure-scrolling test reveals a complete physics narrative.

### 7.2 Specific figure comments

**(C)** The NN overtraining check (Figure 9), ROC curves (Figure 8), and BDT comparison (Figure 12) are standard and well-produced.

**(B) The systematic shift ratio plots (Figures 16-19) show ratio of varied/nominal templates, but the y-axis scale and meaning should be more clearly documented.** Are these per-process or summed? The caption says "for Z->tautau, ggH signal, and ttbar" but it's not clear if all three are overlaid or if only one is shown.

**(C)** The flagship comparison figures (Figures 41-42) effectively communicate the core result. The pull annotation between this measurement and the published CMS result is the key deliverable.

---

## 8. Missing Physics

### 8.1 No discussion of tau fake rate systematic

**(B)** The jet-to-tau fake rate is listed as "Absorbed" into W+jets and QCD normalization in Table 11, but there is no dedicated discussion of whether the fake rate is constant across the NN score distribution. If the fake rate varies with tau p_T or decay mode (it does), then a normalization-only systematic may undercover the shape effect. The note should at least acknowledge this limitation and estimate its potential impact.

### 8.2 No b-veto systematic or discussion

**(C)** The analysis does not apply a b-veto to suppress ttbar, relying instead on the mT cut and template fit. This is a valid approach, but the note does not discuss why a b-veto was not used, given that the ttbar background is 35% of the VBF category. A b-veto would reduce the VBF deficit if the excess is from ttbar mismodeling. This is a design choice that should be briefly discussed.

### 8.3 No electron-to-tau fake rate

**(C)** The Tight anti-electron discriminator is applied, but there is no discussion of the residual e->tau_h fake rate or its impact. This is likely very small but should be mentioned.

### 8.4 No trigger turn-on study

**(B)** The trigger efficiency is treated as a flat 3% normalization uncertainty. However, the trigger has a turn-on curve near the offline thresholds (17 GeV trigger, 20 GeV offline for the muon leg). Without trigger efficiency measurements from CMS Open Data, the 3% is a guess. A simple data/MC comparison of the efficiency as a function of muon p_T near the threshold would validate this assumption. The note acknowledges this is absorbed into the Z normalization, but this effectively double-counts if the 12% Z normalization already covers the trigger.

---

## 9. Number Consistency Check

Cross-checking key numbers between the JSON outputs and the AN text:

| Quantity | JSON | AN text | Match? |
|----------|------|---------|--------|
| mu_hat (NN, full) | 0.6346 | 0.63/0.64 | YES (rounding) |
| mu_err (NN, full) | 1.0786 | 1.08 | YES |
| obs_significance | 0.606 | 0.61 | YES |
| obs_limit_95 | 2.846 | 2.85 | YES |
| GoF chi2 (NN) | 33.117 | 33.1 | YES |
| GoF p (NN) | 0.000 | 0.000 | YES |
| Baseline chi2/ndf (NN) | 17.15/20 = 0.857 | 0.86 | YES |
| VBF chi2/ndf (NN) | 15.97/20 = 0.798 | 0.80 | YES |
| norm_wjets_vbf bestfit | -1.891 | -1.89 | YES |

**Numbers are consistent.** No stale values detected.

---

## 10. Would I Approve This?

**Not yet, but close.** This is a credible Open Data analysis with genuine physics content. The methodology is sound, the note is comprehensive, and the result is sensible. However, I would require the following before approval:

### Must resolve (Category A):

**A1. GoF failure coverage statement.** The note must explicitly state that the GoF p=0.000 means the quoted uncertainty may not have correct frequentist coverage, and present a quantitative argument for why the result is nonetheless reliable. The per-category fits provide this argument, but it needs to be made explicitly in the conclusions. Currently the GoF is called "a known limitation" without addressing the statistical implication for the primary result's uncertainty.

### Must address before PASS (Category B):

**B1. Signal injection tests are trivial.** Acknowledge that Asimov signal injection tests are sanity checks (not bias tests) and either perform proper toy-based injection tests or remove the claim that they "confirm unbiased signal extraction."

**B2. NP over-constraint investigation.** Add a paragraph discussing whether the TES constraint to 0.18 (and MES to 0.32) on full data is physically reasonable. Compare to published analysis NP constraints. If the constraints are driven by template artifacts, state this as a limitation.

**B3. Impact ranking Asimov vs full-data comparison.** Add a brief discussion comparing Tables 10 and 17, explaining the dramatic reshuffling (especially TES from 0.21 to 0.025).

**B4. JES/MET propagation contradiction.** Resolve the contradiction between the Section 7.11 text ("with propagation to MET") and Table 13 ("no MET").

**B5. norm_wjets_baseline zero impact.** Investigate and explain why this NP has zero impact on mu despite a 1.24-sigma pull.

**B6. m_vis/m_col negative mu back-of-envelope.** Add the quantitative explanation showing that S/B ~ 0.003 means even a small normalization offset produces order-10 shifts in mu for non-discriminating observables.

**B7. Published comparison scope.** If the per-channel mu_tau_h result at 8 TeV is available from the CMS evidence paper, use it as the comparison target rather than the full combination.

### Suggestions (Category C):

**C1.** Cross-section era difference. Note the 9% difference in sigma_ggH between YR4 (used here) and NNLO+NNLL (used in published) when comparing mu values.

**C2.** Tau fake rate shape. Acknowledge that normalization-only treatment of jet-to-tau fakes may undercover shape effects.

**C3.** Trigger turn-on. Either show a data/MC turn-on comparison near the threshold or explicitly state that no such study was possible with Open Data.

**C4.** b-veto design choice. Add a sentence explaining why a b-veto was not applied despite ttbar being 35% of the VBF background.

**C5.** The abstract states "mu = 0.64 +/- 1.08" but the body text and JSON give 0.635. Use consistent rounding throughout (0.64 or 0.63, not both).

---

## Classification Summary

| ID | Category | Issue |
|----|----------|-------|
| A1 | A (must resolve) | GoF failure: add explicit coverage statement and quantitative robustness argument |
| B1 | B (must fix) | Signal injection tests are trivial -- relabel or redo |
| B2 | B (must fix) | NP over-constraint (TES 0.18, MES 0.32) discussion needed |
| B3 | B (must fix) | Asimov vs full-data impact ranking comparison missing |
| B4 | B (must fix) | JES MET propagation contradiction (text vs table) |
| B5 | B (must fix) | norm_wjets_baseline zero impact with 1.24-sigma pull |
| B6 | B (must fix) | Quantitative explanation for m_vis/m_col negative mu |
| B7 | B (must fix) | Use per-channel published comparison if available |
| C1 | C (suggestion) | Cross-section era difference in mu comparison |
| C2 | C (suggestion) | Tau fake rate shape acknowledgment |
| C3 | C (suggestion) | Trigger turn-on study or explicit statement |
| C4 | C (suggestion) | b-veto design choice justification |
| C5 | C (suggestion) | Consistent mu rounding (0.63 vs 0.64) |

---

## Verdict

**ITERATE.** Address A1 and the B-category issues, then re-present. The physics is solid and the analysis is well-executed. The primary result is credible. The issues above are all addressable within the current analysis framework without regression to earlier phases.
