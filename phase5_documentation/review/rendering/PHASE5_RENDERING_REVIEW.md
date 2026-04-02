# Phase 5 Rendering Review

**Document:** `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.pdf`
**Date:** 2026-03-25
**Reviewer:** Rendering reviewer (automated + manual inspection)

---

## Summary

The PDF is 70 pages, well within the 50-100 page target. The document compiles
cleanly with only 2 overfull hbox warnings (one significant at 33pt, one minor
at 2pt) and zero overfull vbox warnings. No unresolved cross-references ("??")
or citations ("[?]") were found. All 75 figure inclusions render successfully.
The bibliography contains 22 references. The document is well-structured with
proper title page math, abstract placement, TOC, numbered equations, letter-
numbered appendices, and an unnumbered references section.

---

## Checklist Results

### 1. Page count
**PASS.** 70 pages (target: 50-100).

### 2. Title page
**PASS.** Title renders with proper math: $H\to\tau\tau$, $\mu\tau_\mathrm{h}$,
and $\sqrt{s} = 8$ TeV all appear correctly in the PDF. No visible dollar
signs or literal "sqrt(s)" text.

### 3. Abstract
**PASS.** Abstract appears before the TOC on page 1, unnumbered. Content is
comprehensive (includes primary result, significance, limit, comparison to SM,
and pull convention statement).

### 4. Table of Contents
**PASS.** TOC is present on pages 2-3 with depth 3 (sections, subsections,
subsubsections). Spot-checks:
- "1 Introduction" listed at page 5 -- confirmed: Introduction begins on page 5.
- "A Limitation Index" listed at page 67 -- confirmed: Appendix A starts on page 67.
- "12 Full Data Results" listed at page 51 -- confirmed: Section 12 heading appears on page 51.

### 5. Cross-references
**PASS.** Zero occurrences of "??" in the .tex source or PDF text. All
`\ref{}` cross-references resolve to numbers.

**Note (Category C):** Four `alt=` attributes inside `\includegraphics` contain
broken cross-reference fragments (`tbl.~`, `Figure fig.~`) inherited from the
markdown source. These are invisible in the rendered PDF (they only appear in
accessibility metadata) but should be cleaned up in the markdown source for
correctness.

### 6. Citations
**PASS.** Zero occurrences of "[?]" in the document. All 22 bibliography
entries are cited and resolve correctly.

### 7. Figures
**PASS.** All 75 `\includegraphics` calls render successfully (confirmed via
compilation log -- every figure file is found and used). No broken placeholders.

- 52 total figure environments: 22 composite (2+ images), 30 standalone.
- No `\subfloat` used (correct -- composites use `\includegraphics` + `\hspace` pattern).
- Composite figures use (a)/(b)/(c) labels in unified captions.

**Finding B1 (Category B):** There are more standalone figures (30) than
composites (22). The spec states "more composite figures than standalone
(excluding flagships)." While some standalone figures are legitimate flagships
(signal injection, CLs scan, comparison to published result), there are 5
runs of 3+ consecutive standalone figures:
- Lines 1271-1294: 3 consecutive NN diagnostic plots (ROC, overtraining, feature importance)
- Lines 1647-2284: 7 consecutive standalone (separation power + 4 syst shift plots + impact ranking)
- Lines 2517-2726: 4 consecutive (CLs scan, signal injection, NP pulls Asimov, GoF Asimov)
- Lines 3125-3340: 5 consecutive (10% data: mu comparison, NP pulls, per-category mu, GoF, ratio summary)
- Lines 3791-4130: 4 consecutive (full data: three-way mu, NP pulls, impact ranking, GoF NN)

The 4 systematic shift plots (TES, MES, JES, MET unclustered) in lines
1999-2081 are a natural 2x2 grid candidate. The 10% data diagnostics
(lines 3125-3340) could be partially combined. The full data diagnostics
(lines 3791-4130) similarly have combination potential.

### 8. Tables
**PASS.** No overfull hbox warnings from table content. Tables render within
margins and are readable. The `\midrule` + `\bottomrule` pattern in the .tex
source is a standard pandoc output convention and renders correctly (data rows
appear in the table body as expected).

### 9. Equations
**PASS.** 19 labeled display equations and 1 unnumbered display equation,
plus abundant inline math (~849 `\(` delimiters). Equations cover: cross-
sections, luminosity weighting, transverse mass, isolation, VBF selection,
W+jets scale factor, OS/SS ratio, QCD yield, visible mass, collinear mass,
profile likelihood, expected yield, test statistic, CLs, TES-MET propagation,
and the final result. No LaTeX compilation artifacts or rendering errors.

### 10. Appendices
**PASS.** Two appendices with letter numbering:
- Appendix A: Limitation Index (page 67)
- Appendix B: Reproduction Contract (page 67)
Both use `\appendix` with `\section{}` and render with "A" / "B" prefixes.

### 11. References section
**PASS.** References section begins on page 69, is unnumbered (`\section*`),
and is added to the TOC via `\addcontentsline`. Contains 22 entries with
proper formatting (author, year, title, journal, DOI/URL).

### 12. No visible dollar signs
**PASS.** The one instance of `$<$` (line 761, cutflow table: "Iso $<$ 0.1")
renders correctly as a math less-than sign with no visible dollar signs in
the PDF. All other inline math uses `\(` delimiters consistently.

**Finding C1 (Category C):** Line 761 uses `$<$` while all other inline math
uses `\(` delimiters. Harmonize to `\(<\)` for consistency.

### 13. Page breaks
**PASS overall.** Page breaks are generally sensible. The `\needspace` and
`\FloatBarrier` commands prevent orphaned captions. `\raggedbottom` avoids
ugly vertical spacing.

**Finding B2 (Category B):** The overfull hbox at lines 2265-2275 (33.35pt
too wide) occurs in the paragraph discussing shape systematic impacts. The
inline math expression with the quadrature sum formula
(`\sqrt{0.404^2 + 0.354^2 + 0.267^2 + 0.214^2}`) is too wide for the line.
This will cause text to extend 33pt past the right margin on approximately
page 33. This should be broken into a display equation or reformulated.

### 14. Font consistency
**PASS.** The document uses lmodern throughout. No mixing of roman/sans-serif
outside the standard LaTeX math font switching. `\mathrm{}` is used
consistently for physics notation (standard practice).

### 15. Change Log
**PASS.** The Change Log fits entirely on page 4 (well under 1 page of
content). Contains 7 version entries from 4a-v1 through 5-v1.

---

## Additional Findings

### Finding B3 (Category B): Cross-reference phrasing
Three instances of "Figures X through Figure Y" phrasing in the body text:
- "Figures 31 through Figure 33" (page ~52)
- "Figures 39 through Figure 41" (page ~52)
- "Figures 45 through Figure 46" (page ~59)

The phrasing should be "Figures 31-33" or "Figures 31 through 33" (without
repeating "Figure"). This is a pandoc-crossref artifact from the markdown
`@fig:X through @fig:Y` pattern.

### Finding B4 (Category B): "Figures 1 through Figure 1"
On page 8, the text reads: "as shown in Figures 1 through Figure 1. The
VLoose working point is rejected due to significantly worse data/MC agreement
(chi2/ndf = 4.08, Figure 1). The data/MC ratio of 1.12 at the Loose working
point (Figure 1)."

All three tau ID working point plots (VLoose, Loose, Medium) were composited
into a single Figure 1 (a 3-panel composite), but the body text still refers
to them as if they were separate figures. "Figures 1 through Figure 1" is
confusing and should be rewritten to "Figure 1" with explicit panel references
like "Figure 1(a)" for VLoose, "Figure 1(b)" for Loose, "Figure 1(c)" for
Medium.

### Finding C2 (Category C): Broken refs in alt text
Four `alt=` attributes in `\includegraphics` contain unresolved cross-reference
fragments (`tbl.~.`, `Figure fig.~`). These are invisible in the rendered PDF
but degrade accessibility metadata. Affected figures:
- `nn_overtraining.pdf` (line 1283): `tbl.~.`
- `nn_feature_importance.pdf` (line 1296): `tbl.~`
- `np_pulls_10pct.pdf` (line 3202): `Figure fig.~`
- `gof_toys_10pct.pdf` (line 3322): `Figure fig.~`

### Finding C3 (Category C): Minor overfull hbox
Line 2834: Overfull hbox of 1.96pt. This is barely perceptible (less than
1mm) and can be safely ignored or addressed by adding a hyphenation hint.

---

## Issue Summary

| ID | Category | Description | Location |
|----|----------|-------------|----------|
| B1 | B | More standalone figures (30) than composites (22); 5 runs of 3+ consecutive standalone figures | Throughout |
| B2 | B | Overfull hbox (33pt) from wide inline math expression | Lines 2265-2275 (~page 33) |
| B3 | B | "Figures X through Figure Y" awkward cross-ref phrasing | 3 instances in body text |
| B4 | B | "Figures 1 through Figure 1" from composited tau ID plots | Page 8 |
| C1 | C | Inconsistent math delimiter (`$<$` vs `\(`) | Line 761 |
| C2 | C | Broken cross-refs in alt text attributes (invisible in PDF) | Lines 1283, 1296, 3202, 3322 |
| C3 | C | Minor overfull hbox (2pt) | Line 2834 |

---

## Verdict

**PASS with Category B items to address before final.**

The document renders well overall: 70 pages, clean compilation, all figures
present, no broken cross-references or citations in visible content, proper
structure with abstract/TOC/appendices/references. The 4 Category B items
are typographic quality issues that should be fixed but do not affect the
physics content. The 3 Category C items are minor suggestions.

The most impactful fix would be B4 (the "Figures 1 through Figure 1"
confusion from the composited tau ID plots) and B2 (the 33pt margin
overflow). B1 (standalone/composite ratio) would improve the document's
density but is less critical given the 70-page count is within range.
