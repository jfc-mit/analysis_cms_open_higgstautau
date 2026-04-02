"""
Phase 3 Fix: Compute NN scores and collinear mass for SS SR events.

Addresses review findings A3 (QCD missing from NN score plots) and
B2 (collinear mass QCD template using m_vis proxy).
"""
import logging
import pickle
from pathlib import Path

from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

import numpy as np

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"

FEATURES = [
    "mu_pt", "mu_eta", "tau_pt", "tau_eta", "met_pt", "met_significance",
    "mvis", "mt", "delta_r", "delta_phi_mutau",
    "njets", "lead_jet_pt", "lead_jet_eta", "nbjets",
]

ALL_SAMPLES = [
    "GluGluToHToTauTau", "VBF_HToTauTau",
    "DYJetsToLL", "TTbar",
    "W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu",
    "Run2012B_TauPlusX", "Run2012C_TauPlusX",
]


def compute_collinear_mass(mu_pt, mu_eta, mu_phi, mu_mass,
                            tau_pt, tau_eta, tau_phi, tau_mass,
                            met_pt, met_phi):
    """Compute collinear mass (copied from 03_collinear_mass.py)."""
    mu_ux = np.cos(mu_phi)
    mu_uy = np.sin(mu_phi)
    tau_ux = np.cos(tau_phi)
    tau_uy = np.sin(tau_phi)

    met_x = met_pt * np.cos(met_phi)
    met_y = met_pt * np.sin(met_phi)

    det = mu_ux * tau_uy - mu_uy * tau_ux
    safe_det = np.where(np.abs(det) > 1e-10, det, 1e-10)

    p_nu_mu = (met_x * tau_uy - met_y * tau_ux) / safe_det
    p_nu_tau = (mu_ux * met_y - mu_uy * met_x) / safe_det

    x_mu = mu_pt / (mu_pt + p_nu_mu)
    x_tau = tau_pt / (tau_pt + p_nu_tau)

    is_physical = (x_mu > 0) & (x_mu < 1) & (x_tau > 0) & (x_tau < 1) & (np.abs(det) > 1e-10)

    # Visible mass
    mu_px = mu_pt * np.cos(mu_phi)
    mu_py = mu_pt * np.sin(mu_phi)
    mu_pz = mu_pt * np.sinh(mu_eta)
    mu_e = np.sqrt(mu_px**2 + mu_py**2 + mu_pz**2 + mu_mass**2)
    tau_px = tau_pt * np.cos(tau_phi)
    tau_py = tau_pt * np.sin(tau_phi)
    tau_pz = tau_pt * np.sinh(tau_eta)
    tau_e = np.sqrt(tau_px**2 + tau_py**2 + tau_pz**2 + tau_mass**2)
    m2 = (mu_e + tau_e)**2 - (mu_px + tau_px)**2 - (mu_py + tau_py)**2 - (mu_pz + tau_pz)**2
    mvis = np.sqrt(np.maximum(m2, 0.0))

    x_prod = x_mu * x_tau
    safe_x = np.where(is_physical & (x_prod > 0), x_prod, 1.0)
    m_col = np.where(is_physical, mvis / np.sqrt(safe_x), mvis)

    return m_col, x_mu, x_tau, is_physical


def main():
    log.info("=" * 60)
    log.info("Fix: Computing NN scores and collinear mass for SS SR events")
    log.info("=" * 60)

    # Load trained NN model
    model_path = OUTPUT_DIR / "nn_discriminant_model.pkl"
    if not model_path.exists():
        log.error("NN model not found at %s", model_path)
        return

    with open(model_path, "rb") as f:
        model_data = pickle.load(f)

    nn_model = model_data["model"]
    scaler = model_data["scaler"]
    log.info("Loaded NN model from %s", model_path)

    for sample in ALL_SAMPLES:
        ss_path = OUTPUT_DIR / f"p3_{sample}_ss_sr.npz"
        if not ss_path.exists():
            log.info("Skipping %s (no SS SR file)", sample)
            continue

        d = dict(np.load(ss_path, allow_pickle=True))
        n = len(d["mu_pt"])
        if n == 0:
            log.info("Skipping %s (empty)", sample)
            continue

        # --- NN scores ---
        features = np.column_stack([d[f] for f in FEATURES])
        features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)
        features_scaled = scaler.transform(features)
        scores = nn_model.predict_proba(features_scaled)[:, 1]

        out_nn = OUTPUT_DIR / f"p3_{sample}_ss_sr_nn_score.npz"
        np.savez_compressed(out_nn, nn_score=scores)
        log.info("  %s SS SR NN scores: %d events, mean=%.3f", sample, n, float(np.mean(scores)))

        # --- Collinear mass ---
        m_col, x_mu, x_tau, is_phys = compute_collinear_mass(
            d["mu_pt"], d["mu_eta"], d["mu_phi"], d["mu_mass"],
            d["tau_pt"], d["tau_eta"], d["tau_phi"], d["tau_mass"],
            d["met_pt"], d["met_phi"]
        )

        out_col = OUTPUT_DIR / f"p3_{sample}_ss_sr_collinear.npz"
        np.savez_compressed(out_col, m_col=m_col, x_mu=x_mu, x_tau=x_tau, is_physical=is_phys)
        n_phys = int(np.sum(is_phys))
        log.info("  %s SS SR collinear: %d total, %d physical (%.1f%% unphys)",
                 sample, n, n_phys, (1 - n_phys / n) * 100)

    log.info("\nDone. SS SR NN score and collinear mass files saved.")


if __name__ == "__main__":
    main()
