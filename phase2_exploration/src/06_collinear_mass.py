"""
Phase 2 Step 6: Collinear mass study.

Computes collinear mass approximation, measures unphysical solution fractions
per process [P2-8]. Produces data/MC comparison plots.
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

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep as mh

mh.style.use("CMS")

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"
FIG_DIR = OUTPUT_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

MC_SAMPLES = {
    "GluGluToHToTauTau": {"label": "ggH", "color": "#d62728"},
    "VBF_HToTauTau": {"label": "VBF", "color": "#ff7f0e"},
    "DYJetsToLL": {"label": "DY", "color": "#1f77b4"},
    "TTbar": {"label": r"$t\bar{t}$", "color": "#2ca02c"},
    "W1JetsToLNu": {"label": "W+1j", "color": "#9467bd"},
    "W2JetsToLNu": {"label": "W+2j", "color": "#8c564b"},
    "W3JetsToLNu": {"label": "W+3j", "color": "#e377c2"},
}

BKG_STACK_ORDER = ["DYJetsToLL", "W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu", "TTbar"]
DATA_SAMPLES = ["Run2012B_TauPlusX", "Run2012C_TauPlusX"]


def compute_collinear_mass(mu_pt, mu_eta, mu_phi, mu_mass,
                           tau_pt, tau_eta, tau_phi, tau_mass,
                           met_pt, met_phi):
    """
    Compute collinear approximation mass.

    Returns (m_col, x_mu, x_tau, is_physical) arrays.
    """
    # Muon direction (from leptonic tau decay)
    mu_px = mu_pt * np.cos(mu_phi)
    mu_py = mu_pt * np.sin(mu_phi)

    # Tau_h direction
    tau_px = tau_pt * np.cos(tau_phi)
    tau_py = tau_pt * np.sin(tau_phi)

    # MET components
    met_x = met_pt * np.cos(met_phi)
    met_y = met_pt * np.sin(met_phi)

    # Solve for neutrino momentum fractions along tau directions
    # MET = nu_mu + nu_tau
    # nu_mu is along muon direction, nu_tau along tau_h direction
    # MET_x = alpha * mu_px + beta * tau_px
    # MET_y = alpha * mu_py + beta * tau_py
    # where alpha = (1-x_mu)/x_mu * mu_pt, beta = (1-x_tau)/x_tau * tau_pt

    # Using the collinear approximation:
    # x_tau = fraction of original tau momentum carried by visible tau_h
    # x_mu  = fraction of original tau momentum carried by muon

    # Solve 2x2 system:
    # met_x = a * mu_ux + b * tau_ux  (unit vectors)
    # met_y = a * mu_uy + b * tau_uy
    # where a = p_nu_mu, b = p_nu_tau (neutrino momenta along parent directions)

    det = mu_px * tau_py - mu_py * tau_px

    # Handle zero determinant (parallel muon and tau)
    with np.errstate(divide="ignore", invalid="ignore"):
        a = (met_x * tau_py - met_y * tau_px) / det  # nu from mu-side tau
        b = (mu_px * met_y - mu_py * met_x) / det    # nu from tau_h-side tau

    # x_mu = mu_pt / (mu_pt + a), x_tau = tau_pt / (tau_pt + b)
    with np.errstate(divide="ignore", invalid="ignore"):
        x_mu = mu_pt / (mu_pt + a)
        x_tau = tau_pt / (tau_pt + b)

    # Physical solutions: 0 < x < 1
    is_physical = (x_mu > 0) & (x_mu < 1) & (x_tau > 0) & (x_tau < 1) & (np.abs(det) > 1e-6)

    # Compute collinear mass for physical solutions
    # m_col = m_vis / sqrt(x_mu * x_tau)
    mvis_sq = compute_mvis_sq(mu_pt, mu_eta, mu_phi, mu_mass,
                               tau_pt, tau_eta, tau_phi, tau_mass)

    with np.errstate(divide="ignore", invalid="ignore"):
        m_col = np.where(
            is_physical & (x_mu * x_tau > 0),
            np.sqrt(np.maximum(mvis_sq, 0)) / np.sqrt(x_mu * x_tau),
            np.sqrt(np.maximum(mvis_sq, 0))  # fallback to m_vis
        )

    return m_col, x_mu, x_tau, is_physical


def compute_mvis_sq(mu_pt, mu_eta, mu_phi, mu_mass,
                    tau_pt, tau_eta, tau_phi, tau_mass):
    """Compute visible di-tau invariant mass squared."""
    mu_px = mu_pt * np.cos(mu_phi)
    mu_py = mu_pt * np.sin(mu_phi)
    mu_pz = mu_pt * np.sinh(mu_eta)
    mu_e = np.sqrt(mu_px**2 + mu_py**2 + mu_pz**2 + mu_mass**2)

    tau_px = tau_pt * np.cos(tau_phi)
    tau_py = tau_pt * np.sin(tau_phi)
    tau_pz = tau_pt * np.sinh(tau_eta)
    tau_e = np.sqrt(tau_px**2 + tau_py**2 + tau_pz**2 + tau_mass**2)

    return ((mu_e + tau_e)**2 - (mu_px + tau_px)**2 -
            (mu_py + tau_py)**2 - (mu_pz + tau_pz)**2)


def load_sample(sample_name):
    """Load selected events from npz file."""
    npz_path = OUTPUT_DIR / f"selected_{sample_name}_loose.npz"
    if not npz_path.exists():
        log.warning("Missing: %s", npz_path)
        return None
    return dict(np.load(npz_path))


def main():
    log.info("=" * 60)
    log.info("Phase 2 Step 6: Collinear Mass Study")
    log.info("=" * 60)

    # Load all samples and compute collinear mass
    results = {}

    for sample_name in list(MC_SAMPLES.keys()) + DATA_SAMPLES:
        d = load_sample(sample_name)
        if d is None or len(d["mu_pt"]) == 0:
            continue

        m_col, x_mu, x_tau, is_physical = compute_collinear_mass(
            d["mu_pt"], d["mu_eta"], d["mu_phi"], d["mu_mass"],
            d["tau_pt"], d["tau_eta"], d["tau_phi"], d["tau_mass"],
            d["met_pt"], d["met_phi"]
        )

        n_total = len(m_col)
        n_physical = int(np.sum(is_physical))
        frac_unphysical = 1.0 - n_physical / n_total if n_total > 0 else 0

        results[sample_name] = {
            "m_col": m_col,
            "x_mu": x_mu,
            "x_tau": x_tau,
            "is_physical": is_physical,
            "weight": d["weight"],
            "n_total": n_total,
            "n_physical": n_physical,
            "frac_unphysical": frac_unphysical,
        }

    # Print unphysical solution fractions
    log.info("\n" + "=" * 60)
    log.info("UNPHYSICAL SOLUTION FRACTIONS")
    log.info("=" * 60)
    log.info("%-25s %8s %8s %10s", "Sample", "Total", "Physical", "Unphys %")
    for sample_name in list(MC_SAMPLES.keys()) + DATA_SAMPLES:
        if sample_name in results:
            r = results[sample_name]
            log.info("%-25s %8d %8d %10.1f%%",
                     sample_name, r["n_total"], r["n_physical"],
                     r["frac_unphysical"] * 100)

    # Plot collinear mass (all events, using m_vis for unphysical)
    bins = np.linspace(0, 300, 31)
    bin_centers = 0.5 * (bins[:-1] + bins[1:])

    fig, (ax_main, ax_ratio) = plt.subplots(
        2, 1, figsize=(10, 10), gridspec_kw={"height_ratios": [3, 1]},
        sharex=True
    )
    fig.subplots_adjust(hspace=0)

    bkg_hists = []
    bkg_labels = []
    bkg_colors = []
    total_bkg = np.zeros(len(bins) - 1)

    for sample in BKG_STACK_ORDER:
        if sample not in results:
            continue
        r = results[sample]
        h, _ = np.histogram(r["m_col"], bins=bins, weights=r["weight"])
        bkg_hists.append(h)
        bkg_labels.append(MC_SAMPLES[sample]["label"])
        bkg_colors.append(MC_SAMPLES[sample]["color"])
        total_bkg += h

    mh.histplot(bkg_hists, bins=bins, stack=True, histtype="fill",
                label=bkg_labels, color=bkg_colors, ax=ax_main)

    # Signal overlay x50
    for sample in ["GluGluToHToTauTau", "VBF_HToTauTau"]:
        if sample not in results:
            continue
        r = results[sample]
        h, _ = np.histogram(r["m_col"], bins=bins, weights=r["weight"])
        mh.histplot(h * 50, bins=bins, histtype="step",
                    label=f"{MC_SAMPLES[sample]['label']} x50",
                    color=MC_SAMPLES[sample]["color"], linewidth=2, ax=ax_main)

    # Data
    data_m_col = np.concatenate([results[s]["m_col"] for s in DATA_SAMPLES if s in results])
    h_data, _ = np.histogram(data_m_col, bins=bins)
    data_err = np.sqrt(h_data)
    ax_main.errorbar(bin_centers, h_data, yerr=data_err, fmt="ko",
                     markersize=4, label="Data", zorder=5)

    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(total_bkg > 0, h_data / total_bkg, 0)
        ratio_err = np.where(total_bkg > 0, data_err / total_bkg, 0)
    ax_ratio.errorbar(bin_centers, ratio, yerr=ratio_err, fmt="ko", markersize=4)
    ax_ratio.axhline(1.0, color="gray", linestyle="--", linewidth=1)
    ax_ratio.set_ylim(0.5, 1.5)

    ax_main.set_ylabel("Events / 10 GeV")
    ax_main.set_yscale("log")
    ax_main.set_ylim(bottom=0.1)
    ax_ratio.set_xlabel(r"$m_\mathrm{col}(\mu, \tau_h)$ [GeV]")
    ax_ratio.set_ylabel("Data/MC")
    ax_main.legend(fontsize="x-small", ncol=2)

    mh.label.exp_label(
        exp="CMS", data=True,
        llabel="Open Data",
        rlabel=r"$\sqrt{s} = 8$ TeV, 11.5 fb$^{-1}$",
        loc=0, ax=ax_main,
    )

    for ext in ["pdf", "png"]:
        fig.savefig(FIG_DIR / f"collinear_mass.{ext}",
                    bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info("Saved collinear_mass.pdf/png")

    # Plot physical-only collinear mass
    fig, (ax_main, ax_ratio) = plt.subplots(
        2, 1, figsize=(10, 10), gridspec_kw={"height_ratios": [3, 1]},
        sharex=True
    )
    fig.subplots_adjust(hspace=0)

    bkg_hists_phys = []
    total_bkg_phys = np.zeros(len(bins) - 1)

    for sample in BKG_STACK_ORDER:
        if sample not in results:
            continue
        r = results[sample]
        mask = r["is_physical"]
        h, _ = np.histogram(r["m_col"][mask], bins=bins, weights=r["weight"][mask])
        bkg_hists_phys.append(h)
        total_bkg_phys += h

    mh.histplot(bkg_hists_phys, bins=bins, stack=True, histtype="fill",
                label=bkg_labels, color=bkg_colors, ax=ax_main)

    for sample in ["GluGluToHToTauTau", "VBF_HToTauTau"]:
        if sample not in results:
            continue
        r = results[sample]
        mask = r["is_physical"]
        h, _ = np.histogram(r["m_col"][mask], bins=bins, weights=r["weight"][mask])
        mh.histplot(h * 50, bins=bins, histtype="step",
                    label=f"{MC_SAMPLES[sample]['label']} x50",
                    color=MC_SAMPLES[sample]["color"], linewidth=2, ax=ax_main)

    data_mask = np.concatenate([results[s]["is_physical"] for s in DATA_SAMPLES if s in results])
    h_data_phys, _ = np.histogram(data_m_col[data_mask], bins=bins)
    data_err_phys = np.sqrt(h_data_phys)
    ax_main.errorbar(bin_centers, h_data_phys, yerr=data_err_phys, fmt="ko",
                     markersize=4, label="Data", zorder=5)

    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(total_bkg_phys > 0, h_data_phys / total_bkg_phys, 0)
        ratio_err = np.where(total_bkg_phys > 0, data_err_phys / total_bkg_phys, 0)
    ax_ratio.errorbar(bin_centers, ratio, yerr=ratio_err, fmt="ko", markersize=4)
    ax_ratio.axhline(1.0, color="gray", linestyle="--", linewidth=1)
    ax_ratio.set_ylim(0.5, 1.5)

    ax_main.set_ylabel("Events / 10 GeV")
    ax_main.set_yscale("log")
    ax_main.set_ylim(bottom=0.1)
    ax_ratio.set_xlabel(r"$m_\mathrm{col}(\mu, \tau_h)$ [GeV] (physical solutions only)")
    ax_ratio.set_ylabel("Data/MC")
    ax_main.legend(fontsize="x-small", ncol=2)

    mh.label.exp_label(
        exp="CMS", data=True,
        llabel="Open Data",
        rlabel=r"$\sqrt{s} = 8$ TeV, 11.5 fb$^{-1}$",
        loc=0, ax=ax_main,
    )

    for ext in ["pdf", "png"]:
        fig.savefig(FIG_DIR / f"collinear_mass_physical.{ext}",
                    bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info("Saved collinear_mass_physical.pdf/png")


if __name__ == "__main__":
    main()
