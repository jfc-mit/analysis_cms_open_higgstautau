"""
Phase 4c Step 4: Generate all diagnostic figures for full data results.

Figures:
- Data/MC pre-fit comparison (6 plots: 3 approaches x 2 categories)
- Post-fit data/MC comparison (6 plots)
- NP pulls from full data fit
- mu comparison: Expected vs 10% vs Full (THREE-WAY)
- Impact ranking plot
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
P4B = Path("phase4_inference/4b_partial/outputs")
OUT = Path("phase4_inference/4c_observed/outputs")
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

# Load all results
with open(P4A / "nominal_templates.json") as f:
    nominal = json.load(f)

with open(OUT / "data_histograms_full.json") as f:
    data_hists_file = json.load(f)
data_hists = data_hists_file["data_histograms"]

with open(OUT / "observed_results.json") as f:
    fit_results = json.load(f)

with open(P4A / "expected_results.json") as f:
    expected_results = json.load(f)

with open(P4B / "partial_data_results.json") as f:
    partial_results = json.load(f)

with open(OUT / "diagnostics_full.json") as f:
    diagnostics = json.load(f)

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
    "ggH": r"$ggH$",
    "VBF": r"$VBF$",
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


def plot_data_mc_prefit(approach, cat):
    """Plot pre-fit data/MC comparison with ratio panel."""
    edges = np.array(data_hists[approach][cat]["edges"])
    centers = (edges[:-1] + edges[1:]) / 2
    widths = edges[1:] - edges[:-1]

    # Full data
    data_full = np.array(data_hists[approach][cat]["data_full"])
    data_err = np.array(data_hists[approach][cat]["data_full_err"])

    # Background stacks
    bkg_hists = []
    bkg_labels = []
    bkg_colors = []
    total_bkg = np.zeros_like(data_full)

    for proc in BKG_ORDER:
        if proc in nominal[approach][cat]["processes"]:
            h = np.array(nominal[approach][cat]["processes"][proc]["nominal"])
            bkg_hists.append(h)
            bkg_labels.append(PROC_LABELS[proc])
            bkg_colors.append(PROC_COLORS[proc])
            total_bkg += h

    # Signal (x10 for visibility)
    total_sig = np.zeros_like(data_full)
    for proc in SIG_PROCS:
        if proc in nominal[approach][cat]["processes"]:
            total_sig += np.array(
                nominal[approach][cat]["processes"][proc]["nominal"]
            )

    # Create figure with ratio panel
    fig, (ax_main, ax_ratio) = plt.subplots(
        2,
        1,
        figsize=(10, 10),
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

    # Signal (x10)
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
        centers,
        data_full,
        yerr=data_err,
        fmt="ko",
        markersize=4,
        capsize=2,
        label="Data",
        zorder=5,
    )

    ax_main.set_ylabel("Events")
    ax_main.legend(fontsize="x-small", loc="upper right")
    ax_main.set_xlim(edges[0], edges[-1])
    cat_label = "Baseline" if cat == "baseline" else "VBF"
    mh.label.exp_label(
        exp="CMS",
        data=True,
        llabel="Open Data",
        rlabel=rf"$\sqrt{{s}} = 8$ TeV, {cat_label}",
        loc=0,
        ax=ax_main,
    )

    # Ratio panel
    total_mc = total_bkg + total_sig
    ratio = np.where(total_mc > 0, data_full / total_mc, 1.0)
    ratio_err = np.where(total_mc > 0, data_err / total_mc, 0.0)

    ax_ratio.errorbar(
        centers,
        ratio,
        yerr=ratio_err,
        fmt="ko",
        markersize=4,
        capsize=2,
    )
    ax_ratio.axhline(1.0, color="gray", linestyle="--", linewidth=1)
    ax_ratio.set_ylabel("Data / MC")
    ax_ratio.set_xlabel(APPROACH_LABELS[approach])
    ax_ratio.set_ylim(0.5, 1.5)
    ax_ratio.set_xlim(edges[0], edges[-1])

    save_fig(fig, f"data_mc_prefit_{approach}_{cat}")


def plot_data_mc_postfit(approach, cat):
    """Plot post-fit data/MC comparison with ratio panel."""
    edges = np.array(data_hists[approach][cat]["edges"])
    centers = (edges[:-1] + edges[1:]) / 2

    # Full data
    data_full = np.array(data_hists[approach][cat]["data_full"])
    data_err = np.array(data_hists[approach][cat]["data_full_err"])

    # Post-fit expected from the fit results
    channel_name = f"{approach}_{cat}"
    postfit_data = fit_results[approach].get("postfit_yields", {}).get(channel_name)

    if postfit_data is None:
        log.warning(f"  No post-fit data for {channel_name}")
        return

    postfit_exp = np.array(postfit_data["expected_postfit"])

    # Create figure
    fig, (ax_main, ax_ratio) = plt.subplots(
        2,
        1,
        figsize=(10, 10),
        gridspec_kw={"height_ratios": [3, 1]},
        sharex=True,
    )
    fig.subplots_adjust(hspace=0)

    # Main panel
    mh.histplot(
        [postfit_exp],
        bins=edges,
        ax=ax_main,
        histtype="fill",
        label=["Post-fit prediction"],
        color=["steelblue"],
        alpha=0.7,
        edgecolor="black",
        linewidth=0.5,
    )

    ax_main.errorbar(
        centers,
        data_full,
        yerr=data_err,
        fmt="ko",
        markersize=4,
        capsize=2,
        label="Data",
        zorder=5,
    )

    ax_main.set_ylabel("Events")
    ax_main.legend(fontsize="x-small", loc="upper right")
    ax_main.set_xlim(edges[0], edges[-1])
    cat_label = "Baseline" if cat == "baseline" else "VBF"
    mu_hat = fit_results[approach]["mu_hat"]
    mu_err = fit_results[approach]["mu_err"]
    mh.label.exp_label(
        exp="CMS",
        data=True,
        llabel="Open Data",
        rlabel=rf"$\sqrt{{s}} = 8$ TeV, {cat_label}, $\hat{{\mu}}={mu_hat:.2f}\pm{mu_err:.2f}$",
        loc=0,
        ax=ax_main,
    )

    # Ratio panel
    ratio = np.where(postfit_exp > 0, data_full / postfit_exp, 1.0)
    ratio_err = np.where(postfit_exp > 0, data_err / postfit_exp, 0.0)

    ax_ratio.errorbar(
        centers,
        ratio,
        yerr=ratio_err,
        fmt="ko",
        markersize=4,
        capsize=2,
    )
    ax_ratio.axhline(1.0, color="gray", linestyle="--", linewidth=1)
    ax_ratio.set_ylabel("Data / Post-fit")
    ax_ratio.set_xlabel(APPROACH_LABELS[approach])
    ax_ratio.set_ylim(0.5, 1.5)
    ax_ratio.set_xlim(edges[0], edges[-1])

    save_fig(fig, f"data_mc_postfit_{approach}_{cat}")


def plot_np_pulls():
    """Plot NP pulls from the full data fit (NN score approach)."""
    approach = "nn_score"
    np_pulls = fit_results[approach]["np_pulls"]

    # Sort by |pull|
    sorted_nps = sorted(
        np_pulls.items(), key=lambda x: abs(x[1]["pull"]), reverse=True
    )

    names = [n for n, _ in sorted_nps]
    pulls = [info["pull"] for _, info in sorted_nps]
    unc = [info["uncertainty"] for _, info in sorted_nps]

    fig, ax = plt.subplots(figsize=(10, 10))

    y_pos = np.arange(len(names))

    # 1-sigma and 2-sigma bands
    ax.axvspan(-2, 2, color="yellow", alpha=0.3, label=r"$\pm 2\sigma$")
    ax.axvspan(-1, 1, color="green", alpha=0.3, label=r"$\pm 1\sigma$")
    ax.axvline(0, color="gray", linestyle="--", linewidth=1)

    ax.errorbar(
        pulls,
        y_pos,
        xerr=unc,
        fmt="ko",
        markersize=6,
        capsize=3,
    )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=8)
    ax.set_xlabel(r"$(\hat{\theta} - \theta_0) / \sigma_{\mathrm{pre-fit}}$")
    ax.set_xlim(-3, 3)
    ax.legend(fontsize="x-small", loc="upper right")

    mh.label.exp_label(
        exp="CMS",
        data=True,
        llabel="Open Data",
        rlabel=r"$\sqrt{s} = 8$ TeV, full data",
        loc=0,
        ax=ax,
    )

    fig.tight_layout()
    save_fig(fig, "np_pulls_full")


def plot_mu_comparison_three_way():
    """Plot mu comparison: Expected vs 10% vs Full for all approaches."""
    fig, ax = plt.subplots(figsize=(10, 10))

    approaches = ["mvis", "nn_score", "mcol"]
    approach_labels = [r"$m_{\mathrm{vis}}$", "NN score", r"$m_{\mathrm{col}}$"]

    y_pos = np.arange(len(approaches))

    # Expected (from 4a)
    exp_mu = [expected_results[a]["mu_hat"] for a in approaches]
    exp_err = [expected_results[a]["mu_err"] for a in approaches]

    # 10% data (from 4b)
    pct_mu = [partial_results[a]["mu_hat"] for a in approaches]
    pct_err = [partial_results[a]["mu_err"] for a in approaches]

    # Full data (from 4c)
    full_mu = [fit_results[a]["mu_hat"] for a in approaches]
    full_err = [fit_results[a]["mu_err"] for a in approaches]

    ax.errorbar(
        exp_mu,
        y_pos + 0.25,
        xerr=exp_err,
        fmt="s",
        color="blue",
        markersize=8,
        capsize=5,
        label="Expected (Asimov, 4a)",
    )
    ax.errorbar(
        pct_mu,
        y_pos,
        xerr=pct_err,
        fmt="D",
        color="green",
        markersize=8,
        capsize=5,
        label="10% data (4b)",
    )
    ax.errorbar(
        full_mu,
        y_pos - 0.25,
        xerr=full_err,
        fmt="o",
        color="red",
        markersize=8,
        capsize=5,
        label="Full data (4c)",
    )

    ax.axvline(
        1.0, color="gray", linestyle="--", linewidth=1, label=r"SM ($\mu = 1$)"
    )
    ax.axvline(0.0, color="gray", linestyle=":", linewidth=1)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(approach_labels, fontsize=12)
    ax.set_xlabel(r"Signal strength $\hat{\mu}$")
    ax.legend(fontsize="x-small", loc="upper left")

    mh.label.exp_label(
        exp="CMS",
        data=True,
        llabel="Open Data",
        rlabel=r"$\sqrt{s} = 8$ TeV",
        loc=0,
        ax=ax,
    )

    fig.tight_layout()
    save_fig(fig, "mu_comparison_three_way")


def plot_impact_ranking():
    """Plot impact ranking of NPs on mu (NN score)."""
    impacts = diagnostics.get("impact_ranking", {})
    if not impacts:
        log.warning("  No impact ranking data available")
        return

    # Sort by symmetric impact
    sorted_impacts = sorted(
        impacts.items(), key=lambda x: x[1]["impact_sym"], reverse=True
    )

    # Show top 15
    n_show = min(15, len(sorted_impacts))
    names = [n for n, _ in sorted_impacts[:n_show]]
    imp_up = [info["impact_up"] for _, info in sorted_impacts[:n_show]]
    imp_down = [info["impact_down"] for _, info in sorted_impacts[:n_show]]

    fig, ax = plt.subplots(figsize=(10, 10))

    y_pos = np.arange(n_show)

    ax.barh(
        y_pos,
        imp_up,
        height=0.4,
        align="center",
        color="steelblue",
        alpha=0.7,
        label=r"+1$\sigma$",
    )
    ax.barh(
        y_pos,
        imp_down,
        height=0.4,
        align="center",
        color="coral",
        alpha=0.7,
        label=r"$-1\sigma$",
    )

    ax.axvline(0, color="gray", linestyle="--", linewidth=1)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=8)
    ax.set_xlabel(r"$\Delta\hat{\mu}$")
    ax.legend(fontsize="x-small", loc="upper right")
    ax.invert_yaxis()

    mh.label.exp_label(
        exp="CMS",
        data=True,
        llabel="Open Data",
        rlabel=r"$\sqrt{s} = 8$ TeV, NN score",
        loc=0,
        ax=ax,
    )

    fig.tight_layout()
    save_fig(fig, "impact_ranking_full")


def plot_gof_toys():
    """Plot GoF toy distributions with observed chi2 marked."""
    for approach in ["mvis", "nn_score", "mcol"]:
        res = fit_results[approach]
        toy_chi2s = res.get("gof_toy_chi2s", [])
        obs_chi2 = res["chi2"]
        p_value = res["gof_pvalue"]

        fig, ax = plt.subplots(figsize=(10, 10))

        if toy_chi2s:
            clean = [c for c in toy_chi2s if c < 1000]
            if clean:
                ax.hist(clean, bins=30, color="steelblue", alpha=0.7, label="Toys")
                ax.axvline(
                    obs_chi2,
                    color="red",
                    linewidth=2,
                    linestyle="--",
                    label=f"Obs. $\\chi^2$ = {obs_chi2:.1f}",
                )
                p_str = f"{p_value:.3f}" if p_value is not None else "N/A"
                n_conv = res.get("gof_n_converged", len(clean))
                n_fail = res.get("gof_n_failed", 0)
                n_total = res.get("gof_n_toys", n_conv + n_fail)
                ax.set_xlabel(r"$\chi^2$")
                ax.set_ylabel("Toys")
                ax.legend(
                    fontsize="x-small",
                    title=(
                        f"p-value = {p_str}\n"
                        f"Toys: {n_conv}/{n_total} converged"
                        + (f" ({n_fail} failed)" if n_fail > 0 else "")
                    ),
                    title_fontsize="x-small",
                )

        approach_label = {
            "mvis": r"$m_{\mathrm{vis}}$",
            "nn_score": "NN score",
            "mcol": r"$m_{\mathrm{col}}$",
        }[approach]

        mh.label.exp_label(
            exp="CMS",
            data=True,
            llabel="Open Data",
            rlabel=rf"$\sqrt{{s}} = 8$ TeV, {approach_label}",
            loc=0,
            ax=ax,
        )

        fig.tight_layout()
        save_fig(fig, f"gof_toys_full_{approach}")


def plot_per_category_mu():
    """Plot per-category mu for all approaches."""
    per_cat = diagnostics.get("per_category_fit", {})
    if not per_cat:
        log.warning("  No per-category fit data available")
        return

    fig, ax = plt.subplots(figsize=(10, 10))

    approaches = ["mvis", "nn_score", "mcol"]
    approach_labels = [r"$m_{\mathrm{vis}}$", "NN score", r"$m_{\mathrm{col}}$"]
    y_pos = np.arange(len(approaches))

    for cat_idx, (cat, color, marker) in enumerate(
        [("baseline", "blue", "s"), ("vbf", "red", "D")]
    ):
        mus = []
        errs = []
        for a in approaches:
            cat_res = per_cat.get(a, {}).get(cat, {})
            mus.append(cat_res.get("mu_hat", 0))
            errs.append(cat_res.get("mu_err", 0))

        offset = 0.15 * (1 - 2 * cat_idx)
        cat_label = "Baseline" if cat == "baseline" else "VBF"
        ax.errorbar(
            mus,
            y_pos + offset,
            xerr=errs,
            fmt=marker,
            color=color,
            markersize=8,
            capsize=5,
            label=f"{cat_label} only",
        )

    # Combined
    combined_mu = [fit_results[a]["mu_hat"] for a in approaches]
    combined_err = [fit_results[a]["mu_err"] for a in approaches]
    ax.errorbar(
        combined_mu,
        y_pos,
        xerr=combined_err,
        fmt="o",
        color="black",
        markersize=8,
        capsize=5,
        label="Combined",
    )

    ax.axvline(
        1.0, color="gray", linestyle="--", linewidth=1, label=r"SM ($\mu = 1$)"
    )
    ax.axvline(0.0, color="gray", linestyle=":", linewidth=1)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(approach_labels, fontsize=12)
    ax.set_xlabel(r"Signal strength $\hat{\mu}$")
    ax.legend(fontsize="x-small", loc="upper left")

    mh.label.exp_label(
        exp="CMS",
        data=True,
        llabel="Open Data",
        rlabel=r"$\sqrt{s} = 8$ TeV, full data",
        loc=0,
        ax=ax,
    )

    fig.tight_layout()
    save_fig(fig, "per_category_mu_full")


def main():
    log.info("Generating Phase 4c diagnostic figures")

    # Pre-fit data/MC comparison plots
    log.info("\n--- Pre-fit Data/MC comparison plots ---")
    for approach in ["mvis", "nn_score", "mcol"]:
        for cat in ["baseline", "vbf"]:
            plot_data_mc_prefit(approach, cat)

    # Post-fit data/MC comparison plots
    log.info("\n--- Post-fit Data/MC comparison plots ---")
    for approach in ["mvis", "nn_score", "mcol"]:
        for cat in ["baseline", "vbf"]:
            plot_data_mc_postfit(approach, cat)

    # NP pulls
    log.info("\n--- NP pull plot ---")
    plot_np_pulls()

    # Three-way mu comparison
    log.info("\n--- Three-way mu comparison ---")
    plot_mu_comparison_three_way()

    # Impact ranking
    log.info("\n--- Impact ranking plot ---")
    plot_impact_ranking()

    # GoF toys (individual plots)
    log.info("\n--- GoF toy distributions ---")
    plot_gof_toys()

    # Per-category mu
    log.info("\n--- Per-category mu ---")
    plot_per_category_mu()

    log.info("\nAll Phase 4c figures generated.")


if __name__ == "__main__":
    main()
