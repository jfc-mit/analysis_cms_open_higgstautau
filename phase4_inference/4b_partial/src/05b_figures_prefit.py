"""
Phase 4b Step 5b: Generate data/MC comparison figures.

Produces data/MC plots using the pre-computed histogram data,
independent of the fit results (which are still running).
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

with open(P4A / "nominal_templates.json") as f:
    nominal = json.load(f)

with open(OUT / "data_histograms_10pct.json") as f:
    data_hists_file = json.load(f)
data_hists = data_hists_file["data_histograms"]

PROC_COLORS = {
    "ZTT": "#FFD700",
    "Wjets": "#FF6B6B",
    "QCD": "#C39BD3",
    "ZLL": "#87CEEB",
    "TTbar": "#90EE90",
}
PROC_LABELS = {
    "ZTT": r"$Z \to \tau\tau$",
    "ZLL": r"$Z \to \ell\ell$",
    "TTbar": r"$t\bar{t}$",
    "Wjets": "W+jets",
    "QCD": "QCD multijet",
}
BKG_ORDER = ["QCD", "Wjets", "TTbar", "ZLL", "ZTT"]

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
    """Data/MC comparison with ratio panel."""
    edges = np.array(data_hists[approach][cat]["edges"])
    centers = (edges[:-1] + edges[1:]) / 2

    data_scaled = np.array(data_hists[approach][cat]["data_10pct_scaled"])
    data_err = np.array(data_hists[approach][cat]["data_10pct_scaled_err"])

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

    total_sig = np.zeros_like(data_scaled)
    for proc in ["ggH", "VBF"]:
        if proc in nominal[approach][cat]["processes"]:
            total_sig += np.array(nominal[approach][cat]["processes"][proc]["nominal"])

    fig, (ax_main, ax_ratio) = plt.subplots(
        2, 1, figsize=(10, 10),
        gridspec_kw={"height_ratios": [3, 1]},
        sharex=True,
    )
    fig.subplots_adjust(hspace=0)

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


def plot_mu_comparison():
    """Plot mu comparison from diagnostics per-category fits."""
    diag_path = OUT / "diagnostics_10pct.json"
    if not diag_path.exists():
        log.warning("No diagnostics file, skipping mu comparison")
        return

    with open(diag_path) as f:
        diag = json.load(f)

    per_cat = diag["per_category_fit"]

    fig, ax = plt.subplots(figsize=(10, 10))

    approaches = ["mvis", "nn_score", "mcol"]
    approach_labels = [r"$m_{\mathrm{vis}}$", "NN score", r"$m_{\mathrm{col}}$"]

    y_pos = np.arange(len(approaches))
    offset = 0.15

    for cat, color, marker in [("baseline", "blue", "s"), ("vbf", "red", "o")]:
        mus = []
        errs = []
        for a in approaches:
            mu = per_cat[a][cat]["mu_hat"]
            err = per_cat[a][cat]["mu_err"]
            if mu is None:
                mu, err = 0, 0
            mus.append(mu)
            errs.append(err)

        cat_label = "Baseline" if cat == "baseline" else "VBF"
        y_offset = offset if cat == "baseline" else -offset
        ax.errorbar(
            mus, y_pos + y_offset,
            xerr=errs,
            fmt=marker, color=color, markersize=8, capsize=5,
            label=f"{cat_label} only (10% data x10)",
        )

    ax.axvline(1.0, color="gray", linestyle="--", linewidth=1, label=r"SM ($\mu = 1$)")
    ax.axvline(0.0, color="gray", linestyle=":", linewidth=1)
    ax.set_xlim(-8, 12)

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
    save_fig(fig, "mu_per_category_10pct")


def plot_data_mc_ratio_summary():
    """Summary bar chart of data/MC ratios per approach per category."""
    fig, ax = plt.subplots(figsize=(10, 10))

    diag_path = OUT / "diagnostics_10pct.json"
    if not diag_path.exists():
        return

    with open(diag_path) as f:
        diag = json.load(f)

    prefit = diag["prefit_chi2"]

    approaches = ["mvis", "nn_score", "mcol"]
    labels = [r"$m_{\mathrm{vis}}$", "NN score", r"$m_{\mathrm{col}}$"]

    x = np.arange(len(approaches))
    width = 0.35

    bl_ratios = [prefit[a]["baseline"]["ratio"] for a in approaches]
    vbf_ratios = [prefit[a]["vbf"]["ratio"] for a in approaches]

    bars1 = ax.bar(x - width / 2, bl_ratios, width, label="Baseline", color="steelblue")
    bars2 = ax.bar(x + width / 2, vbf_ratios, width, label="VBF", color="coral")

    ax.axhline(1.0, color="gray", linestyle="--", linewidth=1)
    ax.set_ylabel("Data / MC ratio (10% x10)")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.set_ylim(0, 1.2)

    # Add values on bars
    for bar in bars1:
        ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.01,
                f"{bar.get_height():.3f}", ha="center", va="bottom", fontsize=9)
    for bar in bars2:
        ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 0.01,
                f"{bar.get_height():.3f}", ha="center", va="bottom", fontsize=9)

    mh.label.exp_label(
        exp="CMS", data=True,
        llabel="Open Data",
        rlabel=r"$\sqrt{s} = 8$ TeV, 10% data",
        loc=0, ax=ax,
    )

    fig.tight_layout()
    save_fig(fig, "data_mc_ratio_summary")


def main():
    log.info("Generating Phase 4b pre-fit figures")

    for approach in ["mvis", "nn_score", "mcol"]:
        for cat in ["baseline", "vbf"]:
            plot_data_mc(approach, cat)

    plot_mu_comparison()
    plot_data_mc_ratio_summary()

    log.info("\nAll pre-fit figures generated.")


if __name__ == "__main__":
    main()
