# Phase 5 Constructive Review

**Reviewer:** Constructive reviewer
**Artifact:** `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md` (1603 lines, ~70 rendered pages)
**Date:** 2026-03-25

---

## Overall Assessment

This is a thorough, well-structured analysis note that tells a coherent physics story from motivation through final result. The 70-page length is appropriate for the scope of the analysis. The three-way comparison (Asimov / 10% / full data) across three fitting approaches is a genuine strength that provides transparency about the measurement's evolution. The discussion of the VBF deficit is honest and well-supported. The comparison to the published CMS result is quantitative and convincing.

The findings below are organized to help strengthen what is already a solid document.

---

## Category A: Must Resolve

### A1. Abstract / body numerical inconsistency in the primary result

The abstract (line 18) and the three-way summary in the conclusions (line 1518) quote $\mu = 0.64 \pm 1.08$, while Equation 15 (line 1258), Table 14 (line 1272), the conclusions (lines 1500, 1506), and the comparison section (line 1475) all quote $\mu = 0.63 \pm 1.08$. The change log entry for v4c-v1 (line 43) also says 0.63. This 0.01 discrepancy must be resolved to a single consistent value throughout the document. Check the machine-readable JSON to determine the authoritative number.

**Locations to fix:** line 18 (abstract), line 1518 (conclusions paragraph).

### A2. Duplicate entries in the systematic uncertainty summary table (@tbl:syst-summary)

The summary table (lines 790-813) contains two entries for "$Z\to\tau\tau$ norm" with different impact values (0.097 at line 797 and 0.036 at line 805). Similarly, "Missing bkg norm" (line 803, impact 0.047) and "Missing backgrounds" (line 807, impact 0.032) appear to be the same systematic listed with different names and different impact values. One entry from each pair should be removed, and the surviving entry should carry the correct impact value consistent with the impact ranking table. This is confusing to the reader and undermines confidence in the systematic treatment.

### A3. Impact ranking table discrepancy between Section 7.11 (Asimov) and per-systematic subsection text

The per-systematic subsections (Sections 7.1-7.10) quote individual impact values (e.g., TES = 0.376 total impact, MES = 0.291, JES = 0.165, MET unclustered = 0.191) with TES ranked 1st. However, the Asimov impact ranking table (@tbl:impact-ranking, lines 762-778) shows MES ranked 1st (0.404), MET unclustered 2nd (0.354), JES 3rd (0.267), and TES only 4th (0.214). These are clearly two different sets of numbers. The text in each subsection claims to report the impact "on Asimov data," so they should match the Asimov ranking table. Either the per-subsection numbers are stale from an earlier iteration, or the ranking table was refreshed without updating the subsection text. Reconcile throughout.

---

## Category B: Should Fix

### B1. Repeated article: "the the" typos

Two instances of "the the":
- Line 270: "optimized in the the exploration study"
- Line 1294: "as anticipated in the the 10% validation interpretation"

These should each be reduced to a single "the."

### B2. Prose reference to internal investigation artifacts

Line 1418 references figures using a glob pattern and backtick-escaped filenames: `` `figures/gof_investigation_*.pdf` and `figures/gof_per_category.pdf` ``. This is an internal artifact reference, not a proper figure cross-reference. These figures either should be included in the AN with proper `@fig:` labels and captions, or the reference should be removed. Referring readers to filenames they cannot resolve within the rendered PDF is unhelpful.

### B3. NN input features table lists 15 features but text says 14

Table 7 (@tbl:nn-features, lines 420-437) lists 15 rows of features (including both "Leading jet $p_\mathrm{T}$" and "Leading jet $\eta$" as well as "$N_\mathrm{b-jets}$"). But the text consistently says "14 input features." Count them: $\tau_h$ $p_T$, $m_\mathrm{vis}$, $N_\mathrm{jets}$, MET, $\Delta R$, $\mu$ $p_T$, $\tau_h$ DM, $m_T$, $\Delta\phi$, MET significance, $\mu$ $\eta$, $\tau_h$ $\eta$, leading jet $p_T$, leading jet $\eta$, $N_\mathrm{b-jets}$ = 15 features. Clarify whether it is 14 or 15, and reconcile the table with the text. If MET significance is computed from other inputs and not an independent feature, note that.

### B4. Collinear mass go/no-go threshold interpretation

The text (line 514) says "higher than the strategy estimates but remain below the 50% go/no-go threshold for signal events." The ggH unphysical fraction is 45.7%, which is close to the boundary. The text treats 50% as a hard threshold, but it would strengthen the analysis to briefly acknowledge the proximity and discuss what would change at, say, 48% vs 52%. A sentence noting the sensitivity to this threshold choice would add analytical depth.

### B5. Observed significance statement in full data results

The observed significance is quoted as 0.61 standard deviations (line 1260), but the expected significance from the full data fit is quoted as 0.85 standard deviations (line 1512). It would help the reader to see these presented together in the primary result section (Section 9.3.1), not just in the conclusions. A brief sentence after the observed significance noting the expected significance would make the comparison immediately accessible.

### B6. Full data GoF section could benefit from a quantitative comparison

Section 9.6 presents the GoF p-value of 0.000 with per-category diagnostics, but the comparison to the toy distribution is only given for the NN score ("observed 33.1 vs toy range [10.2, 28.6], mean 17.8"). Providing the same three numbers (observed, toy range, toy mean) for $m_\mathrm{vis}$ and $m_\mathrm{col}$ would let the reader directly compare how far each approach's GoF exceeds the toy distribution.

### B7. Change log entry for v5-v1 uses internal phase terminology

Line 41 references "phase labels" and mentions "internal phase labels" in the context of what was removed. The change log itself contains phrasing like "Added flagship comparison figures" which is methodology jargon. Since the change log is in the rendered AN, consider using physics terminology (e.g., "Added comparison figures showing this measurement vs. published CMS result").

### B8. The "10% data validation" section title might confuse non-CMS readers

"10% Data Validation" is clear to insiders but could confuse external readers who might interpret it as "validating 10% of the analysis." A more descriptive section title such as "Validation on a 10% Data Subsample" would immediately convey the concept.

---

## Category C: Suggestions

### C1. Consider adding a pileup validation figure

Section 11.3 discusses the missing pileup reweighting and estimates the effect as "< 2% on $\mu$ based on the PV distribution agreement observed in the exploration study." Referencing or including the primary vertex multiplicity distribution (the file `figures/pv_npvs.pdf` exists in the figures directory but is not referenced in the AN) would give the reader visual evidence for this claim.

### C2. Add a data quality / sample characterization figure early in the AN

The figure sequence currently jumps from tau ID working point distributions (Section 2.4) directly to control region definitions and the cutflow. Including one or two exploration-era distributions early (e.g., the $m_\mathrm{vis}$ distribution before any selection beyond trigger, or the PV multiplicity distribution) would improve the figure-scrolling test by establishing the dataset characteristics before moving to selection details.

### C3. Systematic shift figures could use a brief interpretive comparison

The four systematic shift figures (TES, MES, JES, MET unclustered -- Figures in Section 7) each show the ratio of varied to nominal templates. A brief sentence comparing the magnitudes across the four figures (e.g., "The TES produces the largest bin-by-bin shape changes at 5-20%, while the MES changes are 2-10%") would help the reader quickly rank their visual importance without needing to cross-reference the impact ranking table.

### C4. Consider adding the expected CLs limit bands to the CLs scan figure

Figure @fig:cls-scan shows the CLs curves for the three approaches but is described as expected limits. Standard HEP presentations of CLs scans include the median expected with 1-sigma and 2-sigma bands. If these are available from the asymptotic calculation, overlaying them would strengthen this flagship figure.

### C5. The NN feature table could include a "Used in published analysis?" column

Since the comparison to the published CMS analysis is a central theme, adding a column to @tbl:nn-features indicating which features overlap with the published analysis's MVA inputs would immediately contextualize the feature choice and help explain any performance differences.

### C6. Consider a paragraph on the choice of Adam optimizer and convergence

The NN configuration table (@tbl:nn-config) notes 30 iterations to convergence. A brief mention of whether early stopping triggered (and at which iteration) versus running the full 30 iterations would document whether the training was well-converged or potentially undertrained.

### C7. The Reproduction Contract appendix could specify the software versions

The reproduction contract (Appendix B) describes how to reproduce the analysis but does not specify the exact versions of key packages (pyhf, scikit-learn, uproot, numpy). Since `pixi.toml` pins these, a brief note saying "Software versions are locked in `pixi.toml`; `pixi install` reproduces the exact environment" would close this gap for the reader.

### C8. Consider adding an equation for the QCD same-sign estimation uncertainty propagation

The QCD estimation section (Section 3.3) defines the QCD yield formula (Equation 9) but does not show the uncertainty propagation formula. Since the 20% normalization uncertainty is an important input to the fit, writing out how the statistical uncertainty on $R_\mathrm{OS/SS}$ and the Poisson uncertainty on the SS yield combine would satisfy the "reproduce every number" completeness test.

### C9. The abstract could mention the comparison to the published CMS result

The abstract currently ends with the observation about the normalization deficit. Adding a sentence noting the pull with the published CMS result ($-0.13\sigma$) would give the reader the key physics takeaway immediately, since this consistency check is arguably the most important physics statement in the analysis.

### C10. Unused figures in the figures directory

Several figures exist on disk but are not referenced in the AN:
`collinear_mass.pdf`, `collinear_mass_physical.pdf`, `delta_phi.pdf`, `delta_r.pdf`, `met_pt.pdf`, `mt.pdf`, `mu_eta.pdf`, `mu_pt.pdf`, `mvis.pdf`, `nbjets.pdf`, `njets.pdf`, `tau_dm.pdf`, `tau_eta.pdf`, `tau_pt.pdf`, `pv_npvs.pdf`, `vbf_deta.pdf`, `vbf_mjj.pdf`.
Some of these (vbf_mjj, vbf_deta, tau_dm, nbjets, mu_eta) are kinematic distributions that would enrich the Kinematics section (Section 5). Including even a few of the more informative ones (e.g., the VBF-specific $m_{jj}$ and $\Delta\eta_{jj}$ distributions) would strengthen the VBF category documentation, which is particularly important given the 31% deficit discussion.

---

## Summary

| Category | Count | Items |
|----------|-------|-------|
| A (must resolve) | 3 | A1, A2, A3 |
| B (should fix) | 8 | B1-B8 |
| C (suggestion) | 10 | C1-C10 |

The analysis note is comprehensive and well-written. The three Category A issues are all resolvable by reconciling numbers and removing duplicates -- they do not reflect physics problems. The Category B items are clarity and completeness improvements that would polish the document. The Category C suggestions would further strengthen what is already a strong analysis note, particularly by leveraging existing figures that are not yet referenced.
