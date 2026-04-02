# Phase 5 BibTeX Review

**Reviewer:** BibTeX Validator
**Date:** 2026-03-25
**Artifact:** `phase5_documentation/outputs/ANALYSIS_NOTE_5_v1.md` + `phase5_documentation/outputs/references.bib`

---

## Summary

- **Unique citation keys in AN:** 22
- **Entries in references.bib:** 27
- **Dangling citations (in AN, not in bib):** 0
- **Orphan entries (in bib, not cited in AN):** 5
- **Entries with missing required metadata:** 6
- **Entries with LaTeX math in titles:** 0
- **Duplicate BibTeX keys:** 0
- **Placeholder/generic titles:** 0
- **PDF compilation citation warnings:** 0

**Threshold check: >= 15 unique citation keys used in AN: PASS (22)**

---

## Findings

### Category A (Must Resolve)

#### A1. `Ellis:1987xu` is typed as `@article` but is a book

This is "QCD and Collider Physics" by Ellis, Stirling, and Webber -- a textbook published by Cambridge University Press. It is listed as `@article` but has no journal, no DOI, no URL, and no eprint. It does have an ISBN and publisher, which are book fields.

**Additionally, this entry is an orphan** -- it is not cited anywhere in the AN. If it is not needed, remove it. If it is needed (e.g., for a QCD background discussion), cite it in the AN and change the entry type to `@book`.

**Fix:** Either remove this orphan entry, or change to `@book` and add a citation in the AN text. If kept, add `url = "https://doi.org/10.1017/CBO9780511628788"` (the book DOI).

#### A2. `Gaiser:1982yw` has a suspicious title and is an orphan

The key `Gaiser:1982yw` typically refers to J. Gaiser's PhD thesis on the Crystal Ball function. However, the title here is "Erratum and addendum: Parametrization of the unresolved hadronic continuum" with authors "Li, Y. and Gaiser, J." -- which does not appear to be a real publication with that exact title. The same volume/page (Phys. Rev. D 25, 2141) is also used for `Li:1983fv`. This entry appears to be fabricated or incorrectly attributed.

**This entry is also an orphan -- not cited in the AN.**

**Fix:** Remove this entry. If a Crystal Ball reference is needed, use the correct Gaiser thesis reference.

#### A3. `Li:1983fv` has a suspicious title and is an orphan

The title "The collinear approximation for tau pair production" attributed to "Li, Y. and Gaiser, J." at Phys. Rev. D 25, 2141 (1982) does not appear to be a real publication. The same Phys. Rev. D volume/page is shared with `Gaiser:1982yw`. Neither entry has a DOI, URL, or eprint to verify. The title does not match any known paper at this journal reference.

**This entry is also an orphan -- not cited in the AN.**

**Fix:** Remove this entry. If a collinear mass approximation reference is needed, find and cite the correct source with verifiable DOI/arXiv.

### Category B (Should Fix)

#### B1. `Pedregosa:2011skl` is missing a DOI or URL

The scikit-learn JMLR paper has no DOI, URL, or eprint. While the journal/volume/pages are correct (JMLR 12, 2825-2830, 2011), best practice requires at least one persistent locator.

**Fix:** Add `url = "https://jmlr.org/papers/v12/pedregosa11a.html"`.

#### B2. `Cranmer:2012sba` is typed as `@article` but should be `@techreport`

HistFactory (CERN-OPEN-2012-016) is a CERN technical report, not a journal article. It has no journal field, which is required for `@article`. The URL to cds.cern.ch is correct.

**Fix:** Change entry type from `@article` to `@techreport` and add `institution = "CERN"`.

#### B3. `pyhf_joss` is typed as `@article` but should be `@software` or `@misc`; also orphan

This is a Zenodo software release (pyhf v0.6.0), not a journal article. It has no journal field. The DOI is a Zenodo DOI (10.5281/zenodo.1169739). Additionally, it is not cited anywhere in the AN (the AN cites `pyhf` for the JOSS paper, and `Cranmer:2012sba` for HistFactory, but never `pyhf_joss`).

**Fix:** Either remove this orphan entry, or change to `@software`/`@misc` and cite it in the AN alongside `[@pyhf]`.

#### B4. `ParticleDataGroup:2022pth` is an orphan -- not cited in the AN

The PDG Review of Particle Physics (2022) is present in `references.bib` but never cited in the AN. For a measurement analysis that uses particle masses and branching ratios, the PDG should likely be cited somewhere (e.g., where tau branching ratios, particle masses, or SM parameters are quoted).

**Fix:** Either cite this reference in the AN where PDG values are used (e.g., tau mass, lepton universality parameters, or any SM constant), or remove if all values are sourced from the YR4 handbook instead.

#### B5. `Gaiser:1982yw` and `Li:1983fv` missing DOI/URL/eprint

Both entries lack any persistent locator (DOI, URL, or eprint). Since they also appear to have fabricated titles (see A2, A3), the primary fix is removal. If valid replacements are added, they must include a DOI or URL.

### Category C (Suggestions)

#### C1. `CMS:2011aa` key vs. year mismatch

The key `CMS:2011aa` suggests 2011, but the publication year is 2008 (JINST 3, S08004). This is the CMS detector paper, and the INSPIRE key `CMS:2011aa` is the standard INSPIRE key for this paper, so it is technically correct. No action needed, but worth noting for anyone unfamiliar with INSPIRE key conventions.

#### C2. Consider citing `ParticleDataGroup:2022pth` for SM constants

Several SM constants appear in the AN (tau mass, branching ratios, Higgs mass). While the YR4 handbook covers Higgs-specific values, the PDG is the standard citation for particle properties. Adding PDG citations would strengthen the provenance trail for numeric constants.

#### C3. `LHCHiggsCrossSectionWorkingGroup:2016ypw` journal field uses non-standard "CERN Report"

The journal field is `"CERN Report"` which is not a standard abbreviation. This is cosmetic and does not affect compilation, but `"CERN Yellow Reports: Monographs"` would be more precise.

---

## Orphan Entry Summary

| BibTeX Key | Status | Recommendation |
|---|---|---|
| `Ellis:1987xu` | Orphan, wrong type, no locator | Remove or fix and cite |
| `Gaiser:1982yw` | Orphan, suspicious title, no locator | Remove |
| `Li:1983fv` | Orphan, suspicious title, no locator | Remove |
| `ParticleDataGroup:2022pth` | Orphan, valid entry | Cite in AN or remove |
| `pyhf_joss` | Orphan, wrong type | Cite in AN or remove |

---

## Entry Completeness Matrix

| Key | title | author | year | doi | url | eprint | Status |
|---|---|---|---|---|---|---|---|
| `CMS:2014nkk` | Y | Y | Y | Y | - | Y | OK |
| `CMS:2017zyp` | Y | Y | Y | Y | - | Y | OK |
| `Aad:2015zhl` | Y | Y | Y | Y | - | Y | OK |
| `LHCHiggsCrossSectionWorkingGroup:2016ypw` | Y | Y | Y | Y | - | Y | OK |
| `CMS:LUM-13-001` | Y | Y | Y | - | Y | - | OK |
| `pyhf` | Y | Y | Y | Y | - | - | OK |
| `pyhf_joss` | Y | Y | Y | Y | Y | - | Orphan, wrong type |
| `Cranmer:2012sba` | Y | Y | Y | - | Y | - | Wrong type |
| `Read:2002hq` | Y | Y | Y | Y | - | - | OK |
| `Cowan:2010js` | Y | Y | Y | Y | - | Y | OK |
| `CMS:2011aa` | Y | Y | Y | Y | - | - | OK |
| `Alwall:2011uj` | Y | Y | Y | Y | - | Y | OK |
| `Nason:2004rx` | Y | Y | Y | Y | - | Y | OK |
| `Sjostrand:2006za` | Y | Y | Y | Y | - | Y | OK |
| `CMS:2018jrd` | Y | Y | Y | Y | - | Y | OK |
| `CMS:2016lmd` | Y | Y | Y | Y | - | Y | OK |
| `Czakon:2011xx` | Y | Y | Y | Y | - | Y | OK |
| `Barlow:1993dm` | Y | Y | Y | Y | - | - | OK |
| `ParticleDataGroup:2022pth` | Y | Y | Y | Y | - | - | Orphan |
| `CMSOpenData:Htautau` | Y | Y | Y | - | Y | - | OK |
| `Gaiser:1982yw` | Y | Y | Y | - | - | - | Orphan, no locator, suspicious |
| `CMS:2012qbp` | Y | Y | Y | Y | - | Y | OK |
| `ATLAS:2012yve` | Y | Y | Y | Y | - | Y | OK |
| `Pedregosa:2011skl` | Y | Y | Y | - | - | - | Missing locator |
| `Li:1983fv` | Y | Y | Y | - | - | - | Orphan, no locator, suspicious |
| `Ellis:1987xu` | Y | Y | Y | - | - | - | Orphan, wrong type, no locator |
| `CMS:PFT-09-001` | Y | Y | Y | - | Y | - | OK |

---

## Verdict

**CONDITIONAL PASS** -- the bibliography compiles without errors and all 22 citations in the AN resolve to valid entries. However, three Category A issues (suspicious/fabricated orphan entries A2, A3, and a mis-typed orphan A1) and five Category B issues must be addressed before final acceptance.

**Required actions before PASS:**
1. Remove `Gaiser:1982yw`, `Li:1983fv`, and either remove or fix `Ellis:1987xu` (Category A -- these entries have unverifiable metadata and are not cited).
2. Fix entry types for `Cranmer:2012sba` and `pyhf_joss` (Category B).
3. Add DOI/URL to `Pedregosa:2011skl` (Category B).
4. Decide on `ParticleDataGroup:2022pth` and `pyhf_joss`: cite them or remove them (Category B).

None of these issues block PDF compilation (the PDF compiles cleanly now), but they represent bibliographic hygiene problems that would be flagged in any peer review.
