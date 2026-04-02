# Phase 1 Arbiter Adjudication: H->tautau Strategy (mu-tau_h, 8 TeV Open Data)

**Arbiter role:** Final adjudicator for 4-bot Phase 1 review
**Date:** 2026-03-24
**Artifact reviewed:** `phase1_strategy/outputs/STRATEGY.md`
**Reviews consulted:**
- Physics review: `phase1_strategy/review/physics/PHASE1_PHYSICS_REVIEW.md`
- Critical review: `phase1_strategy/review/critical/PHASE1_CRITICAL_REVIEW.md`
- Constructive review: `phase1_strategy/review/constructive/PHASE1_CONSTRUCTIVE_REVIEW.md`
**Conventions file:** `conventions/search.md`
**Methodology reference:** `methodology/06-review.md` (sections 6.5, 6.5.1)

---

## Preamble: Context for Adjudication

Three points of context affect severity classification throughout:

1. **Physicist-requested parameters.** The physics prompt explicitly requested
   loosened tau ID (10-15% efficiency), Z normalization uncertainty of 10-15%,
   tight anti-muon veto, W+jets from high-mT, and 4 fitting approaches. Items
   that are direct physicist requirements cannot be classified as executor
   errors, but the strategy MUST still provide quantitative decomposition to
   demonstrate these values are defensible (not arbitrary).

2. **No RAG MCP tools available.** The analysis environment does not have RAG
   corpus access (the corpus is LEP-focused and not applicable to CMS). Web
   search was used instead. Procedural findings about missing corpus queries
   are downgraded to Category C provided the literature coverage is adequate.

3. **LEP-oriented conventions file.** `conventions/search.md` is written for
   e+e- searches. The pp mapping is expected and documented in the strategy.
   Findings about imperfect mapping are evaluated on physics merit, not on
   procedural completeness of the mapping itself.

---

## Structured Adjudication Table

### Category A: Must Resolve (blocks advancement)

| ID | Source(s) | Finding | Arbiter Ruling | Rationale |
|----|-----------|---------|----------------|-----------|
| **A1** | Physics-A1, Critical-A3, Constructive-B4 | **Z->tautau normalization (10-15%) lacks quantitative decomposition.** All three reviewers flagged the Z normalization as inflated relative to references (3.3-4%) without a quantitative breakdown into components. Additionally, Physics-A1 identified double-counting between the trigger efficiency systematic (+/-5%) and the Z normalization (which is stated to cover trigger effects). | **ACCEPTED as Category A.** While the physicist requested 10-15%, the methodology spec requires every systematic to be "motivated by a measurement or published uncertainty." A decomposition is required: theory xsec (~3-4%), trigger efficiency (X%), loosened tau ID (Y%), other (Z%), summed in quadrature. If the decomposition yields 10-15%, the value stands. If it yields less, the value must be adjusted. The trigger efficiency double-counting must be resolved: either the 5% trigger systematic is removed (absorbed into Z normalization) or the Z normalization is reduced and the trigger systematic stands as independent. Cost to fix: ~15 minutes of strategy text revision. |
| **A2** | Physics-A3, Critical-A2, Constructive-A2 | **Signal cross-section normalization is ambiguous and potentially inconsistent.** All three reviewers independently flagged this. The strategy uses 19.6 pb (tutorial) for MC normalization and 21.39 pb (YR4) for signal interpretation. Since the signal MC sample is `GluGluToHToTauTau` (filtered to tautau decays), the normalization cross-section should be sigma_prod x BR, not sigma_prod alone. The strategy text is ambiguous about whether "sigma x BR implicitly in the generator filter" means the sample contains only H->tautau events (sigma for weight = sigma_prod, correct) or that sigma already includes BR (sigma for weight = sigma_prod x BR, also correct but then 19.6 pb is sigma_prod not sigma x BR). Additionally, using different cross-sections for normalization (tutorial) vs. interpretation (YR4) biases mu by ~8.4%. | **ACCEPTED as Category A.** This is a potential O(10%) bias on the primary observable. Required fixes: (1) Unambiguously state whether the signal MC contains only H->tautau events or all H decays. (2) Write the explicit normalization formula showing which sigma enters w = sigma x L / N_gen. (3) Use a single consistent cross-section set. If YR4 is the reference, normalize signal MC to YR4 values. The tutorial cross-sections may be retained for backgrounds where no better value is available. Cost: ~20 minutes. |
| **A3** | Physics-A2 | **NN-regressed MET approach (c) has no quantitative success criterion.** Only the physics reviewer raised this, but the finding is valid. Approach (c) trains a neural network to regress generator-level MET -- a hard regression task. The strategy provides no threshold for success (e.g., X% MET resolution improvement), no data validation plan (regression target exists only in MC), and no explicit downscope decision if the approach fails. Without these, approach (c) could consume significant Phase 3-4 effort with no clear exit criterion. | **ACCEPTED as Category A.** Required: (1) Define a quantitative success metric (e.g., >15% improvement in MET resolution on MC test set, validated by Z->tautau mass peak resolution in data). (2) Define an explicit downscope: if the metric is not met at the end of Phase 3, approach (c) is dropped and documented as a negative result. (3) Note the MC-only training risk (detector simulation artifacts). Cost: ~15 minutes. |
| **A4** | Physics-A4, Critical-B1, Constructive-B2 | **QCD OS/SS ratio is ambiguous (0.80 vs 1.06, a 30% discrepancy) with no committed measurement plan and no procedure for negative bins.** All three reviewers flagged this. The two literature values differ by 30% and are on opposite sides of 1.0. The strategy defers the choice to Phase 2 without committing to measure the ratio from data. Additionally, no procedure is defined for bins where SS data minus MC goes negative. | **ACCEPTED as Category A.** The OS/SS ratio directly determines the QCD normalization. A 30% ambiguity is not acceptable as a strategy input. Required: (1) Commit to measuring the OS/SS ratio from data in an anti-isolated control region as the primary method. State that neither the tutorial nor published default is used blindly. (2) Define the procedure for negative-bin cases (e.g., set to zero with systematic covering the absolute value, or merge bins until positive). Cost: ~10 minutes. |
| **A5** | Critical-A6, Critical-A7 | **Uncited numeric constants: signal acceptance (+/-5%) and fragmentation uncertainty (+/-2%).** The critical reviewer identified two systematic values assigned without citations. Per CLAUDE.md: "Every number that enters the analysis must come from a citable source. At review, any uncited numeric constant is Category A." | **ACCEPTED as Category A.** Both values must be cited. Required: (1) Cite the specific CMS analysis where Powheg vs aMC@NLO acceptance difference was measured, with the numerical result. (2) Cite the specific CMS result for the Pythia/Herwig fragmentation comparison yielding ~2%. If the values cannot be cited (because they are approximate recollections), state this honestly and commit to deriving them from literature in Phase 4a. Cost: ~15 minutes (web search + citation). |
| **A6** | Physics-A5, Constructive-C3 | **Collinear mass fallback (visible mass for unphysical solutions) creates a composite observable.** The physics reviewer raised this at Category A; the constructive reviewer raised it at Category C. Events with x < 0 or x > 1 (~30-50%) use visible mass instead of collinear mass, creating a bimodal distribution. The fraction of unphysical solutions differs between signal and background, making the composite observable signal/background-dependent. Systematic variations (TES, MET scale) can shift events between the "physical" and "fallback" populations, creating discontinuous systematic responses. | **ACCEPTED as Category A (reduced scope).** The physics concern is valid: this is a composite observable and the discontinuity risk is real. However, at Phase 1 (strategy), the fix is to document awareness and commit to verification, not to solve it. Required: (1) Document the expected unphysical solution fraction for signal vs each background. (2) Commit to checking in Phase 4a that systematic variations produce smooth template changes (no sharp boundaries in the discriminant). (3) If discontinuities are found, the fallback strategy must be revised (e.g., truncation to [epsilon, 1-epsilon]). Cost: ~10 minutes of text. |

---

### Category B: Must Fix Before PASS

| ID | Source(s) | Finding | Arbiter Ruling | Rationale |
|----|-----------|---------|----------------|-----------|
| **B1** | Physics-B1, Constructive-A1 | **No expected sensitivity estimate.** The constructive reviewer raised this at Category A; the physics reviewer at Category B. The strategy states "O(10-100) signal events" but never estimates sigma(mu) or S/sqrt(B). Without this, neither the feasibility of the four-approach comparison nor the appropriateness of the systematic budget can be assessed. | **ACCEPTED as Category B.** This is important for honest framing but does not block the strategy's structural correctness. Required: add a rough S/sqrt(B) estimate for at least the visible mass approach in the Baseline category. State the expected sigma(mu) order of magnitude. If sigma(mu) ~ 1-2, reframe the analysis goal explicitly: the scientific contribution is the four-approach comparison, not the signal strength value itself. |
| **B2** | Critical-A1 | **COMMITMENTS.md not produced.** The critical reviewer flagged this as a mandatory artifact per the methodology. | **DOWNGRADED to Category B.** The Phase 1 CLAUDE.md does not list COMMITMENTS.md as a required deliverable (the required artifact is `outputs/STRATEGY.md`). The methodology reference (03-phases.md) may mention it, but the Phase 1 gate artifact table lists only STRATEGY.md. COMMITMENTS.md is valuable for traceability but its absence does not block advancement. The strategy already contains a clear [D1]-[D12], [A1]-[A4], [L1]-[L3] labeling system. Required: produce COMMITMENTS.md as a tracking artifact listing all labels with `[ ]` status. This is ~10 minutes of work and should be done but is not blocking. |
| **B3** | Critical-A5, Constructive-A3 | **Diboson contribution not quantified; conventions mapping incomplete.** The strategy dismisses diboson as "Not applicable" without citing the actual contribution from reference analyses. R1 includes diboson. The +/-5% blanket uncertainty on "missing backgrounds" is not a substitute for quantifying the expected diboson yield. Additionally, the PDF uncertainty is normalization-only, while references implement event-level PDF variations affecting acceptance. | **ACCEPTED as Category B.** Required: (1) Cite the diboson contribution from R1 (or R2) in the mu-tau_h channel. If truly < 3%, state with citation. (2) Acknowledge that PDF normalization-only treatment may miss acceptance effects and commit to investigating event-level PDF weights in Phase 2 (check NanoAOD branches). The ISR/PDF mapping concern from the constructive reviewer is reasonable but the strategy's coverage of jet pT threshold variation partially addresses the ISR jet modeling. |
| **B4** | Critical-A4 | **No RAG corpus queries documented.** The Phase 1 CLAUDE.md mandates corpus queries. | **DOWNGRADED to Category C.** The RAG corpus is LEP-focused and not available in this environment. The strategy conducted web-based literature review and cites three reference analyses with arXiv IDs. The procedural requirement is LEP-oriented; for CMS Open Data, web search is the appropriate equivalent. The strategy should add a one-line note: "RAG corpus queries are not applicable (corpus is LEP-focused; web-based literature review used instead)." |
| **B5** | Physics-B7, Critical-B6 | **No blinding/bias-avoidance strategy discussed.** The physics reviewer raised this at Category B. For Open Data with published results, traditional blinding is moot, but the strategy should commit to Asimov validation before looking at data. | **ACCEPTED as Category B.** Required: add a brief section stating (1) the analysis uses Open Data with published results, so traditional blinding does not apply, (2) the fit framework will be validated on Asimov data before running on observed data, (3) the NN will be developed using MC only, with data used only for validation after the architecture is frozen. |
| **B6** | Physics-B3, Physics-B4 | **VBF selection thresholds (m_jj > 300, |Delta_eta| > 2.5) not motivated; Zeppenfeld centrality as hard cut may kill statistics.** The VBF thresholds are intermediate between R1's tight and loose categories without motivation. The Zeppenfeld centrality requirement on top of m_jj and Delta_eta may reduce the VBF category to single-digit events. | **ACCEPTED as Category B.** Required: (1) Motivate the VBF thresholds or state they will be optimized in Phase 2/3. (2) Commit to evaluating the VBF yield with and without the Zeppenfeld centrality requirement in Phase 2. If the VBF category drops below ~20 events, remove the centrality cut or use it as an NN input. |
| **B7** | Physics-B5, Constructive-B3 | **W+jets extrapolation assumes mT-independence of fake rate without shape validation.** Both reviewers flagged the need for a shape comparison between high-mT and low-mT regions, not just normalization stability from varying the mT boundary. | **ACCEPTED as Category B.** Required: add to the validation strategy a shape comparison of W+jets m_vis distribution between high-mT (>70 GeV) and intermediate-mT (30-70 GeV) regions. If shapes differ significantly, the W+jets shape must be taken from the low-mT MC prediction. |
| **B8** | Physics-B6 | **Common mu for ggH and VBF assumes SM production ratios without stating it.** | **ACCEPTED as Category B.** Required: add an explicit statement that the common mu assumes SM ggH/VBF production mode ratios. Note this as a limitation. A profiled mu_VBF cross-check is suggested but not required at this stage. |
| **B9** | Physics-B2 | **NN training weight scheme needs clarification.** Generator-level weights for training vs luminosity-scaled weights for template construction is standard but should be stated explicitly. | **ACCEPTED as Category B.** Required: one paragraph clarifying (1) training uses generator-level weights (not lumi-scaled), (2) template construction uses lumi-scaled weights, (3) the artificial S/B ratio in training does not bias the discriminant shape. |
| **B10** | Critical-B8 | **Published channel-specific comparison targets not extracted.** The strategy quotes combined mu values from R1 and R2, not mu-tau_h-specific values. | **ACCEPTED as Category B.** Required: extract the mu-tau_h channel-specific signal strength from R1 Table 6 (or equivalent). This is the binding comparison target for Phase 4. |
| **B11** | Critical-B9 | **Potential double-counting between W+jets data-driven normalization and jet->tau fake rate systematic.** Section 9.2 lists both "W+jets normalization: 10-20%" and "Jet->tau fake rate: 20%" affecting W+jets. If the data-driven normalization already absorbs the fake rate, these are double-counted. | **ACCEPTED as Category B.** Required: clarify whether these are independent systematics or the same effect. If the W+jets normalization from the high-mT sideband already captures the fake rate (which it does, since the sideband normalization implicitly includes the fake rate), then the jet->tau fake rate systematic should not be applied independently to W+jets normalization. It may still apply to the W+jets shape. |
| **B12** | Critical-B3, Constructive-B1 | **Four fitting approaches may be overscoped; no go/no-go criteria or priority ordering.** Both reviewers flagged the risk of quadrupling the systematic evaluation and validation work without defining exit criteria. | **ACCEPTED as Category B.** Required: (1) Define a priority ordering for the four approaches (e.g., (a) visible mass is baseline and always completed; (b) NN discriminant is primary ML approach; (c) NN-regressed MET is exploratory; (d) collinear mass is analytic benchmark). (2) Define go/no-go criteria for approaches (b) and (c) at the end of Phase 2 (e.g., data/MC agreement on discriminant, AUC threshold, overtraining test). |
| **B13** | Critical-B4 | **Tau energy scale implementation underspecified.** TES is typically the dominant shape systematic in H->tautau. The strategy assigns +/-3% per decay mode but does not specify which NanoAOD variables encode decay mode, how the TES shift propagates to MET, or which decay modes are present. | **ACCEPTED as Category B.** Required: specify (1) the TES is applied to Tau_pt (and propagated to MET via Tau_pt change), (2) decay modes are encoded in Tau_decayMode, (3) available decay modes will be enumerated in Phase 2 data exploration. |
| **B14** | Critical-B7 | **SVfit dismissed without evidence of attempted installation.** [D12] states SVfit is complex, but no evidence of attempting installation (e.g., searching for a Python SVfit package) is documented. Per methodology: "Single generator without evidence of attempting installation is Category B." The same principle applies. | **ACCEPTED as Category B.** Required: document what was attempted. Was `pip search svfit`, `conda search svfit`, or a GitHub search for Python SVfit performed? If no attempt was made, state this honestly. The collinear mass + NN-regressed MET alternatives are reasonable, but the analysis should show it tried before accepting the limitation. |
| **B15** | Critical-B5 | **Pileup reweighting procedure underspecified.** The strategy says "vary pileup profile by +/-5%" without specifying the baseline reweighting procedure (data/MC PV distribution ratio) or what the 5% is applied to. | **ACCEPTED as Category B.** Required: specify (1) baseline pileup reweighting uses data/MC ratio of PV_npvs distributions, (2) the +/-5% variation is applied to the data pileup profile used for deriving the reweighting, (3) if no official pileup profile is available, describe how it will be obtained. |
| **B16** | Constructive-B5 | **Missing parton shower ISR/FSR systematics.** Published CMS analyses include PS scale variations. The strategy does not include them or document their absence. | **ACCEPTED as Category B.** Required: (1) In Phase 2, check whether the NanoAOD files contain PSWeight branches. (2) If present, include PS ISR/FSR up/down variations. (3) If absent, document as a limitation under [L3] and assign a PS uncertainty based on R1/R2 values. |
| **B17** | Critical-B6 | **No justification for binned template fit vs alternatives.** The methodology requires defending the chosen technique against alternatives. | **DOWNGRADED to Category C.** At Phase 1, the choice of template fit with pyhf is well-motivated by the tooling requirement (pyhf is in the mandatory tool list). Unbinned fits with zfit are an alternative but the discriminant distributions (m_vis, NN score) are naturally binned. A one-sentence justification is sufficient: "Binned template fits are standard for H->tautau analyses at the LHC, compatible with the mandatory pyhf tool, and allow straightforward systematic propagation via template morphing." |

---

### Category C: Suggestions (applied before commit, no re-review)

| ID | Source(s) | Finding | Arbiter Ruling |
|----|-----------|---------|----------------|
| **C1** | Physics-C1, Critical-C1, Constructive-C1 | **Consider a 0-jet/boosted/VBF category split.** All three reviewers suggested this. | NOTED. Worth exploring in Phase 2, but not required. The two-category scheme is defensible given the statistics. Add a sentence noting that a finer categorization will be evaluated in Phase 2 if statistics permit. |
| **C2** | Physics-C2 | **Add Delta_phi(mu, MET) to NN inputs.** | NOTED. Good suggestion. Add to the candidate list in Section 5.4. |
| **C3** | Physics-C3 | **Verify BR(H->tautau) = 6.256% is used consistently.** | NOTED. Ensure this value is used unrounded in all calculations. |
| **C4** | Physics-C4 | **Evaluate full Barlow-Beeston in VBF category.** | NOTED. Flag for Phase 4a evaluation. |
| **C5** | Physics-C5 | **Report profile likelihood scan of mu.** | NOTED. Standard practice; add to flagship figures or required validation. |
| **C6** | Physics-C6 | **Document that four approaches are correlated.** | NOTED. Required statement: the four mu values share data and background estimation, are not independent, and should not be combined. |
| **C7** | Critical-C2 | **Anti-electron discriminator rationale.** | NOTED. Add one sentence motivating the tight anti-electron WP (conservative rejection of e->tau fakes even in mu-tau_h channel). |
| **C8** | Critical-C3 | **QCD shape uncertainty from isolation threshold variation.** | NOTED. Good idea; add to Phase 4 systematic evaluation plan. |
| **C9** | Critical-C4 | **Negative MC weights discussion.** | NOTED. Check in Phase 2. MadGraph+Pythia6 LO samples typically have no negative weights. |
| **C10** | Critical-C5 | **VBF binning with < 1 expected event per bin.** | NOTED. Already covered in the strategy (Section 16, item 6). Commit to a minimum of 5 expected events per bin after merging. |
| **C11** | Critical-C6 | **Literature review timestamps suggest superficial review.** | NOTED as process concern. The literature coverage (3 references, systematic table) is adequate. |
| **C12** | Constructive-C2 | **Specify NN training framework (PyTorch, etc.).** | NOTED. Specify in Phase 2; add `pytorch` or `scikit-learn` to pixi.toml. |
| **C13** | Constructive-C4 | **Signal contamination in CRs.** | NOTED. Estimate signal contamination in high-mT CR and SS CR in Phase 3. |
| **C14** | Constructive-B6 | **No embedding discussed.** | DOWNGRADED to C. Add a sentence acknowledging that the published analyses use embedding for Z->tautau and that the absence of embedded samples in Open Data motivates the larger Z normalization uncertainty. |
| **C15** | Constructive-B7 | **Missing backgrounds +/-5% uncertainty correlation structure.** | DOWNGRADED to C. Specify in Phase 4a whether this is correlated or independent with individual background normalization uncertainties. |
| **C16** | (arbiter-raised) | **Add RAG corpus non-applicability note.** The strategy should state that RAG corpus queries are not applicable (corpus is LEP-focused) and that web-based literature review was used instead. | Add one line. |

---

## Arbiter-Raised Findings (not caught by any reviewer)

### AR1. ttbar cross-section inconsistency (Category B)

The strategy uses 225.2 pb (LO MadGraph) for ttbar normalization (Section 3.2)
and assigns an 8% uncertainty (Section 9.2). However, the NNLO+NNLL value is
252.9 pb -- a 12% difference that exceeds the 8% uncertainty. The critical
reviewer noted this in A2 but framed it around the signal cross-section. For
ttbar specifically: either use the NNLO+NNLL value for normalization (recommended)
or increase the normalization uncertainty to cover the LO-to-NNLO gap (~12%).
An 8% uncertainty that does not cover the known ~12% offset from best theory
is not conservative -- it is underestimated.

**Required action:** Either normalize ttbar to 252.9 pb (NNLO+NNLL) with a
~5% theory uncertainty, or increase the LO-based uncertainty to >= 12%.

### AR2. No explicit statement of what mu = 1 corresponds to (Category C)

The strategy defines mu = sigma_obs / sigma_SM but does not state explicitly
which sigma_SM enters the denominator. This is related to A2 but is a separate
concern: the AN must state that mu = 1 corresponds to the SM prediction using
YR4 cross-sections, with the specific numerical value of sigma_SM x BR in the
mu-tau_h final state.

---

## Independent Regression Checklist

- [ ] **Any validation test failures without 3 documented remediation attempts?**
  N/A -- Phase 1 has no validation tests. No regression trigger.

- [ ] **Any single systematic > 80% of total uncertainty?**
  POTENTIAL FLAG. Z->tautau normalization at 10-15% on a background that is
  60-70% of the total could dominate the total uncertainty. The decomposition
  required by A1 will clarify this. If the decomposition confirms 10-15% is
  justified, this is acceptable (the dominant systematic is the dominant
  background normalization, which is physically expected). If it is inflated,
  A1 addresses it. No separate regression trigger at this time.

- [ ] **Any tautological comparison presented as independent validation?**
  POTENTIAL RISK. The strategy's validation plan compares data to MC for
  Z->tautau normalization, then uses that MC as the Z->tautau template in
  the fit. This is a closure check, not independent validation. However,
  this is standard practice in H->tautau analyses (the Z peak region
  constrains the normalization, not the shape in the signal region).
  No regression trigger, but flag for Phase 4a review.

- [ ] **Any > 50% bin exclusion?**
  POTENTIAL RISK. The collinear mass approach (d) excludes 30-50% of events
  (those with unphysical solutions) from the collinear mass and substitutes
  visible mass. This is not bin exclusion per se but is a significant fraction
  of events receiving a different treatment. Addressed by A6. No separate
  regression trigger.

- [ ] **Any > 30% deviation from reference value?**
  N/A -- no results yet. The comparison targets (B10) must be extracted
  before Phase 4.

- [ ] **All binding commitments [D1]-[D12] feasible?**
  [D1] (four approaches): feasible but overscoped (B12 addresses).
  [D2] (cross-sections): inconsistent (A2 addresses).
  [D12] (no SVfit): accepted without evidence (B14 addresses).
  All others appear feasible.

- [ ] **Fit chi2 identically zero?**
  N/A -- no fit yet.

---

## Summary of Reviewer Agreement

| Topic | Physics | Critical | Constructive | Agreement |
|-------|---------|----------|--------------|-----------|
| Z normalization inflated | A1 | A3 | B4 | **3/3 agree, severity A/A/B** |
| Cross-section inconsistency | A3 | A2 | A2 | **3/3 agree, severity A** |
| NN-regressed MET no criterion | A2 | -- | -- | **1/3, validated independently** |
| QCD OS/SS ambiguity | A4 | B1 | B2 | **3/3 agree, severity A/B/B** |
| Collinear mass fallback | A5 | -- | C3 | **2/3, severity A/C** |
| Uncited constants | -- | A6, A7 | -- | **1/3, valid per methodology** |
| No sensitivity estimate | B1 | -- | A1 | **2/3, severity B/A** |
| COMMITMENTS.md missing | -- | A1 | -- | **1/3, downgraded to B** |
| Diboson/conventions | -- | A5 | A3 | **2/3, severity A/A, downgraded to B** |
| No corpus queries | -- | A4 | -- | **1/3, downgraded to C** |
| Blinding/bias avoidance | B7 | -- | -- | **1/3, accepted at B** |
| VBF thresholds | B3, B4 | -- | -- | **1/3, accepted at B** |
| W+jets shape validation | B5 | B2 | B3 | **3/3 agree, severity B** |
| Common mu assumption | B6 | -- | -- | **1/3, accepted at B** |
| NN training weights | B2 | -- | -- | **1/3, accepted at B** |
| Channel-specific targets | -- | B8 | -- | **1/3, accepted at B** |
| W+jets double-counting | -- | B9 | -- | **1/3, accepted at B** |
| Four-approach scoping | -- | B3 | B1 | **2/3, severity B** |
| TES implementation | -- | B4 | -- | **1/3, accepted at B** |
| SVfit non-attempt | -- | B7 | -- | **1/3, accepted at B** |
| Pileup procedure | -- | B5 | C5 | **2/3, severity B/C** |
| PS ISR/FSR systematics | -- | -- | B5 | **1/3, accepted at B** |
| ttbar xsec inconsistency | -- | (partial in A2) | -- | **Arbiter-raised, B** |

---

## Verdict

**ITERATE.**

Six Category A findings must be resolved before the strategy can advance to
Phase 2. Seventeen Category B findings must be fixed before PASS (most are
small text additions; a few require web search for citations). Category C
items should be applied before the commit.

### Priority-Ordered Fix List for the Fixer Agent

**Category A (must resolve -- blocks advancement):**

1. **A2: Signal cross-section normalization.** Unambiguously state whether
   the signal MC is H->tautau-only (it is, given the sample name). Write the
   explicit weight formula. Use YR4 cross-sections consistently for signal.
   Resolve the tutorial vs YR4 discrepancy -- use one set.

2. **A1: Z normalization decomposition + trigger double-counting.** Provide
   a quantitative breakdown of the 10-15% into components. Remove the
   separate 5% trigger systematic (absorbed into the Z normalization) OR
   reduce the Z normalization and keep the trigger systematic as independent.

3. **A4: QCD OS/SS ratio.** Commit to measuring from data in anti-isolated
   CR. Define the negative-bin procedure.

4. **A5: Cite the 5% signal acceptance and 2% fragmentation values.** Find
   and cite the specific CMS publications, or commit to deriving them in
   Phase 4a with an explicit placeholder.

5. **A3: NN-regressed MET success criterion.** Define quantitative metric,
   data validation plan (Z peak resolution), and explicit downscope decision.

6. **A6: Collinear mass fallback.** Document expected unphysical fraction
   per process. Commit to checking template smoothness under systematic
   variations in Phase 4a. Define fallback revision plan if discontinuities
   are found.

**Category B (must fix before PASS -- prioritized):**

7. **B1: Expected sensitivity estimate.** Add rough S/sqrt(B) or sigma(mu)
   estimate. Reframe analysis goal if sigma(mu) ~ 1-2.

8. **AR1: ttbar normalization.** Use NNLO+NNLL value (252.9 pb) with ~5%
   theory uncertainty, or increase the LO-based uncertainty to >= 12%.

9. **B3: Diboson quantification.** Cite diboson contribution from R1.
   Acknowledge normalization-only PDF limitation.

10. **B10: Channel-specific comparison targets.** Extract mu-tau_h signal
    strength from R1 Table 6.

11. **B11: W+jets normalization / fake rate double-counting.** Clarify
    independence; remove double-counting if present.

12. **B5: Blinding/bias avoidance section.** Add brief section.

13. **B12: Priority ordering + go/no-go criteria for four approaches.**

14. **B6: VBF selection motivation.** Motivate thresholds or commit to
    Phase 2 optimization. Evaluate Zeppenfeld centrality impact.

15. **B7: W+jets shape validation.** Add shape comparison requirement.

16. **B8: Common mu assumes SM production ratios.** Add statement.

17. **B9: NN training weight clarification.** Add one paragraph.

18. **B2: COMMITMENTS.md.** Produce the tracking artifact.

19. **B13: TES implementation details.** Specify variables and propagation.

20. **B14: SVfit attempt documentation.** Document what was searched for.

21. **B15: Pileup reweighting procedure.** Specify baseline + variation.

22. **B16: PS ISR/FSR systematics.** Check NanoAOD for PSWeight branches;
    document plan.

23. **B17 (downgraded to C): Technique justification.** One sentence.

**Category C (apply before commit):** C1-C16 as listed above. These are
small text additions and do not require re-review.

---

## Dismissal Register

| Finding | Dismissed? | Justification |
|---------|-----------|---------------|
| Critical-A4 (corpus queries) | Downgraded A->C | RAG corpus is LEP-focused, not available for CMS. Web-based literature review is adequate. Cost: 0. Physics impact: none (literature coverage is adequate with 3 references). Commitment: add one-line note documenting the non-applicability. |
| Critical-A1 (COMMITMENTS.md) | Downgraded A->B | Phase 1 gate artifact is STRATEGY.md. COMMITMENTS.md is valuable but not listed in the phase gate table. Cost: ~10 min. Physics impact: none (labels already in STRATEGY.md). |
| Critical-B6 (technique justification) | Downgraded B->C | pyhf is a mandatory tool; binned template fits are standard for H->tautau. One sentence suffices. Cost: ~2 min. |
| Constructive-B6 (embedding) | Downgraded B->C | Embedding is not available in Open Data. Acknowledging its absence takes one sentence. Cost: ~2 min. |
| Constructive-B7 (missing bkg correlation) | Downgraded B->C | Correlation structure is a Phase 4a detail, not a strategy-blocking issue. Cost: ~2 min in Phase 4a. |

---

**Final verdict: ITERATE.** Address the six Category A items and seventeen
Category B items listed above. The fixer agent should work through the
priority-ordered list sequentially. After fixes, the revised STRATEGY.md
must be re-reviewed by a fresh reviewer panel.
