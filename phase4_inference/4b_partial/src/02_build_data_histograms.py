"""
Phase 4b Step 2: Build data histograms from 10% subsample.

Histograms the 10% data in all discriminants and categories.
Produces both raw (for fitting) and scaled-by-10 (for comparison to full MC).
Also builds the QCD template from 10% SS data.
"""
import logging
import json
import numpy as np
from pathlib import Path
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

P3 = Path("phase3_selection/outputs")
P4A = Path("phase4_inference/4a_expected/outputs")
OUT = Path("phase4_inference/4b_partial/outputs")
OUT.mkdir(parents=True, exist_ok=True)

DATA_SAMPLES = ["Run2012B_TauPlusX", "Run2012C_TauPlusX"]

# Load the merged templates from 4a to get the correct (merged) binning
with open(P4A / "nominal_templates.json") as f:
    nominal_4a = json.load(f)

# Background estimation parameters
with open(P3 / "background_estimation.json") as f:
    bkg_est = json.load(f)
R_OSSS = bkg_est["r_osss"]
SF_W = bkg_est["sf_w"]

# MC sample tags
MC_SAMPLES = {
    "ggH": "GluGluToHToTauTau",
    "VBF": "VBF_HToTauTau",
    "DY": "DYJetsToLL",
    "TTbar": "TTbar",
    "W1J": "W1JetsToLNu",
    "W2J": "W2JetsToLNu",
    "W3J": "W3JetsToLNu",
}

# VBF categorization
VBF_MJJ_CUT = 200.0
VBF_DETA_CUT = 2.0

# Raw binning (before merging) — must match Phase 4a pre-merge binning
RAW_BINNING = {
    "mvis": {"bins": 25, "lo": 0.0, "hi": 250.0},
    "nn_score": {"bins": 20, "lo": 0.0, "hi": 1.0},
    "mcol": {"bins": 25, "lo": 0.0, "hi": 300.0},
}


def categorize(arrays):
    """Split events into Baseline and VBF."""
    njets = arrays["njets"]
    mjj = arrays["mjj"]
    deta = arrays["deta_jj"]
    is_vbf = (njets >= 2) & (mjj > VBF_MJJ_CUT) & (np.abs(deta) > VBF_DETA_CUT)
    return ~is_vbf, is_vbf


def get_merged_edges(approach, cat):
    """Get the merged bin edges from the 4a nominal templates."""
    return np.array(nominal_4a[approach][cat]["edges"])


def build_histogram_merged(values, weights, approach, cat):
    """Build histogram with the merged binning from Phase 4a."""
    edges = get_merged_edges(approach, cat)
    h, _ = np.histogram(values, bins=edges, weights=weights)
    return h.astype(np.float64), edges


def main():
    log.info("Building data histograms from 10% subsample")

    data_hists = {}

    for approach in ["mvis", "nn_score", "mcol"]:
        log.info(f"\n--- Approach: {approach} ---")
        data_hists[approach] = {}

        for cat_name in ["baseline", "vbf"]:
            # Accumulate data from both run periods
            h_data = None

            for tag in DATA_SAMPLES:
                # Load 10% subsample
                arr = np.load(
                    OUT / f"p3_{tag}_os_sr_10pct.npz", allow_pickle=True
                )
                arrays = {k: arr[k] for k in arr.keys()}
                weights = arrays["weight"].astype(np.float64)

                # Get observable
                if approach == "mvis":
                    obs = arrays["mvis"]
                elif approach == "nn_score":
                    nn = np.load(
                        OUT / f"p3_{tag}_os_sr_nn_score_10pct.npz",
                        allow_pickle=True,
                    )
                    obs = nn["nn_score"]
                else:
                    col = np.load(
                        OUT / f"p3_{tag}_os_sr_collinear_10pct.npz",
                        allow_pickle=True,
                    )
                    obs = col["m_col"]

                # Categorize
                is_bl, is_vbf = categorize(arrays)
                cat_mask = is_bl if cat_name == "baseline" else is_vbf

                h, edges = build_histogram_merged(
                    obs[cat_mask], weights[cat_mask], approach, cat_name
                )

                if h_data is None:
                    h_data = h
                else:
                    h_data += h

            n_bins = len(h_data)
            data_hists[approach][cat_name] = {
                "data_10pct": h_data.tolist(),
                "data_10pct_scaled": (h_data * 10.0).tolist(),
                "data_10pct_err": np.sqrt(h_data).tolist(),
                "data_10pct_scaled_err": (np.sqrt(h_data) * 10.0).tolist(),
                "edges": edges.tolist(),
                "n_bins": n_bins,
                "total_10pct": float(h_data.sum()),
                "total_scaled": float(h_data.sum() * 10.0),
            }

            # Get expected total from 4a
            exp_total = sum(
                p["yield"]
                for p in nominal_4a[approach][cat_name]["processes"].values()
            )

            log.info(
                f"  {approach} {cat_name}: "
                f"10% data = {h_data.sum():.0f}, "
                f"scaled = {h_data.sum() * 10:.0f}, "
                f"expected = {exp_total:.0f}, "
                f"ratio = {h_data.sum() * 10 / exp_total:.3f}"
            )

    # Also build 10% QCD template from 10% SS data
    log.info("\n--- Building 10% QCD template ---")
    qcd_10pct = {}

    for approach in ["mvis", "nn_score", "mcol"]:
        qcd_10pct[approach] = {}
        for cat_name in ["baseline", "vbf"]:
            # 10% SS data
            h_data_ss = None
            for tag in DATA_SAMPLES:
                arr_ss = np.load(
                    OUT / f"p3_{tag}_ss_sr_10pct.npz", allow_pickle=True
                )
                arrays_ss = {k: arr_ss[k] for k in arr_ss.keys()}
                w_ss = arrays_ss["weight"].astype(np.float64)

                if approach == "mvis":
                    obs_ss = arrays_ss["mvis"]
                elif approach == "nn_score":
                    nn_ss = np.load(
                        OUT / f"p3_{tag}_ss_sr_nn_score_10pct.npz",
                        allow_pickle=True,
                    )
                    obs_ss = nn_ss["nn_score"]
                else:
                    col_ss = np.load(
                        OUT / f"p3_{tag}_ss_sr_collinear_10pct.npz",
                        allow_pickle=True,
                    )
                    obs_ss = col_ss["m_col"]

                is_bl, is_vbf = categorize(arrays_ss)
                cat_mask = is_bl if cat_name == "baseline" else is_vbf

                h, _ = build_histogram_merged(
                    obs_ss[cat_mask], w_ss[cat_mask], approach, cat_name
                )
                if h_data_ss is None:
                    h_data_ss = h
                else:
                    h_data_ss += h

            # Full SS MC (NOT subsampled — we use full MC)
            h_mc_ss = None
            for mc_name, mc_tag in MC_SAMPLES.items():
                arr_ss = np.load(
                    P3 / f"p3_{mc_tag}_ss_sr.npz", allow_pickle=True
                )
                arrays_ss = {k: arr_ss[k] for k in arr_ss.keys()}
                w_ss = arrays_ss["weight"].astype(np.float64)
                if mc_tag in ("W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu"):
                    w_ss *= SF_W

                if approach == "mvis":
                    obs_ss = arrays_ss["mvis"]
                elif approach == "nn_score":
                    nn_ss = np.load(
                        P3 / f"p3_{mc_tag}_ss_sr_nn_score.npz",
                        allow_pickle=True,
                    )
                    obs_ss = nn_ss["nn_score"]
                else:
                    col_ss = np.load(
                        P3 / f"p3_{mc_tag}_ss_sr_collinear.npz",
                        allow_pickle=True,
                    )
                    obs_ss = col_ss["m_col"]

                is_bl, is_vbf = categorize(arrays_ss)
                cat_mask = is_bl if cat_name == "baseline" else is_vbf

                h, _ = build_histogram_merged(
                    obs_ss[cat_mask], w_ss[cat_mask], approach, cat_name
                )
                if h_mc_ss is None:
                    h_mc_ss = h
                else:
                    h_mc_ss += h

            # QCD from 10% data: scale SS MC by 0.1 to match 10% data
            # QCD_10pct = (Data_SS_10pct - MC_SS * 0.1) * R_OS/SS
            # Then scale by 10 to compare to full prediction
            h_qcd_10pct = (h_data_ss - h_mc_ss * 0.1) * R_OSSS
            h_qcd_10pct[h_qcd_10pct < 0] = 0.0

            qcd_10pct[approach][cat_name] = {
                "qcd_10pct": h_qcd_10pct.tolist(),
                "qcd_10pct_scaled": (h_qcd_10pct * 10.0).tolist(),
                "data_ss_10pct": h_data_ss.tolist(),
                "mc_ss_full_scaled_0p1": (h_mc_ss * 0.1).tolist(),
            }

            # Compare to 4a QCD
            qcd_4a = nominal_4a[approach][cat_name]["processes"]["QCD"]["yield"]
            log.info(
                f"  {approach} {cat_name} QCD: "
                f"10% scaled = {h_qcd_10pct.sum() * 10:.0f}, "
                f"4a = {qcd_4a:.0f}, "
                f"ratio = {h_qcd_10pct.sum() * 10 / max(qcd_4a, 1):.3f}"
            )

    # Save
    output = {"data_histograms": data_hists, "qcd_10pct": qcd_10pct}
    with open(OUT / "data_histograms_10pct.json", "w") as f:
        json.dump(output, f, indent=2)
    log.info(f"\nSaved to {OUT / 'data_histograms_10pct.json'}")


if __name__ == "__main__":
    main()
