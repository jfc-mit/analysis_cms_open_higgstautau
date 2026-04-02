"""
Phase 2 Step 1: Complete sample inventory of all CMS Open Data NanoAOD files.

Documents: tree names, branch names/types, event counts, schema details.
Checks for weight/flag branches (genWeight, PSWeight, LHEPdfWeight).
Checks GenPart structure, tau decay mode values, and other data archaeology items.
"""
import logging
import json
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
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"

SAMPLES = {
    "GluGluToHToTauTau": {"desc": "ggH signal", "is_mc": True},
    "VBF_HToTauTau": {"desc": "VBF signal", "is_mc": True},
    "DYJetsToLL": {"desc": "Drell-Yan", "is_mc": True},
    "TTbar": {"desc": "ttbar", "is_mc": True},
    "W1JetsToLNu": {"desc": "W+1jet", "is_mc": True},
    "W2JetsToLNu": {"desc": "W+2jets", "is_mc": True},
    "W3JetsToLNu": {"desc": "W+3jets", "is_mc": True},
    "Run2012B_TauPlusX": {"desc": "Data Run2012B", "is_mc": False},
    "Run2012C_TauPlusX": {"desc": "Data Run2012C", "is_mc": False},
}

# Cross-sections in pb (from Strategy)
XSEC = {
    "GluGluToHToTauTau": 21.39 * 0.06256,  # sigma_prod * BR
    "VBF_HToTauTau": 1.600 * 0.06256,
    "DYJetsToLL": 3503.7,
    "TTbar": 252.9,
    "W1JetsToLNu": 6381.2,
    "W2JetsToLNu": 2039.8,
    "W3JetsToLNu": 612.5,
}
LUMI = 11467.0  # pb^-1


def inspect_sample(sample_name, info):
    """Full inspection of a single sample."""
    fpath = DATA_DIR / f"{sample_name}.root"
    if not fpath.exists():
        log.warning("File not found: %s", fpath)
        return None

    result = {"name": sample_name, "description": info["desc"], "is_mc": info["is_mc"]}

    f = uproot.open(fpath)

    # Tree names
    result["trees"] = list(f.keys())
    tree = f["Events"]
    result["num_events"] = tree.num_entries

    # All branch names and types
    branches = {}
    for bname in sorted(tree.keys()):
        btype = str(tree[bname].typename)
        branches[bname] = btype
    result["branches"] = branches
    result["num_branches"] = len(branches)

    # Check for weight/flag branches
    weight_branches = [b for b in tree.keys() if any(
        kw in b.lower() for kw in ["weight", "flag", "lhe", "ps", "genweight"]
    )]
    result["weight_branches"] = weight_branches

    # Read small sample (1000 events) for detailed checks
    n_check = min(1000, tree.num_entries)

    # Check for specific commitment branches
    log.info("  Checking for PSWeight, LHEPdfWeight, genWeight branches...")
    for bcheck in ["PSWeight", "LHEPdfWeight", "LHEScaleWeight", "genWeight",
                    "LHEWeight_originalXWGTUP"]:
        if bcheck in tree.keys():
            arr = tree[bcheck].array(entry_stop=n_check)
            if isinstance(arr, ak.Array):
                flat = ak.to_numpy(ak.flatten(arr)) if arr.ndim > 1 else ak.to_numpy(arr)
            else:
                flat = np.asarray(arr).flatten()
            result[f"branch_{bcheck}"] = {
                "found": True,
                "min": float(np.nanmin(flat)) if len(flat) > 0 else None,
                "max": float(np.nanmax(flat)) if len(flat) > 0 else None,
                "mean": float(np.nanmean(flat)) if len(flat) > 0 else None,
                "std": float(np.nanstd(flat)) if len(flat) > 0 else None,
                "n_unique": int(len(np.unique(flat[:1000]))) if len(flat) > 0 else 0,
                "all_ones": bool(np.all(flat == 1.0)) if len(flat) > 0 else False,
                "any_negative": bool(np.any(flat < 0)) if len(flat) > 0 else False,
            }
        else:
            result[f"branch_{bcheck}"] = {"found": False}

    # Check HLT trigger branches
    hlt_branches = [b for b in tree.keys() if b.startswith("HLT_")]
    result["hlt_branches"] = hlt_branches
    for hlt in hlt_branches:
        arr = tree[hlt].array(entry_stop=n_check)
        flat = ak.to_numpy(arr) if isinstance(arr, ak.Array) else np.asarray(arr)
        result[f"hlt_{hlt}"] = {
            "frac_true": float(np.mean(flat)),
            "n_true": int(np.sum(flat)),
        }

    # Check tau decay mode values
    if "Tau_decayMode" in tree.keys():
        arr = tree["Tau_decayMode"].array(entry_stop=n_check)
        flat = ak.to_numpy(ak.flatten(arr))
        unique_vals = sorted(np.unique(flat).tolist())
        result["tau_decay_modes"] = unique_vals
        log.info("  Tau_decayMode unique values: %s", unique_vals)

    # Check GenPart structure (MC only)
    if info["is_mc"] and "GenPart_pdgId" in tree.keys():
        arr_pdg = tree["GenPart_pdgId"].array(entry_stop=n_check)
        flat_pdg = ak.to_numpy(ak.flatten(arr_pdg))
        unique_pdg = sorted(np.unique(flat_pdg).tolist())
        result["genpart_pdgids"] = unique_pdg
        result["genpart_n_unique_pdgids"] = len(unique_pdg)

        # Check for taus (pdgId=15) and higgs (pdgId=25) in signal
        if sample_name in ["GluGluToHToTauTau", "VBF_HToTauTau"]:
            n_higgs = int(np.sum(np.abs(flat_pdg) == 25))
            n_taus = int(np.sum(np.abs(flat_pdg) == 15))
            n_muons = int(np.sum(np.abs(flat_pdg) == 13))
            result["genpart_n_higgs"] = n_higgs
            result["genpart_n_taus"] = n_taus
            result["genpart_n_muons"] = n_muons
            log.info("  GenPart: %d Higgs, %d taus, %d muons in %d events",
                     n_higgs, n_taus, n_muons, n_check)

        # Check GenPart_status values
        if "GenPart_status" in tree.keys():
            arr_status = tree["GenPart_status"].array(entry_stop=n_check)
            flat_status = ak.to_numpy(ak.flatten(arr_status))
            unique_status = sorted(np.unique(flat_status).tolist())
            result["genpart_status_values"] = unique_status

    # Count multiplicities
    for coll in ["nMuon", "nTau", "nJet", "nGenPart"]:
        if coll in tree.keys():
            arr = tree[coll].array(entry_stop=n_check)
            flat = ak.to_numpy(arr) if isinstance(arr, ak.Array) else np.asarray(arr)
            result[f"mult_{coll}"] = {
                "mean": float(np.mean(flat)),
                "min": int(np.min(flat)),
                "max": int(np.max(flat)),
            }

    # Expected events from xsec * lumi
    if info["is_mc"] and sample_name in XSEC:
        expected = XSEC[sample_name] * LUMI
        ratio = tree.num_entries / expected if expected > 0 else None
        result["expected_events_xsec_lumi"] = expected
        result["ngen_over_expected"] = ratio
        log.info("  Expected from xsec*lumi: %.0f, N_gen: %d, ratio: %.2f",
                 expected, tree.num_entries, ratio if ratio else 0)

    f.close()
    return result


def main():
    log.info("=" * 60)
    log.info("Phase 2 Step 1: Sample Inventory")
    log.info("=" * 60)

    all_results = {}

    for sample_name, info in SAMPLES.items():
        log.info("\n--- %s (%s) ---", sample_name, info["desc"])
        result = inspect_sample(sample_name, info)
        if result is not None:
            all_results[sample_name] = result
            log.info("  Events: %d, Branches: %d",
                     result["num_events"], result["num_branches"])
            if result.get("weight_branches"):
                log.info("  Weight/flag branches: %s", result["weight_branches"])
            if result.get("hlt_branches"):
                log.info("  HLT branches: %s", result["hlt_branches"])

    # Summary
    log.info("\n" + "=" * 60)
    log.info("SUMMARY")
    log.info("=" * 60)

    # Check branch consistency across samples
    all_branch_sets = {}
    for name, result in all_results.items():
        all_branch_sets[name] = set(result["branches"].keys())

    mc_names = [n for n, i in SAMPLES.items() if i["is_mc"]]
    data_names = [n for n, i in SAMPLES.items() if not i["is_mc"]]

    # Find branches common to all MC samples
    mc_common = set.intersection(*[all_branch_sets[n] for n in mc_names if n in all_branch_sets])
    data_common = set.intersection(*[all_branch_sets[n] for n in data_names if n in all_branch_sets])

    mc_only = mc_common - data_common
    data_only = data_common - mc_common
    shared = mc_common & data_common

    log.info("Branches common to all MC: %d", len(mc_common))
    log.info("Branches common to all Data: %d", len(data_common))
    log.info("MC-only branches: %s", sorted(mc_only))
    log.info("Data-only branches: %s", sorted(data_only))
    log.info("Shared branches: %d", len(shared))

    # Save results
    output_path = OUTPUT_DIR / "sample_inventory.json"
    # Convert numpy types to native python
    def convert(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        elif isinstance(obj, (np.floating,)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2, default=convert)
    log.info("Inventory saved to %s", output_path)


if __name__ == "__main__":
    main()
