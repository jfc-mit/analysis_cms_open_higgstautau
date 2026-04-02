"""
Phase 4a Step 6: Generate all figures.

Produces:
- Pre-fit template stacks (3 approaches x 2 categories)
- NP pull/constraint plot
- Impact ranking plot
- Signal injection linearity
- Systematic shift comparison plots
- CLs limit scan
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

OUT = Path("phase4_inference/4a_expected/outputs")
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

# Colors for processes
COLORS = {
    "ggH": "#D32F2F",
    "VBF": "#FF9800",
    "ZTT": "#4CAF50",
    "ZLL": "#81C784",
    "TTbar": "#2196F3",
    "Wjets": "#9C27B0",
    "QCD": "#FFC107",
}

LABELS = {
    "ggH": r"ggH ($\times 10$)",
    "VBF": r"VBF ($\times 10$)",
    "ZTT": r"$Z \to \tau\tau$",
    "ZLL": r"$Z \to \ell\ell$",
    "TTbar": r"$t\bar{t}$",
    "Wjets": "W+jets",
    "QCD": "QCD",
}

APPROACH_LABELS = {
    "mvis": r"$m_{\mathrm{vis}}$ [GeV]",
    "nn_score": "NN score",
    "mcol": r"$m_{\mathrm{col}}$ [GeV]",
}

BINNING = {
    "mvis": {"bins": 25, "lo": 0.0, "hi": 250.0},
    "nn_score": {"bins": 20, "lo": 0.0, "hi": 1.0},
    "mcol": {"bins": 25, "lo": 0.0, "hi": 300.0},
}


def save_fig(fig, name):
    """Save figure as PDF and PNG."""
    for ext in ["pdf", "png"]:
        fig.savefig(FIG / f"{name}.{ext}", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info(f"  Saved {name}")


def plot_template_stack(approach, cat):
    """Plot stacked template histogram for one approach and category."""
    with open(OUT / "nominal_templates.json") as f:
        nominal = json.load(f)

    cat_data = nominal[approach][cat]
    # Use stored edges (may differ from BINNING after VBF bin merging, F1 fix)
    if "edges" in cat_data and cat_data["edges"] is not None:
        edges = np.array(cat_data["edges"])
    else:
        b = BINNING[approach]
        edges = np.linspace(b["lo"], b["hi"], b["bins"] + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])
    widths = edges[1:] - edges[:-1]

    # Background stack (bottom to top)
    bkg_order = ["QCD", "Wjets", "TTbar", "ZLL", "ZTT"]
    bkg_hists = []
    bkg_labels = []
    bkg_colors = []
    for proc in bkg_order:
        h = np.array(cat_data["processes"][proc]["nominal"])
        bkg_hists.append(h)
        bkg_labels.append(LABELS[proc])
        bkg_colors.append(COLORS[proc])

    # Signal (scaled by 10)
    h_ggH = np.array(cat_data["processes"]["ggH"]["nominal"]) * 10
    h_VBF = np.array(cat_data["processes"]["VBF"]["nominal"]) * 10
    h_signal = h_ggH + h_VBF

    # Asimov data (sum of all)
    h_asimov = np.sum(bkg_hists, axis=0) + np.array(cat_data["processes"]["ggH"]["nominal"]) + np.array(cat_data["processes"]["VBF"]["nominal"])

    fig, (ax_main, ax_ratio) = plt.subplots(
        2, 1, figsize=(10, 10), gridspec_kw={"height_ratios": [3, 1]}, sharex=True,
    )
    fig.subplots_adjust(hspace=0)

    # Stack
    mh.histplot(
        bkg_hists,
        bins=edges,
        stack=True,
        histtype="fill",
        label=bkg_labels,
        color=bkg_colors,
        ax=ax_main,
    )

    # Signal (line)
    mh.histplot(
        h_signal,
        bins=edges,
        histtype="step",
        label=r"Signal ($\times 10$)",
        color="red",
        linewidth=2,
        ax=ax_main,
    )

    # Asimov data points
    ax_main.errorbar(
        centers, h_asimov,
        yerr=np.sqrt(np.maximum(h_asimov, 0)),
        fmt="ko", markersize=4, label="Asimov data",
    )

    ax_main.set_ylabel("Events / bin")
    ax_main.legend(fontsize="x-small", loc="upper right")
    ax_main.set_xlim(edges[0], edges[-1])

    mh.label.exp_label(
        exp="CMS", data=True, llabel="Open Data",
        rlabel=r"11.5 fb$^{-1}$ (8 TeV)", loc=0, ax=ax_main,
    )

    # Ratio
    total_mc = np.sum(bkg_hists, axis=0) + np.array(cat_data["processes"]["ggH"]["nominal"]) + np.array(cat_data["processes"]["VBF"]["nominal"])
    ratio = np.where(total_mc > 0, h_asimov / total_mc, 1.0)
    ratio_err = np.where(total_mc > 0, np.sqrt(np.maximum(h_asimov, 0)) / total_mc, 0.0)

    ax_ratio.errorbar(centers, ratio, yerr=ratio_err, fmt="ko", markersize=4)
    ax_ratio.axhline(1.0, color="gray", linestyle="--", linewidth=1)
    ax_ratio.set_ylim(0.8, 1.2)
    ax_ratio.set_ylabel("Asimov / Pred.")
    ax_ratio.set_xlabel(APPROACH_LABELS[approach])

    save_fig(fig, f"template_{approach}_{cat}")


def plot_signal_injection():
    """Plot signal injection test results."""
    with open(OUT / "validation_results.json") as f:
        val = json.load(f)

    fig, ax = plt.subplots(figsize=(10, 10))

    for approach_key, marker, color, label in [
        ("signal_injection", "o", "#D32F2F", "NN score"),
        ("signal_injection_mvis", "s", "#2196F3", r"$m_{\mathrm{vis}}$"),
        ("signal_injection_mcol", "^", "#4CAF50", r"$m_{\mathrm{col}}$"),
    ]:
        data = val[approach_key]
        mu_inj = [d["mu_inject"] for d in data if d["mu_hat"] is not None]
        mu_hat = [d["mu_hat"] for d in data if d["mu_hat"] is not None]
        mu_err = [d["mu_err"] for d in data if d["mu_hat"] is not None]

        ax.errorbar(mu_inj, mu_hat, yerr=mu_err, fmt=marker, color=color,
                     markersize=8, label=label, capsize=4)

    # Perfect recovery line
    ax.plot([-1, 6], [-1, 6], "k--", linewidth=1, label="Expected")
    ax.set_xlabel(r"Injected $\mu$")
    ax.set_ylabel(r"Recovered $\hat{\mu}$")
    ax.set_xlim(-0.5, 5.5)
    ax.set_ylim(-1, 7)
    ax.legend(fontsize="x-small")

    mh.label.exp_label(
        exp="CMS", data=True, llabel="Open Data",
        rlabel=r"11.5 fb$^{-1}$ (8 TeV)", loc=0, ax=ax,
    )

    save_fig(fig, "signal_injection")


def plot_impact_ranking():
    """Plot NP impact ranking."""
    with open(OUT / "validation_results.json") as f:
        val = json.load(f)

    impacts = val["impact_ranking"][:15]  # top 15

    fig, ax = plt.subplots(figsize=(10, 10))

    names = [imp["name"] for imp in impacts]
    y_pos = np.arange(len(names))

    # Impact bars
    up_vals = [imp["impact_up"] for imp in impacts]
    down_vals = [imp["impact_down"] for imp in impacts]

    ax.barh(y_pos, up_vals, height=0.4, color="#2196F3", alpha=0.7, label=r"$+1\sigma$")
    ax.barh(y_pos - 0.4, down_vals, height=0.4, color="#FF9800", alpha=0.7, label=r"$-1\sigma$")

    ax.set_yticks(y_pos - 0.2)
    ax.set_yticklabels(names, fontsize=8)
    ax.set_xlabel(r"$\Delta\hat{\mu}$")
    ax.legend(fontsize="x-small")
    ax.axvline(0, color="gray", linestyle="-", linewidth=0.5)

    mh.label.exp_label(
        exp="CMS", data=True, llabel="Open Data",
        rlabel=r"11.5 fb$^{-1}$ (8 TeV)", loc=0, ax=ax,
    )

    fig.tight_layout()
    save_fig(fig, "impact_ranking")


def plot_np_pulls():
    """Plot NP pull distribution."""
    with open(OUT / "expected_results.json") as f:
        results = json.load(f)

    # Use NN score
    pulls = results["nn_score"]["np_pulls"]

    fig, ax = plt.subplots(figsize=(10, 10))

    names = list(pulls.keys())
    y_pos = np.arange(len(names))
    values = [pulls[n]["bestfit"] for n in names]
    errors = [pulls[n]["uncertainty"] for n in names]

    # For NPs, the pull is (theta_hat - theta_0) / sigma
    # For normsys, init is 0 and sigma is 1
    # For Asimov, all pulls should be ~0
    ax.errorbar(values, y_pos, xerr=errors, fmt="ko", markersize=4, capsize=3)
    ax.axvline(0, color="red", linestyle="--", linewidth=1)
    ax.fill_betweenx([-1, len(names)], -1, 1, color="green", alpha=0.1)
    ax.fill_betweenx([-1, len(names)], -2, 2, color="yellow", alpha=0.1)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=7)
    ax.set_xlabel(r"$(\hat{\theta} - \theta_0) / \sigma_\theta$")
    ax.set_xlim(-3, 3)
    ax.set_ylim(-0.5, len(names) - 0.5)

    mh.label.exp_label(
        exp="CMS", data=True, llabel="Open Data",
        rlabel=r"11.5 fb$^{-1}$ (8 TeV)", loc=0, ax=ax,
    )

    fig.tight_layout()
    save_fig(fig, "np_pulls")


def plot_cls_scan():
    """Plot CLs scan for limit."""
    with open(OUT / "expected_results.json") as f:
        results = json.load(f)

    fig, ax = plt.subplots(figsize=(10, 10))

    for approach, color, label in [
        ("nn_score", "#D32F2F", "NN score"),
        ("mvis", "#2196F3", r"$m_{\mathrm{vis}}$"),
        ("mcol", "#4CAF50", r"$m_{\mathrm{col}}$"),
    ]:
        scan = results[approach].get("cls_scan", [])
        if scan:
            poi = [s["poi"] for s in scan]
            obs = [s["obs_cls"] for s in scan]
            exp_med = [s["exp_cls"][2] for s in scan]

            ax.plot(poi, obs, "-", color=color, label=f"{label} (obs/Asimov)")
            ax.plot(poi, exp_med, "--", color=color, alpha=0.7)

    ax.axhline(0.05, color="red", linestyle=":", linewidth=1, label="95% CL")
    ax.set_xlabel(r"$\mu$")
    ax.set_ylabel(r"CL$_s$")
    ax.set_ylim(0, 1)
    ax.set_xlim(0, 10)
    ax.legend(fontsize="x-small")

    mh.label.exp_label(
        exp="CMS", data=True, llabel="Open Data",
        rlabel=r"11.5 fb$^{-1}$ (8 TeV)", loc=0, ax=ax,
    )

    save_fig(fig, "cls_scan")


def plot_systematic_shifts():
    """Plot systematic shift comparison for primary approach."""
    with open(OUT / "nominal_templates.json") as f:
        nominal = json.load(f)

    with open(OUT / "shape_systematic_templates.json") as f:
        systs = json.load(f)

    approach = "nn_score"
    cat = "baseline"
    # Use stored edges (handles merged bins from F1 fix)
    cat_data = nominal[approach][cat]
    if "edges" in cat_data and cat_data["edges"] is not None:
        edges = np.array(cat_data["edges"])
    else:
        b = BINNING[approach]
        edges = np.linspace(b["lo"], b["hi"], b["bins"] + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])

    for syst_name in ["tes", "mes", "jes", "met_uncl"]:
        fig, ax = plt.subplots(figsize=(10, 10))

        for proc, color in [("ZTT", "#4CAF50"), ("ggH", "#D32F2F"), ("TTbar", "#2196F3")]:
            syst_proc = {"ggH": "ggH", "ZTT": "ZTT", "TTbar": "TTbar"}.get(proc)
            if proc == "ggH":
                syst_proc = "ggH"
            elif proc == "VBF":
                syst_proc = "VBF_sig"

            nom_h = np.array(nominal[approach][cat]["processes"][proc]["nominal"])
            key = f"{syst_proc}_{cat}_{approach}"
            h_up_raw = systs[syst_name]["up"].get(key)
            h_down_raw = systs[syst_name]["down"].get(key)
            h_up = np.array(h_up_raw) if h_up_raw is not None else nom_h.copy()
            h_down = np.array(h_down_raw) if h_down_raw is not None else nom_h.copy()
            # Guard against mismatched bin counts (shouldn't happen after fix)
            if len(h_up) != len(nom_h) or len(h_down) != len(nom_h):
                continue

            # Plot ratio
            ratio_up = np.where(nom_h > 0, h_up / nom_h, 1.0)
            ratio_down = np.where(nom_h > 0, h_down / nom_h, 1.0)

            ax.plot(centers, ratio_up, "-", color=color, label=f"{proc} up")
            ax.plot(centers, ratio_down, "--", color=color, label=f"{proc} down")

        ax.axhline(1.0, color="gray", linestyle="-", linewidth=0.5)
        ax.set_xlabel(APPROACH_LABELS[approach])
        ax.set_ylabel("Variation / Nominal")
        ax.set_ylim(0.8, 1.2)
        ax.legend(fontsize="x-small")

        syst_labels = {"tes": "Tau Energy Scale", "mes": "Muon Energy Scale",
                       "jes": "Jet Energy Scale", "met_uncl": "MET Unclustered"}

        mh.label.exp_label(
            exp="CMS", data=True, llabel=f"Open Data\n{syst_labels[syst_name]}",
            rlabel=r"11.5 fb$^{-1}$ (8 TeV)", loc=0, ax=ax,
        )

        save_fig(fig, f"syst_shift_{syst_name}")


def plot_gof_toys():
    """Plot GoF toy distribution."""
    with open(OUT / "validation_results.json") as f:
        val = json.load(f)

    gof = val.get("gof", {})
    toy_chi2s = gof.get("toy_chi2s", [])
    obs_chi2 = gof.get("chi2", 0)

    if not toy_chi2s:
        log.warning("No GoF toys to plot")
        return

    fig, ax = plt.subplots(figsize=(10, 10))

    ax.hist(toy_chi2s, bins=30, color="#2196F3", alpha=0.7, label="Toys")
    ax.axvline(obs_chi2, color="red", linewidth=2, label=f"Observed: {obs_chi2:.2f}")
    ax.set_xlabel(r"$\chi^2$")
    ax.set_ylabel("Toys")
    ax.legend(fontsize="x-small")

    p_val = gof.get("p_value_toys")
    if p_val is not None:
        ax.text(0.95, 0.95, f"p-value = {p_val:.3f}",
                transform=ax.transAxes, ha="right", va="top", fontsize=12)

    mh.label.exp_label(
        exp="CMS", data=True, llabel="Open Data\nGoodness of Fit",
        rlabel=r"11.5 fb$^{-1}$ (8 TeV)", loc=0, ax=ax,
    )

    save_fig(fig, "gof_toys")


def main():
    log.info("Generating Phase 4a figures")

    # Template stacks
    for approach in ["mvis", "nn_score", "mcol"]:
        for cat in ["baseline", "vbf"]:
            log.info(f"Plotting template stack: {approach} / {cat}")
            plot_template_stack(approach, cat)

    # Signal injection
    log.info("Plotting signal injection")
    plot_signal_injection()

    # Impact ranking
    log.info("Plotting impact ranking")
    plot_impact_ranking()

    # NP pulls
    log.info("Plotting NP pulls")
    plot_np_pulls()

    # CLs scan
    log.info("Plotting CLs scan")
    plot_cls_scan()

    # Systematic shifts
    log.info("Plotting systematic shifts")
    plot_systematic_shifts()

    # GoF toys
    log.info("Plotting GoF toys")
    plot_gof_toys()

    log.info(f"\nAll figures saved to {FIG}")


if __name__ == "__main__":
    main()
