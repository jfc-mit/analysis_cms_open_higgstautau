# Phase 1 Re-Review: Post-Fix Verification

**Reviewer role:** Critical re-reviewer (fix verification)
**Date:** 2026-03-24
**Artifact reviewed:** `phase1_strategy/outputs/STRATEGY.md` (1283 lines, post-fix)
**Supporting artifact:** `phase1_strategy/outputs/COMMITMENTS.md`
**Arbiter verdict reviewed:** `phase1_strategy/review/arbiter/PHASE1_ARBITER.md`
**Conventions file:** `conventions/search.md`

**Scope:** This is NOT a from-scratch review. The goal is to verify that
all 6 Category A and 17 Category B findings from the arbiter's ITERATE
verdict have been properly resolved by the fixer agent, and to check
whether any fixes introduced new issues.

---

## Category A Verification

### A1: Z normalization decomposition + trigger double-counting
**Status: RESOLVED.**

Section 7.1 (lines 492-521) now contains an explicit quantitative
decomposition table:

| Component | Estimate | Source |
|-----------|----------|--------|
| Theory cross-section | 3-4% | FEWZ NNLO |
| Trigger efficiency | ~5% | No SFs available |
| Tau ID loosening | 5-8% | Loose vs Tight WP |
| Statistical | ~2% | Z peak region |
| **Total (quadrature)** | **8-11%** | Rounds to 10-15% |

The decomposition is physically sensible and the quadrature sum of 8-11%
supports the 10-15% range (with the rounding justified by residual
correlations).

The trigger double-counting is explicitly resolved: the trigger efficiency
component is "absorbed into the Z normalization uncertainty" (line 505-512),
and the separate trigger systematic in Section 9.2 is retained only for
signal, ttbar, and W+jets — NOT for ZTT/ZLL. The summary table (line 905)
confirms: "Trigger efficiency: 3% — Signal, TTbar, W+jets (NOT ZTT —
absorbed in Z norm [D6])." The trigger uncertainty is also reduced from
5% to 3% for the non-Z processes, which is reasonable since the cross-
trigger plateau region is well above the offline pT thresholds.

**Verdict: Properly resolved. No remaining issues.**

---

### A2: Signal cross-section normalization
**Status: RESOLVED.**

Section 3.2 (lines 157-216) now clearly states:

1. The signal MC samples contain **only H->tautau events** (line 159-162).
2. The explicit weight formula is given (lines 166-169):
   - Signal: w = sigma_prod x BR(H->tautau) x L_int / N_gen
   - Backgrounds: w = sigma x L_int / N_gen
3. YR4 cross-sections are used consistently for signal (lines 173-192):
   ggH = 21.39 pb (N3LO), VBF = 1.600 pb (NNLO QCD + NLO EW),
   BR(H->tautau) = 6.256%.
4. The tutorial vs YR4 discrepancy is acknowledged (lines 181-183):
   "the CMS Open Data tutorial uses 19.6 pb ... we use YR4 to avoid the
   ~8.4% bias."
5. mu = 1 is explicitly defined (lines 210-216): sigma_SM x BR =
   (21.39 + 1.600) x 0.06256 = 1.438 pb for ggH + VBF.

The cross-section table (lines 148-156) shows the computed sigma x BR
values and per-event weights for each sample. The signal rows use the
YR4-derived values consistently.

**Verdict: Properly resolved. No remaining issues.**

---

### A3: NN-regressed MET success criterion
**Status: RESOLVED.**

Section 8.3 (lines 742-763) now contains:

1. **Quantitative success metric** [D13]: >15% MET resolution improvement
   on MC test set (line 743-746), defined as RMS of
   (MET_reco - MET_gen)/MET_gen.
2. **Data validation plan** (lines 747-752): Z->tautau mass peak width
   improvement >10% (Gaussian sigma reduction) in the Z peak region
   (60-120 GeV) in data.
3. **Overtraining check** (lines 753-755): consistency between training
   and test MC within 20% relative.
4. **Explicit downscope** (lines 757-763): if >15% not met by end of
   Phase 3, approach (c) is dropped. If MC passes but data fails, results
   reported with caveat.

The priority ordering table in Section 2.2 (lines 96-104) also lists the
go/no-go for approach (c) at priority 4 (lowest).

**Verdict: Properly resolved. No remaining issues.**

---

### A4: QCD OS/SS ratio
**Status: RESOLVED.**

Section 7.3 (lines 565-609) now:

1. **Commits to measuring from data** (lines 575-582): "Measure the OS/SS
   ratio from data in a QCD-enriched anti-isolated control region."
   Explicitly states: "Neither the tutorial value (0.80) nor the published
   analysis value (1.06) is used blindly."
2. **Negative-bin procedure** (lines 587-594): first merge adjacent bins
   (minimum 5 expected events per merged bin), then set negative bins to
   zero with asymmetric shape uncertainty equal to the absolute value.

The validation plan (lines 596-603) includes measuring the OS/SS ratio
in bins of m_vis to check for mass dependence — a good addition.

**Verdict: Properly resolved. No remaining issues.**

---

### A5: Uncited numeric constants (5% acceptance, 2% fragmentation)
**Status: RESOLVED.**

Both values are now honestly acknowledged as estimates rather than cited
as published values:

1. **Signal acceptance (+/-5%):** Section 9.1, signal acceptance row
   (line 838) explicitly states: "The +/-5% acceptance uncertainty is an
   approximate estimate ... no single publication was found with this exact
   number ... web searches ... did not yield a citable value." It commits
   to deriving the value quantitatively in Phase 4a from muR/muF scale
   variations (7-point envelope). The COMMITMENTS.md tracks this as P4a-1.

2. **Fragmentation (+/-2%):** Section 9.1, fragmentation row (line 870)
   states: "The +/-2% uncertainty ... is an approximate estimate ... web
   searches ... found values of ~1% in CMS jet energy scale studies
   (JINST 6 (2011) P11002, arXiv:1107.4277)." Commits to Phase 4a
   confirmation (COMMITMENTS.md P4a-2).

This is the correct resolution: honest acknowledgment of approximations
with a commitment to derive proper values. The partial citation of the
JES study for the fragmentation value is a good-faith attempt.

**Verdict: Properly resolved. No remaining issues.**

---

### A6: Collinear mass fallback
**Status: RESOLVED.**

Section 8.4 (lines 788-817) now contains:

1. **Expected unphysical fractions** (lines 788-797): table with
   per-process estimates (signal ~30%, Z->tautau ~35%, W+jets ~40-50%,
   ttbar ~40-50%, QCD ~50-60%). These are marked as estimates to be
   measured in Phase 2 (COMMITMENTS.md P2-8).

2. **Template smoothness commitment** (lines 803-811): Phase 4a check
   that migration between physical/fallback populations under +/-1 sigma
   TES is < 10%, and that template shapes change smoothly.

3. **Fallback revision plan** (lines 812-817): two alternatives if
   discontinuities are found: (a) clamping x to [0.01, 0.99], or
   (b) using visible mass for all events and demoting collinear mass
   to an NN input.

The priority table (line 103) also lists the go/no-go for approach (d):
unphysical fraction < 50% for signal + template smoothness check.

**Verdict: Properly resolved. No remaining issues.**

---

## Category B Verification

### B1: Expected sensitivity estimate
**Status: RESOLVED.**

Section 2.1 (lines 46-63) now contains a quantitative S/sqrt(B) estimate:
- Baseline: S/sqrt(B) ~ 0.7-1.5
- VBF: S/sqrt(B) ~ 0.7-2.1
- Combined: S/sqrt(B) ~ 1.0-2.6

Expected sigma(mu) ~ 1-2 is stated. The analysis goal is reframed:
"The analysis is not expected to achieve standalone discovery-level
significance. The scientific contribution is the four-approach comparison
methodology."

**Verdict: Properly resolved.**

---

### AR1: ttbar at NNLO+NNLL or >= 12% uncertainty
**Status: RESOLVED.**

Section 3.2 (lines 199-204) now uses 252.9 pb (NNLO+NNLL, Top++v2.0)
with ~5% theory uncertainty. The tutorial LO value (225.2 pb) is
acknowledged and explicitly rejected: "using the LO value with an 8%
uncertainty would not cover the known offset to best theory" (lines
621-624). The summary table (line 981) confirms "TTbar norm: 5% NNLO+NNLL."

**Verdict: Properly resolved.**

---

### B2: COMMITMENTS.md produced
**Status: RESOLVED.**

COMMITMENTS.md exists (65 lines) and contains:
- All 13 binding decisions [D1]-[D13] with status checkboxes
- All 4 constraints [A1]-[A4]
- All 3 limitations [L1]-[L3]
- 10 Phase 2 commitments (P2-1 through P2-10) with traceability
- 6 Phase 4a commitments (P4a-1 through P4a-6)

The tracking artifact is well-structured and links each commitment to
its origin finding.

**Verdict: Properly resolved.**

---

### B3: Diboson quantification + PDF limitation
**Status: RESOLVED.**

Section 4.2, [A3] (lines 263-280) now:
- Cites R1 (Table 2) for diboson normalization uncertainties (15-30%
  non-VBF, 15-100% VBF)
- Estimates the diboson contribution at ~1-3% from cross-sections
- Specifies the correlation structure for the +/-5% (single correlated
  NP on all MC backgrounds, independent of individual normalization NPs)
- Notes it is not applied to data-driven backgrounds

The PDF limitation is acknowledged in the signal acceptance row of
Section 9.1 (line 840): "Currently implemented as normalization-only.
Limitation: this misses PDF acceptance effects." Phase 2 check for
LHEPdfWeight branches is committed (COMMITMENTS.md P2-6).

**Verdict: Properly resolved.**

---

### B5: Blinding/bias avoidance section
**Status: RESOLVED.**

Section 9.3 (lines 910-935) adds a complete blinding/bias-avoidance
strategy with all three required elements:
1. Open Data → traditional blinding not applicable (line 913)
2. Asimov validation before observed data (lines 917-922)
3. NN architecture frozen before data exposure (lines 923-927)
4. CR validation before SR examination (lines 928-931)

**Verdict: Properly resolved.**

---

### B6: VBF selection motivation
**Status: RESOLVED.**

Section 6.1 (lines 436-450) now motivates the thresholds: "intermediate
between R1's tight VBF category (m_jj > 700, |Delta_eta| > 4.0) and
loose VBF category (m_jj > 500, |Delta_eta| > 3.5)" with "deliberately
looser to retain more events given our single-channel statistics."
Commits to Phase 2 optimization and evaluates Zeppenfeld centrality
impact with a <20 events threshold for removal.

**Verdict: Properly resolved.**

---

### B7: W+jets shape validation
**Status: RESOLVED.**

Section 7.2 (lines 551-556) adds shape comparison between high-mT and
intermediate-mT regions with quantitative pass criteria: "chi2/ndf > 3
or KS p-value < 0.05" triggers use of MC-predicted shape instead.

**Verdict: Properly resolved.**

---

### B8: Common mu assumes SM production ratios
**Status: RESOLVED.**

Section 6.2, [D11] (lines 469-481) now explicitly states: "which assumes
SM production mode ratios (i.e., sigma_ggH / sigma_VBF is fixed to the
SM prediction)" and notes it as a limitation. A profiled mu_VBF
cross-check is mentioned as optional.

**Verdict: Properly resolved.**

---

### B9: NN training weight clarification
**STATUS: RESOLVED.**

Section 8.2 (lines 685-696) adds a clear paragraph: training uses
generator-level weights (class-balanced), template construction uses
luminosity-scaled weights, and explains why the artificial S/B ratio
in training does not bias the discriminant shape (likelihood ratio
invariance).

**Verdict: Properly resolved.**

---

### B10: Channel-specific comparison targets
**STATUS: RESOLVED.**

Section 10.1 (lines 949-966) now extracts mu-tau_h-specific values:
- R1 (8 TeV, mu-tau_h): mu ~ 0.8-1.0 +/- 0.4-0.5 (from Figure 16a)
- R2 (13 TeV, mu-tau_h): mu ~ 1.0-1.2 +/- 0.3-0.4 (from Figure 21b)

These are identified as "binding comparison targets for Phase 4" with
the 3-sigma validation target rule applied.

**Minor note:** These are read from figures, not tabulated values. This
introduces ~0.1-0.2 uncertainty on the central value. This is acceptable
for a Phase 1 target (the exact value will be refined in Phase 4 if
needed). Not a blocking issue.

**Verdict: Properly resolved.**

---

### B11: W+jets normalization / fake rate double-counting
**STATUS: RESOLVED.**

Section 9.1, tau fake rate row (line 878) now clearly separates
normalization from shape: "The normalization component of the fake rate
is already absorbed into the data-driven W+jets (high-mT sideband) and
QCD (SS sideband) estimates ... Therefore, a separate fake rate
normalization systematic would double-count the data-driven
normalization. The 20% fake rate systematic is applied as a shape-only
uncertainty."

The summary table (line 907) confirms: "Jet->tau fake rate: 20%
(shape only — normalization absorbed by data-driven W+jets and QCD
estimates)."

**Verdict: Properly resolved.**

---

### B12: Priority ordering + go/no-go criteria
**STATUS: RESOLVED.**

Section 2.2 (lines 96-111) adds a priority table with four levels:
1. Visible mass (baseline, always completed)
2. NN discriminant (go: AUC > 0.75, no overtraining, data/MC chi2/ndf < 3)
3. Collinear mass (go: unphysical < 50%, template smoothness)
4. NN-regressed MET (go: >15% MET resolution improvement)

Clear statement: "If an approach fails its go/no-go criterion, it is
dropped and documented as a negative result."

**Verdict: Properly resolved.**

---

### B13: TES implementation details
**STATUS: RESOLVED.**

Section 9.1, tau calibration row (line 858) now specifies: TES applied
to `Tau_pt`, propagated to MET via `MET_px -= delta_Tau_px, MET_py -=
delta_Tau_py`. Decay modes encoded in `Tau_decayMode` with typical
values listed (DM 0, 1, 10, 11). Exact enumeration committed to Phase 2
(COMMITMENTS.md P2-10).

**Verdict: Properly resolved.**

---

### B14: SVfit attempt documentation
**STATUS: RESOLVED.**

Section 10.3, [D12] (lines 1020-1036) now documents:
- GitHub search: three C++ implementations found (veelken/SVfit,
  veelken/SVfit_standalone, SVfit/ClassicSVfit)
- PyPI search: no results
- conda-forge search: no results
- Neural-network-based alternative from NIM A: no public package
- Wrapping C++ via pybind11: possible but significant effort (~days)

This is an honest documentation of the search attempt.

**Verdict: Properly resolved.**

---

### B15: Pileup reweighting procedure
**STATUS: RESOLVED.**

Section 9.1, pileup row (line 877) now specifies:
1. Baseline: reweight MC PV_npvs to match data PV_npvs
2. Ratio method: w_PU(npvs) = f_data(npvs) / f_MC(npvs)
3. +/-5% variation applied as a linear tilt on the data pileup profile
4. Data PV_npvs distribution measured in signal-depleted sample

**Verdict: Properly resolved.**

---

### B16: PS ISR/FSR systematics
**STATUS: RESOLVED.**

Section 9.1, parton shower row (line 869): commits to checking NanoAOD
for PSWeight branches in Phase 2 (COMMITMENTS.md P2-5). If present,
apply as shape systematics. If absent, assign PS uncertainty from R1/R2
values (1-3% acceptance, 1-5% shape) under [L3].

**Verdict: Properly resolved.**

---

### B17 (downgraded to C): Technique justification
**STATUS: RESOLVED.**

Section 15.1 (lines 1199-1205): "Binned template fits are standard for
H->tautau analyses at the LHC (R1, R2 both use this approach), are
compatible with the mandatory pyhf tool, and allow straightforward
systematic propagation via template morphing."

**Verdict: Properly resolved.**

---

## Category C Spot-Check

I will not exhaustively verify all 16 Category C items but spot-check
the most important ones:

- **C1 (finer categorization):** Section 6.3 (line 465): "A finer
  categorization (0-jet / 1-jet / VBF) will be evaluated in Phase 2."
  Present.
- **C6 (four approaches correlated):** Section 8 (lines 642-648):
  explicitly states results are "not independent" and "must not be
  combined." Present.
- **C7 (anti-electron discriminator):** Section 5.2 (lines 334-336):
  rationale given for tight anti-electron WP. Present.
- **C14 (embedding):** Section 7.1 (lines 516-520): acknowledges
  embedded samples used in R1/R2 and their absence in Open Data. Present.
- **C16 (RAG non-applicability):** Section 9.1 (lines 828-831): "RAG
  corpus queries are not applicable ... web-based literature review was
  used instead." Present.
- **AR2 (mu = 1 definition):** Section 3.2 (lines 210-216): explicitly
  defines mu = 1 with numerical value. Present.

**Verdict: Category C items appear to have been applied.**

---

## New Issues Check

I scanned the full document for issues that may have been introduced by
the fixes or that were not caught in the first review cycle:

### None found at Category A level.

The fixes are clean and internally consistent. The document reads as a
coherent strategy with properly motivated decisions.

### Minor observations (Category C, no re-review needed):

1. **Sensitivity estimate range is broad.** The S/sqrt(B) ~ 1.0-2.6
   combined estimate spans a factor of 2.6. This is acceptable for
   Phase 1 (the exact value depends on the tau ID WP and selection
   efficiency, which are Phase 2 deliverables), but the note writer in
   Phase 4a should narrow this with the actual selection efficiency.

2. **Trigger efficiency reduced from 5% to 3% for non-Z processes
   (line 879).** The reduction is justified by the text ("cross-trigger
   plateau region is well above the offline pT thresholds") but the 3%
   value is itself uncited. This is acceptable at Phase 1 — the actual
   trigger turn-on will be measured in Phase 2 — but should be confirmed
   or revised with data.

3. **The collinear mass unphysical fractions (lines 788-797) are
   qualitative estimates.** The table is labeled as "Expected" with a
   commitment to measure in Phase 2 (P2-8). This is the correct approach
   for Phase 1.

None of these rise above Category C.

---

## Conventions Cross-Check

The `conventions/search.md` required systematic sources are all
addressed in Section 9.1 with explicit "Will implement" or "Not
applicable because [reason]" for each row. The mapping from LEP-specific
sources to pp equivalents is documented. The required validation checks
from conventions/search.md (closure tests, signal injection, NP pulls,
impact ranking, GoF, look-elsewhere) are all enumerated in Section 14.1.
Look-elsewhere is correctly noted as not applicable (fixed mass).

**Verdict: Conventions coverage is complete.**

---

## COMMITMENTS.md Cross-Check

All [D1]-[D13] from the strategy are present in COMMITMENTS.md. All
[A1]-[A4] and [L1]-[L3] are present. The Phase 2 and Phase 4a forward
commitments trace back to specific arbiter findings. The tracking
artifact is well-structured and suitable for Phase 2+ verification.

**Verdict: COMMITMENTS.md is complete and consistent with STRATEGY.md.**

---

## Summary

| Category A Finding | Status | Remaining Issues |
|--------------------|--------|-----------------|
| A1: Z normalization decomposition + trigger | RESOLVED | None |
| A2: Signal cross-section normalization | RESOLVED | None |
| A3: NN-regressed MET success criterion | RESOLVED | None |
| A4: QCD OS/SS ratio from data + negative bins | RESOLVED | None |
| A5: Uncited numeric constants | RESOLVED | None |
| A6: Collinear mass fallback | RESOLVED | None |

| Category B Finding | Status | Remaining Issues |
|--------------------|--------|-----------------|
| B1: Sensitivity estimate | RESOLVED | None |
| AR1: ttbar NNLO+NNLL | RESOLVED | None |
| B2: COMMITMENTS.md | RESOLVED | None |
| B3: Diboson + PDF | RESOLVED | None |
| B5: Blinding section | RESOLVED | None |
| B6: VBF motivation | RESOLVED | None |
| B7: W+jets shape validation | RESOLVED | None |
| B8: Common mu statement | RESOLVED | None |
| B9: NN training weights | RESOLVED | None |
| B10: Channel-specific targets | RESOLVED | None |
| B11: W+jets fake rate double-counting | RESOLVED | None |
| B12: Priority ordering + go/no-go | RESOLVED | None |
| B13: TES implementation | RESOLVED | None |
| B14: SVfit search documentation | RESOLVED | None |
| B15: Pileup reweighting | RESOLVED | None |
| B16: PS ISR/FSR | RESOLVED | None |
| B17: Technique justification | RESOLVED | None |

**New Category A issues found:** None.
**New Category B issues found:** None.

---

## Verdict

**PASS.**

All 6 Category A findings have been properly resolved with substantive
content, not just minimal patches. All 17 Category B findings have been
adequately addressed. The Category C spot-check confirms those items were
also applied. The COMMITMENTS.md artifact is present and well-structured.
No new blocking issues were introduced by the fixes.

The strategy is ready to advance to Phase 2.
