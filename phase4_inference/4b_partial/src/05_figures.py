"""
Phase 4b Step 5: Generate diagnostic figures for 10% data validation.

- Data/MC comparison plots with ratio panels (6 plots)
- NP pull plot from 10% fit
- mu comparison: expected vs 10% for all approaches
- GoF toy distributions
"""
import logging
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep as mh
from pathlib import Path
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

mh.style.use("CMS")

P4A = Path("phase4_inference/4a_expected/outputs")
OUT = Path("phase4_inference/4b_partial/outputs")
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

# Load data
with open(P4A / "nominal_templates.json") as f:
    nominal = json.load(f)

with open(OUT / "data_histograms_10pct.json") as f:
    data_hists_file = json.load(f)
data_hists = data_hists_file["data_histograms"]

with open(OUT / "partial_data_results.json") as f:
    fit_results = json.load(f)

with open(P4A / "expected_results.json") as f:
    expected_results = json.load(f)

# Process colors and labels
PROC_COLORS = {
    "ZTT": "#FFD700",
    "Wjets": "#FF6B6B",
    "QCD": "#C39BD3",
    "ZLL": "#87CEEB",
    "TTbar": "#90EE90",
    "ggH": "#FF4444",
    "VBF": "#4444FF",
}
PROC_LABELS = {
    "ZTT": r"$Z \to \tau\tau$",
    "ZLL": r"$Z \to \ell\ell$",
    "TTbar": r"$t\bar{t}$",
    "Wjets": "W+jets",
    "QCD": "QCD multijet",
    "ggH": r"$ggH$ (x10)",
    "VBF": r"$VBF$ (x10)",
}
BKG_ORDER = ["QCD", "Wjets", "TTbar", "ZLL", "ZTT"]
SIG_PROCS = ["ggH", "VBF"]

APPROACH_LABELS = {
    "mvis": r"$m_{\mathrm{vis}}$ [GeV]",
    "nn_score": "NN score",
    "mcol": r"$m_{\mathrm{col}}$ [GeV]",
}


def save_fig(fig, name):
    """Save figure as PDF and PNG."""
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig.savefig(FIG / f"{name}.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info(f"  Saved {name}")


def plot_data_mc(approach, cat):
    """Plot data/MC comparison with ratio panel for one approach/category."""
    edges = np.array(data_hists[approach][cat]["edges"])
    centers = (edges[:-1] + edges[1:]) / 2
    widths = edges[1:] - edges[:-1]

    # Data (10% scaled x10)
    data_scaled = np.array(data_hists[approach][cat]["data_10pct_scaled"])
    data_err = np.array(data_hists[approach][cat]["data_10pct_scaled_err"])

    # Background stacks
    bkg_hists = []
    bkg_labels = []
    bkg_colors = []
    total_bkg = np.zeros_like(data_scaled)

    for proc in BKG_ORDER:
        if proc in nominal[approach][cat]["processes"]:
            h = np.array(nominal[approach][cat]["processes"][proc]["nominal"])
            bkg_hists.append(h)
            bkg_labels.append(PROC_LABELS[proc])
            bkg_colors.append(PROC_COLORS[proc])
            total_bkg += h

    # Signal (x10 for visibility)
    total_sig = np.zeros_like(data_scaled)
    for proc in SIG_PROCS:
        if proc in nominal[approach][cat]["processes"]:
            total_sig += np.array(
                nominal[approach][cat]["processes"][proc]["nominal"]
            )

    # Create figure with ratio panel
    fig, (ax_main, ax_ratio) = plt.subplots(
        2, 1, figsize=(10, 10),
        gridspec_kw={"height_ratios": [3, 1]},
        sharex=True,
    )
    fig.subplots_adjust(hspace=0)

    # Main panel: stacked backgrounds
    mh.histplot(
        bkg_hists,
        bins=edges,
        ax=ax_main,
        stack=True,
        histtype="fill",
        label=bkg_labels,
        color=bkg_colors,
        edgecolor="black",
        linewidth=0.5,
    )

    # Signal (stacked on top of background, x10)
    mh.histplot(
        [total_sig * 10],
        bins=edges,
        ax=ax_main,
        stack=False,
        histtype="step",
        label=[r"Signal ($\mu=1$) $\times 10$"],
        color=["red"],
        linewidth=2,
    )

    # Data points
    ax_main.errorbar(
        centers, data_scaled, yerr=data_err,
        fmt="ko", markersize=4, capsize=2,
        label="Data (10% x10)",
        zorder=5,
    )

    ax_main.set_ylabel("Events")
    ax_main.legend(fontsize="x-small", loc="upper right")
    ax_main.set_xlim(edges[0], edges[-1])
    cat_label = "Baseline" if cat == "baseline" else "VBF"
    mh.label.exp_label(
        exp="CMS", data=True,
        llabel="Open Data",
        rlabel=rf"$\sqrt{{s}} = 8$ TeV, {cat_label}",
        loc=0, ax=ax_main,
    )

    # Ratio panel
    ratio = np.where(total_bkg > 0, data_scaled / total_bkg, 1.0)
    ratio_err = np.where(total_bkg > 0, data_err / total_bkg, 0.0)

    ax_ratio.errorbar(
        centers, ratio, yerr=ratio_err,
        fmt="ko", markersize=4, capsize=2,
    )
    ax_ratio.axhline(1.0, color="gray", linestyle="--", linewidth=1)
    ax_ratio.set_ylabel("Data / MC")
    ax_ratio.set_xlabel(APPROACH_LABELS[approach])
    ax_ratio.set_ylim(0.5, 1.5)
    ax_ratio.set_xlim(edges[0], edges[-1])

    save_fig(fig, f"data_mc_{approach}_{cat}")


def plot_np_pulls():
    """Plot NP pulls from the 10% fit (NN score approach)."""
    approach = "nn_score"
    np_pulls = fit_results[approach]["np_pulls"]

    # Sort by |pull|
    sorted_nps = sorted(np_pulls.items(), key=lambda x: abs(x[1]["pull"]), reverse=True)

    names = [n for n, _ in sorted_nps]
    pulls = [info["pull"] for _, info in sorted_nps]
    unc = [info["uncertainty"] for _, info in sorted_nps]

    fig, ax = plt.subplots(figsize=(10, 10))

    y_pos = np.arange(len(names))

    # 1-sigma and 2-sigma bands
    ax.axvspan(-2, 2, color="yellow", alpha=0.3, label=r"$\pm 2\sigma$")
    ax.axvspan(-1, 1, color="green", alpha=0.3, label=r"$\pm 1\sigma$")
    ax.axvline(0, color="gray", linestyle="--", linewidth=1)

    # Pull points with post-fit uncertainty as error bars
    # The "pull" is (bestfit - init) / uncertainty
    # Show the pull value, with error bar = post-fit unc / pre-fit unc
    ax.errorbar(
        pulls, y_pos,
        xerr=[info["uncertainty"] for _, info in sorted_nps],
        fmt="ko", markersize=6, capsize=3,
    )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=8)
    ax.set_xlabel("Pull (post-fit - pre-fit) / uncertainty")
    ax.set_xlim(-3, 3)
    ax.legend(fontsize="x-small", loc="upper right")

    mh.label.exp_label(
        exp="CMS", data=True,
        llabel="Open Data",
        rlabel=r"$\sqrt{s} = 8$ TeV, 10% data",
        loc=0, ax=ax,
    )

    fig.tight_layout()
    save_fig(fig, "np_pulls_10pct")


def plot_mu_comparison():
    """Plot mu comparison: expected vs 10% for all approaches."""
    fig, ax = plt.subplots(figsize=(10, 10))

    approaches = ["mvis", "nn_score", "mcol"]
    approach_labels = [r"$m_{\mathrm{vis}}$", "NN score", r"$m_{\mathrm{col}}$"]

    y_pos = np.arange(len(approaches))

    # Expected (from 4a)
    exp_mu = [expected_results[a]["mu_hat"] for a in approaches]
    exp_err = [expected_results[a]["mu_err"] for a in approaches]

    # 10% data
    obs_mu = [fit_results[a]["mu_hat"] for a in approaches]
    obs_err = [fit_results[a]["mu_err"] for a in approaches]

    ax.errorbar(
        exp_mu, y_pos + 0.15,
        xerr=exp_err,
        fmt="s", color="blue", markersize=8, capsize=5,
        label="Expected (Asimov, 4a)",
    )
    ax.errorbar(
        obs_mu, y_pos - 0.15,
        xerr=obs_err,
        fmt="o", color="red", markersize=8, capsize=5,
        label="Observed (10% data x10)",
    )

    ax.axvline(1.0, color="gray", linestyle="--", linewidth=1, label=r"SM ($\mu = 1$)")
    ax.axvline(0.0, color="gray", linestyle=":", linewidth=1)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(approach_labels, fontsize=12)
    ax.set_xlabel(r"Signal strength $\mu$")
    ax.legend(fontsize="x-small", loc="upper right")

    mh.label.exp_label(
        exp="CMS", data=True,
        llabel="Open Data",
        rlabel=r"$\sqrt{s} = 8$ TeV, 10% data",
        loc=0, ax=ax,
    )

    fig.tight_layout()
    save_fig(fig, "mu_comparison_10pct")


def plot_gof_toys():
    """Plot GoF toy distributions with observed chi2 marked."""
    fig, axes = plt.subplots(1, 3, figsize=(10, 10))

    for idx, approach in enumerate(["mvis", "nn_score", "mcol"]):
        ax = axes[idx]
        toy_chi2s = fit_results[approach].get("gof_toy_chi2s", [])
        obs_chi2 = fit_results[approach]["chi2"]
        p_value = fit_results[approach]["gof_pvalue"]

        if toy_chi2s:
            clean = [c for c in toy_chi2s if c < 1000]
            if clean:
                ax.hist(clean, bins=30, color="steelblue", alpha=0.7, label="Toys")
                ax.axvline(
                    obs_chi2, color="red", linewidth=2, linestyle="--",
                    label=f"Obs. $\\chi^2$ = {obs_chi2:.1f}",
                )
                ax.set_xlabel(r"$\chi^2$")
                ax.set_ylabel("Toys")
                approach_label = {
                    "mvis": r"$m_{\mathrm{vis}}$",
                    "nn_score": "NN score",
                    "mcol": r"$m_{\mathrm{col}}$",
                }[approach]
                ax.legend(fontsize="x-small", title=f"{approach_label}\np = {p_value:.3f}")
        else:
            ax.text(0.5, 0.5, "No toy data", ha="center", va="center",
                    transform=ax.transAxes)

    fig.tight_layout()
    save_fig(fig, "gof_toys_10pct")


def main():
    log.info("Generating Phase 4b diagnostic figures")

    # Data/MC comparison plots
    log.info("\n--- Data/MC comparison plots ---")
    for approach in ["mvis", "nn_score", "mcol"]:
        for cat in ["baseline", "vbf"]:
            plot_data_mc(approach, cat)

    # NP pulls
    log.info("\n--- NP pull plot ---")
    plot_np_pulls()

    # mu comparison
    log.info("\n--- mu comparison plot ---")
    plot_mu_comparison()

    # GoF toys
    log.info("\n--- GoF toy distributions ---")
    plot_gof_toys()

    log.info("\nAll figures generated.")


if __name__ == "__main__":
    main()
