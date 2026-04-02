"""
Phase 4a Step 3: Build pyhf workspaces for all three fitting approaches.

Creates a simultaneous Baseline+VBF fit workspace for each approach:
- m_vis, NN score, m_col
Each workspace has:
- Signal (ggH + VBF) with mu as POI
- Backgrounds: ZTT, ZLL, TTbar, Wjets, QCD
- Normalization systematics (normsys)
- Shape systematics (histosys)
- MC statistical uncertainty (staterror / Barlow-Beeston)
"""
import logging
import json
import numpy as np
import pyhf
from pathlib import Path
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

OUT = Path("phase4_inference/4a_expected/outputs")

# Load templates
with open(OUT / "nominal_templates.json") as f:
    nominal = json.load(f)

with open(OUT / "shape_systematic_templates.json") as f:
    shape_systs = json.load(f)

# Process ordering
SIGNAL_PROCS = ["ggH", "VBF"]
BKG_PROCS = ["ZTT", "ZLL", "TTbar", "Wjets", "QCD"]
ALL_PROCS = SIGNAL_PROCS + BKG_PROCS

# Categories
CATEGORIES = ["baseline", "vbf"]

# Approach-specific process name mapping for shape systs
SHAPE_PROC_MAP = {
    "ggH": "ggH",
    "VBF": "VBF_sig",
    "ZTT": "ZTT",
    "ZLL": "ZLL",
    "TTbar": "TTbar",
    "Wjets": "Wjets",
    "QCD": "QCD",
}


def safe_template(h, min_val=1e-6):
    """Ensure all bins are positive for pyhf."""
    h = np.array(h, dtype=np.float64)
    h[h < min_val] = min_val
    return h.tolist()


def merge_low_stats_bins(templates_dict, shape_systs_dict, approach, cat,
                         min_expected=5.0):
    """Merge adjacent bins in the VBF category until every bin has
    at least `min_expected` total background events.

    [FIX F1: ensures numerical stability for GoF toys by eliminating
     near-empty bins that cause convergence failures.]

    Returns the merged nominal dict, merged shape systs, and new edges.
    Modifies data in-place in the nominal and shape dicts.
    """
    cat_data = templates_dict[approach][cat]
    procs_data = cat_data["processes"]

    # Compute total expected per bin (all processes)
    total = None
    for proc in ALL_PROCS:
        pd = procs_data.get(proc, {})
        if not pd:
            continue
        h = np.array(pd["nominal"])
        if total is None:
            total = h.copy()
        else:
            total += h

    if total is None:
        return

    # Determine which bins to merge
    # Greedily merge from left: if a bin has < min_expected, merge it
    # with the next bin
    n_bins = len(total)
    merge_groups = []  # list of lists of original bin indices
    current_group = [0]
    current_sum = total[0]

    for i in range(1, n_bins):
        if current_sum < min_expected:
            # Merge this bin into the current group
            current_group.append(i)
            current_sum += total[i]
        else:
            merge_groups.append(current_group)
            current_group = [i]
            current_sum = total[i]
    merge_groups.append(current_group)

    # If the last group is too small, merge it with the previous
    if len(merge_groups) > 1 and sum(total[i] for i in merge_groups[-1]) < min_expected:
        merge_groups[-2].extend(merge_groups[-1])
        merge_groups.pop()

    n_merged = len(merge_groups)
    if n_merged == n_bins:
        log.info(f"    No merging needed for {approach}/{cat} (all bins >= {min_expected})")
        return

    log.info(f"    Merging {approach}/{cat}: {n_bins} -> {n_merged} bins "
             f"(min total expected per bin: {min_expected})")

    # Helper to merge a histogram according to groups
    def merge_hist(h_arr):
        h = np.array(h_arr)
        return np.array([h[group].sum() for group in merge_groups])

    def merge_stat_err(err_arr):
        err = np.array(err_arr)
        return np.array([np.sqrt((err[group]**2).sum()) for group in merge_groups])

    # Merge nominal templates
    for proc in list(procs_data.keys()):
        pd = procs_data[proc]
        pd["nominal"] = merge_hist(pd["nominal"]).tolist()
        pd["stat_err"] = merge_stat_err(pd["stat_err"]).tolist()
        # yield stays the same (it's the sum)

    # Merge edges
    old_edges = np.array(cat_data["edges"])
    new_edges = [old_edges[group[0]] for group in merge_groups] + [old_edges[-1]]
    cat_data["edges"] = new_edges

    # Merge shape systematic templates
    for syst_name in shape_systs_dict:
        for dir_name in ["up", "down"]:
            for proc_key_suffix in ["ggH", "VBF_sig", "ZTT", "ZLL", "TTbar", "Wjets", "QCD"]:
                key = f"{proc_key_suffix}_{cat}_{approach}"
                if key in shape_systs_dict[syst_name][dir_name]:
                    h = shape_systs_dict[syst_name][dir_name][key]
                    shape_systs_dict[syst_name][dir_name][key] = merge_hist(h).tolist()

    return n_merged


def get_shape_syst(syst_name, proc, cat, approach):
    """Get up/down histograms for a shape systematic."""
    syst_proc = SHAPE_PROC_MAP.get(proc, proc)
    key = f"{syst_proc}_{cat}_{approach}"
    h_up = shape_systs.get(syst_name, {}).get("up", {}).get(key)
    h_down = shape_systs.get(syst_name, {}).get("down", {}).get(key)
    return h_up, h_down


def build_workspace(approach):
    """Build a pyhf workspace for a given fitting approach."""
    log.info(f"Building workspace for approach: {approach}")

    channels = []

    for cat in CATEGORIES:
        channel_name = f"{approach}_{cat}"
        log.info(f"  Channel: {channel_name}")

        samples = []
        cat_data = nominal[approach][cat]

        for proc in ALL_PROCS:
            proc_data = cat_data["processes"].get(proc, {})
            if not proc_data:
                log.warning(f"    Missing process {proc} in {channel_name}")
                continue

            nom = safe_template(proc_data["nominal"])
            stat_err = proc_data["stat_err"]

            # Build modifier list
            modifiers = []

            # ---------- POI (signal strength) ----------
            if proc in SIGNAL_PROCS:
                modifiers.append({
                    "name": "mu",
                    "type": "normfactor",
                    "data": None,
                })

            # ---------- Normalization systematics ----------
            # Luminosity: 2.6% on all MC (not QCD which is data-driven)
            if proc != "QCD":
                modifiers.append({
                    "name": "lumi",
                    "type": "normsys",
                    "data": {"hi": 1.026, "lo": 0.974},
                })

            # Z->tautau normalization: 12%
            if proc == "ZTT":
                modifiers.append({
                    "name": "norm_ztt",
                    "type": "normsys",
                    "data": {"hi": 1.12, "lo": 0.88},
                })

            # Z->ll normalization: correlated with ZTT
            if proc == "ZLL":
                modifiers.append({
                    "name": "norm_ztt",
                    "type": "normsys",
                    "data": {"hi": 1.12, "lo": 0.88},
                })

            # TTbar normalization: 5%
            if proc == "TTbar":
                modifiers.append({
                    "name": "norm_ttbar",
                    "type": "normsys",
                    "data": {"hi": 1.05, "lo": 0.95},
                })

            # W+jets normalization: 10% (data-driven SF uncertainty + shape extrapolation)
            if proc == "Wjets":
                modifiers.append({
                    "name": f"norm_wjets_{cat}",
                    "type": "normsys",
                    "data": {"hi": 1.10, "lo": 0.90},
                })

            # QCD normalization: 20%
            if proc == "QCD":
                modifiers.append({
                    "name": f"norm_qcd_{cat}",
                    "type": "normsys",
                    "data": {"hi": 1.20, "lo": 0.80},
                })

            # Signal theory: ggH scale (+4.4/-6.9%), PDF+alphas (3.2%), BR (1.7%)
            if proc == "ggH":
                modifiers.append({
                    "name": "theory_ggH_scale",
                    "type": "normsys",
                    "data": {"hi": 1.044, "lo": 0.931},  # +4.4/-6.9%
                })
                modifiers.append({
                    "name": "theory_ggH_pdf",
                    "type": "normsys",
                    "data": {"hi": 1.032, "lo": 0.968},
                })
                modifiers.append({
                    "name": "theory_br_tautau",
                    "type": "normsys",
                    "data": {"hi": 1.017, "lo": 0.983},
                })

            # Signal theory: VBF scale (+0.3/-0.2%), PDF+alphas (2.2%), BR (1.7%)
            if proc == "VBF":
                modifiers.append({
                    "name": "theory_vbf_scale",
                    "type": "normsys",
                    "data": {"hi": 1.003, "lo": 0.998},
                })
                modifiers.append({
                    "name": "theory_vbf_pdf",
                    "type": "normsys",
                    "data": {"hi": 1.022, "lo": 0.978},
                })
                modifiers.append({
                    "name": "theory_br_tautau",
                    "type": "normsys",
                    "data": {"hi": 1.017, "lo": 0.983},
                })

            # Trigger efficiency: 3% on signal, TTbar, W+jets (NOT ZTT/ZLL)
            if proc in ("ggH", "VBF", "TTbar", "Wjets"):
                modifiers.append({
                    "name": "trigger_eff",
                    "type": "normsys",
                    "data": {"hi": 1.03, "lo": 0.97},
                })

            # Tau ID efficiency: 5% on events with genuine taus
            if proc in ("ggH", "VBF", "ZTT"):
                modifiers.append({
                    "name": "tau_id_eff",
                    "type": "normsys",
                    "data": {"hi": 1.05, "lo": 0.95},
                })

            # Muon ID+iso: 2% on all MC
            if proc != "QCD":
                modifiers.append({
                    "name": "muon_id_iso",
                    "type": "normsys",
                    "data": {"hi": 1.02, "lo": 0.98},
                })

            # b-tag efficiency: 5% on TTbar
            if proc == "TTbar":
                modifiers.append({
                    "name": "btag_eff",
                    "type": "normsys",
                    "data": {"hi": 1.05, "lo": 0.95},
                })

            # Missing backgrounds: 5% on all MC-based backgrounds
            if proc in ("ZTT", "ZLL", "TTbar"):
                modifiers.append({
                    "name": "norm_missing_bkg",
                    "type": "normsys",
                    "data": {"hi": 1.05, "lo": 0.95},
                })

            # ---------- Shape systematics ----------
            for syst_name in ["tes", "mes", "jes", "met_uncl"]:
                h_up, h_down = get_shape_syst(syst_name, proc, cat, approach)
                if h_up is not None and h_down is not None:
                    h_up = safe_template(h_up)
                    h_down = safe_template(h_down)
                    modifiers.append({
                        "name": f"shape_{syst_name}",
                        "type": "histosys",
                        "data": {"hi_data": h_up, "lo_data": h_down},
                    })

            # ---------- MC statistical uncertainty (staterror) ----------
            if proc != "QCD":
                # Use Barlow-Beeston lite
                modifiers.append({
                    "name": f"staterror_{channel_name}",
                    "type": "staterror",
                    "data": stat_err,
                })

            sample = {
                "name": proc,
                "data": nom,
                "modifiers": modifiers,
            }
            samples.append(sample)

        channel = {
            "name": channel_name,
            "samples": samples,
        }
        channels.append(channel)

    # Build observations (Asimov = sum of nominal MC + signal at mu=1)
    observations = []
    for cat in CATEGORIES:
        channel_name = f"{approach}_{cat}"
        cat_data = nominal[approach][cat]

        total = None
        for proc in ALL_PROCS:
            proc_data = cat_data["processes"].get(proc, {})
            if proc_data:
                h = np.array(proc_data["nominal"])
                if total is None:
                    total = h.copy()
                else:
                    total += h

        observations.append({
            "name": channel_name,
            "data": total.tolist(),
        })

    # Build workspace spec
    spec = {
        "channels": channels,
        "observations": observations,
        "measurements": [
            {
                "name": f"Htautau_{approach}",
                "config": {
                    "poi": "mu",
                    "parameters": [
                        {"name": "mu", "bounds": [[-30.0, 30.0]], "inits": [1.0]},
                    ],
                },
            }
        ],
        "version": "1.0.0",
    }

    # Validate
    log.info(f"  Validating workspace...")
    try:
        pyhf.Workspace(spec)
        log.info(f"  Workspace valid!")
    except Exception as e:
        log.error(f"  Workspace validation failed: {e}")
        raise

    return spec


def main():
    log.info("Building pyhf workspaces")

    # [FIX F1] Merge low-stats bins to ensure >= 10 expected events per bin,
    # preventing GoF toy convergence failures.
    # The threshold of 10 (not 5) is chosen because individual process bins
    # can be at the 1e-6 floor even when the total is ~5, and Poisson
    # fluctuations of small totals cause convergence failures in toys.
    # Applied to ALL categories for m_vis and m_col (baseline bin 0 for
    # m_vis is completely empty at 0-10 GeV).
    log.info("\n=== Merging low-stats bins (F1 fix) ===")
    for approach in ["mvis", "mcol"]:
        for cat in ["baseline", "vbf"]:
            merge_low_stats_bins(nominal, shape_systs, approach, cat,
                                 min_expected=10.0)
    # NN score: also check (may not need merging)
    for cat in ["baseline", "vbf"]:
        merge_low_stats_bins(nominal, shape_systs, "nn_score", cat,
                             min_expected=10.0)

    # Re-save the merged templates so downstream scripts are consistent
    with open(OUT / "nominal_templates.json", "w") as f:
        json.dump(nominal, f, indent=2)
    with open(OUT / "shape_systematic_templates.json", "w") as f:
        json.dump(shape_systs, f, indent=2)
    log.info("Saved merged templates.\n")

    workspaces = {}
    for approach in ["mvis", "nn_score", "mcol"]:
        spec = build_workspace(approach)

        # Save workspace
        ws_path = OUT / f"workspace_{approach}.json"
        with open(ws_path, "w") as f:
            json.dump(spec, f, indent=2)
        log.info(f"Saved workspace to {ws_path}")

        # Quick validation: try to build model
        ws = pyhf.Workspace(spec)
        model = ws.model()
        log.info(f"  Model has {model.config.npars} parameters")
        log.info(f"  Channels: {model.config.channels}")
        log.info(f"  NP names: {model.config.par_names}")
        log.info(f"  Expected data length: {len(ws.data(model))}")

        workspaces[approach] = spec

    log.info("\nAll workspaces built successfully!")


if __name__ == "__main__":
    main()
