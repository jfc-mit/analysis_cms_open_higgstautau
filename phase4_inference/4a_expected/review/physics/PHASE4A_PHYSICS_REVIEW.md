# Phase 4a Physics Review: Expected Results

**Reviewer role:** Senior physicist (physics reviewer)
**Date:** 2026-03-24
**Artifacts reviewed:**
- `ANALYSIS_NOTE_4a_v1.pdf` (51 pages)
- `INFERENCE_EXPECTED.md`
- `expected_results.json`
- `validation_results.json`

---

## Executive Summary

This is a well-constructed Phase 4a deliverable. The analysis note is
comprehensive (51 pages), the statistical model is correctly formulated,
the systematic uncertainty program is thorough and well-motivated, and
the validation tests pass. The expected results are physically sensible
and consistent with the reduced scope of a single-channel, single-period
CMS Open Data analysis. The NN approach demonstrates a clear factor-of-2.6
improvement over the visible mass baseline, which is the key scientific
result.

I identify 2 Category A findings, 4 Category B findings, and 6 Category C
suggestions. The Category A items require resolution before advancing to
Phase 4b.

**Recommendation: ITERATE** -- resolve Category A items, then proceed.

---

## 1. Statistical Model Construction

### 1.1 Model structure -- PASS

The binned profile likelihood ratio with pyhf is correctly formulated
(Eq. 14-16 in the AN). The simultaneous fit across Baseline and VBF
categories with a common signal strength modifier mu is standard CMS
practice. The signal parameterization (ggH + VBF sharing a single mu)
is appropriate for this measurement scope.

The number of parameters (~71 = 21 NPs + ~50 staterror gammas + 1 POI)
is reasonable for a 2-category fit with 20-25 bins per category.

### 1.2 Template construction -- PASS with notes

The template yields are internally consistent across the three
approaches (same events, different observables). The S/sqrt(B) values
(0.57 Baseline, 0.33 VBF for NN score) are consistent with the expected
sensitivity. The QCD template from SS data with R_OS/SS = 0.979 is
properly constructed with negative bins zeroed.

### 1.3 Binning -- acceptable

The 20-bin NN score and 25-bin mass templates are reasonable. The VBF
category has low statistics in some bins (< 5 events for some processes),
but the Barlow-Beeston treatment handles this correctly.

---

## 2. Systematic Uncertainties

### 2.1 Overall assessment -- GOOD

The systematic program includes 21 nuisance parameters covering
normalization and shape effects. The completeness table (Table 20 in
the AN, Section 8.17) compares against both reference analyses (R1: CMS
8 TeV evidence, R2: CMS 13 TeV observation) and covers all required
sources. The two missing items (pileup reweighting, generator comparison)
are genuine CMS Open Data limitations, properly documented.

### 2.2 Shape systematic implementation -- GOOD

The four shape systematics (TES, MES, JES, MET unclustered) are properly
propagated through the full reconstruction chain including MET correction,
observable recomputation, and NN re-evaluation. The shift ratio plots
(Figures 29-32) demonstrate non-trivial bin-by-bin shape effects with
physically sensible patterns. The self-check verification (Section 3.2 of
INFERENCE_EXPECTED.md) confirms each systematic produces non-zero effects
in the expected direction.

### 2.3 TES post-fit constraint -- (B) Should address

The TES post-fit uncertainty is 0.21 (constrained from 1.0 by a factor
of ~5). This is an aggressive constraint from a single Asimov fit.
While the TES is genuinely well-constrained by the Z peak shape in this
analysis, a factor-of-5 constraint from Asimov data alone warrants
scrutiny. The concern is that the NN score distribution may have
artificial sensitivity to the TES variation if the NN learned to exploit
tau pT features that are not perfectly modeled.

**Action:** Verify that the TES constraint is driven by the Z peak region
(background-dominated bins) rather than the signal-enriched region. If
the constraint comes predominantly from signal-region bins, the
measurement could be biased by the very template shapes it is trying to
measure. A simple check: compare the TES post-fit uncertainty between
the Baseline-only fit and the VBF-only fit. The Baseline (with ~39k ZTT
events) should drive the constraint.

### 2.4 MES impact asymmetry -- (C) Suggestion

The MES impact is asymmetric: +0.225/-0.346. While energy scale
systematics can produce asymmetric effects, this level of asymmetry
(factor ~1.5) for a 1% variation is worth understanding. Check whether
this arises from the non-linear NN response to muon pT changes.

### 2.5 MET unclustered impact asymmetry -- (B) Should address

The MET unclustered impact is highly asymmetric: -0.266/+0.047 (factor
~6). This is flagged in the AN text (p. 35) as expected because "the
signal sensitivity is more vulnerable to MET increases than decreases."
However, such extreme asymmetry suggests the up and down variations may
not bracket the true uncertainty symmetrically. The 10% scaling of the
MET magnitude is a crude approach -- the actual unclustered energy
uncertainty affects the MET direction as well as magnitude.

**Action:** Verify that the MET unclustered variation is implemented as
a coherent shift (not just magnitude scaling). If only the magnitude is
scaled, the directional component of the MET uncertainty is missing.
Document whether the current treatment is conservative or potentially
incomplete.

---

## 3. Expected Results

### 3.1 Signal strength precision -- PASS

The key results are:
- NN score: sigma(mu) = 1.15, expected significance 0.89 sigma
- m_vis: sigma(mu) = 2.99, expected significance 0.33 sigma
- m_col: sigma(mu) = 3.72, expected significance 0.26 sigma

These are physically sensible. The NN improvement factor of 2.6 over
m_vis is consistent with the AUC improvement from 0.5 (no discrimination)
to 0.825. The absolute precision (sigma(mu) = 1.15) is consistent with
the scaling estimate in Section 9.4: 1/(sqrt(11.5/24.6) x 0.23 x 1.15)
= 5.3 relative to the published combined result, compared to the observed
factor of 4.3. The slight over-estimation is reasonable given that the
scaling is approximate.

### 3.2 Collinear mass worse than visible mass -- PASS

The collinear mass performing worse than the visible mass (sigma(mu) =
3.72 vs 2.99) is physically sensible and well-explained: the 45.7%
unphysical solution fraction for ggH signal (Table 18) dilutes the mass
resolution improvement. Events falling back to m_vis effectively make
m_col a worse version of m_vis for nearly half the signal. This is
consistent with the known limitations of the collinear approximation in
the mu-tau_h channel at 8 TeV.

### 3.3 CLs limits -- PASS

The 95% CL upper limits (2.36 NN, 6.20 m_vis, 7.81 m_col) are
consistent with the expected sigma(mu) values via the approximate
relation limit ~ 2 x sigma(mu). The CLs scan (Figure 40) shows smooth
curves with correct behavior.

### 3.4 Resolving power statement -- PASS

The resolving power statement (p. 42-43) correctly states that the NN
approach can distinguish signal strengths differing by ~2.3 at 2-sigma.
This is appropriate for a Phase 4a expected-results note.

---

## 4. Validation Tests

### 4.1 Signal injection -- PASS

All injection points (mu = 0, 1, 2, 5) are recovered with pulls < 0.01
for all three approaches. The increasing sigma(mu) with mu for the NN
approach (1.09 to 1.46) correctly reflects the growing Poisson variance
in signal-enriched bins.

### 4.2 Nuisance parameter pulls on Asimov -- PASS

All pulls are zero by construction on Asimov data, as expected. The
post-fit uncertainties provide useful information about the constraining
power of the data.

### 4.3 Goodness of fit -- PASS with caveat

The chi2 = 0 on Asimov data and p-value = 1.0 are trivially expected.
The toy-based validation (200 toys for NN, 100 for m_vis, 99 for m_col)
confirms the machinery works.

### 4.4 GoF toy chi2 outliers -- (A) Must resolve

**Critical finding.** The toy chi2 distributions for m_vis and m_col
contain extreme outliers that indicate fit instabilities:

- **m_vis toys:** chi2 values of 96,962; 169,702; 107,699; 105,902
  (4 out of 100 toys, i.e. 4% failure rate)
- **m_col toys:** chi2 value of 95,004 (1 out of 99 toys, i.e. ~1%
  failure rate)
- **NN score toys:** No outliers (all chi2 values in range 4-11,
  200 toys clean)

These chi2 values of O(100,000) indicate catastrophic fit failures --
the minimizer did not converge, or a nuisance parameter was driven to
an unphysical boundary. A 4% failure rate for m_vis toys is concerning
because it suggests the m_vis workspace has marginal numerical stability.

The NN score workspace shows no such issues, which is reassuring for the
primary approach. However, the m_vis and m_col workspaces are used as
cross-checks and their results must be reliable.

**Action required:** (1) Investigate the failed toy fits -- identify which
nuisance parameters diverge. (2) Check for empty bins in the m_vis and
m_col VBF templates that could cause likelihood evaluation failures.
(3) Consider adding a convergence quality cut when computing GoF p-values
(exclude toys where the minimizer reports non-convergence). (4) Report
the cleaned p-values alongside the raw ones.

### 4.5 NN validation -- PASS

The NN is well-validated:
- Test AUC = 0.825 exceeds the 0.75 go/no-go threshold
- KS overtraining test passes (p = 0.127 signal, p = 0.686 background)
- BDT cross-check shows comparable AUC (0.820) with slightly more
  overtraining
- Input variable quality gate: 11/14 pass chi2/ndf < 5
- Feature importance ranking is physically sensible (m_vis, delta_R,
  MET dominate)

The three variables failing the chi2/ndf < 5 gate (N_jets: 40.68,
N_b-jets: 32.35, delta_R: 5.16) are documented with adequate
justification (LO generator limitations, per-category normalization
parameters in the fit).

---

## 5. Systematic Completeness

### 5.1 Pileup reweighting -- (B) Should address

The missing pileup reweighting is documented as a CMS Open Data
limitation (no official pileup weights). The claim that it is "partially
absorbed by the large Z normalization uncertainty (12%)" is reasonable
but not quantified. Pileup affects shape distributions, not just
normalization -- the Z peak position, jet multiplicity modeling, and MET
resolution all depend on pileup.

**Action:** Quantify the potential pileup effect by comparing the
PV_npvs distribution between data and MC (this was presumably done in
Phase 2). If the distributions differ significantly, the shape effect on
the NN score could be non-negligible. At minimum, state the observed
data/MC PV_npvs disagreement level in the AN and argue that the shape
effects are subdominant to the existing shape systematics.

### 5.2 QCD shape uncertainty -- (B) Should address

The QCD shape uncertainty (from isolation threshold variation) was
committed to in Phase 1 (P4a-6 in COMMITMENTS.md) but is marked as [D]
(downscoped) with the justification that "QCD norm uncertainty (20%) is
conservative and covers shape effects." This is weak justification -- a
normalization uncertainty does not cover shape effects by definition. The
QCD template is derived from SS data and its shape in NN score space
could differ from the OS QCD shape.

However, the QCD is only 15% of the Baseline background and has
relatively flat NN score distribution (Figure 11), so the shape
uncertainty is unlikely to be a dominant effect. The 20% normalization
uncertainty (which ranks 7th in the impact ranking) does provide some
protection.

**Action:** Acknowledge in the AN that the QCD shape uncertainty is a
known limitation, not merely covered by the normalization uncertainty.
Consider adding a brief argument based on the flatness of the QCD NN
score distribution -- if the QCD shape is approximately flat, shape
variations have minimal impact on the signal extraction.

### 5.3 Tau energy scale by decay mode -- (C) Suggestion

The published analyses (R1, R2) apply per-decay-mode TES uncertainties
(1-3% depending on 1-prong, 1-prong+pi0, 3-prong). This analysis uses
an inclusive 3% for all decay modes. The inclusive approach is
conservative (3% is the largest per-DM value) but loses the
discrimination power that per-DM uncertainties provide. This is
acceptable for Phase 4a but should be noted as a simplification.

---

## 6. Analysis Note Quality

### 6.1 Document completeness -- GOOD

The AN is 51 pages with 43 figures, 27 tables, and 15 references. It
covers all required sections: introduction, data samples, event
selection, background estimation, discriminant variables, kinematic
distributions, statistical method, systematic uncertainties, expected
results, validation, and conclusions. The change log is present. The
abstract correctly summarizes the expected results.

### 6.2 Figure quality -- GOOD

Figures use CMS style with appropriate labels. The ratio panels have no
visible gaps (hspace=0 appears correctly applied). Signal is shown
scaled by x10 for visibility. Systematic shift ratio plots (Figures
29-32) effectively communicate the shape effects.

### 6.3 Cross-reference consistency -- (A) Must resolve

The approach comparison table in Section 5.4 (Table 19) reports pre-fit
expected significances of 0.80 sigma, 1.52 sigma, and 0.68 sigma for
m_vis, NN, and m_col respectively. These are based on a simple
S/sqrt(B) counting estimate. However, the profile likelihood results in
Section 9.2 (Table 23) give 0.33 sigma, 0.89 sigma, and 0.26 sigma.

The discrepancy between pre-fit S/sqrt(B) significance and post-fit
profile likelihood significance is expected (the profile likelihood
accounts for systematic uncertainties, background normalization freedom,
and shape information across all bins), but the AN does not explicitly
reconcile these numbers. A reader might be confused by a factor-of-1.7
difference between the two "expected significance" values reported for
the NN approach (1.52 vs 0.89).

**Action:** Add a sentence in Section 9.2 explaining why the profile
likelihood significance is lower than the pre-fit S/sqrt(B) estimate.
The key factors are: (1) the S/sqrt(B) estimate in Table 19 uses an
optimized signal window (score > 0.8) while the profile likelihood uses
the full distribution, (2) systematic uncertainties degrade the
sensitivity, and (3) the Asimov significance formula accounts for NP
profiling. The two numbers are not directly comparable and this should
be stated clearly.

### 6.4 Number of NN score bins -- (C) Suggestion

The INFERENCE_EXPECTED.md states 20 bins for NN score and 25 for the
mass observables, but the GoF section mentions "45 = 20+25 for nn_score"
(20 baseline + 25 VBF). Verify this is correct -- using different
binnings for the same observable in different categories is unusual.
If VBF uses 25 bins while Baseline uses 20, explain the rationale.
If both use 20, the ndf calculation should be 40 not 45.

### 6.5 Template yield discrepancy -- (C) Suggestion

In Table 9 (category yields, p. 11), DY is reported as a combined
45,052.3 for Baseline and 412.9 for VBF. In Table 2 of
INFERENCE_EXPECTED.md (Section 2.1), ZTT + ZLL for Baseline is
38,873.9 + 6,121.7 = 44,995.6. The 57-event discrepancy (0.1%) is
likely a rounding issue between different stages of the analysis, but
should be verified for consistency.

### 6.6 References -- (C) Suggestion

The reference list (15 entries) is adequate but could benefit from
including the PDG reference for m_H = 125.09 GeV (Aad et al. 2015 is
cited for the mass but this is the ATLAS+CMS combination paper, not the
PDG). Also, the Barlow-Beeston reference should cite the original
1993 paper (which is present) but the staterror implementation in pyhf
could additionally reference the pyhf documentation or the HistFactory
paper for the "lite" variant.

---

## 7. Regression Checklist

- [ ] Any validation test failures without 3 documented remediation
      attempts?
  **YES -- GoF toy outliers in m_vis and m_col (Finding 4.4).** These
  are not remediated. Category A.

- [x] Any single systematic > 80% of total uncertainty?
  **No.** TES is the largest at 0.376/1.15 = 33%. Well below 80%.

- [x] Any GoF toy distribution inconsistent with observed chi2?
  **Partially.** The Asimov chi2 = 0 is always below the toy distribution
  (p = 1.0), which is expected. However, the toy outliers in m_vis/m_col
  indicate fit instability, not GoF inconsistency per se.

- [x] Any flat-prior gate excluding > 50% of bins?
  **No.** All bins are included.

- [x] Any tautological comparison presented as independent validation?
  **No.** The NP pulls being zero on Asimov is correctly noted as
  "by construction."

- [x] Any visually identical distributions that should be independent?
  **No.**

- [x] Any result with > 30% relative deviation from a well-measured
      reference value?
  **No.** The sigma(mu) = 1.15 is 4.3x the published combined result,
  quantitatively consistent with the reduced scope (Section 9.4 scaling
  gives 5.3x expected).

- [x] All binding commitments [D1]-[DN] from the strategy fulfilled?
  **Yes.** [D1] three approaches implemented (fourth properly dropped per
  [D13]). [D2] YR4 cross-sections. [D3] W+jets SF. [D4] QCD from SS.
  [D6] Z norm 12%. [D10] Baseline+VBF. [D11] Common mu. All [A] and [L]
  labels accounted for. Phase 4a commitments P4a-1 through P4a-6
  addressed or formally downscoped.

- [x] Is the fit chi2 identically zero?
  **Yes, but by construction on Asimov.** This is the expected result --
  the Asimov data IS the model prediction. This is not a circularity
  concern for Phase 4a; the meaningful GoF test occurs with real data in
  Phase 4b/4c.

---

## 8. Finding Summary

### Category A -- Must resolve before advancing

**A1. GoF toy fit failures in m_vis and m_col workspaces.**
The m_vis GoF toys have 4/100 catastrophic failures (chi2 ~ 100,000)
and m_col has 1/99. These indicate numerical instability in these
workspaces, likely from empty or near-empty bins in the VBF category
under toy fluctuations. The NN workspace (0/200 failures) is clean.
Investigate the source, apply mitigation (e.g., minimum bin content
threshold, improved starting values), and report corrected GoF metrics.

**A2. Pre-fit vs post-fit significance inconsistency not explained.**
Table 19 reports NN expected significance of 1.52 sigma while Table 23
reports 0.89 sigma. Both numbers are correct in their respective
contexts, but the AN does not reconcile them. A reader could interpret
this as a factor-of-1.7 degradation from systematics, when in reality
the pre-fit estimate is a different metric (cut-and-count in an optimized
window vs. full-shape profile likelihood). Add explicit text bridging
these two results.

### Category B -- Should address before final approval

**B1. TES post-fit constraint (factor 5 from prior).** Verify the
constraint is driven by the Z peak (background-dominated) region, not
the signal region. Report the Baseline-only vs VBF-only TES constraint
as a cross-check.

**B2. MET unclustered asymmetry.** The factor-6 asymmetry in MET
unclustered impact (-0.266/+0.047) should be investigated. Verify the
variation implementation is a coherent shift, not just magnitude scaling.
Document whether the directional component of the uncertainty is covered.

**B3. Pileup reweighting.** Quantify the data/MC PV_npvs disagreement
and argue that the shape effect on the NN discriminant is subdominant
to existing shape systematics.

**B4. QCD shape uncertainty.** Strengthen the justification for
downscoping the QCD shape uncertainty (P4a-6). The statement that "20%
normalization covers shape effects" is insufficient -- normalization and
shape are different uncertainty types. Argue from the QCD NN score
flatness instead.

### Category C -- Suggestions

**C1.** Consider per-decay-mode TES uncertainties for the final analysis
note (Phase 5), even if the inclusive 3% is used for the fit.

**C2.** Verify the NN score binning is consistent across categories
(20 Baseline + 25 VBF appears in the ndf calculation but is not
documented in the binning table).

**C3.** Check the 57-event template yield discrepancy between Table 9
and the INFERENCE_EXPECTED.md DY totals.

**C4.** The MES asymmetry (+0.225/-0.346) is worth understanding but
is not blocking.

**C5.** Add a PDG reference for m_H = 125.09 GeV and consider citing
the pyhf staterror documentation.

**C6.** In the systematic shift plots (Figures 29-32), the NN score
axis labels are small and the legend overlaps with data in some cases.
Minor formatting issue.

---

## 9. Verdict

**ITERATE.** The analysis is fundamentally sound. The statistical model
is correct, the NN approach is well-validated, and the expected results
are physically sensible. However, the two Category A findings require
resolution:

1. The GoF toy failures must be investigated and fixed before proceeding
   to data, as the m_vis and m_col cross-check workspaces must be
   numerically stable for the data fit.

2. The significance inconsistency between Tables 19 and 23 is a
   documentation issue but could mislead readers and reviewers.

After resolving these items, the analysis is ready for Phase 4b (10%
data validation). The Category B items should be addressed before the
Phase 4b review but are not strict blockers for beginning 4b work.

---

## 10. Approval Assessment

**Would I approve this for 10% data validation?**

**Yes, contingent on A1 and A2 resolution.** The core result (NN score
sigma(mu) = 1.15, the primary approach) has a clean workspace with no
toy failures, and all validation tests pass. The physics is correct,
the systematic program is comprehensive, and the comparison to published
results is quantitatively consistent. The factor-of-2.6 improvement from
NN over visible mass is the key scientific finding and is well-supported.

The NN approach is ready for data. The m_vis and m_col cross-checks need
numerical stabilization before they can be trusted with data.
