"""
Phase 4a Step 2: Build shape systematic templates.

For each shape systematic (TES, MES, JES, MET unclustered), shifts the
relevant kinematic quantity, recomputes all derived observables (m_vis,
m_col, MET, NN score), and rebuilds templates.

Key: JES variations cause category migration (Baseline <-> VBF).
"""
import logging
import json
import pickle
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

# ---------- configuration ----------
VBF_MJJ_CUT = 200.0
VBF_DETA_CUT = 2.0

BINNING = {
    "mvis": {"bins": 25, "lo": 0.0, "hi": 250.0},
    "nn_score": {"bins": 20, "lo": 0.0, "hi": 1.0},
    "mcol": {"bins": 25, "lo": 0.0, "hi": 300.0},
}

with open(P3 / "background_estimation.json") as f:
    bkg_est = json.load(f)
R_OSSS = bkg_est["r_osss"]
SF_W = bkg_est["sf_w"]

MC_SAMPLES = {
    "ggH": "GluGluToHToTauTau",
    "VBF_sig": "VBF_HToTauTau",
    "DY": "DYJetsToLL",
    "TTbar": "TTbar",
    "W1J": "W1JetsToLNu",
    "W2J": "W2JetsToLNu",
    "W3J": "W3JetsToLNu",
}
DATA_SAMPLES = ["Run2012B_TauPlusX", "Run2012C_TauPlusX"]

# Load NN model
log.info("Loading NN model...")
with open(P3 / "nn_discriminant_model.pkl", "rb") as f:
    nn_data = pickle.load(f)
NN_MODEL = nn_data["model"]
NN_SCALER = nn_data["scaler"]
NN_FEATURES = nn_data["features"]
log.info(f"NN features: {NN_FEATURES}")

# Shape systematics definitions
SHAPE_SYSTS = {
    "tes": {
        "label": "Tau energy scale",
        "variation": 0.03,  # +-3%
        "affects": "tau_pt",
    },
    "mes": {
        "label": "Muon energy scale",
        "variation": 0.01,  # +-1%
        "affects": "mu_pt",
    },
    "jes": {
        "label": "Jet energy scale",
        "variation": 0.03,  # +-3%
        "affects": "jet_pt",
    },
    "met_uncl": {
        "label": "MET unclustered energy",
        "variation": 0.10,  # +-10%
        "affects": "met",
    },
}


def load_arrays(sample_tag, region="os_sr"):
    """Load arrays for a sample."""
    d = np.load(P3 / f"p3_{sample_tag}_{region}.npz", allow_pickle=True)
    return {k: d[k].copy() for k in d.keys()}


def compute_mvis(mu_pt, mu_eta, mu_phi, mu_mass, tau_pt, tau_eta, tau_phi, tau_mass):
    """Compute visible di-tau mass."""
    # Use 4-vector addition
    mu_px = mu_pt * np.cos(mu_phi)
    mu_py = mu_pt * np.sin(mu_phi)
    mu_pz = mu_pt * np.sinh(mu_eta)
    mu_e = np.sqrt(mu_px**2 + mu_py**2 + mu_pz**2 + mu_mass**2)

    tau_px = tau_pt * np.cos(tau_phi)
    tau_py = tau_pt * np.sin(tau_phi)
    tau_pz = tau_pt * np.sinh(tau_eta)
    tau_e = np.sqrt(tau_px**2 + tau_py**2 + tau_pz**2 + tau_mass**2)

    m2 = (mu_e + tau_e) ** 2 - (mu_px + tau_px) ** 2 - (mu_py + tau_py) ** 2 - (mu_pz + tau_pz) ** 2
    return np.sqrt(np.maximum(m2, 0.0))


def compute_mt(mu_pt, mu_phi, met_pt, met_phi):
    """Compute transverse mass."""
    dphi = mu_phi - met_phi
    return np.sqrt(2.0 * mu_pt * met_pt * (1.0 - np.cos(dphi)))


def compute_collinear_mass(mu_pt, mu_eta, mu_phi, mu_mass, tau_pt, tau_eta, tau_phi, tau_mass, met_pt, met_phi):
    """Compute collinear approximation mass."""
    mvis = compute_mvis(mu_pt, mu_eta, mu_phi, mu_mass, tau_pt, tau_eta, tau_phi, tau_mass)

    # MET decomposition
    met_px = met_pt * np.cos(met_phi)
    met_py = met_pt * np.sin(met_phi)

    mu_px = mu_pt * np.cos(mu_phi)
    mu_py = mu_pt * np.sin(mu_phi)
    tau_px = tau_pt * np.cos(tau_phi)
    tau_py = tau_pt * np.sin(tau_phi)

    # Solve for neutrino fractions
    # Using the collinear approximation: neutrinos parallel to visible leptons
    det = mu_px * tau_py - mu_py * tau_px
    # Avoid division by zero
    safe_det = np.where(np.abs(det) < 1e-10, 1e-10, det)

    nu_mu_pt = (met_px * tau_py - met_py * tau_px) / safe_det * mu_pt
    nu_tau_pt = (mu_px * met_py - mu_py * met_px) / safe_det * tau_pt

    x_mu = mu_pt / (mu_pt + np.abs(nu_mu_pt))
    x_tau = tau_pt / (tau_pt + np.abs(nu_tau_pt))

    # Physical solutions: 0 < x < 1
    is_physical = (nu_mu_pt >= 0) & (nu_tau_pt >= 0) & (x_mu > 0) & (x_mu < 1) & (x_tau > 0) & (x_tau < 1)

    m_col = np.where(is_physical, mvis / np.sqrt(np.maximum(x_mu * x_tau, 1e-10)), mvis)
    # Cap at range
    m_col = np.clip(m_col, 0, 5000)

    return m_col


def compute_nn_score(arrays):
    """Compute NN scores from kinematic arrays."""
    # Build feature matrix in the same order as training
    feature_map = {
        "mu_pt": arrays["mu_pt"],
        "mu_eta": arrays["mu_eta"],
        "tau_pt": arrays["tau_pt"],
        "tau_eta": arrays["tau_eta"],
        "met_pt": arrays["met_pt"],
        "met_significance": arrays["met_significance"],
        "mvis": arrays["mvis"],
        "mt": arrays["mt"],
        "delta_r": arrays["delta_r"],
        "delta_phi_mutau": arrays["delta_phi_mutau"],
        "njets": arrays["njets"],
        "lead_jet_pt": arrays["lead_jet_pt"],
        "lead_jet_eta": arrays["lead_jet_eta"],
        "nbjets": arrays["nbjets"],
    }
    X = np.column_stack([feature_map[f].astype(np.float64) for f in NN_FEATURES])
    X_scaled = NN_SCALER.transform(X)
    proba = NN_MODEL.predict_proba(X_scaled)[:, 1]
    return proba


def apply_shift(arrays, syst_name, direction):
    """Apply a systematic shift and return modified arrays.

    direction: +1 for up, -1 for down
    """
    arr = {k: v.copy() for k, v in arrays.items()}
    syst = SHAPE_SYSTS[syst_name]
    scale = 1.0 + direction * syst["variation"]

    if syst_name == "tes":
        # Shift tau_pt, propagate to MET
        old_tau_pt = arr["tau_pt"].copy()
        arr["tau_pt"] = arr["tau_pt"] * scale
        # MET correction: MET_px -= (new_tau_px - old_tau_px), same for py
        delta_tau_px = (arr["tau_pt"] - old_tau_pt) * np.cos(arr["tau_phi"])
        delta_tau_py = (arr["tau_pt"] - old_tau_pt) * np.sin(arr["tau_phi"])
        met_px = arr["met_pt"] * np.cos(arr["met_phi"]) - delta_tau_px
        met_py = arr["met_pt"] * np.sin(arr["met_phi"]) - delta_tau_py
        arr["met_pt"] = np.sqrt(met_px**2 + met_py**2).astype(np.float32)
        arr["met_phi"] = np.arctan2(met_py, met_px).astype(np.float32)

    elif syst_name == "mes":
        # Shift mu_pt, propagate to MET
        old_mu_pt = arr["mu_pt"].copy()
        arr["mu_pt"] = arr["mu_pt"] * scale
        delta_mu_px = (arr["mu_pt"] - old_mu_pt) * np.cos(arr["mu_phi"])
        delta_mu_py = (arr["mu_pt"] - old_mu_pt) * np.sin(arr["mu_phi"])
        met_px = arr["met_pt"] * np.cos(arr["met_phi"]) - delta_mu_px
        met_py = arr["met_pt"] * np.sin(arr["met_phi"]) - delta_mu_py
        arr["met_pt"] = np.sqrt(met_px**2 + met_py**2).astype(np.float32)
        arr["met_phi"] = np.arctan2(met_py, met_px).astype(np.float32)

    elif syst_name == "jes":
        # Shift all jet pT, recompute mjj for VBF categorization.
        # JES does NOT propagate to MET because jet phi is not stored
        # in Phase 3 arrays. The vector subtraction
        #   MET_px -= (jet_pt_shifted - jet_pt_nom) * cos(jet_phi)
        # requires jet_phi per jet, which is unavailable.
        # JES therefore affects ONLY jet-based quantities: lead/sublead
        # jet pT, mjj, and VBF category migration. This is documented
        # as a limitation in the artifact.
        # [FIX F2: removed hardcoded 0.5/0.3 MET propagation factors]
        has_lead = arr["lead_jet_pt"] > 0
        has_sublead = arr["sublead_jet_pt"] > 0

        # Scale jet pTs
        arr["lead_jet_pt"] = np.where(has_lead, arr["lead_jet_pt"] * scale, arr["lead_jet_pt"])
        arr["sublead_jet_pt"] = np.where(has_sublead, arr["sublead_jet_pt"] * scale, arr["sublead_jet_pt"])

        # Recompute mjj for VBF categorization
        # mjj = 2 * pt1 * pt2 * (cosh(deta) - cos(dphi))
        # Since we don't have jet phis, scale mjj approximately
        # mjj scales as pt1 * pt2, so mjj_new = mjj_old * scale^2
        has_mjj = arr["mjj"] > 0
        arr["mjj"] = np.where(has_mjj, arr["mjj"] * scale ** 2, arr["mjj"])

        # MET is NOT modified by JES (jet phi unavailable; see comment above)

    elif syst_name == "met_uncl":
        # Shift ONLY the unclustered energy component of MET.
        # [FIX F3: previous code scaled total MET, double-counting
        #  TES/MES/JES contributions. Now we subtract clustered objects
        #  before scaling.]
        # MET = -(sum of all visible objects). Decompose into:
        #   MET_total = MET_clustered + MET_unclustered
        # where clustered = jets + muon + tau.
        # Scale only the unclustered residual by +-10%.

        met_px = arr["met_pt"] * np.cos(arr["met_phi"])
        met_py = arr["met_pt"] * np.sin(arr["met_phi"])

        # Clustered contributions: muon + tau + jets
        mu_px = arr["mu_pt"] * np.cos(arr["mu_phi"])
        mu_py = arr["mu_pt"] * np.sin(arr["mu_phi"])
        tau_px = arr["tau_pt"] * np.cos(arr["tau_phi"])
        tau_py = arr["tau_pt"] * np.sin(arr["tau_phi"])

        # Jets: use lead and sublead (best available; higher-order jets
        # are subdominant). Jet phi is not stored, so we approximate
        # jet contributions using lead_jet_eta as a proxy for the
        # direction. However, since we only need the *magnitude* of
        # the clustered jet contribution to MET, and we cannot
        # reconstruct the vector, we use a conservative approach:
        # estimate the jet px/py contribution as zero (jets contribute
        # to MET via their vector sum, which can be in any direction).
        # This means the unclustered component is:
        #   MET_uncl = MET_total + muon + tau  (adding back the lepton
        #   contributions that are part of the "clustered" set)
        # Note: the sign convention is MET = -sum(visible), so the
        # clustered lepton contribution to MET is -(mu + tau).
        # Therefore: MET_uncl = MET_total - (-(mu + tau)) = MET + mu + tau

        clustered_px = mu_px + tau_px
        clustered_py = mu_py + tau_py

        # Unclustered = total MET + clustered leptons
        # (because MET = -clustered - unclustered, so unclustered = -MET - clustered,
        #  but we want the vector to scale, so: MET_uncl_px = met_px + clustered_px)
        # Equivalently: MET_total = -clustered - unclustered
        #   => unclustered_px = -(met_px + clustered_px)
        # After scaling: unclustered_new = unclustered * scale
        #   => met_new = -clustered - unclustered_new
        #              = -clustered - unclustered * scale
        #              = met_old + unclustered * (1 - scale)
        #              = met_old - (met_px + clustered_px) * (scale - 1)
        # Wait, let's be precise:
        # met_px = -(clustered_px + uncl_px)
        # uncl_px = -(met_px + clustered_px)
        # After scaling uncl by `scale`:
        # met_new_px = -(clustered_px + scale * uncl_px)
        #            = -(clustered_px + scale * (-(met_px + clustered_px)))
        #            = -clustered_px + scale * met_px + scale * clustered_px
        #            = (scale - 1) * clustered_px + scale * met_px
        #            = met_px + (scale - 1) * (met_px + clustered_px)

        met_px_new = met_px + (scale - 1.0) * (met_px + clustered_px)
        met_py_new = met_py + (scale - 1.0) * (met_py + clustered_py)

        arr["met_pt"] = np.sqrt(met_px_new**2 + met_py_new**2).astype(np.float32)
        arr["met_phi"] = np.arctan2(met_py_new, met_px_new).astype(np.float32)

    # Recompute derived quantities
    arr["mvis"] = compute_mvis(
        arr["mu_pt"], arr["mu_eta"], arr["mu_phi"], arr["mu_mass"],
        arr["tau_pt"], arr["tau_eta"], arr["tau_phi"], arr["tau_mass"],
    )
    arr["mt"] = compute_mt(arr["mu_pt"], arr["mu_phi"], arr["met_pt"], arr["met_phi"])
    arr["delta_r"] = np.sqrt(
        (arr["mu_eta"] - arr["tau_eta"]) ** 2
        + np.minimum(np.abs(arr["mu_phi"] - arr["tau_phi"]), 2 * np.pi - np.abs(arr["mu_phi"] - arr["tau_phi"])) ** 2
    )

    return arr


def categorize(arrays):
    """Categorize events into Baseline/VBF."""
    njets = arrays["njets"]
    mjj = arrays["mjj"]
    deta = arrays["deta_jj"]
    is_vbf = (njets >= 2) & (mjj > VBF_MJJ_CUT) & (np.abs(deta) > VBF_DETA_CUT)
    return ~is_vbf, is_vbf


def build_histogram(values, weights, binning_key):
    """Build histogram."""
    b = BINNING[binning_key]
    h, edges = np.histogram(values, bins=b["bins"], range=(b["lo"], b["hi"]), weights=weights)
    return h.astype(np.float64), edges


def build_shifted_templates_mc(sample_tag, proc_name, syst_name, direction, region="os_sr"):
    """Build shifted templates for one MC sample, one systematic, one direction."""
    arr = load_arrays(sample_tag, region)
    weights = arr["weight"].astype(np.float64)
    if sample_tag in ("W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu") and region == "os_sr":
        weights = weights * SF_W
    if sample_tag in ("W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu") and region == "ss_sr":
        weights = weights * SF_W

    # Apply shift
    arr_shifted = apply_shift(arr, syst_name, direction)

    # Compute observables
    mvis = arr_shifted["mvis"]
    mcol = compute_collinear_mass(
        arr_shifted["mu_pt"], arr_shifted["mu_eta"], arr_shifted["mu_phi"], arr_shifted["mu_mass"],
        arr_shifted["tau_pt"], arr_shifted["tau_eta"], arr_shifted["tau_phi"], arr_shifted["tau_mass"],
        arr_shifted["met_pt"], arr_shifted["met_phi"],
    )
    nn_score = compute_nn_score(arr_shifted)

    # Categorize (with shifted jet properties for JES)
    is_bl, is_vbf = categorize(arr_shifted)

    result = {}
    for cat_name, cat_mask in [("baseline", is_bl), ("vbf", is_vbf)]:
        # DY decomposition
        if proc_name == "DY" and "is_ztt" in arr:
            is_ztt = arr["is_ztt"].astype(bool)
            for sub_name, sub_mask in [("ZTT", is_ztt), ("ZLL", ~is_ztt)]:
                combined_mask = cat_mask & sub_mask
                result_key = f"{sub_name}_{cat_name}"
                result[result_key] = {
                    "mvis": build_histogram(mvis[combined_mask], weights[combined_mask], "mvis")[0],
                    "nn_score": build_histogram(nn_score[combined_mask], weights[combined_mask], "nn_score")[0],
                    "mcol": build_histogram(mcol[combined_mask], weights[combined_mask], "mcol")[0],
                }
        else:
            result_key = f"{proc_name}_{cat_name}"
            result[result_key] = {
                "mvis": build_histogram(mvis[cat_mask], weights[cat_mask], "mvis")[0],
                "nn_score": build_histogram(nn_score[cat_mask], weights[cat_mask], "nn_score")[0],
                "mcol": build_histogram(mcol[cat_mask], weights[cat_mask], "mcol")[0],
            }

    return result


def main():
    log.info("Building shape systematic templates")

    # Load nominal templates for comparison
    with open(OUT / "nominal_templates.json") as f:
        nominal = json.load(f)

    shape_syst_templates = {}

    for syst_name in SHAPE_SYSTS:
        log.info(f"\n=== Systematic: {syst_name} ({SHAPE_SYSTS[syst_name]['label']}) ===")
        shape_syst_templates[syst_name] = {"up": {}, "down": {}}

        for direction, dir_name in [(+1, "up"), (-1, "down")]:
            log.info(f"  Direction: {dir_name}")

            # Initialize accumulators for combined processes
            combined = {}
            for approach in ["mvis", "nn_score", "mcol"]:
                for cat in ["baseline", "vbf"]:
                    combined[f"Wjets_{cat}_{approach}"] = None

            # Process each MC sample
            for proc_name, sample_tag in MC_SAMPLES.items():
                if proc_name in ("W1J", "W2J", "W3J"):
                    # W+jets combined below
                    pass
                else:
                    result = build_shifted_templates_mc(
                        sample_tag, proc_name, syst_name, direction
                    )
                    for key, hists in result.items():
                        for approach, h in hists.items():
                            full_key = f"{key}_{approach}"
                            shape_syst_templates[syst_name][dir_name][full_key] = h.tolist()

            # W+jets combined
            for wj_tag in ["W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu"]:
                result = build_shifted_templates_mc(wj_tag, "Wjets_part", syst_name, direction)
                # The result has keys like "Wjets_part_baseline" and "Wjets_part_vbf"
                for key, hists in result.items():
                    # Replace "Wjets_part" with "Wjets"
                    cat = key.replace("Wjets_part_", "")
                    for approach, h in hists.items():
                        comb_key = f"Wjets_{cat}_{approach}"
                        if combined[comb_key] is None:
                            combined[comb_key] = h.copy()
                        else:
                            combined[comb_key] += h

            for comb_key, h in combined.items():
                if h is not None:
                    shape_syst_templates[syst_name][dir_name][comb_key] = h.tolist()

            # QCD: build shifted QCD from shifted SS data minus shifted SS MC
            log.info(f"  Building QCD template with {syst_name} {dir_name} shift")
            # For data SS, we don't apply MC-level shifts to data
            # But the SS MC subtraction changes under systematic shifts
            # For QCD estimation: QCD = (Data_SS - MC_SS) * R_OS/SS
            # Under systematic shifts, the MC templates in SS change
            # Data stays the same (data doesn't have TES/MES/JES shifts)

            for approach in ["mvis", "nn_score", "mcol"]:
                for cat in ["baseline", "vbf"]:
                    # Data SS (unshifted)
                    h_data_ss = None
                    for data_tag in DATA_SAMPLES:
                        arr_ss = load_arrays(data_tag, "ss_sr")
                        w_ss = arr_ss["weight"].astype(np.float64)
                        if approach == "mvis":
                            obs = arr_ss["mvis"]
                        elif approach == "nn_score":
                            nn_ss = np.load(P3 / f"p3_{data_tag}_ss_sr_nn_score.npz")["nn_score"]
                            obs = nn_ss
                        else:
                            obs = np.load(P3 / f"p3_{data_tag}_ss_sr_collinear.npz")["m_col"]

                        is_bl, is_vbf = categorize(arr_ss)
                        cm = is_bl if cat == "baseline" else is_vbf
                        h, _ = build_histogram(obs[cm], w_ss[cm], approach)
                        h_data_ss = h if h_data_ss is None else h_data_ss + h

                    # MC SS (shifted)
                    h_mc_ss = None
                    for mc_name, mc_tag in MC_SAMPLES.items():
                        arr_ss = load_arrays(mc_tag, "ss_sr")
                        w_ss = arr_ss["weight"].astype(np.float64)
                        if mc_tag in ("W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu"):
                            w_ss = w_ss * SF_W

                        # Apply shift to MC SS
                        arr_shifted = apply_shift(arr_ss, syst_name, direction)

                        if approach == "mvis":
                            obs = arr_shifted["mvis"]
                        elif approach == "nn_score":
                            obs = compute_nn_score(arr_shifted)
                        else:
                            obs = compute_collinear_mass(
                                arr_shifted["mu_pt"], arr_shifted["mu_eta"], arr_shifted["mu_phi"], arr_shifted["mu_mass"],
                                arr_shifted["tau_pt"], arr_shifted["tau_eta"], arr_shifted["tau_phi"], arr_shifted["tau_mass"],
                                arr_shifted["met_pt"], arr_shifted["met_phi"],
                            )

                        is_bl, is_vbf = categorize(arr_shifted)
                        cm = is_bl if cat == "baseline" else is_vbf
                        h, _ = build_histogram(obs[cm], w_ss[cm], approach)
                        h_mc_ss = h if h_mc_ss is None else h_mc_ss + h

                    h_qcd = (h_data_ss - h_mc_ss) * R_OSSS
                    h_qcd[h_qcd < 0] = 0.0
                    shape_syst_templates[syst_name][dir_name][f"QCD_{cat}_{approach}"] = h_qcd.tolist()

    # ------------------------------------------------------------------
    # [FIX F4] Template smoothing: smooth shape systematic ratios to
    # suppress MC statistical noise in low-stats signal processes.
    # For each systematic, process, and category, compute the ratio
    # shifted/nominal, apply a 3-bin moving average, then multiply
    # the smoothed ratio by the nominal template.
    # ------------------------------------------------------------------
    log.info("\n=== Applying template smoothing (F4 fix) ===")
    for syst_name in SHAPE_SYSTS:
        for dir_name in ["up", "down"]:
            for approach in ["mvis", "nn_score", "mcol"]:
                for cat in ["baseline", "vbf"]:
                    for proc_key_suffix in ["ggH", "VBF_sig", "ZTT", "ZLL", "TTbar", "Wjets", "QCD"]:
                        key = f"{proc_key_suffix}_{cat}_{approach}"
                        if key not in shape_syst_templates[syst_name][dir_name]:
                            continue

                        h_shifted = np.array(shape_syst_templates[syst_name][dir_name][key])
                        # Look up the nominal process name
                        nom_proc = proc_key_suffix.replace("VBF_sig", "VBF")
                        h_nom = np.array(
                            nominal[approach][cat]["processes"].get(nom_proc, {}).get("nominal", [])
                        )
                        if len(h_nom) == 0 or h_nom.sum() == 0:
                            continue

                        # Compute ratio, protecting against zero-division
                        with np.errstate(divide="ignore", invalid="ignore"):
                            ratio = np.where(h_nom > 1e-10, h_shifted / h_nom, 1.0)

                        # Moving average smoothing (window=3, edge-aware)
                        smoothed_ratio = np.copy(ratio)
                        n = len(ratio)
                        for i in range(n):
                            lo = max(0, i - 1)
                            hi = min(n, i + 2)
                            smoothed_ratio[i] = np.mean(ratio[lo:hi])

                        # Reconstruct the smoothed template
                        h_smoothed = h_nom * smoothed_ratio
                        # Ensure non-negative
                        h_smoothed = np.maximum(h_smoothed, 0.0)
                        shape_syst_templates[syst_name][dir_name][key] = h_smoothed.tolist()

    log.info("Template smoothing applied to all shape systematics.")

    # Compute relative impacts and log summary
    log.info("\n=== Shape Systematic Impact Summary ===")
    for syst_name in SHAPE_SYSTS:
        log.info(f"\n{syst_name} ({SHAPE_SYSTS[syst_name]['label']}):")
        for approach in ["mvis", "nn_score", "mcol"]:
            for cat in ["baseline", "vbf"]:
                for proc in ["ggH", "VBF_sig", "ZTT", "ZLL", "TTbar", "Wjets", "QCD"]:
                    # Map proc name
                    nom_proc = proc.replace("VBF_sig", "VBF")
                    key = f"{proc}_{cat}_{approach}"
                    nom_key = nom_proc

                    if key in shape_syst_templates[syst_name]["up"]:
                        h_nom = np.array(nominal[approach][cat]["processes"].get(nom_proc, {}).get("nominal", []))
                        h_up = np.array(shape_syst_templates[syst_name]["up"][key])
                        h_down = np.array(shape_syst_templates[syst_name]["down"][key])

                        if len(h_nom) > 0 and h_nom.sum() > 0:
                            rel_up = (h_up.sum() - h_nom.sum()) / h_nom.sum() * 100
                            rel_down = (h_down.sum() - h_nom.sum()) / h_nom.sum() * 100
                            log.info(f"  {approach:10s} {cat:10s} {nom_proc:8s}: up={rel_up:+.2f}% down={rel_down:+.2f}%")

    # Save
    with open(OUT / "shape_systematic_templates.json", "w") as f:
        json.dump(shape_syst_templates, f)
    log.info(f"\nSaved shape systematic templates to {OUT / 'shape_systematic_templates.json'}")


if __name__ == "__main__":
    main()
