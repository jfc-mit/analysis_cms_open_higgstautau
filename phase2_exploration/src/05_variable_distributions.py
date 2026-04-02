"""
Phase 2 Step 5: Variable distributions and data/MC comparison plots.

Reads preselected events from npz files. Produces stacked MC vs data plots
with ratio panels for all key discriminating variables.
Computes separation power (ROC AUC) for variable ranking.
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
from sklearn.metrics import roc_auc_score

mh.style.use("CMS")

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"
FIG_DIR = OUTPUT_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Sample configuration
MC_SAMPLES = {
    "GluGluToHToTauTau": {"label": "ggH", "color": "#d62728"},
    "VBF_HToTauTau": {"label": "VBF", "color": "#ff7f0e"},
    "DYJetsToLL": {"label": "DY", "color": "#1f77b4"},
    "TTbar": {"label": r"$t\bar{t}$", "color": "#2ca02c"},
    "W1JetsToLNu": {"label": "W+1j", "color": "#9467bd"},
    "W2JetsToLNu": {"label": "W+2j", "color": "#8c564b"},
    "W3JetsToLNu": {"label": "W+3j", "color": "#e377c2"},
}

# Stacking order (backgrounds first, then signal on top)
BKG_STACK_ORDER = ["DYJetsToLL", "W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu", "TTbar"]
SIG_SAMPLES = ["GluGluToHToTauTau", "VBF_HToTauTau"]
DATA_SAMPLES = ["Run2012B_TauPlusX", "Run2012C_TauPlusX"]

# Variable definitions: (branch, label, bins, range, log_y)
VARIABLES = [
    ("mvis", r"$m_\mathrm{vis}(\mu, \tau_h)$ [GeV]", 30, (0, 300), True),
    ("mt", r"$m_T(\mu, E_T^\mathrm{miss})$ [GeV]", 15, (0, 30), False),
    ("mu_pt", r"$p_T^\mu$ [GeV]", 25, (20, 120), True),
    ("tau_pt", r"$p_T^{\tau_h}$ [GeV]", 25, (20, 120), True),
    ("mu_eta", r"$\eta^\mu$", 25, (-2.1, 2.1), False),
    ("tau_eta", r"$\eta^{\tau_h}$", 25, (-2.3, 2.3), False),
    ("met_pt", r"$E_T^\mathrm{miss}$ [GeV]", 30, (0, 150), True),
    ("njets", r"$N_\mathrm{jets}$", 8, (-0.5, 7.5), True),
    ("nbjets", r"$N_{b-\mathrm{jets}}$", 5, (-0.5, 4.5), True),
    ("pv_npvs", r"$N_\mathrm{PV}$", 40, (0, 40), False),
    ("tau_dm", r"$\tau_h$ decay mode", 12, (-1.5, 10.5), True),
]


def load_sample(sample_name):
    """Load selected events from npz file."""
    npz_path = OUTPUT_DIR / f"selected_{sample_name}_loose.npz"
    if not npz_path.exists():
        log.warning("Missing: %s", npz_path)
        return None
    return dict(np.load(npz_path))


def compute_delta_phi(phi1, phi2):
    """Compute delta-phi wrapped to [-pi, pi]."""
    dphi = phi1 - phi2
    return np.arctan2(np.sin(dphi), np.cos(dphi))


def compute_delta_r(eta1, phi1, eta2, phi2):
    """Compute DeltaR."""
    deta = eta1 - eta2
    dphi = compute_delta_phi(phi1, phi2)
    return np.sqrt(deta**2 + dphi**2)


def make_data_mc_plot(variable, xlabel, nbins, xrange, log_y,
                      mc_data, data_arr, data_weights=None):
    """Make a stacked MC vs data plot with ratio panel."""
    fig, (ax_main, ax_ratio) = plt.subplots(
        2, 1, figsize=(10, 10), gridspec_kw={"height_ratios": [3, 1]},
        sharex=True
    )
    fig.subplots_adjust(hspace=0)

    bin_edges = np.linspace(xrange[0], xrange[1], nbins + 1)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    bin_width = bin_edges[1] - bin_edges[0]

    # Stack backgrounds
    bkg_hists = []
    bkg_labels = []
    bkg_colors = []
    total_bkg = np.zeros(nbins)

    for sample in BKG_STACK_ORDER:
        if sample not in mc_data or mc_data[sample] is None:
            continue
        vals = mc_data[sample][variable]
        weights = mc_data[sample]["weight"]
        h, _ = np.histogram(vals, bins=bin_edges, weights=weights)
        bkg_hists.append(h)
        bkg_labels.append(MC_SAMPLES[sample]["label"])
        bkg_colors.append(MC_SAMPLES[sample]["color"])
        total_bkg += h

    # Plot stacked backgrounds
    if bkg_hists:
        mh.histplot(
            bkg_hists,
            bins=bin_edges,
            stack=True,
            histtype="fill",
            label=bkg_labels,
            color=bkg_colors,
            ax=ax_main,
        )

    # Signal (overlay, not stacked, scaled x50 for visibility)
    sig_scale = 50
    for sample in SIG_SAMPLES:
        if sample not in mc_data or mc_data[sample] is None:
            continue
        vals = mc_data[sample][variable]
        weights = mc_data[sample]["weight"]
        h_sig, _ = np.histogram(vals, bins=bin_edges, weights=weights)
        mh.histplot(
            h_sig * sig_scale,
            bins=bin_edges,
            histtype="step",
            label=f"{MC_SAMPLES[sample]['label']} x{sig_scale}",
            color=MC_SAMPLES[sample]["color"],
            linewidth=2,
            ax=ax_main,
        )

    # Data
    if data_arr is not None and len(data_arr) > 0:
        h_data, _ = np.histogram(data_arr, bins=bin_edges)
        data_err = np.sqrt(h_data)
        ax_main.errorbar(
            bin_centers, h_data,
            yerr=data_err,
            fmt="ko",
            markersize=4,
            label="Data",
            zorder=5,
        )

        # Ratio panel
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = np.where(total_bkg > 0, h_data / total_bkg, 0)
            ratio_err = np.where(total_bkg > 0, data_err / total_bkg, 0)
        ax_ratio.errorbar(bin_centers, ratio, yerr=ratio_err, fmt="ko", markersize=4)
        ax_ratio.axhline(1.0, color="gray", linestyle="--", linewidth=1)
        ax_ratio.set_ylim(0.5, 1.5)
        ax_ratio.set_ylabel("Data/MC")
    else:
        ax_ratio.set_ylim(0.5, 1.5)
        ax_ratio.set_ylabel("Data/MC")

    ax_ratio.set_xlabel(xlabel)
    if log_y:
        ax_main.set_yscale("log")
        ax_main.set_ylim(bottom=0.1)
    ax_main.set_ylabel(f"Events / {bin_width:.1f}")
    ax_main.legend(fontsize="x-small", ncol=2)

    # CMS label on main panel only
    mh.label.exp_label(
        exp="CMS", data=True,
        llabel="Open Data",
        rlabel=r"$\sqrt{s} = 8$ TeV, 11.5 fb$^{-1}$",
        loc=0, ax=ax_main,
    )

    # Save
    for ext in ["pdf", "png"]:
        fig.savefig(
            FIG_DIR / f"{variable}.{ext}",
            bbox_inches="tight", dpi=200, transparent=True,
        )
    plt.close(fig)
    log.info("  Saved %s.pdf/png", variable)


def compute_separation_power(mc_data, variable):
    """Compute ROC AUC for signal vs background separation."""
    # Combine signals
    sig_vals = []
    sig_weights = []
    for sample in SIG_SAMPLES:
        if sample in mc_data and mc_data[sample] is not None:
            sig_vals.append(mc_data[sample][variable])
            sig_weights.append(mc_data[sample]["weight"])

    # Combine backgrounds
    bkg_vals = []
    bkg_weights = []
    for sample in BKG_STACK_ORDER:
        if sample in mc_data and mc_data[sample] is not None:
            bkg_vals.append(mc_data[sample][variable])
            bkg_weights.append(mc_data[sample]["weight"])

    if not sig_vals or not bkg_vals:
        return None

    sig_vals = np.concatenate(sig_vals)
    sig_weights = np.concatenate(sig_weights)
    bkg_vals = np.concatenate(bkg_vals)
    bkg_weights = np.concatenate(bkg_weights)

    # Create labels
    labels = np.concatenate([np.ones(len(sig_vals)), np.zeros(len(bkg_vals))])
    values = np.concatenate([sig_vals, bkg_vals])
    weights = np.concatenate([sig_weights, bkg_weights])

    # Filter out non-finite
    mask = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
    if np.sum(mask) < 10:
        return None

    try:
        auc = roc_auc_score(labels[mask], values[mask], sample_weight=np.abs(weights[mask]))
        return max(auc, 1.0 - auc)  # Ensure AUC >= 0.5
    except Exception:
        return None


def main():
    log.info("=" * 60)
    log.info("Phase 2 Step 5: Variable Distributions")
    log.info("=" * 60)

    # Load all samples
    mc_data = {}
    for sample_name in list(MC_SAMPLES.keys()):
        mc_data[sample_name] = load_sample(sample_name)

    # Combine data
    data_arrays = {}
    for sample_name in DATA_SAMPLES:
        d = load_sample(sample_name)
        if d is not None:
            for key in d:
                if key not in data_arrays:
                    data_arrays[key] = []
                data_arrays[key].append(d[key])
    for key in data_arrays:
        data_arrays[key] = np.concatenate(data_arrays[key])

    # Add derived variables
    for name, d in list(mc_data.items()) + [("data", data_arrays)]:
        if d is None or len(d.get("mu_pt", [])) == 0:
            continue
        d["delta_phi"] = np.abs(compute_delta_phi(d["mu_phi"], d["tau_phi"]))
        d["delta_r"] = compute_delta_r(d["mu_eta"], d["mu_phi"],
                                        d["tau_eta"], d["tau_phi"])
        d["met_significance"] = d.get("met_pt", np.array([])) / np.sqrt(np.maximum(d.get("met_pt", np.array([1.0])), 1.0))
        # The MET significance should come from the file directly but we stored met_pt
        # We'll use met_pt/sqrt(met_pt) as a proxy

    # Add derived variable definitions
    extra_vars = [
        ("delta_phi", r"$|\Delta\phi(\mu, \tau_h)|$", 20, (0, 3.14159), False),
        ("delta_r", r"$\Delta R(\mu, \tau_h)$", 25, (0.5, 5.0), False),
    ]

    all_variables = VARIABLES + extra_vars

    # Make plots
    for variable, xlabel, nbins, xrange, log_y in all_variables:
        log.info("Plotting %s...", variable)
        data_arr = data_arrays.get(variable)
        make_data_mc_plot(variable, xlabel, nbins, xrange, log_y, mc_data, data_arr)

    # Compute separation power
    log.info("\n" + "=" * 60)
    log.info("SEPARATION POWER (ROC AUC)")
    log.info("=" * 60)

    sep_results = {}
    for variable, xlabel, _, _, _ in all_variables:
        auc = compute_separation_power(mc_data, variable)
        if auc is not None:
            sep_results[variable] = auc
            log.info("  %-20s AUC = %.4f", variable, auc)
        else:
            log.info("  %-20s AUC = N/A", variable)

    # Rank by separation power
    ranked = sorted(sep_results.items(), key=lambda x: x[1], reverse=True)
    log.info("\nRanked by separation power:")
    for i, (var, auc) in enumerate(ranked, 1):
        log.info("  %2d. %-20s %.4f", i, var, auc)

    # Make separation power bar chart
    LABEL_MAP = {
        "tau_pt": r"$p_{\mathrm{T}}^{\tau_h}$",
        "mvis": r"$m_{\mathrm{vis}}$",
        "njets": r"$N_{\mathrm{jets}}$",
        "met_pt": r"$p_{\mathrm{T}}^{\mathrm{miss}}$",
        "mu_pt": r"$p_{\mathrm{T}}^{\mu}$",
        "delta_r": r"$\Delta R(\mu, \tau_h)$",
        "mt": r"$m_{\mathrm{T}}(\mu, p_{\mathrm{T}}^{\mathrm{miss}})$",
        "delta_phi": r"$\Delta\phi(\mu, \tau_h)$",
        "met_sig": r"MET significance",
        "nbjets": r"$N_{b\text{-jets}}$",
        "mu_eta": r"$\eta^{\mu}$",
        "tau_eta": r"$\eta^{\tau_h}$",
        "pv_npvs": r"$N_{\mathrm{PV}}$",
    }
    fig, ax = plt.subplots(figsize=(10, 10))
    vars_sorted = [v for v, _ in ranked]
    aucs_sorted = [a for _, a in ranked]
    labels_sorted = [LABEL_MAP.get(v, v) for v in vars_sorted]
    y_pos = np.arange(len(vars_sorted))
    ax.barh(y_pos, aucs_sorted, color="#1f77b4", edgecolor="black")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels_sorted)
    ax.set_xlabel("ROC AUC (Signal vs Background)")
    ax.set_xlim(0.5, 1.0)
    ax.invert_yaxis()
    mh.label.exp_label(
        exp="CMS", data=True,
        llabel="Open Simulation",
        rlabel=r"$\sqrt{s} = 8$ TeV",
        loc=0, ax=ax,
    )
    for ext in ["pdf", "png"]:
        fig.savefig(FIG_DIR / f"separation_power.{ext}",
                    bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info("Saved separation_power.pdf/png")

    # Print data/MC summary
    log.info("\n" + "=" * 60)
    log.info("DATA/MC YIELD SUMMARY")
    log.info("=" * 60)
    n_data = len(data_arrays.get("mu_pt", []))
    total_mc = sum(
        np.sum(mc_data[s]["weight"]) for s in MC_SAMPLES if mc_data[s] is not None
    )
    log.info("Data events:  %d", n_data)
    log.info("Total MC:     %.1f", total_mc)
    log.info("Data/MC ratio: %.3f", n_data / total_mc if total_mc > 0 else 0)


if __name__ == "__main__":
    main()
