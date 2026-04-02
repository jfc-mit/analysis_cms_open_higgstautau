# Phase 1 Critical Review: H->tautau Strategy

**Reviewer:** Critical Reviewer
**Date:** 2026-03-24
**Artifact:** `phase1_strategy/outputs/STRATEGY.md`
**Conventions file:** `conventions/search.md`
**Verdict:** FAIL — Category A issues must be resolved before advancing.

---

## Summary

The strategy document is comprehensive in scope, covering 17 sections with
12 decisions, 4 constraints, and 3 limitations. It correctly identifies the
signal and background processes, proposes four fitting approaches as requested
by the physics prompt, enumerates conventions/search.md sources row-by-row,
and tabulates three reference analyses. However, several Category A issues
must be resolved before advancing to Phase 2.

---

## Category A: Must Resolve (blocks advancement)

### A1. COMMITMENTS.md not produced

The methodology (03-phases.md, line ~750) **mandates** a `COMMITMENTS.md`
tracking artifact at Phase 1 completion, listing every commitment with
machine-readable status. This file does not exist. The experiment log
confirms the strategy was written but does not mention COMMITMENTS.md.
Without it, Phase 4a and Phase 5 reviewers cannot systematically verify
that all Phase 1 commitments were fulfilled. This is a mandatory artifact
per the methodology.

**Required action:** Produce `COMMITMENTS.md` listing every [D], [A], [L]
label and every systematic source commitment with `[ ]` / `[x]` status.

### A2. Cross-section normalization is potentially circular

[D2] commits to normalizing MC with the tutorial cross-sections (which are
LO MadGraph values for backgrounds). For the ttbar sample, the tutorial
uses 225.2 pb (LO) while the current best value is 252.9 pb (NNLO+NNLL).
That is a 12% discrepancy. The strategy then assigns an 8% normalization
uncertainty on ttbar (Section 9.2), which does not cover the known 12%
offset from the best-available theory prediction.

More critically, Section 3.2 says the ggH cross-section of 19.6 pb
"includes sigma x BR(H->tautau) implicitly in the generator filter."
This statement is ambiguous and potentially incorrect. If the generator
filter already accounts for the branching ratio, then the weight
calculation `w = sigma x L / N_gen` using sigma = 19.6 pb would
double-count the branching ratio. Alternatively, if sigma = 19.6 pb is
the inclusive production cross-section, then the event weight is correct
only if the MC sample already has the BR applied at generation level. This
must be unambiguously clarified: what exactly is the generator-level
filter? Does the sample contain all H decays or only H->tautau decays?
This propagates directly to the signal yield and thus to mu.

**Required action:** (1) Clarify whether the signal MC samples contain
all Higgs decays or only H->tautau. State whether BR(H->tautau) must be
applied in the weight or is already implicit. (2) Either use best-available
(NNLO+NNLL) cross-sections for all processes with theory uncertainties,
or justify why LO values are acceptable AND ensure the normalization
uncertainty covers the known LO-to-NNLO difference for each process.

### A3. Z->tautau normalization uncertainty is inflated without rigorous justification

[D6] assigns a 10-15% uncertainty on Z->tautau normalization "to cover
missing trigger turn-on effects and the larger tau efficiency scale factors
from the loosened tau ID." The reference analyses R1 and R2 used 3.3% and
4%, respectively. This analysis assigns 3-4x larger uncertainty without a
quantitative decomposition.

Per the CLAUDE.md methodology: "Every systematic variation must be motivated
by a measurement or published uncertainty. Arbitrary conservative inflations
mask the analysis's true sensitivity." The 10-15% comes from the physics
prompt (user request), not from a measurement. While the user's intent is
understood (absorb missing scale factors), the strategy must decompose this:
how much is the NNLO cross-section uncertainty (~3-4%)? How much is the
trigger efficiency uncertainty without SFs? How much is the loosened tau ID
uncertainty? These components should be added in quadrature, not lumped
into a single inflated number.

If the decomposition yields ~10-15%, the number is justified. If it yields
~7%, then 10-15% is conservative inflation. The strategy currently provides
no decomposition.

**Required action:** Provide a quantitative breakdown of the Z->tautau
normalization uncertainty into its components (theory xsec, trigger SF,
tau ID SF, luminosity). Show that the components sum in quadrature to
the quoted 10-15%, or adjust the value.

### A4. No corpus queries documented

The Phase 1 CLAUDE.md mandates: "Before writing the strategy, query the
experiment corpus (via MCP tools): (1) search_lep_corpus: prior
measurements, (2) search_lep_corpus: standard systematics, (3)
compare_measurements: cross-experiment results, (4) get_paper: drill into
each reference analysis." The experiment log mentions "web searches" for
literature but does not document any RAG corpus queries. The strategy cites
papers by arXiv ID and TWiki URLs but does not reference any corpus query
results.

This is a procedural requirement. The absence of corpus queries means the
strategy may be missing information available in the RAG corpus that web
searches did not surface.

**Required action:** Execute the mandatory corpus queries and document
results. If the RAG corpus is not available (e.g., this is a CMS analysis
and the corpus is LEP-focused), document this as a constraint with
justification for why web-based literature review is adequate.

### A5. Conventions file applicability is questionable

The strategy maps `conventions/search.md` (written for e+e- LEP searches)
to a pp collider Higgs search. The mapping is documented in Section 9.1
("the pp-specific equivalents are used where noted"), but several mappings
are questionable:

- **"4-fermion backgrounds (pp equivalent: electroweak backgrounds)"** is
  marked "Not applicable" because diboson samples are missing. But the
  convention's intent is that all irreducible electroweak backgrounds are
  evaluated. At the LHC, WW/WZ/ZZ with tau final states are indeed
  backgrounds to H->tautau. Dismissing them as "< 3%" without a
  quantitative estimate from the reference analyses is insufficient. R1
  and R2 both include diboson backgrounds. The +/-5% blanket uncertainty
  on total background [A3] is not a substitute for understanding the
  composition.

- **"ISR modeling (pp equivalent: PDF uncertainty)"** -- ISR at LEP and
  PDFs at the LHC are fundamentally different systematics. The mapping is
  reasonable but the implementation is "normalization only" with no
  event-level reweighting. The reference analyses implement event-level
  PDF variations that affect acceptance. The strategy should acknowledge
  this difference and assess its impact.

**Required action:** (1) Quantify the expected diboson contribution
using reference analysis numbers (R1 Section 7 or equivalent). If it is
truly < 3% in the mu-tau_h channel after selection, state this with a
citation. (2) Assess whether normalization-only PDF uncertainty is adequate
or whether the absence of event-level PDF reweighting biases the acceptance
estimate.

### A6. Signal acceptance uncertainty is uncited

Section 9.1 assigns +/-5% signal acceptance uncertainty "based on comparison
of Powheg and aMC@NLO in published CMS analyses." Which CMS analyses?
What was the actual measured difference? Per the CLAUDE.md: "Every number
that enters the analysis must come from a citable source." The 5% is
currently uncited.

**Required action:** Cite the specific published CMS analysis(es) where
the Powheg vs. aMC@NLO acceptance difference was measured, with the
actual numerical values found.

### A7. Fragmentation model uncertainty is uncited

Section 9.1 assigns +/-2% for fragmentation/hadronization based on
"Pythia/Herwig comparisons in published CMS results." Which results?
Same issue as A6 -- an uncited numeric constant.

**Required action:** Cite the specific source for the 2% fragmentation
uncertainty.

---

## Category B: Should Address (weakens the analysis)

### B1. The OS/SS ratio for QCD has contradictory values

Section 7.3 states the OS/SS ratio is "~0.80 (as in the CMS tutorial) or
~1.06 (as in the published CMS analysis)." These differ by 33%. The
strategy does not commit to which value will be used or how the correct
value will be determined. Using the wrong OS/SS ratio directly biases the
QCD estimate.

**Required action:** Commit to measuring the OS/SS ratio from data in an
anti-isolated control region (this is already mentioned as a validation
step). State that the measured value supersedes both the tutorial and
published defaults. Assign the uncertainty based on the measurement, not
a pre-assumed 20-30%.

### B2. No validation region between W CR and SR

The W+jets estimation (Section 7.2) extrapolates from mT > 70 GeV to
mT < 30 GeV. The validation region is "30 < mT < 70 GeV." However, this
intermediate region is contaminated by both Z->tautau and signal. The
strategy does not discuss how to isolate the W+jets contribution in this
VR. Furthermore, `conventions/search.md` warns: "If the VRs are
kinematically distant from the SR, closure there does not validate the
extrapolation." The mT > 70 GeV to mT < 30 GeV extrapolation spans the
full mT spectrum -- the VR at 30-70 GeV should be explicitly defined with
its expected composition.

**Required action:** Define the expected background composition in the
intermediate-mT VR and describe how the W+jets closure test will account
for Z->tautau and other contamination.

### B3. Four fitting approaches may be overscoped

[D1] requires all four fitting approaches. With O(10-100) signal events
after selection, the NN discriminant (approach b) and NN-regressed MET
mass (approach c) each require careful training and validation. The
strategy acknowledges "NN training stability" as a risk (Section 16, item
2) but does not define a concrete fallback. If the NN approaches fail,
what is the minimum viable analysis? The methodology requires a
downscoping plan (methodology/12-downscoping.md).

This is a strategic concern: four approaches quadruple the systematic
evaluation work, the plotting work, and the review burden. The strategy
should define a priority ordering and explicit go/no-go criteria for each
ML approach at the end of Phase 2.

**Required action:** Define explicit go/no-go criteria for approaches (b)
and (c): what metric threshold (e.g., AUC, overtraining test, data/MC
agreement on the discriminant) determines whether each approach proceeds
to Phase 4? Define a priority ordering for the four approaches.

### B4. Tau energy scale uncertainty implementation is underspecified

The strategy assigns +/-3% tau energy scale per decay mode, which matches
R1. But the implementation details are missing: which decay modes are
present in the NanoAOD? Are decay-mode-dependent energy scale corrections
available? How is the TES variation propagated to MET (since MET is
recomputed from calibrated objects)? The TES is typically the dominant
shape systematic in H->tautau analyses -- its implementation must be
spelled out.

**Required action:** Specify the TES implementation: which variable
encodes the tau energy (Tau_pt? A dedicated energy variable?), which decay
modes are available (Tau_decayMode values), and how the MET propagation
works when the tau pT is shifted.

### B5. Pileup reweighting implementation is vague

Section 9.1 states "Vary pileup profile by +/-5% to assess impact." In
the reference analyses, pileup reweighting is done using the number of
primary vertices or the true number of interactions, with the uncertainty
evaluated by varying the minimum-bias cross-section by +/-5%. The strategy
says "PV_npvs distribution reweighting" but does not describe:
(a) whether pileup reweighting is applied as a correction (data/MC PV
distribution ratio) or only as a systematic variation,
(b) what the +/-5% is applied to (the PV distribution? a cross-section?).

**Required action:** Specify the pileup reweighting procedure precisely.

### B6. Technique justification is missing

The methodology (03-phases.md, line ~173) requires: "Explicitly defend the
chosen technique against alternatives." The strategy selects a binned
template fit with pyhf but does not justify this choice against alternatives.
Why not an unbinned fit (e.g., with zfit)? Why not a counting experiment?
The justification should be brief but present.

**Required action:** Add a brief justification for the binned template fit
technique against at least one alternative.

### B7. Method parity with SVfit is accepted without evidence of attempted installation

[D12] states "SVfit is not implemented" because "A Python implementation
is complex and outside the scope of available tools." The methodology
(03-phases.md, line ~72-86) explicitly states: "Single generator without
evidence of attempting installation is Category B." The same principle
applies to SVfit. Did anyone attempt to install or implement SVfit? Is
there a Python package (e.g., `svfit` or `ClassicSVfit`)? The strategy
should document what was attempted and what failed, not just that it was
deemed complex.

**Required action:** Document evidence of attempted SVfit installation
or implementation. If no attempt was made, this remains Category B.

### B8. Published numerical results not extracted from reference analyses

The methodology (03-phases.md, line ~207-212) requires: "Extract published
numerical results (central values and uncertainties at representative
kinematic points) from the reference analyses and record them in the
strategy artifact. These become binding comparison targets at Phase 4c
review." The strategy tabulates R1: mu = 0.78 +/- 0.27 and R2: mu =
0.98 +/- 0.18, but these are combined all-channel results, not mu-tau_h
specific. The mu-tau_h channel-specific signal strengths from R1 and R2
should be extracted as the proper comparison targets.

**Required action:** Extract the mu-tau_h channel-specific signal strength
from R1 (Table 6 of JHEP 05 (2014) 104) or R2. These are the binding
comparison targets for Phase 4.

### B9. Jet->tau fake rate systematic is redundant with data-driven W+jets

The systematic summary (Section 9.2) lists both "W+jets normalization:
10-20%" and "Jet->tau fake rate: 20%" affecting W+jets. If the W+jets
normalization is determined from data in the high-mT CR, the fake rate
uncertainty is already absorbed into the data-driven normalization
uncertainty. Double-counting inflates the W+jets uncertainty and reduces
sensitivity. The strategy should clarify whether these are independent
systematics or the same effect counted twice.

**Required action:** Clarify the relationship between the W+jets
data-driven normalization uncertainty and the jet->tau fake rate systematic.
If they are correlated, remove the double-counting.

---

## Category C: Suggestions

### C1. Consider a boosted/0-jet category split

The strategy uses only two categories (Baseline + VBF). R1 used 0-jet,
boosted (1-jet), and VBF. Adding a boosted category (1 high-pT jet,
Higgs recoiling against it) would improve ggH sensitivity. With the
available statistics, this may or may not be beneficial, but the
exploration of a 3-category scheme should at least be mentioned as a
Phase 2 investigation item.

### C2. Anti-electron discriminator rationale

[D8] specifies tight anti-muon discriminator (well motivated for
mu-tau_h). The strategy also applies `Tau_idAntiEleTight` but provides
no rationale. In the mu-tau_h channel, electron->tau_h fakes are less of
a concern than muon->tau_h fakes. Why tight and not medium or loose?

### C3. QCD shape uncertainty is underspecified

The QCD shape is taken from the SS control region. The uncertainty is
described as "comparing SS and anti-isolated control regions." But the SS
and anti-isolated regions may have very different kinematic properties.
Consider also evaluating the QCD shape uncertainty by varying the
isolation inversion threshold.

### C4. Missing discussion of negative weights

If any MC samples have negative generator weights (possible with NLO
generators), the strategy should address how these are handled in
template construction and Barlow-Beeston treatment.

### C5. Binning strategy needs more detail

Section 8.1 proposes "25 bins from 0 to 250 GeV (10 GeV/bin)" for the
visible mass. In the VBF category, with O(10-50) events total, many bins
will have < 1 expected event. The strategy mentions bin merging as a
possibility in Section 16 but does not commit to a rebinning criterion.
Standard practice: merge bins until each has >= 5 expected events.

### C6. Experiment log timestamps suggest very fast literature review

The experiment log shows data inspection at 01:50, literature review at
01:52 (2 minutes later), and cross-section investigation at 01:55. A
thorough literature review of three reference analyses in 3 minutes is
unlikely to be comprehensive. This is a process concern, not a content
concern, but it suggests the literature review may have been superficial.

---

## Conventions/search.md Row-by-Row Verification

| Convention source | Strategy coverage | Status |
|-------------------|-------------------|--------|
| Signal xsec theory uncertainty | QCD scale + PDF from YR4 | OK |
| Signal acceptance | +/-5% (uncited) | **A6** |
| Signal shape | TES + MET variations | OK (but TES implementation underspecified, **B4**) |
| ISR/PDF modeling | PDF normalization only | **A5** (normalization-only may miss acceptance effects) |
| 4-fermion/electroweak backgrounds | Not applicable (uncited) | **A5** |
| Background normalization | Z: 10-15%, W: data-driven, QCD: data-driven, TTbar: 8% | OK (but Z inflated **A3**, TTbar low **A2**) |
| Background shape | Described for Z, W, QCD | OK |
| qq(gamma)/QCD radiation | Jet pT threshold variation | OK |
| MC statistics | Barlow-Beeston | OK |
| Detector simulation | Data/MC comparison | OK (vague) |
| Object calibration (muon) | 1% ES, 2% ID, 1% iso | OK |
| Object calibration (tau) | 3% TES, 10% ID | OK (but 10% ID is uncited) |
| Object calibration (jet) | 2-5% JES, 10% JER | OK |
| Object calibration (MET) | Propagated + 10% unclustered | OK |
| Beam energy/PDF | PDF normalization | OK (but see A5) |
| Luminosity | 2.6% | OK |
| QCD scale variations | 7-point for signal | OK |
| Fragmentation model | +/-2% (uncited) | **A7** |
| Heavy flavour treatment | b-tag 5% | OK |

---

## Reference Analysis Parity Check

| Feature | R1 (8 TeV evidence) | R2 (13 TeV obs.) | This analysis | Gap? |
|---------|---------------------|-------------------|---------------|------|
| Mass variable | SVfit | SVfit | Visible + collinear + NN | SVfit missing (**B7**) |
| Categories | 0-jet, boosted, VBF | Multiple | Baseline + VBF | Fewer categories (**C1**) |
| MVA | BDT discriminant | DeepTau + categories | NN discriminant | Comparable |
| Tau ID SFs | Official POG | Official POG | None (loosened WP) | Weaker (**A3**) |
| Trigger SFs | Official | Official | None | Weaker (**A3**) |
| Diboson | Included | Included | Missing | Gap (**A5**) |
| Single top | Included | Included | Missing | Gap (covered by [A3]) |
| Statistical method | Profile likelihood | Profile likelihood | pyhf profile likelihood | Comparable |
| PDF uncertainty | Event-level | Event-level | Normalization only | Weaker (**A5**) |

---

## Regression Checklist (pre-emptive)

- [ ] Any validation test failures without 3 documented remediation attempts? -- N/A (Phase 1)
- [ ] Any single systematic > 80% of total uncertainty? -- The Z->tautau normalization at 10-15% may dominate. Flag for Phase 4a review.
- [ ] Flat-prior gate excluding > 50% of bins? -- N/A
- [ ] Tautological comparison? -- Risk: if the same MC used for templates is also the "theory comparison," it is tautological. The strategy does not identify an independent theory comparison target. **This is a gap -- see B8.**
- [ ] All binding commitments [D1]-[D12] feasible? -- [D1] (four approaches) may be overscoped (**B3**). [D12] (no SVfit) accepted without evidence (**B7**).

---

## Verdict

**FAIL.** Seven Category A issues block advancement. The most critical are:

1. Missing COMMITMENTS.md (procedural, easy to fix)
2. Cross-section normalization ambiguity for signal (could propagate to wrong mu)
3. Inflated Z normalization without decomposition (masks sensitivity)
4. Missing corpus queries (procedural)
5. Diboson quantification and PDF uncertainty adequacy (completeness)
6-7. Uncited numeric constants for acceptance and fragmentation uncertainties

Nine Category B issues should be addressed before PASS. The most impactful
are the OS/SS ratio ambiguity (B1), the SVfit non-attempt (B7), the
missing channel-specific comparison targets (B8), and the potential
W+jets double-counting (B9).

All Category A items must be resolved and re-reviewed. Category B items
must be fixed before the arbiter can issue PASS.
