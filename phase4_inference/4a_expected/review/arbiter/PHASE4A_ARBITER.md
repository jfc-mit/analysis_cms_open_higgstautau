# Phase 4a Arbiter Verdict: Expected Results

**Arbiter:** Phase 4a arbiter
**Date:** 2026-03-24
**Panel:** Physics reviewer, Critical reviewer, Constructive reviewer

**Artifacts reviewed:**
- `INFERENCE_EXPECTED.md`
- `expected_results.json`
- `validation_results.json`
- `02_shape_systematics.py` (lines 245-264, JES/MET propagation)
- `03_build_workspace.py` (line 203, tau ID sizing)
- `STRATEGY.md` (Sections 5, 9.1, 9.2)
- `COMMITMENTS.md`

---

## Executive Summary

The Phase 4a deliverable is fundamentally sound. The statistical model is
correctly formulated in pyhf, the NN approach delivers sigma(mu) = 1.15
with a clean workspace (0/200 toy failures), signal injection tests pass,
and the expected results are physically consistent with the reduced scope
of a single-channel 8 TeV open data analysis. The analysis note is
comprehensive at 51 pages.

However, the review panel identified genuine issues that must be resolved.
After independent evaluation, I sustain 4 findings at Category A, promote
1 to Category A, and reclassify several others. The most consequential
issues are: (1) catastrophic GoF toy failures in the m_vis/m_col
workspaces, (2) physically incorrect JES-to-MET propagation, (3) MET
unclustered scaling applied to total MET rather than unclustered component,
and (4) noisy shape systematic templates that may be driving the aggressive
TES post-fit constraint.

**Verdict: ITERATE** -- resolve the 5 Category A findings, then re-review.

---

## Adjudication Table

| ID | Finding | Source | Their Cat | Final Cat | Rationale |
|----|---------|--------|-----------|-----------|-----------|
| F1 | GoF toy chi2 outliers in m_vis (4/100) and m_col (1/99) workspaces | Physics A1, Critical A1, Constructive A1 | A, A, A | **A** | All three reviewers agree. Verified in `validation_results.json`: m_vis toys include chi2 values of 96,962; 169,702; 107,699; 105,902 (lines 364, 366, 372, 375). m_col has 95,004 (line 409). These are 4-5 orders of magnitude above the bulk distribution (8-18 for m_vis, 7-22 for m_col). The NN workspace is clean (200 toys, range 4-11). A 4% failure rate in m_vis toys indicates structural instability -- likely from near-empty bins in VBF templates causing likelihood evaluation failures under toy fluctuations. These workspaces are cross-checks, not the primary result, but they must be numerically stable before fitting data. |
| F2 | JES MET propagation uses hardcoded factors 0.5/0.3 | Critical A2 | A | **A** | Verified in `02_shape_systematics.py` lines 250-251: `met_px -= total_jet_pt_change * 0.5` and `met_py -= total_jet_pt_change * 0.3`. The comment explicitly states "direction unknown" because jet phi is not stored. Using fixed directional projections (0.5, 0.3) is physically incorrect -- there is no basis for these numbers. The JES shape systematic ranks 4th in impact (delta_mu ~ 0.17) and this impact may be partially artificial. The correct fix is to retrieve jet phi from Phase 3 arrays (it should be available as jets are reconstructed objects) and use proper vector propagation, or to remove the MET component of JES and document the limitation. Only the critical reviewer identified this; the physics and constructive reviewers missed it. I sustain at Category A because the impact ranking is corrupted by an incorrect implementation. |
| F3 | MET unclustered systematic scales total MET, not unclustered component | Critical A3 | A | **A** | Verified in `02_shape_systematics.py` lines 261-262: `met_px = met_px * scale` and `met_py = met_py * scale`. The code comments even say "unclustered component" but then scales the total MET vector. The correct procedure subtracts the clustered contributions (jets + leptons) before scaling and adds them back. By scaling everything, the variation double-counts the jet/lepton energy scales already covered by TES, MES, and JES. This inflates the MET unclustered impact (rank 3, delta_mu ~ 0.19). Only the critical reviewer caught this. I sustain at Category A because it introduces double-counting of energy scale effects. |
| F4 | Shape systematic templates dominated by MC statistical noise | Constructive A3, Critical B3 | A, B | **A (promoted)** | The constructive reviewer raised this at Category A; the critical reviewer raised a related observation (B3, signal MC fluctuations) at Category B. I promote to Category A based on the following chain of evidence: (a) TES post-fit uncertainty = 0.21, constraining from 1.0 by a factor of ~5; (b) the physics reviewer notes this is more aggressive than published CMS analyses (0.3-0.6 typical); (c) the constructive reviewer observes that ggH up/down ratios oscillate between 0.80-1.20 across adjacent bins; (d) with only ~143 ggH events in the Baseline category spread across 20 bins, statistical fluctuations in the shape ratio exceed the genuine 3% TES physics effect. The fit interprets these fluctuations as precision shape information, producing artificial NP constraints. This affects all four shape systematics and their combined contribution of delta_mu ~ 0.55. Template smoothing or rebinning is required to separate genuine shape information from MC noise. |
| F5 | Tau ID efficiency reduced from 10% (strategy) to 5% without formal revision | Critical A4 | A | **B (downgraded)** | I carefully examined the strategy document. The physicist who drafted the strategy requested loosening to 10-15% for an initial conservative estimate, and the user subsequently directed specific values (Z norm 10-15%, tau ID loosened). The 5% value used in the implementation is cited as "CMS tau POG, loosened WP" and matches the published CMS 13 TeV reference analysis (R2). The strategy's 10% was explicitly described as "conservative for Open Data without official SFs" -- using a value that matches the published measurement is a reasonable refinement, not a silent reduction. However, the change was not formally documented in COMMITMENTS.md with a justification. Downgraded to Category B: document the revision from 10% to 5% with the CMS POG citation, and update COMMITMENTS.md. |
| F6 | ggH QCD scale values differ between strategy table and implementation | Critical A5 | A | **C (downgraded)** | I examined the strategy document carefully. There is an internal inconsistency IN THE STRATEGY ITSELF: Section 5 (data samples) correctly states "Scale: +4.4%/-6.9%, PDF+alpha_s: +/-3.2%" from YR4. However, the conventions table (Section 9.1) and the summary table (Section 9.2, row "Signal ggH xsec (scale)") list "+7.2%/-7.8%" as the scale component. The +7.2%/-7.8% is the combined scale+PDF+alpha_s envelope. The implementation correctly separates these: scale +4.4%/-6.9% and PDF 3.2% as independent NPs, which is the correct YR4 decomposition and matches Section 5 of the strategy. The implementation is RIGHT; the strategy summary table conflated two uncertainty components. This is a documentation issue in the strategy, not an error in Phase 4a. Downgrade to Category C: add a footnote in the artifact reconciling the two strategy entries. |
| F7 | Pileup reweighting committed but not implemented | Critical A6, Physics B3 | A, B | **B** | The strategy says "Will implement" for pileup reweighting with a specific procedure using PV_npvs distributions. The implementation drops it with the justification that official pileup weights are unavailable. The critical reviewer correctly notes that the strategy anticipated this and provided a PV_npvs-based alternative. However, I evaluate this as Category B rather than A for Phase 4a because: (1) the primary NN approach workspace is clean and well-validated, (2) the pileup effect is a shape correction that is partially absorbed by the 12% Z normalization and the per-category normalization freedoms, (3) at 8 TeV with ~20 pileup interactions, the effect is smaller than at 13 TeV, and (4) implementing pileup reweighting would require re-running Phase 3. The critical reviewer's point is valid that this was committed, but addressing it at Phase 4b (before data) is acceptable. Must be implemented before Phase 4c. |
| F8 | Pre-fit vs post-fit significance not reconciled in AN | Physics A2 | A | **B (downgraded)** | The physics reviewer identified that Table 19 (S/sqrt(B) = 1.52 sigma) and Table 23 (profile likelihood = 0.89 sigma) are not reconciled. Both numbers are correct in their contexts -- the first is a cut-and-count estimate in an optimized signal window, the second is the full profile likelihood result. The discrepancy is expected and well-understood by any statistician. This is a documentation clarity issue, not a physics error. Downgrade to Category B: add a bridging sentence explaining why the two metrics differ. |
| F9 | COMMITMENTS.md not created/updated in Phase 4a outputs | Constructive A2 | A | **C (downgraded)** | COMMITMENTS.md exists in `phase1_strategy/outputs/COMMITMENTS.md` and is fully populated with [D], [x], and status entries for all commitments including P4a-1 through P4a-6. The constructive reviewer may not have found it because it is in the Phase 1 outputs directory rather than the analysis root. The artifact's Section 9 ("Strategy Decision Verification") provides an equivalent tracking table. The COMMITMENTS.md file exists and is updated. Downgrade to Category C: consider symlinking or copying to the analysis root for discoverability. |
| F10 | Jet->tau fake rate shape systematic committed but not implemented | Critical B1 | B | **B** | Sustained. The strategy committed to shape-only fake rate uncertainty evaluated from anti-isolated sideband. The artifact claims it is "absorbed in W+jets/QCD norm." Normalization and shape are different uncertainty types. However, QCD is only 15% of the Baseline background with a relatively flat NN score distribution, so the missing shape systematic is unlikely to be dominant. Must be addressed or formally downscoped with quantitative justification. |
| F11 | Signal acceptance uncertainty committed but not implemented | Critical B2 | B | **B** | Sustained. P4a-1 is marked [D] in COMMITMENTS.md due to missing muR/muF weight branches. The strategy's 5% placeholder is not present. The signal theory normalization (scale + PDF + BR) is implemented, but acceptance effects on selection efficiency under scale variations are not covered. This is a genuine gap, though subdominant to the shape systematics. |
| F12 | MET unclustered impact asymmetry (factor 6) | Physics B2, Constructive B1 | B, B | **B** | Both reviewers agree. The -0.266/+0.047 asymmetry is extreme. However, this finding is SUBSUMED by F3 (incorrect MET unclustered implementation). Once F3 is fixed (scaling only the unclustered component), the asymmetry will likely change substantially. Defer investigation until after the fix. |
| F13 | QCD shape uncertainty downscoped with weak justification | Physics B4, Critical B4 | B, B | **B** | Both reviewers agree that "20% normalization covers shape effects" is insufficient. The critical reviewer correctly notes that varying the isolation threshold does not require full reprocessing. The physics reviewer suggests arguing from the flatness of the QCD NN score distribution. Both arguments should appear in the justification. |
| F14 | m_col performs worse than m_vis | Constructive B4 | B | **C** | The artifact already explains this quantitatively: 45.7% unphysical solution fraction for ggH dilutes the mass resolution. The fallback to m_vis for unphysical events makes m_col a degraded version of m_vis for nearly half the signal. This is a known limitation of the collinear approximation and is well-documented. Downgrade to suggestion: the additional study the constructive reviewer proposes (physical-solution-only subset) would strengthen the narrative but is not required for Phase 4a. |
| F15 | Data/Prediction ratio 0.943 | Constructive B5 | B | **C** | The 6% excess prediction is within the 20% QCD normalization uncertainty and will be absorbed by the fit. This is a pre-fit observation; post-fit QCD normalization will adjust. Not concerning for Phase 4a expected results. |

---

## Findings Not Raised by Reviewers

### F16. m_col has 99 toys instead of 100 -- silent failure (Category C)

Both the critical reviewer (C1) and constructive reviewer (C6) noted this
but only as suggestions. The 99th toy likely failed silently (convergence
failure that was caught and excluded, or a crash). Combined with the
catastrophic outlier in the remaining 99 toys, this reinforces F1.
Category C because it is subsumed by the F1 investigation.

### F17. No convergence quality monitoring in toy fits (Category B)

None of the reviewers explicitly raised this, but the GoF toy outliers
(F1) and the missing m_col toy (F16) together indicate that the toy
fitting machinery does not monitor or report convergence quality. The
`05_validation.py` script should log the minimizer status for each toy
and report the fraction of non-converged fits. This is standard practice
in pyhf toy studies. Category B because it is needed for reliable GoF
interpretation on data.

---

## Final Classification Summary

| Category | Count | IDs |
|----------|-------|-----|
| **A (must resolve)** | 5 | F1 (GoF toys), F2 (JES MET propagation), F3 (MET unclustered scaling), F4 (shape template noise/TES overconstraint) |
| **B (must fix before PASS)** | 7 | F5 (tau ID documentation), F7 (pileup), F8 (significance reconciliation), F10 (fake rate shape), F11 (signal acceptance), F12 (MET asymmetry, deferred to post-F3), F13 (QCD shape justification), F17 (convergence monitoring) |
| **C (suggestion)** | 5 | F6 (ggH scale reconciliation), F9 (COMMITMENTS.md location), F14 (m_col study), F15 (Data/Pred ratio), F16 (99 toys) |

**Note:** F4 comprises 4 items in the Category A count header but is a single
finding. Total Category A count is 4 findings (F1, F2, F3, F4).

---

## Priority-Ordered Fix List

### Category A -- Must resolve before re-review

**1. F2 + F3: Fix shape systematic MET propagation (highest priority)**

These two findings are coupled and should be fixed together in
`02_shape_systematics.py`:

- **F2 (JES):** Retrieve jet phi from Phase 3 arrays. If available,
  propagate JES to MET using the correct vector formula:
  `MET_px -= (jet_pt_shifted - jet_pt_nominal) * cos(jet_phi)` for each
  jet. If jet phi is genuinely unavailable, remove the MET component of
  JES entirely and document that JES affects only category migration, not
  MET. Do NOT use hardcoded directional factors.

- **F3 (MET unclustered):** Compute the unclustered component by
  subtracting clustered objects:
  `MET_uncl = MET_total - sum(jet pT vectors) - muon pT vector - tau pT vector`.
  Scale only `MET_uncl` by +/-10%, then recompute the total MET. If the
  individual object momenta are available (they should be from Phase 3
  arrays), this is straightforward.

After fixing, re-run the full shape systematic pipeline, rebuild
workspaces, and regenerate all downstream results. Compare the impact
ranking before and after -- the JES and MET unclustered impacts should
change. If they decrease substantially, the original impacts were
indeed artifacts of the incorrect implementation.

**2. F4: Address shape systematic template noise**

Quantify MC statistical noise vs genuine shape effect for each of the
four shape systematics. Specifically:

- For each systematic and each process, compute the expected statistical
  uncertainty per bin from finite MC: sigma_stat = 1/sqrt(N_bin).
- Compare this to the observed bin-to-bin variation in the ratio
  (shifted/nominal).
- If sigma_stat > |ratio - 1| in most bins (i.e., the noise exceeds the
  signal), the shape template is noise-dominated.

Remediation options (implement one):
(a) Apply Gaussian kernel smoothing to the ratio (shifted/nominal),
    then multiply the smoothed ratio by the nominal template to get the
    shifted template. This preserves the broad shape trend while
    suppressing statistical noise.
(b) Reduce NN score binning from 20 to 10 bins, doubling the per-bin
    statistics. This is cruder but simpler.
(c) Symmetrize up/down variations: shifted = nominal * (up/down)^(+/-0.5),
    which cancels some statistical fluctuations.

After remediation, verify that the TES post-fit uncertainty relaxes from
0.21 to something more physical (>0.3). If it does, the original
constraint was fitting noise. Report both pre- and post-smoothing values.

**3. F1: Investigate and fix GoF toy failures**

- Re-run the m_vis and m_col GoF toys with convergence logging. For each
  toy, record the minimizer status (converged/not), the number of
  iterations, and any NP at its boundary.
- Identify the root cause. Most likely: near-empty bins in VBF templates
  cause likelihood evaluation failures when toy fluctuations drive bin
  contents negative (below the 1e-6 floor).
- Fix: either (a) rebin VBF templates to ensure minimum 5 expected
  events per bin, or (b) raise the minimum bin content floor, or
  (c) merge low-statistics VBF bins.
- Report cleaned p-values (excluding non-converged toys) alongside the
  raw values, with the fraction excluded clearly stated.

### Category B -- Must fix before PASS (address after A items)

**4. F5:** Document the tau ID 10% to 5% change in COMMITMENTS.md with
the CMS POG citation and the reasoning that 5% matches the published
13 TeV measurement. This is a documentation fix, not a code change.

**5. F8:** Add a bridging sentence in Section 9.2 of the AN explaining
that pre-fit S/sqrt(B) significance (Table 19) and post-fit profile
likelihood significance (Table 23) are different metrics: the former uses
a cut-and-count window, the latter uses the full binned shape with
systematic profiling. They are not directly comparable.

**6. F7:** Formally downscope pileup reweighting with a [D] label and a
quantitative argument: report the data/MC PV_npvs disagreement level
from Phase 2, argue that the shape effect on the NN discriminant is
subdominant to the four implemented shape systematics (TES, MES, JES,
MET uncl total impact ~ 0.55 on mu), and commit to implementing before
Phase 4c if the data fit shows NP pulls suggesting pileup mismodeling.

**7. F10 + F13:** The QCD shape systematic and jet->tau fake rate shape
systematic are both downscoped. Strengthen the justification by:
(a) plotting the QCD NN score distribution and demonstrating its
approximate flatness, (b) arguing that a flat shape has negligible
impact on signal extraction regardless of normalization, and
(c) noting that the 20% QCD norm (rank 7 in impacts) already provides
substantial freedom. Formally mark both as [D] with this justification.

**8. F11:** Add the 5% signal acceptance placeholder from the strategy
or formally downscope with a [D] label and quantitative argument that
the effect is subdominant (signal acceptance changes from scale
variations are typically 1-3% for inclusive categories, well within the
existing signal theory normalization uncertainties).

**9. F17:** Add convergence monitoring to toy fits. Log minimizer status,
report non-convergence fraction.

### Category C -- Apply before commit

**10. F6:** Add a footnote in the systematic completeness table noting
that the strategy's Section 9.2 table entry "+7.2%/-7.8% ggH scale" was
a combined scale+PDF+alpha_s envelope, while the implementation correctly
decomposes this into scale (+4.4%/-6.9%) and PDF+alpha_s (3.2%) as
independent NPs per YR4 best practice. Reference Section 5 of the
strategy for the original decomposition.

**11. F9:** The COMMITMENTS.md file exists and is up-to-date. No action
required beyond noting its location for discoverability.

**12. F14, F15, F16:** Minor improvements to documentation and
presentation. Apply if time permits.

---

## Regression Assessment

No phase regression is required. All Category A findings are Phase 4a
implementation issues that can be resolved within this phase:

- F2/F3: Code fixes in `02_shape_systematics.py`
- F4: Template processing (smoothing or rebinning)
- F1: Workspace stability (rebinning or floor adjustment)

None of these require changes to Phase 1 (strategy), Phase 2
(exploration), or Phase 3 (selection). The Phase 3 arrays contain the
necessary kinematic information; the issue is how Phase 4a processes them.

---

## Orchestrator Regression Checklist (independent evaluation)

- [x] Any validation test failures without 3 documented remediation
      attempts? **YES -- F1 (GoF toy failures). Category A sustained.**
- [x] Any single systematic > 80% of total uncertainty? **No.** TES is
      largest at 33% of total.
- [x] Any GoF toy distribution inconsistent with observed chi2? **YES --
      m_vis and m_col toy distributions contain catastrophic outliers.
      Covered by F1.**
- [x] Any flat-prior gate excluding > 50% of bins? **No.**
- [x] Any tautological comparison presented as independent validation?
      **No.** NP pulls = 0 on Asimov correctly noted as by construction.
- [x] Any visually identical distributions that should be independent?
      **No.**
- [x] Any result with > 30% relative deviation from a well-measured
      reference value? **No.** sigma(mu) = 1.15 is 4.3x the published
      combined result, quantitatively consistent with reduced scope.
- [x] All binding commitments [D1]-[DN] from the strategy fulfilled?
      **All [D] and [A] labels addressed.** Tau ID sizing change
      undocumented (F5, Category B). Pileup commitment dropped (F7,
      Category B). QCD shape dropped (F13, Category B). All have
      reasonable justifications but need formal [D] documentation.
- [x] Is the fit chi2 identically zero? **Yes, by construction on Asimov.
      Expected and correct for Phase 4a. Not a circularity concern.**

---

## Verdict

**ITERATE.**

The analysis is fundamentally sound. The NN approach delivers clean
results with a well-validated workspace, physically sensible expected
sensitivity (sigma(mu) = 1.15, 0.89-sigma expected significance), and a
comprehensive systematic program. The factor-of-2.6 improvement over
visible mass is the key scientific result and is well-supported.

However, 4 Category A findings must be resolved before advancing:

1. **F2 + F3 (MET propagation):** The JES and MET unclustered shape
   systematics have incorrect MET implementations that corrupt the impact
   ranking. These are the 3rd and 4th largest systematics and together
   contribute delta_mu ~ 0.25 to the total uncertainty. Fixing them will
   change the results.

2. **F4 (template noise):** The shape systematic templates are
   noise-dominated for signal processes, producing an artificially tight
   TES constraint (post-fit 0.21, compared to 0.3-0.6 in published
   analyses). This affects the uncertainty decomposition.

3. **F1 (GoF toy stability):** The m_vis and m_col workspaces have 4% and
   1% catastrophic failure rates. These must be stabilized before fitting
   data.

After resolving Category A items, the 7 Category B items must be addressed
before the arbiter will issue PASS. The most important Category B items
are the systematic documentation (F5, F7, F8) and convergence monitoring
(F17).

The analysis does NOT need to return to an earlier phase. All fixes are
within Phase 4a scope.

---

## Re-review Scope

After fixes, the re-review should focus on:

1. The corrected shape systematic implementations (F2, F3) -- verify the
   impact ranking has changed and the new values are physically sensible.
2. The smoothed/rebinned shape templates (F4) -- verify the TES post-fit
   constraint has relaxed.
3. The stabilized GoF toy fits (F1) -- verify the failure rate is < 1%
   for all workspaces.
4. Updated documentation for Category B items.

A single critical reviewer is sufficient for the re-review (the issues
are well-defined and the scope is narrow). If the impact ranking changes
substantially (any systematic moving by more than 2 ranks), a full
re-review panel should be convened.
