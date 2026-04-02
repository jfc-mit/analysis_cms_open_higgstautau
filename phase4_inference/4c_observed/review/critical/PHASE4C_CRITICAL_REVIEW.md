# Phase 4c Critical Review: Full Data Observed Results

**Reviewer:** Critical reviewer (1-bot)
**Artifact:** `phase4_inference/4c_observed/outputs/INFERENCE_OBSERVED.md`
**Supporting data:** `observed_results.json`, `diagnostics_full.json`
**Date:** 2026-03-24

---

## Summary Verdict

The Phase 4c artifact presents a coherent set of full-data results with
a physically sensible primary result (mu = 0.63 +/- 1.08 from the NN
score approach). The analysis identifies and correctly contextualizes
the alternative-approach pathologies. However, there are several
findings requiring correction or clarification, most notably a
**Category A** goodness-of-fit problem and multiple **Category B**
number inconsistencies between the artifact text and the machine-readable
JSON outputs.

---

## Finding F1 [Category A]: GoF p-value = 0.00 for ALL approaches, including the primary NN score

**Description:** The GoF toy-based p-value is reported as 0.00 for all
three approaches (Section 7 of the artifact). For the NN score, the
observed chi2 = 33.1 while all 171 converged toys have chi2 values in
the range ~10-30 (visually confirmed from the GoF plot, where the
observed chi2 = 33.1 lies to the right of the entire toy distribution).
This means the observed data is a worse fit than every single toy
realization.

The artifact dismisses this by stating "the toy-based GoF p-value of 0.00
reflects this over-parameterization rather than genuine mismodeling." This
reasoning is **incorrect**. The negative ndf explains why a chi2/ndf ratio
is not meaningful, but it does NOT explain why the observed chi2 exceeds
all toy chi2 values. Toys are generated from the post-fit model using the
same over-parameterized model, so the toy distribution already accounts
for the negative ndf. A p-value of 0.00 means the data is inconsistent
with the model at the level probed by the toys --- this is a genuine
GoF failure.

For context, the 10% data (Phase 4b) achieved a GoF p-value of 0.209 for
the NN score approach. The full data shows dramatically worse agreement.

**Additionally concerning:** 29 out of 200 toys (14.5%) failed to
converge for the NN score approach. This is a substantial failure rate.
While the artifact reports this in the JSON, the INFERENCE_OBSERVED.md
does not mention it at all. The m_vis and m_col toy sets show 0 failures
(200/200 converged), so the 14.5% failure rate in the NN score is specific
to that workspace and requires investigation.

**Required action:**
1. Investigate the source of the GoF failure. Is it driven by a specific
   category (Baseline vs VBF)? Compute separate per-category GoF.
2. Report the GoF honestly --- do not dismiss p = 0.00 with the negative
   ndf argument. If the model genuinely does not describe the data, this
   is a physics issue.
3. Report and investigate the 14.5% toy convergence failure rate for the
   NN score workspace. Consider whether the converged toys form a biased
   subset.
4. If the GoF failure is confirmed as genuine mismodeling, this may
   trigger phase regression (concrete trigger: "GoF toy distribution
   inconsistent with observed chi2 (outside 95% interval)").

---

## Finding F2 [Category B]: NP pull values in the artifact table are inconsistent with the JSON

**Description:** The NP pull table in Section 5 of the artifact reports
values that do not match the machine-readable JSON (`observed_results.json`
-> `nn_score` -> `np_pulls`). Specifically:

| NP | Artifact pull | JSON pull | Artifact post-fit unc | JSON uncertainty |
|----|---------------|-----------|----------------------|-----------------|
| norm_wjets_vbf | -2.16 | -2.155 | 0.59 | 0.877 |
| shape_jes | -2.02 | -2.023 | 0.56 | 0.697 |
| norm_wjets_baseline | +1.50 | +1.504 | 0.54 | 0.827 |
| norm_qcd_vbf | -1.48 | -1.481 | 0.68 | 0.859 |
| shape_met_uncl | -1.14 | -1.141 | 0.60 | 0.296 |
| norm_qcd_baseline | +1.12 | +1.115 | 0.34 | 0.683 |
| norm_missing_bkg | -0.94 | -0.943 | 0.75 | 0.894 |
| norm_ztt | -0.79 | -0.787 | 0.40 | 0.544 |

The pull values match reasonably (rounding differences), but the
**post-fit uncertainties reported in the artifact are systematically wrong**.
For example, norm_wjets_vbf has JSON uncertainty 0.877, but the artifact
reports 0.59. shape_met_uncl has JSON uncertainty 0.296, but the artifact
reports 0.60. These are not rounding errors; they are entirely different
numbers. This suggests the artifact table was constructed from a different
fit result or was manually transcribed with errors.

The number consistency gate requires all numerical values in the AN to
match the latest machine-readable outputs, with discrepancy > 1% relative
being Category A. While this is the inference artifact (not the AN), the
principle applies: the authoritative numbers are in the JSON, and the
artifact must reproduce them faithfully.

**Required action:** Regenerate the NP pull table in the artifact from
the JSON data. Ensure the "Post-fit unc." column matches
`np_pulls[name]["uncertainty"]` from `observed_results.json`.

---

## Finding F3 [Category B]: Impact ranking numbers partially inconsistent

**Description:** The impact ranking in Section 6 of the artifact reports
"Symmetric Impact" values. Cross-checking against `diagnostics_full.json`:

| NP | Artifact impact | JSON impact_sym |
|----|----------------|-----------------|
| shape_mes | 0.438 | 0.438 | OK |
| shape_jes | 0.414 | 0.414 | OK |
| shape_met_uncl | 0.336 | 0.336 | OK |
| norm_ztt | 0.115 | 0.115 | OK |
| norm_wjets_vbf | 0.093 | 0.093 | OK |

These match. However, the impact ranking plot (Figure `impact_ranking_full.png`)
shows a notable feature: **several NPs have exactly zero impact in the
up or down direction.** Specifically from the JSON:

- shape_met_uncl: impact_up = 0.000, impact_down = 0.672
- shape_tes: impact_up = 0.000, impact_down = -0.071
- trigger_eff: impact_up = 0.000, impact_down = 0.032
- norm_wjets_baseline: impact_up = 0.000, impact_down = 0.025
- tau_id_eff: impact_up = 0.000, impact_down = 0.014
- norm_missing_bkg: impact_up = 0.000, impact_down = 0.005

Having exactly zero impact in one direction is suspicious. The impact
calculation fixes the NP at +/-1 sigma from its pre-fit value and refits.
An impact of exactly 0.0 typically means the refit with the NP frozen at
+1 sigma returned the exact same mu_hat as the nominal fit, which could
indicate that the fixed NP value (+1 sigma from pre-fit) falls on or near
the best-fit value (since these NPs are already pulled). But having 6 NPs
with impact_up = exactly 0.000 (not approximately zero, but identically
zero) is unusual. This may indicate a numerical issue in the impact
calculation, such as the optimizer returning to the same minimum when
one direction is constrained.

**Required action:** Investigate whether the zero-impact-up values are
a numerical artifact. Consider rerunning the impact calculation with the
NP fixed at bestfit +/- 1*postfit_uncertainty rather than init +/- 1.0,
which is the standard impact formula used in published analyses.

---

## Finding F4 [Category B]: The pull definition may be non-standard

**Description:** The code in `02_fit_full_data.py` (line 112) computes
the pull as:

```python
"pull": float((bestfit[i] - init_val) / uncertainties[i])
```

This divides by the **post-fit** uncertainty. The standard convention in
HEP for "pull" is (bestfit - prefit) / prefit_uncertainty, where the
prefit uncertainty is 1.0 for standard Gaussian-constrained NPs. The
alternative definition (bestfit - prefit) / postfit_uncertainty is
sometimes called "constraint" or is used in different contexts.

The distinction matters: for norm_wjets_vbf, the bestfit is -1.891 with
postfit uncertainty 0.877. Using the standard pull definition:
pull_standard = (-1.891 - 0) / 1.0 = -1.891 sigma (< 2 sigma).
Using the code's definition:
pull_code = (-1.891 - 0) / 0.877 = -2.155 sigma (> 2 sigma).

The artifact flags norm_wjets_vbf and shape_jes as "> 2 sigma" pulls,
but this is based on the non-standard definition. Under the standard
definition, neither NP exceeds 2 sigma:
- norm_wjets_vbf: bestfit = -1.891 -> standard pull = -1.89
- shape_jes: bestfit = -1.410 -> standard pull = -1.41

This does not change the physics conclusion (the NPs are still
substantially pulled), but the presentation should clarify which
convention is used and whether "2 sigma" flags are warranted under the
standard convention.

**Required action:** State explicitly which pull convention is used. If
using (bestfit - init) / postfit_uncertainty, note that this is the
"constraint" definition and that neither NP exceeds 2 sigma under the
standard convention. The flags in the artifact table should be adjusted
accordingly, or both conventions should be presented.

---

## Finding F5 [Category B]: VBF data/MC deficit of 31% is persistent and not adequately investigated

**Description:** The VBF category shows a consistent data/MC ratio of
~0.69 across all three approaches (artifact Section 2, confirmed by
diagnostics_full.json). This was already flagged in Phase 4b (where
data/MC ~ 0.65 in 10% data), and the artifact notes it "persists."

The artifact attributes this to "known limitations of the MC modeling in
the VBF-enriched phase space for this open data sample" (Section 2) and
argues the NN score approach is robust against it (Section 4.2). While
the NN score result may be robust due to limited VBF statistical weight,
a 31% normalization deficit is large and deserves quantitative
investigation:

1. **Which MC process drives the excess?** The pre-fit VBF plots show
   ttbar (green) and W+jets (red) as major components. If these are
   over-predicted, the 10%/20% normalization uncertainties may be
   insufficient. The norm_wjets_vbf pull of -1.89 sigma supports this.
2. **Is the JES variation absorbing the deficit?** shape_jes is pulled
   to -1.41 sigma (post-fit). JES shifts can migrate events between
   categories. A -1.41 sigma JES pull would reduce the predicted yield
   in VBF by shifting events to Baseline. Has this been verified?
3. **Does this deficit affect the mu extraction?** The per-category VBF
   NN score result is mu_VBF = -0.04 +/- 1.34 (from diagnostics_full.json).
   This is consistent with zero signal and could be a consequence of the
   deficit absorbing what would otherwise be a signal contribution.

**Required action:** Add a quantitative breakdown of which processes
contribute to the VBF over-prediction. Verify that the NP pulls
(norm_wjets_vbf, shape_jes, norm_qcd_vbf) are absorbing the deficit
consistently and that the combined absorption is compatible with the
31% deficit magnitude. This does not need to be a full investigation,
but a short accounting is needed.

---

## Finding F6 [Category B]: Expected sigma(mu) values differ between 4a and 4c artifacts

**Description:** The INFERENCE_OBSERVED.md Section 4.1 quotes the
Phase 4a expected uncertainty for NN score as sigma = 1.28 (e.g., "Phase
4a expected uncertainty (sigma_expected = 1.28 vs sigma_observed = 1.08)").
However, the Phase 4a INFERENCE_EXPECTED.md Section 4.1 reports
sigma(mu) = 1.247 for NN score. The expected_results.json file does not
include mu_err directly, but the Phase 4a artifact clearly states 1.247.

The 4c artifact uses 1.28 in multiple places (Sections 3.1, 4.1). This
could be a value from a different fit version or a transcription error.
A 2.6% discrepancy is above the 1% threshold.

**Required action:** Verify which value is correct and update the 4c
artifact to use the authoritative Phase 4a number. If the value changed
between workspace versions, document which version is being compared.

---

## Finding F7 [Category C]: Post-fit plots lack uncertainty bands

**Description:** The post-fit data/MC comparison plots (e.g.,
`data_mc_postfit_nn_score_baseline.png`) show the post-fit prediction as
a filled histogram and data as points, but no uncertainty band is shown
on the post-fit prediction. Standard practice is to show a hatched or
shaded band representing the post-fit systematic + statistical
uncertainty on the prediction. Without this, the visual impression of
the data/MC agreement is incomplete --- the reader cannot judge whether
deviations are within the model uncertainty.

**Required action:** Add post-fit uncertainty bands to the prediction
in the data/MC comparison plots, or add a note explaining why they are
omitted (e.g., "post-fit covariance matrix not propagated to per-bin
uncertainties").

---

## Finding F8 [Category C]: Post-fit plots do not show stacked process composition

**Description:** The post-fit data/MC comparison plots show only the
total post-fit prediction as a single blue histogram. Unlike the pre-fit
plots (which show individual process stacks), the post-fit plots lose
the process decomposition. This makes it impossible to visually assess
how individual processes shifted in the fit.

Showing the post-fit stacked composition would be informative (especially
for understanding how the W+jets and QCD normalizations adjusted in VBF),
but is not strictly required.

**Required action:** Consider adding stacked process decomposition to
the post-fit plots, at least for the primary NN score approach. This
would require propagating the post-fit NP values to individual process
predictions.

---

## Finding F9 [Category C]: Artifact Section 11 quotes expected significance 0.81, but JSON says 0.846

**Description:** The conclusions (Section 11) state "expected sensitivity
of 0.81 sigma." The observed_results.json for nn_score has
`exp_significance: 0.8461690960500586`. The Phase 4a artifact reports
0.814 sigma. The 0.81 in the conclusions does not precisely match either
source.

**Required action:** Update to the correct value with appropriate
rounding. Use 0.85 sigma (from the 4c full-data expected) or 0.81 sigma
(from the 4a Asimov), but be explicit about which is being quoted.

---

## Finding F10 [Category C]: NP pull plot uses pull = (bestfit - init) / postfit_unc, but the x-axis label says "Pull (post-fit - pre-fit) / uncertainty"

**Description:** The x-axis label on the NP pull figure
(`np_pulls_full.png`) is ambiguous about which uncertainty is in the
denominator. Given Finding F4 above, this should be clarified to either
"(bestfit - prefit) / postfit uncertainty" or the standard "bestfit /
prefit uncertainty" convention.

**Required action:** Clarify the x-axis label to specify the denominator
convention.

---

## Regression Checklist

Evaluated per the mandatory post-review regression checklist:

- [ ] Any validation test failures without 3 documented remediation attempts?
  **YES** -- GoF p = 0.00 for all approaches. No remediation attempted. (Finding F1)
- [x] Any single systematic > 80% of total uncertainty?
  No. The top systematic (shape_mes) has impact 0.44 on a total uncertainty of 1.08.
- [ ] Any GoF toy distribution inconsistent with observed chi2?
  **YES** -- observed chi2 lies outside the entire toy distribution for all three approaches. (Finding F1)
- [x] Any flat-prior gate excluding > 50% of bins?
  No.
- [x] Any tautological comparison presented as independent validation?
  No.
- [x] Any visually identical distributions that should be independent?
  No.
- [x] Any result with > 30% relative deviation from a well-measured reference value?
  The primary result mu = 0.63 +/- 1.08 is consistent with both mu = 1 (SM) and the published mu = 0.78. No deviation flag triggered.
- [x] All binding commitments [D1]-[DN] from the strategy fulfilled?
  The 4c artifact does not re-verify strategy commitments (this was done at 4a). No new commitments were introduced.
- [x] Is the fit chi2 identically zero?
  No. chi2 = 33.1 for NN score, nonzero.

**Regression trigger: YES.** Two boxes are checked: GoF p = 0.00 and GoF
toy distribution inconsistent with observed chi2. Per the regression
checklist, these must be investigated even if the primary result is
physically sensible. However, given this is a 1-bot review at Phase 4c
with no arbiter, I recommend the following pragmatic path: if
investigation reveals the GoF failure is driven by the well-understood
VBF normalization deficit (already documented), and the primary NN
score result is not materially affected, a documented explanation may
suffice in lieu of full phase regression. But the investigation must
happen --- the current dismissal in the artifact is insufficient.

---

## Category Summary

| Category | Finding | Description |
|----------|---------|-------------|
| **A** | F1 | GoF p = 0.00 for all approaches; 14.5% toy convergence failures for NN score |
| **B** | F2 | NP pull table post-fit uncertainties inconsistent with JSON |
| **B** | F3 | Multiple NPs with exactly zero impact in one direction |
| **B** | F4 | Pull definition non-standard; 2-sigma flags may be inflated |
| **B** | F5 | 31% VBF deficit not quantitatively decomposed |
| **B** | F6 | Expected sigma(mu) quoted as 1.28 but 4a reports 1.247 |
| **C** | F7 | Post-fit plots lack uncertainty bands |
| **C** | F8 | Post-fit plots lack stacked process composition |
| **C** | F9 | Expected significance 0.81 vs JSON 0.846 |
| **C** | F10 | NP pull plot x-axis label ambiguous |

---

## Verdict: FAIL

One Category A finding (F1: GoF failure) blocks advancement. Five
Category B findings require correction. The Category A finding requires
investigation before it can be resolved --- it may not require phase
regression if the cause is identified and documented, but the current
artifact's dismissal of p = 0.00 is not acceptable.

After resolving F1 (investigation + honest reporting) and fixing
F2-F6 (number corrections + VBF accounting + pull convention
clarification), the artifact should be re-reviewed.
