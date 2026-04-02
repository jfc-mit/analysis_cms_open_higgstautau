# Phase 4a Constructive Review: Expected Results

**Reviewer:** Constructive reviewer
**Date:** 2026-03-24
**Artifact:** `phase4_inference/4a_expected/outputs/INFERENCE_EXPECTED.md`
**AN Draft:** `phase4_inference/4a_expected/outputs/ANALYSIS_NOTE_4a_v1.md`

---

## Overall Assessment

The Phase 4a artifact and analysis note present a well-structured statistical
analysis of the H->tautau signal strength using three discriminant approaches.
The NN approach achieves sigma(mu) = 1.15, which is a factor 2.6 improvement
over the visible mass baseline and consistent with the expected sensitivity
for a single-channel, single-period open data analysis. The systematic
program is comprehensive relative to the CMS Open Data constraints, and
the fit validation (signal injection, NP pulls) passes cleanly.

The analysis has genuine resolving power: the NN approach can set an expected
95% CL upper limit of mu < 2.36, which excludes enhanced production models
at the 2x SM level. However, standalone SM Higgs discovery significance is
only 0.89 sigma, so the measurement's primary scientific value is the
multi-approach comparison methodology, which is correctly framed in the AN.

Several opportunities for improvement are identified below, along with
genuine issues that must be addressed.

---

## Category A: Must Resolve

### A1. GoF toy distributions contain catastrophic outliers (m_vis and m_col)

The toy chi2 distributions for the m_vis and m_col workspaces contain
extreme outliers that indicate fit instability:

- **m_vis:** 4 toys out of 100 have chi2 values of ~97,000, ~170,000,
  ~108,000, and ~106,000. The remaining 96 toys cluster around 8-18.
- **m_col:** 1 toy out of 99 has chi2 ~ 95,000. The remaining 98 toys
  cluster around 7-22.
- **NN score:** All 200 toys cluster in the 4-11 range with no outliers.

These catastrophic chi2 values (5 orders of magnitude above normal) indicate
that 4-5% of toy fits are failing catastrophically -- likely hitting
convergence failures, unphysical NP values, or singular Hessians. This is
NOT reported in the artifact or AN, which state only "p-value = 1.0 for all
approaches" and "validates the toy generation and fitting machinery." The
presence of 4/100 catastrophic failures in the m_vis fit machinery
is a serious concern that directly undermines the claim that the GoF
validates the fit:

1. If these are convergence failures, the workspace has a stability problem
   that will manifest on real data.
2. If these are genuine toy outcomes, the model has a structural issue
   (possibly related to negative-bin handling or staterror instability in
   low-statistics bins).
3. The GoF p-value of 1.0 is technically correct (Asimov chi2 = 0 < all
   toy chi2) but is misleading when 4% of the reference distribution is
   corrupt.

**Required action:** Investigate the catastrophic toy chi2 values. Log the
NP post-fit values for those toys. If they are convergence failures, exclude
them and report the fraction excluded. If they are genuine, investigate the
model structure. Document the investigation regardless of outcome. This
finding is separate from the chi2/ndf = 0 on Asimov (which is expected by
construction).

### A2. Missing COMMITMENTS.md tracking artifact

The Phase 4 CLAUDE.md requires: "At Phase 4a start, read COMMITMENTS.md
(created at Phase 1 completion). Update every line's status." No
COMMITMENTS.md file exists in the analysis root. The strategy document
contains 13 [D] decisions, 4 [A] constraints, and 3 [L] limitations, and
Phase 4a must track their status. Without this artifact, there is no
auditable record of which Phase 1 commitments have been addressed,
modified, or silently dropped.

Most critically, [D1] committed to four fitting approaches, but only three
were implemented (the NN-regressed MET approach was dropped, labeled [D13]).
This was properly documented in the INFERENCE_EXPECTED.md artifact under
"Strategy Decision Verification." However, the formal tracking artifact
is still required.

**Required action:** Create COMMITMENTS.md with all [D], [A], and [L]
labels from STRATEGY.md. Mark each as [x] (resolved), [D] (formally
downscoped), or [ ] (pending). The [D13] downscope of the NN-MET approach
must be marked as [D] with its documented justification.

### A3. Shape systematic ratio plots show excessive bin-to-bin noise

The TES, MES, MET unclustered, and JES shape systematic ratio plots (all
showing Variation/Nominal vs NN score) exhibit large bin-to-bin fluctuations
that appear statistical rather than physical:

- **TES:** ggH up/down variations oscillate wildly between 0.80 and 1.20
  with no smooth trend, particularly at high NN score where MC statistics
  are low.
- **MES:** The 1% muon energy scale produces variations of up to +-10%
  in individual bins for ggH (visible in the figure), which is
  disproportionately large for a 1% energy shift. This suggests the
  shape change is dominated by statistical fluctuations from the limited
  ggH MC sample (4,603 events spread across 20 bins times 2 categories).
- **MET unclustered and JES:** Similar noise patterns.

When the up/down variations are dominated by MC statistical fluctuations
rather than the genuine physical effect of the systematic shift, the fit
treats statistical noise as systematic shape information. This inflates
the systematic uncertainty and constrains NPs artificially. The TES
post-fit uncertainty of 0.21 (constrained from 1.0) is suspiciously
aggressive -- the data (or in this case Asimov data) should not constrain
the TES to 21% of its prior unless the templates contain genuine shape
information at that precision level.

**Required action:** Quantify the MC statistical noise vs genuine shape
effect for each shape systematic. One approach: compare the RMS of
bin-to-bin fluctuations in the ratio to the expected statistical
uncertainty from finite MC. If the noise exceeds the genuine shape shift,
apply template smoothing (e.g., Gaussian kernel smoothing of the ratio,
or rebinning with fewer NN score bins for shape systematics). Alternatively,
increase the NN score binning from 20 to 10 bins, which would
reduce statistical noise while preserving the broad shape information.
Report the pre- and post-smoothing impact on mu.

---

## Category B: Should Address

### B1. Highly asymmetric MET unclustered energy impact suggests broken down variation

The MET unclustered systematic has a highly asymmetric impact:
Delta_mu(up) = -0.266, Delta_mu(down) = +0.047. The ratio is 5.7:1. For
a symmetric +-10% variation of a single quantity (MET magnitude), such
extreme asymmetry is unexpected unless there is a physical threshold effect.
The artifact explains this as "the signal sensitivity is more vulnerable to
MET increases than decreases," but this deserves more investigation.

Possibilities: (a) The down variation is partially absorbed by the
Barlow-Beeston parameters, masking its true effect. (b) The MET
propagation to NN features introduces a nonlinear response. (c) There is
a floor effect where MET scaling down brings values near zero where the
response flattens.

**Suggested action:** Plot the MET unclustered up/down template ratios for
the Baseline AND VBF categories separately to check whether the asymmetry
originates in one category. Check whether the up variation passes through
any selection thresholds (e.g., events migrating past the mT < 30 GeV cut
under varied MET). If the asymmetry is understood and physical, document
the explanation quantitatively. If it is a propagation artifact, fix it.

### B2. GoF figure shows only NN score toys; m_vis and m_col GoF not visualized

The GoF figure (`gof_toys.pdf`) appears to show only the NN score toy
distribution (200 toys, chi2 range 4-11). The m_vis and m_col toy
distributions -- which contain the catastrophic outliers noted in A1 -- are
not shown. The AN text states "200 toy fits" without clarifying that only
the NN score toys are plotted.

**Suggested action:** Either produce separate GoF plots for all three
approaches (preferred, for completeness), or produce a single figure with
three panels. This would make the catastrophic outlier issue visually
apparent and prompt investigation.

### B3. NP constraint on TES (post-fit uncertainty 0.21) is suspiciously tight

The TES NP post-fit uncertainty shrinks from 1.0 to 0.21 on the Asimov
fit. This means the template shapes in the fit constrain the TES to 21%
of its prior. For context:

- In published CMS H->tautau analyses, per-decay-mode TES is constrained
  to post-fit uncertainties of ~0.3-0.6 (not as aggressive as 0.21).
- The inclusive 3% TES variation in this analysis covers all decay modes,
  so the effective per-bin shape sensitivity should be smoother and less
  constraining than a per-DM variation.

A post-fit uncertainty of 0.21 on an inclusive TES NP, combined with the
noisy shape systematic templates (finding A3), strongly suggests the fit
is fitting statistical fluctuations in the template shapes rather than the
physical TES effect. This would lead to underestimated post-fit systematic
uncertainties and overconfident results.

This is closely related to A3 but flagged separately because the
consequence (overconstraint) is a physics-level concern, not just a
technical one.

**Suggested action:** After addressing A3 (template smoothing or
rebinning), check whether the TES post-fit uncertainty relaxes to a more
physical value (>0.3). If it does, the original templates were indeed
fitting noise.

### B4. m_col performs worse than m_vis despite being a "better" mass estimator

The collinear mass approach yields sigma(mu) = 3.72, which is 24% worse
than the simple visible mass (sigma(mu) = 2.99). The artifact attributes
this to the high unphysical solution fraction (45.7% for ggH), but the
analysis could benefit from a more quantitative investigation. Specifically:

- What is sigma(mu) if only events with physical collinear solutions are
  used?
- Is the degradation due to the fallback (using m_vis for unphysical
  events) diluting the mass peak, or due to the collinear mass resolution
  being inherently poor for this dataset?
- Would a cut on x_mu and x_tau (e.g., requiring both > 0.1) improve the
  mass resolution enough to offset the efficiency loss?

This is relevant because the strategy motivated m_col as an SVfit
alternative. If it consistently underperforms m_vis, the AN should explain
why more concretely (beyond the unphysical fraction), as a journal referee
would ask this question.

**Suggested action:** Add a brief study or explanatory paragraph in the AN
quantifying the m_col performance for the physical-solution subset vs the
full sample. This would strengthen the narrative and preempt referee
questions.

### B5. Data/Prediction ratio of 0.943 deserves attention

The corrected yield summary shows Data/Prediction = 0.943, meaning the
total prediction (MC + data-driven QCD) overshoots data by 6%. The AN
attributes this to QCD overestimation, which is plausible, but 6% is
non-trivial:

- The QCD estimate is 11,195 events. A 6% excess in the total (72,111
  vs 67,988) corresponds to ~4,123 excess events, which is 37% of the
  QCD estimate.
- This suggests the QCD normalization should be closer to ~7,000 events
  (37% lower), not 11,200.

The 20% QCD normalization uncertainty allows the fit to adjust this, but
the large pre-fit discrepancy means the QCD NP will pull significantly on
real data. This is worth monitoring.

**Suggested action:** Verify that the QCD estimate would be consistent
with the observed Data/MC discrepancy. If the implied QCD correction is
~37%, the 20% normalization uncertainty may be too narrow to cover it.
Consider whether the R_OS/SS value or the SS MC subtraction procedure
introduces a bias. Document this cross-check.

### B6. The AN should quantify the stat/syst decomposition more precisely

The AN states the total systematic uncertainty is ~0.56 and computes
the statistical component as sqrt(1.15^2 - 0.56^2) = 1.00. This is a
useful decomposition, but it should be obtained directly from the fit
(freezing NPs to their best-fit values to get stat-only, freezing the
POI to get syst-only) rather than by subtraction.

**Suggested action:** Perform a stat-only fit (all NPs fixed at nominal)
and a syst-only evaluation (data stat set to infinity) to validate the
subtraction. Report both the direct decomposition and the quadrature
check.

### B7. NN score Asimov data points show perfectly flat Asimov/Pred ratio

The NN score Baseline template figure shows Asimov/Pred = 1.000 in all
bins with error bars. This is correct by construction (Asimov data IS the
prediction), but the figure could be more informative by showing the
expected statistical uncertainty per bin (the Poisson sqrt(N) error bars),
which gives the reader a sense of the statistical precision in each bin.
The current error bars are present but very small compared to the axis
range of 0.8-1.2, making them hard to read.

**Suggested action:** Consider using a y-axis range of 0.95-1.05 or
removing the ratio panel for Asimov template plots (since it is
uninformative by construction). Alternatively, add a note in the caption
clarifying that the ratio panel becomes informative on data.

---

## Category C: Suggestions

### C1. Consider per-decay-mode TES for improved sensitivity

The analysis uses an inclusive 3% TES uncertainty across all tau decay
modes. Published CMS analyses use per-DM values: 1% for 1-prong, 3% for
1-prong+pi0, and 3% for 3-prong. Since the reduced NanoAOD contains the
decay mode information (it is used as an NN input), implementing per-DM
TES would:
- Reduce the TES impact on 1-prong taus (1% vs 3%)
- Provide more physically motivated templates
- Better match the reference analyses

This could improve sigma(mu) modestly by reducing the leading systematic.

### C2. Consider adaptive binning for VBF templates

The VBF category has very low statistics in several bins (<5 expected
events). While Barlow-Beeston handles this, the GoF and shape systematic
evaluations would benefit from fewer, wider bins in the VBF category.
The current uniform binning (same as Baseline) is suboptimal given the
~50x lower event count in VBF.

### C3. Impact ranking figure could include post-fit uncertainty bars

The impact ranking figure shows only the Delta_mu bars. Standard practice
(and the pyhf tutorial) includes the post-fit NP pull (central value +
error bar) alongside the impact bars. This is especially useful for
identifying NPs that are pulled or constrained. The NP pulls figure
exists separately but combining them would improve the presentation.

### C4. CLs scan should include expected limit bands

The CLs scan figure shows observed/Asimov CLs curves for all three
approaches but does not include the expected +-1sigma and +-2sigma bands
(the green and yellow bands standard in CMS limit plots). These bands
are available from the exp_cls array in expected_results.json (which
contains the 5 quantiles). Adding them would make the limit plot more
informative and consistent with standard CMS presentation.

### C5. Consider mentioning the analysis's unique methodological contribution more prominently

The comparison of three fitting approaches on the same data is genuinely
useful for the field. The factor-of-2.6 improvement from NN over m_vis,
and the underperformance of m_col, are concrete results with pedagogical
value. The AN could strengthen this narrative by:
- Adding a dedicated "Approach comparison" subsection in the Results
  section (beyond the table in Section 4.6)
- Plotting sigma(mu) and expected significance as bar charts side by side
  for the three approaches
- Discussing which NN input features drive the improvement

### C6. The 99 m_col toys (instead of 100) should be noted

The m_col GoF uses 99 toys instead of the requested 100. This suggests one
toy failed silently. Combined with finding A1 (catastrophic chi2 outliers),
this reinforces the concern about fit stability in the m_col workspace.

### C7. Improve readability of the systematic shift ratio plots

The ratio plots for systematic variations overlay up/down shifts for three
processes (ZTT, ggH, TTbar) with 6 overlapping lines. At NN score > 0.5,
where statistics are low, the lines are essentially noise. Consider either:
- Showing only ZTT (the dominant process) in the main plot
- Smoothing the ratio or showing a running average
- Showing absolute template shapes (nominal + varied) rather than ratios
  for the signal process, since the signal shape is the physically
  important quantity

---

## Resolving Power Assessment

**Can this analysis discriminate between physics models?**

Yes, within a limited scope. The NN approach with sigma(mu) = 1.15 can:
- Set a 95% CL upper limit of mu < 2.36, excluding enhanced production
  at 2x SM at 95% CL
- Distinguish mu = 0 from mu = 1 at 0.89 sigma (not significant)
- Distinguish mu = 0 from mu = 3 at ~2.6 sigma (marginal evidence)

This is consistent with the expected sensitivity for a single channel
with 11.5 fb-1. The analysis is statistically limited (stat uncertainty
~1.00 vs syst ~0.56), so the resolving power will improve with data but
is fundamentally limited by the single-channel scope.

**Would a journal referee accept this?**

The AN draft is detailed and well-structured. A referee would likely raise:
1. The m_col underperformance relative to m_vis (addressed in B4)
2. Whether the noisy shape templates inflate the systematic uncertainty
   or create artificial constraints (A3, B3)
3. The catastrophic GoF toys (A1) as a stability concern
4. The missing expected limit bands in the CLs scan (C4)
5. The 6% Data/Prediction discrepancy and its implications for the QCD
   estimate (B5)

With the Category A issues resolved and Category B items addressed, the
AN would be at a reasonable standard for a single-channel open data
measurement.

---

## Summary

| Category | Count | Key issues |
|----------|-------|------------|
| A (must resolve) | 3 | Catastrophic GoF toy outliers, missing COMMITMENTS.md, noisy shape systematic templates |
| B (should address) | 7 | Asymmetric MET impact, GoF visualization, TES overconstraint, m_col underperformance, Data/Pred ratio, stat/syst decomposition, Asimov ratio panels |
| C (suggestion) | 7 | Per-DM TES, adaptive VBF binning, impact plot style, CLs bands, approach comparison narrative, missing toy, systematic plot readability |
