"""
Phase 2 Step 2: Data quality assessment.

Checks for NaN/inf, empty branches, outliers, unphysical values across all samples.
Produces data archaeology findings for Open Data.
"""
import logging
from pathlib import Path

from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

import uproot
import awkward as ak
import numpy as np

DATA_DIR = Path("/eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool")

SAMPLES_TO_CHECK = ["GluGluToHToTauTau", "DYJetsToLL", "Run2012B_TauPlusX"]
N_CHECK = 50000  # Check 50k events per sample


def check_branch_quality(tree, branch_name, n_events):
    """Check a branch for NaN, inf, outliers, empty values."""
    try:
        arr = tree[branch_name].array(entry_stop=n_events)
    except Exception as e:
        return {"error": str(e)}

    result = {}

    # Flatten jagged arrays
    if arr.ndim > 1:
        flat = ak.to_numpy(ak.flatten(arr))
        result["jagged"] = True
        result["n_entries_per_event_mean"] = float(ak.mean(ak.num(arr)))
    else:
        flat = ak.to_numpy(arr)
        result["jagged"] = False

    if len(flat) == 0:
        result["empty"] = True
        return result

    result["empty"] = False
    result["dtype"] = str(flat.dtype)
    result["n_values"] = len(flat)

    if np.issubdtype(flat.dtype, np.floating):
        result["n_nan"] = int(np.sum(np.isnan(flat)))
        result["n_inf"] = int(np.sum(np.isinf(flat)))
        valid = flat[np.isfinite(flat)]
        if len(valid) > 0:
            result["min"] = float(np.min(valid))
            result["max"] = float(np.max(valid))
            result["mean"] = float(np.mean(valid))
            result["std"] = float(np.std(valid))
    elif np.issubdtype(flat.dtype, np.integer) or np.issubdtype(flat.dtype, np.bool_):
        result["n_nan"] = 0
        result["n_inf"] = 0
        result["min"] = int(np.min(flat))
        result["max"] = int(np.max(flat))
        result["mean"] = float(np.mean(flat))
        n_unique = len(np.unique(flat))
        result["n_unique"] = n_unique
        if n_unique <= 20:
            result["unique_values"] = sorted(np.unique(flat).tolist())

    return result


def main():
    log.info("=" * 60)
    log.info("Phase 2 Step 2: Data Quality Assessment")
    log.info("=" * 60)

    issues = []

    for sample_name in SAMPLES_TO_CHECK:
        fpath = DATA_DIR / f"{sample_name}.root"
        f = uproot.open(fpath)
        tree = f["Events"]
        log.info("\n=== %s (%d events, checking %d) ===",
                 sample_name, tree.num_entries, min(N_CHECK, tree.num_entries))

        for bname in sorted(tree.keys()):
            result = check_branch_quality(tree, bname, N_CHECK)

            if result.get("error"):
                log.warning("  %s: ERROR: %s", bname, result["error"])
                issues.append(f"{sample_name}/{bname}: read error")
                continue

            if result.get("empty"):
                log.warning("  %s: EMPTY branch", bname)
                issues.append(f"{sample_name}/{bname}: empty branch")
                continue

            # Check for issues
            if result.get("n_nan", 0) > 0:
                log.warning("  %s: %d NaN values", bname, result["n_nan"])
                issues.append(f"{sample_name}/{bname}: {result['n_nan']} NaN")

            if result.get("n_inf", 0) > 0:
                log.warning("  %s: %d Inf values", bname, result["n_inf"])
                issues.append(f"{sample_name}/{bname}: {result['n_inf']} Inf")

            # Physics sanity checks
            if "pt" in bname.lower() and result.get("min", 0) < 0:
                log.warning("  %s: negative pT (min=%.3f)", bname, result["min"])
                issues.append(f"{sample_name}/{bname}: negative pT")

            if bname in ["Muon_eta", "Tau_eta", "Jet_eta"]:
                if abs(result.get("min", 0)) > 10 or abs(result.get("max", 0)) > 10:
                    log.warning("  %s: extreme eta (min=%.1f, max=%.1f)",
                                bname, result["min"], result["max"])
                    issues.append(f"{sample_name}/{bname}: extreme eta")

            # Log key branch stats
            if bname in ["Muon_pt", "Tau_pt", "MET_pt", "Jet_pt", "PV_npvs",
                         "Muon_pfRelIso04_all", "Tau_idIsoRaw",
                         "Muon_tightId", "Tau_idDecayMode", "Tau_idAntiMuTight",
                         "Tau_idAntiEleTight", "Tau_idIsoLoose", "Tau_idIsoVLoose",
                         "Tau_decayMode", "MET_significance"]:
                log.info("  %s: min=%.3f max=%.3f mean=%.3f%s%s",
                         bname, result.get("min", 0), result.get("max", 0),
                         result.get("mean", 0),
                         f" unique={result['unique_values']}" if "unique_values" in result else "",
                         " [JAGGED]" if result.get("jagged") else "")

        f.close()

    log.info("\n" + "=" * 60)
    log.info("DATA QUALITY SUMMARY")
    log.info("=" * 60)
    if issues:
        log.warning("Found %d issues:", len(issues))
        for issue in issues:
            log.warning("  - %s", issue)
    else:
        log.info("No data quality issues found.")


if __name__ == "__main__":
    main()
