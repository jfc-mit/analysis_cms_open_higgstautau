"""
Phase 4a Step 1: Build nominal templates for all fitting approaches and categories.

Loads Phase 3 arrays, applies categorization, builds histograms for:
- 3 fitting approaches: m_vis, NN score, m_col
- 2 categories: Baseline, VBF
- 7 processes: ggH, VBF, ZTT, ZLL, TTbar, Wjets, QCD

QCD estimated from same-sign data minus MC, scaled by OS/SS ratio.
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

# ---------- paths ----------
P3 = Path("phase3_selection/outputs")
OUT = Path("phase4_inference/4a_expected/outputs")
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "figures").mkdir(exist_ok=True)

# ---------- configuration ----------
LUMI = 11467.0  # pb^-1

# Binning definitions
BINNING = {
    "mvis": {"bins": 25, "lo": 0.0, "hi": 250.0, "label": r"$m_{\mathrm{vis}}$ [GeV]"},
    "nn_score": {"bins": 20, "lo": 0.0, "hi": 1.0, "label": "NN score"},
    "mcol": {"bins": 25, "lo": 0.0, "hi": 300.0, "label": r"$m_{\mathrm{col}}$ [GeV]"},
}

# VBF categorization thresholds (from Phase 3)
VBF_MJJ_CUT = 200.0
VBF_DETA_CUT = 2.0

# OS/SS ratio and W+jets SF from Phase 3 background estimation
with open(P3 / "background_estimation.json") as f:
    bkg_est = json.load(f)
R_OSSS = bkg_est["r_osss"]  # 0.979
SF_W = bkg_est["sf_w"]  # 0.999

# MC samples and their tags
MC_SAMPLES = {
    "ggH": "GluGluToHToTauTau",
    "VBF": "VBF_HToTauTau",
    "DY": "DYJetsToLL",
    "TTbar": "TTbar",
    "W1J": "W1JetsToLNu",
    "W2J": "W2JetsToLNu",
    "W3J": "W3JetsToLNu",
}
DATA_SAMPLES = ["Run2012B_TauPlusX", "Run2012C_TauPlusX"]


def load_os_sr(sample_tag):
    """Load OS signal region arrays for a sample."""
    d = np.load(P3 / f"p3_{sample_tag}_os_sr.npz", allow_pickle=True)
    return {k: d[k] for k in d.keys()}


def load_ss_sr(sample_tag):
    """Load SS signal region arrays for a sample."""
    d = np.load(P3 / f"p3_{sample_tag}_ss_sr.npz", allow_pickle=True)
    return {k: d[k] for k in d.keys()}


def load_nn_score(sample_tag, region="os_sr"):
    """Load NN scores for a sample."""
    d = np.load(P3 / f"p3_{sample_tag}_{region}_nn_score.npz", allow_pickle=True)
    return d["nn_score"]


def load_collinear(sample_tag, region="os_sr"):
    """Load collinear mass for a sample."""
    d = np.load(P3 / f"p3_{sample_tag}_{region}_collinear.npz", allow_pickle=True)
    return d["m_col"]


def categorize(arrays):
    """Split events into Baseline and VBF categories.

    Returns boolean masks for each category.
    """
    njets = arrays["njets"]
    mjj = arrays["mjj"]
    deta = arrays["deta_jj"]
    # VBF: >= 2 jets, mjj > 200, |deta_jj| > 2.0
    # mjj and deta_jj are set to -1 and -99 when fewer than 2 jets
    is_vbf = (njets >= 2) & (mjj > VBF_MJJ_CUT) & (np.abs(deta) > VBF_DETA_CUT)
    is_baseline = ~is_vbf
    return is_baseline, is_vbf


def build_histogram(values, weights, binning_key):
    """Build a histogram with the specified binning."""
    b = BINNING[binning_key]
    h, edges = np.histogram(
        values, bins=b["bins"], range=(b["lo"], b["hi"]), weights=weights
    )
    return h.astype(np.float64), edges


def ensure_min_events(hist, min_events=0.0):
    """Set negative bins to zero (for QCD subtraction)."""
    hist = hist.copy()
    hist[hist < 0] = 0.0
    return hist


def compute_stat_error(values, weights, binning_key):
    """Compute statistical uncertainty per bin (sqrt(sum w^2))."""
    b = BINNING[binning_key]
    w2, _ = np.histogram(
        values, bins=b["bins"], range=(b["lo"], b["hi"]), weights=weights ** 2
    )
    return np.sqrt(w2)


def main():
    log.info("Building nominal templates for Phase 4a")

    # Storage for all templates
    templates = {}

    for approach in ["mvis", "nn_score", "mcol"]:
        log.info(f"--- Approach: {approach} ---")
        templates[approach] = {"baseline": {}, "vbf": {}}

        for cat_name in ["baseline", "vbf"]:
            templates[approach][cat_name] = {
                "processes": {},
                "edges": None,
            }

        # ----- MC processes -----
        for proc_name, sample_tag in MC_SAMPLES.items():
            log.info(f"  Processing {proc_name} ({sample_tag})")
            arr = load_os_sr(sample_tag)
            weights = arr["weight"].astype(np.float64)

            # DY decomposition
            if proc_name == "DY":
                is_ztt = arr["is_ztt"].astype(bool)
                # Process ZTT
                for sub_name, sub_mask in [("ZTT", is_ztt), ("ZLL", ~is_ztt)]:
                    sub_arr = {k: v[sub_mask] for k, v in arr.items()}
                    sub_w = weights[sub_mask]

                    # Get observable
                    if approach == "mvis":
                        obs = sub_arr["mvis"]
                    elif approach == "nn_score":
                        nn_all = load_nn_score(sample_tag, "os_sr")
                        obs = nn_all[sub_mask]
                    else:  # mcol
                        mcol_all = load_collinear(sample_tag, "os_sr")
                        obs = mcol_all[sub_mask]

                    # Categorize
                    is_bl, is_vbf = categorize(sub_arr)

                    for cat_name, cat_mask in [("baseline", is_bl), ("vbf", is_vbf)]:
                        h, edges = build_histogram(obs[cat_mask], sub_w[cat_mask], approach)
                        err = compute_stat_error(obs[cat_mask], sub_w[cat_mask], approach)
                        templates[approach][cat_name]["processes"][sub_name] = {
                            "nominal": h.tolist(),
                            "stat_err": err.tolist(),
                            "yield": float(h.sum()),
                            "raw_events": int(cat_mask.sum()),
                        }
                        templates[approach][cat_name]["edges"] = edges.tolist()
                        log.info(f"    {sub_name} {cat_name}: yield={h.sum():.1f}, raw={cat_mask.sum()}")
                continue

            # W+jets: combine all W samples with SF
            if proc_name in ("W1J", "W2J", "W3J"):
                continue  # Handle below

            # Get observable
            if approach == "mvis":
                obs = arr["mvis"]
            elif approach == "nn_score":
                obs = load_nn_score(sample_tag, "os_sr")
            else:  # mcol
                obs = load_collinear(sample_tag, "os_sr")

            # Categorize
            is_bl, is_vbf = categorize(arr)

            for cat_name, cat_mask in [("baseline", is_bl), ("vbf", is_vbf)]:
                h, edges = build_histogram(obs[cat_mask], weights[cat_mask], approach)
                err = compute_stat_error(obs[cat_mask], weights[cat_mask], approach)
                templates[approach][cat_name]["processes"][proc_name] = {
                    "nominal": h.tolist(),
                    "stat_err": err.tolist(),
                    "yield": float(h.sum()),
                    "raw_events": int(cat_mask.sum()),
                }
                templates[approach][cat_name]["edges"] = edges.tolist()
                log.info(f"    {proc_name} {cat_name}: yield={h.sum():.1f}, raw={cat_mask.sum()}")

        # ----- W+jets (combined) -----
        log.info("  Processing W+jets (combined W1J+W2J+W3J)")
        for cat_name in ["baseline", "vbf"]:
            h_total = None
            err2_total = None
            raw_total = 0
            for wj_tag in ["W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu"]:
                arr = load_os_sr(wj_tag)
                weights = arr["weight"].astype(np.float64) * SF_W

                if approach == "mvis":
                    obs = arr["mvis"]
                elif approach == "nn_score":
                    obs = load_nn_score(wj_tag, "os_sr")
                else:
                    obs = load_collinear(wj_tag, "os_sr")

                is_bl, is_vbf = categorize(arr)
                cat_mask = is_bl if cat_name == "baseline" else is_vbf

                h, edges = build_histogram(obs[cat_mask], weights[cat_mask], approach)
                err = compute_stat_error(obs[cat_mask], weights[cat_mask], approach)

                if h_total is None:
                    h_total = h
                    err2_total = err ** 2
                else:
                    h_total = h_total + h
                    err2_total = err2_total + err ** 2
                raw_total += int(cat_mask.sum())

            templates[approach][cat_name]["processes"]["Wjets"] = {
                "nominal": h_total.tolist(),
                "stat_err": np.sqrt(err2_total).tolist(),
                "yield": float(h_total.sum()),
                "raw_events": raw_total,
            }
            log.info(f"    Wjets {cat_name}: yield={h_total.sum():.1f}, raw={raw_total}")

        # ----- QCD (data-driven from SS) -----
        log.info("  Processing QCD (data-driven from SS region)")
        for cat_name in ["baseline", "vbf"]:
            # Data SS
            h_data_ss = None
            for data_tag in DATA_SAMPLES:
                arr_ss = load_ss_sr(data_tag)
                w_ss = arr_ss["weight"].astype(np.float64)

                if approach == "mvis":
                    obs_ss = arr_ss["mvis"]
                elif approach == "nn_score":
                    obs_ss = load_nn_score(data_tag, "ss_sr")
                else:
                    obs_ss = load_collinear(data_tag, "ss_sr")

                is_bl, is_vbf = categorize(arr_ss)
                cat_mask = is_bl if cat_name == "baseline" else is_vbf

                h, _ = build_histogram(obs_ss[cat_mask], w_ss[cat_mask], approach)
                if h_data_ss is None:
                    h_data_ss = h
                else:
                    h_data_ss = h_data_ss + h

            # MC SS (subtract from data)
            h_mc_ss = None
            for mc_name, mc_tag in MC_SAMPLES.items():
                arr_ss = load_ss_sr(mc_tag)
                w_ss = arr_ss["weight"].astype(np.float64)
                # Apply W+jets SF to W samples
                if mc_tag in ("W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu"):
                    w_ss = w_ss * SF_W

                if approach == "mvis":
                    obs_ss = arr_ss["mvis"]
                elif approach == "nn_score":
                    obs_ss = load_nn_score(mc_tag, "ss_sr")
                else:
                    obs_ss = load_collinear(mc_tag, "ss_sr")

                is_bl, is_vbf = categorize(arr_ss)
                cat_mask = is_bl if cat_name == "baseline" else is_vbf

                h, _ = build_histogram(obs_ss[cat_mask], w_ss[cat_mask], approach)
                if h_mc_ss is None:
                    h_mc_ss = h
                else:
                    h_mc_ss = h_mc_ss + h

            # QCD = (Data_SS - MC_SS) * R_OS/SS
            h_qcd = (h_data_ss - h_mc_ss) * R_OSSS
            h_qcd = ensure_min_events(h_qcd)

            # Statistical error: dominated by data SS statistics
            # err ~ R_OS/SS * sqrt(N_data_SS per bin)
            err_qcd = R_OSSS * np.sqrt(np.maximum(h_data_ss, 0.0))

            templates[approach][cat_name]["processes"]["QCD"] = {
                "nominal": h_qcd.tolist(),
                "stat_err": err_qcd.tolist(),
                "yield": float(h_qcd.sum()),
                "raw_events": int(h_data_ss.sum()),
            }
            log.info(f"    QCD {cat_name}: yield={h_qcd.sum():.1f}")

    # ----- Summary -----
    log.info("\n=== Template Summary ===")
    for approach in ["mvis", "nn_score", "mcol"]:
        for cat in ["baseline", "vbf"]:
            log.info(f"\n{approach} / {cat}:")
            total_bkg = 0.0
            total_sig = 0.0
            for proc, data in templates[approach][cat]["processes"].items():
                log.info(f"  {proc:8s}: yield={data['yield']:10.1f}  raw={data['raw_events']:6d}")
                if proc in ("ggH", "VBF"):
                    total_sig += data["yield"]
                else:
                    total_bkg += data["yield"]
            log.info(f"  {'Signal':8s}: {total_sig:10.1f}")
            log.info(f"  {'Bkg':8s}: {total_bkg:10.1f}")
            if total_bkg > 0:
                log.info(f"  S/sqrt(B) = {total_sig / np.sqrt(total_bkg):.3f}")

    # Save templates
    with open(OUT / "nominal_templates.json", "w") as f:
        json.dump(templates, f, indent=2)
    log.info(f"\nSaved nominal templates to {OUT / 'nominal_templates.json'}")


if __name__ == "__main__":
    main()
