"""
Phase 3 Step 3: Collinear mass implementation.

Implements the collinear approximation for di-tau mass reconstruction.
Reports physical solution fractions per process and category.
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

import numpy as np

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"

SAMPLES = [
    "GluGluToHToTauTau", "VBF_HToTauTau",
    "DYJetsToLL", "TTbar",
    "W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu",
    "Run2012B_TauPlusX", "Run2012C_TauPlusX",
]


def compute_collinear_mass(mu_pt, mu_eta, mu_phi, mu_mass,
                            tau_pt, tau_eta, tau_phi, tau_mass,
                            met_pt, met_phi):
    """Compute collinear mass.

    The collinear approximation assumes neutrinos from tau decays are
    collinear with their parent taus. This allows reconstruction of the
    full di-tau invariant mass.

    x_mu = p_mu / p_tau1_gen: momentum fraction carried by the muon
    x_tau = p_tau_h / p_tau2_gen: momentum fraction carried by the tau_h

    MET is decomposed along the mu and tau_h directions to solve for
    the neutrino momenta.

    Returns: m_col, x_mu, x_tau, is_physical
    """
    n = len(mu_pt)

    # Unit vectors in transverse plane for mu and tau
    mu_ux = np.cos(mu_phi)
    mu_uy = np.sin(mu_phi)
    tau_ux = np.cos(tau_phi)
    tau_uy = np.sin(tau_phi)

    # MET components
    met_x = met_pt * np.cos(met_phi)
    met_y = met_pt * np.sin(met_phi)

    # Solve: MET = nu_mu + nu_tau (collinear with mu and tau respectively)
    # MET_x = p_nu_mu * cos(phi_mu) + p_nu_tau * cos(phi_tau)
    # MET_y = p_nu_mu * sin(phi_mu) + p_nu_tau * sin(phi_tau)
    # This is: [cos(phi_mu), cos(phi_tau)] [p_nu_mu]   [MET_x]
    #          [sin(phi_mu), sin(phi_tau)] [p_nu_tau] = [MET_y]

    det = mu_ux * tau_uy - mu_uy * tau_ux
    # Avoid division by zero for parallel mu and tau
    safe_det = np.where(np.abs(det) > 1e-10, det, 1e-10)

    p_nu_mu = (met_x * tau_uy - met_y * tau_ux) / safe_det
    p_nu_tau = (mu_ux * met_y - mu_uy * met_x) / safe_det

    # Momentum fractions
    x_mu = mu_pt / (mu_pt + p_nu_mu)
    x_tau = tau_pt / (tau_pt + p_nu_tau)

    # Physical solutions: 0 < x < 1 for both
    is_physical = (x_mu > 0) & (x_mu < 1) & (x_tau > 0) & (x_tau < 1) & (np.abs(det) > 1e-10)

    # Visible mass
    mvis = compute_mvis_fast(mu_pt, mu_eta, mu_phi, mu_mass,
                              tau_pt, tau_eta, tau_phi, tau_mass)

    # Collinear mass: m_col = m_vis / sqrt(x_mu * x_tau)
    x_prod = x_mu * x_tau
    safe_x = np.where(is_physical & (x_prod > 0), x_prod, 1.0)
    m_col = np.where(is_physical, mvis / np.sqrt(safe_x), mvis)

    return m_col, x_mu, x_tau, is_physical


def compute_mvis_fast(mu_pt, mu_eta, mu_phi, mu_mass, tau_pt, tau_eta, tau_phi, tau_mass):
    """Fast visible mass computation."""
    mu_px = mu_pt * np.cos(mu_phi)
    mu_py = mu_pt * np.sin(mu_phi)
    mu_pz = mu_pt * np.sinh(mu_eta)
    mu_e = np.sqrt(mu_px**2 + mu_py**2 + mu_pz**2 + mu_mass**2)
    tau_px = tau_pt * np.cos(tau_phi)
    tau_py = tau_pt * np.sin(tau_phi)
    tau_pz = tau_pt * np.sinh(tau_eta)
    tau_e = np.sqrt(tau_px**2 + tau_py**2 + tau_pz**2 + tau_mass**2)
    m2 = (mu_e + tau_e)**2 - (mu_px + tau_px)**2 - (mu_py + tau_py)**2 - (mu_pz + tau_pz)**2
    return np.sqrt(np.maximum(m2, 0.0))


def main():
    log.info("=" * 60)
    log.info("Phase 3 Step 3: Collinear Mass Implementation")
    log.info("=" * 60)

    results = {}

    for sample in SAMPLES:
        path = OUTPUT_DIR / f"p3_{sample}_os_sr.npz"
        if not path.exists():
            log.info("Skipping %s (no data)", sample)
            continue

        d = dict(np.load(path, allow_pickle=True))
        if len(d["mu_pt"]) == 0:
            continue

        m_col, x_mu, x_tau, is_phys = compute_collinear_mass(
            d["mu_pt"], d["mu_eta"], d["mu_phi"], d["mu_mass"],
            d["tau_pt"], d["tau_eta"], d["tau_phi"], d["tau_mass"],
            d["met_pt"], d["met_phi"]
        )

        n_total = len(m_col)
        n_phys = int(np.sum(is_phys))
        frac_unphys = 1.0 - n_phys / n_total if n_total > 0 else 0

        results[sample] = {
            "n_total": n_total,
            "n_physical": n_phys,
            "frac_unphysical": frac_unphys,
            "m_col_mean_physical": float(np.mean(m_col[is_phys])) if n_phys > 0 else 0,
            "m_col_std_physical": float(np.std(m_col[is_phys])) if n_phys > 0 else 0,
        }

        log.info("%-25s: %d total, %d physical (%.1f%% unphysical), "
                 "mean m_col = %.1f GeV",
                 sample, n_total, n_phys, frac_unphys * 100,
                 results[sample]["m_col_mean_physical"])

        # Save collinear mass to npz
        np.savez_compressed(
            OUTPUT_DIR / f"p3_{sample}_os_sr_collinear.npz",
            m_col=m_col,
            x_mu=x_mu,
            x_tau=x_tau,
            is_physical=is_phys,
        )

    # VBF category breakdown
    log.info("\n--- VBF Category Breakdown ---")
    for sample in SAMPLES:
        path_sr = OUTPUT_DIR / f"p3_{sample}_os_sr.npz"
        path_col = OUTPUT_DIR / f"p3_{sample}_os_sr_collinear.npz"
        if not path_sr.exists() or not path_col.exists():
            continue
        d = dict(np.load(path_sr, allow_pickle=True))
        col = dict(np.load(path_col, allow_pickle=True))
        if len(d["mu_pt"]) == 0:
            continue

        vbf_mask = (d["njets"] >= 2) & (d["mjj"] > 200) & (np.abs(d["deta_jj"]) > 2.0)
        baseline_mask = ~vbf_mask

        for cat_name, cat_mask in [("Baseline", baseline_mask), ("VBF", vbf_mask)]:
            n_total = int(np.sum(cat_mask))
            if n_total == 0:
                continue
            n_phys = int(np.sum(col["is_physical"][cat_mask]))
            log.info("  %-25s %8s: %d total, %d physical (%.1f%% unphysical)",
                     sample, cat_name, n_total, n_phys,
                     (1.0 - n_phys / n_total) * 100)

    # Save summary
    with open(OUTPUT_DIR / "collinear_mass_results.json", "w") as f:
        json.dump(results, f, indent=2)
    log.info("\nResults saved to collinear_mass_results.json")


if __name__ == "__main__":
    main()
