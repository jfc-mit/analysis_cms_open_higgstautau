# Phase 4a Critical Review: Expected Results

**Reviewer:** Critical reviewer
**Artifact:** `phase4_inference/4a_expected/outputs/INFERENCE_EXPECTED.md`
**Supporting files:** `expected_results.json`, `validation_results.json`, workspaces, figures
**Date:** 2026-03-24

---

## Summary

The Phase 4a artifact presents a well-structured statistical model for
the H->tautau search in the mu-tau_h final state using three fitting
approaches (m_vis, NN score, m_col). The pyhf workspace construction is
sound, signal injection tests pass, and the impact ranking is physically
reasonable. However, several issues require resolution before advancing.

---

## Category A Findings (Must Resolve)

### A1. Toy GoF chi2 outliers indicate fit instability in m_vis and m_col workspaces

The `validation_results.json` GoF toy distributions for the m_vis and
m_col workspaces contain catastrophic outliers:

- **m_vis toys:** chi2 values of 96,962, 169,702, 107,699, and 105,902
  appear among 100 toys where the typical values are O(10-17). These are
  4-5 orders of magnitude larger than the bulk distribution.
- **m_col toys:** chi2 value of 95,004 among 99 toys with typical values
  O(8-18).
- **NN score toys:** No such outliers in 200 toys (all values in range
  4-11).

This indicates the m_vis and m_col fit models have convergence failures
or numerical instabilities in a significant fraction (~4%) of toy fits.
The p-value of 1.0 is still reported because the observed chi2 is near
zero, but the existence of these outliers means the fit model is not
robust. When real data is fit (Phase 4b/4c), convergence failures may
occur and go undetected.

**Required action:** Investigate the source of the toy fit failures.
Likely causes include bins with very small expected yields (near the
`min_val=1e-6` floor in `safe_template()`) causing numerical issues, or
the Barlow-Beeston gammas becoming unconstrained. Report the fraction of
failed toys and either fix the underlying issue or document the failure
mode with a mitigation strategy (e.g., rebinning low-statistics bins,
setting a higher minimum bin content).

### A2. JES MET propagation is physically incorrect

In `02_shape_systematics.py` lines 209-253, the JES systematic
propagation to MET uses hardcoded numerical factors:

```python
met_px -= total_jet_pt_change * 0.5  # factor 0.5 since direction unknown
met_py -= total_jet_pt_change * 0.3
```

The comment states "direction unknown" because jet phi is not stored.
This is not a valid approximation -- using fixed factors of 0.5 and 0.3
introduces a systematic bias in the MET response that has no physical
basis. The correct approach is either:

(a) Store jet phi in the Phase 3 arrays and propagate JES to MET
    properly: `MET_px -= (jet_pt_new - jet_pt_old) * cos(jet_phi)`, or
(b) If jet phi is truly unavailable, apply JES as a normalization-only
    systematic (category migration effect) without modifying MET, and
    document this limitation.

The current implementation creates an asymmetric, direction-dependent
MET shift that is neither the correct propagation nor a principled
approximation. The JES shape systematic impact (rank 4, delta_mu ~0.17)
may be partially artificial.

**Required action:** Fix the JES-to-MET propagation or remove the MET
component and document the limitation. If jet phi can be retrieved from
Phase 3 arrays, use the correct vector propagation.

### A3. MET unclustered energy systematic incorrectly scales total MET

In `02_shape_systematics.py` lines 255-264, the MET unclustered energy
systematic scales the entire MET vector by +/-10%:

```python
met_px = met_px * scale
met_py = met_py * scale
```

This is incorrect. The unclustered energy is only the component of MET
not associated with reconstructed objects (jets, leptons). The correct
procedure is:

```
MET_uncl = MET_total - sum(jet pT vectors) - muon pT vector - tau pT vector
MET_uncl_shifted = MET_uncl * (1 +/- 0.10)
MET_total_shifted = MET_uncl_shifted + sum(jet pT vectors) + muon pT + tau pT
```

By scaling the total MET, the current implementation effectively also
scales the clustered components (jets, leptons), which should remain
fixed under this systematic. This inflates the MET unclustered impact
(rank 3, delta_mu ~0.19). The MET unclustered uncertainty should affect
only the soft recoil, not the hard objects already accounted for by TES,
MES, and JES.

**Required action:** Implement the correct unclustered energy variation
by subtracting the clustered contribution before scaling, or document
why the simplified treatment is acceptable given the overall uncertainty
budget.

### A4. Tau ID efficiency reduced from 10% (strategy) to 5% without formal revision

The Phase 1 strategy (Section 9.1, row "Object calibration -- Tau")
explicitly committed to a 10% tau ID efficiency uncertainty:
> "Tau ID efficiency: loosened WP increases uncertainty; assign +/-10%
> per genuine tau (conservative for Open Data without official SFs)."

The summary table (Section 9.2) lists "Tau ID efficiency: 10%".

The Phase 4a implementation uses 5% (`03_build_workspace.py` line 203:
`"hi": 1.05, "lo": 0.95`). The artifact states this is from "CMS tau
POG, loosened WP" but does not cite a specific measurement or document
the revision from the strategy commitment. The strategy's 10% was
motivated by the lack of official scale factors for Open Data and the
loosened working point -- these conditions have not changed.

This is a silent reduction of a committed uncertainty by a factor of 2.
Per the CLAUDE.md regression checklist, "a decision committed in Phase 1
but silently replaced with an alternative approach is Category A."

**Required action:** Either restore the 10% tau ID uncertainty as
committed in the strategy, or formally revise [D7]-related uncertainty
with a documented justification (e.g., a Phase 2/3 data-driven
measurement of the tau ID efficiency scale factor uncertainty).

### A5. ggH QCD scale uncertainty reduced from +7.2%/-7.8% to +4.4%/-6.9% without documented justification

The Phase 1 strategy (Section 9.1 and 9.2) commits to ggH QCD scale
uncertainty of +7.2%/-7.8% from YR4. The Phase 4a implementation uses
+4.4%/-6.9% (`03_build_workspace.py` line 159:
`"hi": 1.044, "lo": 0.931`).

Both values are attributed to "YR4" but they differ significantly. The
+7.2%/-7.8% in the strategy includes the full scale + PDF + alpha_s
uncertainty on the ggH cross-section (combined envelope), while the
+4.4%/-6.9% is the scale-only component (with PDF treated separately as
3.2%). The artifact and workspace correctly separate scale and PDF, so
the total is comparable, but the strategy table row "Signal ggH xsec
(scale)" lists +7.2%/-7.8% as the scale component alone.

**Required action:** Clarify in the artifact which YR4 table/column
the +4.4%/-6.9% values come from (inclusive cross-section scale
uncertainty vs. acceptance-level scale variation). If the strategy's
+7.2%/-7.8% conflated scale+PDF while the implementation correctly
separates them, document this reconciliation explicitly in the
systematic completeness table.

### A6. Pileup reweighting committed in strategy but not implemented

The strategy (Section 9.1, "Additional pp-specific systematics") commits
to implementing pileup reweighting with a +/-5% systematic variation.
The status column says "Will implement." The completeness table in the
artifact (Section 6) lists pileup as "Not implemented" with a note that
"CMS Open Data NanoAOD does not include official pileup weights."

However, the strategy itself already anticipated this situation and
specified the procedure: "If no official CMS pileup profile is available
for Open Data, the data PV_npvs distribution serves as the target
directly." The strategy provided a concrete implementation method using
PV_npvs reweighting -- the absence of official pileup weights does not
prevent implementation.

The Phase 1 strategy said "Will implement" (not "Will implement if
available"). This is a binding commitment that was silently dropped.

**Required action:** Either implement the PV_npvs-based pileup
reweighting as described in the strategy (using the data PV_npvs
distribution as the target), or formally downscope with a [D] label and
quantitative justification for why the 12% Z normalization uncertainty
adequately covers the pileup effect.

---

## Category B Findings (Should Address)

### B1. Jet->tau fake rate shape systematic committed but not implemented

The strategy commits to a 20% jet->tau fake rate shape systematic
(Section 9.1: "Will implement (shape only)"). The artifact's
completeness table says it is "Absorbed in W+jets/QCD norm." The
strategy explicitly anticipated and rejected this absorption argument:
the strategy states the normalization component is absorbed, but the
shape component must be evaluated separately.

The artifact should either implement the fake rate shape systematic or
provide a quantitative argument that the 10% W+jets and 20% QCD
normalization uncertainties cover both normalization and shape effects.
Currently, no shape uncertainty from fake rate modeling is present.

### B2. Signal acceptance uncertainty committed but downscoped without quantitative substitute

The strategy commits to deriving signal acceptance uncertainty from
muR/muF scale variations in Phase 4a (P4a-1). COMMITMENTS.md marks this
as "[D] No muR/muF weight branches in NanoAOD." This is a legitimate
limitation, but the strategy also specified a 5% placeholder. The
current implementation has no signal acceptance systematic at all --
neither the 5% placeholder nor the scale-variation-derived value.

The total signal theory uncertainty (scale + PDF + BR) is present, but
acceptance effects from selection efficiency changes under scale
variations are not covered. This is a gap: scale variations change the
pT spectrum of the Higgs, which changes the selection efficiency,
especially for the VBF category.

### B3. Shape systematic shift plot (TES) shows excessive bin-to-bin fluctuations

The TES systematic shift figure (`syst_shift_tes.pdf`) shows
bin-to-bin variations of 10-20% for the ggH signal in the NN score
distribution. While some shape variation is expected, the pattern is
very noisy (e.g., ggH_down fluctuates between 0.80 and 1.20 across
adjacent bins). This suggests the shape systematic templates are
dominated by statistical fluctuations in the signal MC sample (~143
events in baseline) rather than genuine physics effects.

When MC statistical fluctuations dominate the shape systematic
templates, the fit can absorb statistical noise as "systematic
variation," leading to overcoverage. Consider smoothing the shape
systematic templates (e.g., using a polynomial or Gaussian kernel) or
symmetrizing the up/down variations to reduce the noise.

### B4. QCD shape systematic not evaluated under isolation threshold variation

COMMITMENTS.md item P4a-6 is marked "[D] Not implemented. Would require
reprocessing with different isolation thresholds." The strategy committed
to evaluating QCD shape uncertainty by varying the anti-isolation
threshold. The downscope justification ("would require reprocessing") is
weak -- varying the isolation threshold in the QCD estimation is a
standard procedure and does not require full reprocessing, only
re-running the QCD template estimation step with a different threshold.

The 20% QCD normalization uncertainty may not cover shape effects. At
minimum, document the expected shape variation magnitude.

### B5. Fragmentation uncertainty committed but downscoped without substitute

COMMITMENTS.md P4a-2 is marked "[D] No PS weight branches available."
The strategy committed to confirming or replacing a 2% fragmentation
uncertainty. Neither the 2% placeholder nor any substitute is present
in the implemented systematics. While this is expected to be subdominant,
it was a strategy commitment.

### B6. Number of m_vis bins may be insufficient for VBF category

The VBF category has ~1,224 total background events in 25 bins for
m_vis, giving an average of ~49 events/bin. However, the distribution
is peaked, so tail bins likely have < 5 expected events. The
`safe_template()` function floors bins at 1e-6, which creates
effectively empty bins. Combined with Barlow-Beeston gammas, this may
cause the toy fit instabilities observed in A1.

Consider rebinning the VBF category to ensure a minimum of ~5 expected
events per bin, or using adaptive binning.

### B7. CLs scan uses "obs/Asimov" label suggesting observed data was used

The CLs scan figure legend says "obs/Asimov" for all three approaches.
In a Phase 4a expected-results context, there should be no "observed"
result -- only expected. The dashed vs solid curves suggest the
"observed" is just the Asimov-as-observed, which is correct for Phase
4a, but the labeling may cause confusion. Relabel as "Expected (median)"
and show the +/-1,2 sigma expected bands, which are standard for CLs
limit presentations.

---

## Category C Findings (Suggestions)

### C1. GoF toy count inconsistency

The NN score GoF uses 200 toys, m_vis uses 100, and m_col uses 99
(one fewer than the stated 100). The unequal toy counts are unexplained.
Use a uniform count (200 for all) and investigate why m_col has 99
instead of 100 (likely a failed fit that was silently dropped rather
than reported).

### C2. Impact ranking figure should show pre-fit and post-fit impacts

The impact ranking figure shows only the +/-1sigma impacts on mu. The
standard CMS presentation includes both pre-fit (open) and post-fit
(filled) impact bars, plus the NP pull+constraint in a separate panel.
The NP pulls figure exists separately, but combining them into a
standard "Brazilian flag" impact plot would be more informative.

### C3. Template plot Asimov/Pred ratio panel is trivially 1.0

The ratio panel in the template plots (e.g., NN score baseline) shows
Asimov/Prediction = 1.000 everywhere by construction (since Asimov data
IS the prediction). This is not informative. For Phase 4a, consider
showing the signal/background ratio or the uncertainty band instead.
The ratio panel becomes meaningful only in Phase 4b/4c with real data.

### C4. Per-systematic documentation should include more physical interpretation

The artifact's systematic documentation (Sections 3.1-3.2) is primarily
tabular. The Phase 4a CLAUDE.md requires "running prose, not just
tables" for per-systematic documentation. Add a paragraph for each
systematic group explaining the physical origin, why the chosen
variation size is appropriate, and how the impact on the final result
compares to expectations.

### C5. Missing expected +/-1,2 sigma bands on CLs limit

The CLs limit values are reported without the +/-1,2 sigma expected
bands (which require running toys or using the asymptotic formulas).
These bands are standard for limit presentations and help assess the
analysis sensitivity.

---

## Decision Label Traceability: [D1]-[D13]

| Label | Strategy Commitment | Phase 4a Status | Verdict |
|-------|-------------------|----------------|---------|
| [D1] | Four fitting approaches | Three implemented (mvis, nn_score, mcol). NN-MET dropped per [D13]. | OK -- formally downscoped |
| [D2] | YR4 cross-sections | Implemented in MC weights | OK |
| [D3] | W+jets from high-mT | SF=0.999, 10% norm uncertainty | OK |
| [D4] | QCD from SS | R_OS/SS=0.979, 20% norm uncertainty | OK |
| [D5] | Primary trigger | Applied | OK |
| [D6] | Z norm 10-15% | 12% implemented | OK |
| [D7] | Loosened tau ID | Loose WP selected | OK, but tau ID uncertainty reduced (see A4) |
| [D8] | Anti-muon Tight | Applied | OK |
| [D9] | MVA vs cut-based comparison | NN selected as primary | OK |
| [D10] | Two categories | Baseline + VBF (thresholds optimized in P2/P3) | OK -- optimization documented |
| [D11] | Common mu fit | Implemented | OK |
| [D12] | SVfit not implemented | Collinear mass as alternative | OK |
| [D13] | NN-MET success criterion | Dropped, documented as negative result | OK -- formally downscoped |

**Issues:** [D7]-associated tau ID uncertainty silent reduction (A4).
Strategy's ggH scale values do not match implementation (A5). Pileup
reweighting commitment dropped (A6).

---

## Regression Assessment

No physics issues traceable to earlier phases are identified that would
require full phase regression. The VBF threshold change (m_jj 300->200,
|deta_jj| 2.5->2.0) was documented as a Phase 2 optimization and is
legitimate. The systematic sizing issues (A4, A5, A6) are Phase 4a
implementation issues that can be resolved within this phase.

---

## Verdict

**FAIL -- 6 Category A findings must be resolved before advancing.**

The core statistical framework (pyhf workspace, signal injection, NP
pulls) is sound and the expected results are physically reasonable.
However, the toy fit instabilities (A1), incorrect JES/MET propagation
(A2, A3), and silent reductions of committed systematic uncertainties
(A4, A5, A6) must be addressed. The Category B items should also be
resolved to strengthen the analysis before Phase 4b.
