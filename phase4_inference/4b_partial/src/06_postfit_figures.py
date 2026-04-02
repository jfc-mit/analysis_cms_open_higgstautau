"""
Phase 4b Step 6: Post-fit figures using saved results.
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

with open(OUT / "partial_data_results.json") as f:
    fit_results = json.load(f)

with open(P4A / "expected_results.json") as f:
    expected_results = json.load(f)


def save_fig(fig, name):
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig.savefig(FIG / f"{name}.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info(f"  Saved {name}")


def plot_np_pulls():
    """NP pulls from NN score fit."""
    np_pulls = fit_results["nn_score"]["np_pulls"]
    sorted_nps = sorted(np_pulls.items(), key=lambda x: abs(x[1]["pull"]), reverse=True)

    names = [n for n, _ in sorted_nps]
    pulls = [info["pull"] for _, info in sorted_nps]
    unc = [info["uncertainty"] for _, info in sorted_nps]

    fig, ax = plt.subplots(figsize=(10, 10))
    y_pos = np.arange(len(names))

    ax.axvspan(-2, 2, color="yellow", alpha=0.3, label=r"$\pm 2\sigma$")
    ax.axvspan(-1, 1, color="green", alpha=0.3, label=r"$\pm 1\sigma$")
    ax.axvline(0, color="gray", linestyle="--", linewidth=1)

    ax.errorbar(pulls, y_pos, xerr=unc, fmt="ko", markersize=6, capsize=3)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize="xx-small")
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
    """Expected vs observed mu for all approaches."""
    fig, ax = plt.subplots(figsize=(10, 10))

    approaches = ["mvis", "nn_score", "mcol"]
    labels = [r"$m_{\mathrm{vis}}$", "NN score", r"$m_{\mathrm{col}}$"]
    y_pos = np.arange(len(approaches))

    exp_mu = [expected_results[a]["mu_hat"] for a in approaches]
    exp_err = [expected_results[a]["mu_err"] for a in approaches]
    obs_mu = [fit_results[a]["mu_hat"] for a in approaches]
    obs_err = [fit_results[a]["mu_err"] for a in approaches]

    ax.errorbar(
        exp_mu, y_pos + 0.15, xerr=exp_err,
        fmt="s", color="blue", markersize=8, capsize=5,
        label="Expected (Asimov, 4a)",
    )
    ax.errorbar(
        obs_mu, y_pos - 0.15, xerr=obs_err,
        fmt="o", color="red", markersize=8, capsize=5,
        label="Observed (10% data, scaled MC)",
    )

    ax.axvline(1.0, color="gray", linestyle="--", linewidth=1, label=r"SM ($\mu = 1$)")
    ax.axvline(0.0, color="gray", linestyle=":", linewidth=1)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize="small")
    ax.set_xlabel(r"Signal strength $\mu$")
    ax.legend(fontsize="x-small", loc="upper left")

    mh.label.exp_label(
        exp="CMS", data=True,
        llabel="Open Data",
        rlabel=r"$\sqrt{s} = 8$ TeV, 10% data",
        loc=0, ax=ax,
    )

    fig.tight_layout()
    save_fig(fig, "mu_comparison_10pct")


def plot_gof_toys():
    """GoF toy distributions for all approaches."""
    approach_labels = {
        "mvis": r"$m_{\mathrm{vis}}$",
        "nn_score": "NN score",
        "mcol": r"$m_{\mathrm{col}}$",
    }

    for approach in ["mvis", "nn_score", "mcol"]:
        res = fit_results[approach]
        toy_chi2s = res.get("gof_toy_chi2s", [])
        obs_chi2 = res["chi2"]
        p_value = res["gof_pvalue"]

        if toy_chi2s:
            clean = [c for c in toy_chi2s if c < 1000]
            if clean:
                fig, ax = plt.subplots(figsize=(10, 10))

                ax.hist(clean, bins=30, color="steelblue", alpha=0.7, label="Toys")
                ax.axvline(
                    obs_chi2, color="red", linewidth=2, linestyle="--",
                    label=f"Obs. = {obs_chi2:.1f}",
                )
                p_str = f"{p_value:.3f}" if p_value is not None else "N/A"
                ax.set_xlabel(r"$\chi^2$")
                ax.set_ylabel("Toys")
                ax.legend(fontsize="x-small")
                ax.text(
                    0.95, 0.95,
                    f"{approach_labels[approach]}\n$p$ = {p_str}",
                    transform=ax.transAxes, ha="right", va="top",
                    fontsize="small",
                    bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
                )

                mh.label.exp_label(
                    exp="CMS", data=True,
                    llabel="Open Data",
                    rlabel=r"$\sqrt{s} = 8$ TeV, 10% data",
                    loc=0, ax=ax,
                )

                fig.tight_layout()
                save_fig(fig, f"gof_toys_10pct_{approach}")

    # Also produce the combined 3-panel figure for backward compatibility
    fig, axes = plt.subplots(1, 3, figsize=(10, 10))

    for idx, approach in enumerate(["mvis", "nn_score", "mcol"]):
        ax = axes[idx]
        res = fit_results[approach]
        toy_chi2s = res.get("gof_toy_chi2s", [])
        obs_chi2 = res["chi2"]
        p_value = res["gof_pvalue"]

        if toy_chi2s:
            clean = [c for c in toy_chi2s if c < 1000]
            if clean:
                ax.hist(clean, bins=30, color="steelblue", alpha=0.7, label="Toys")
                ax.axvline(
                    obs_chi2, color="red", linewidth=2, linestyle="--",
                    label=f"Obs. = {obs_chi2:.1f}",
                )
                p_str = f"{p_value:.3f}" if p_value is not None else "N/A"
                ax.set_xlabel(r"$\chi^2$")
                ax.set_ylabel("Toys")
                ax.legend(fontsize="x-small")
                ax.text(
                    0.95, 0.95,
                    f"{approach_labels[approach]}\n$p$ = {p_str}",
                    transform=ax.transAxes, ha="right", va="top",
                    fontsize="small",
                    bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
                )

    mh.label.exp_label(
        exp="CMS", data=True,
        llabel="Open Data",
        rlabel=r"$\sqrt{s} = 8$ TeV, 10% data",
        loc=0, ax=axes[0],
    )

    fig.tight_layout()
    save_fig(fig, "gof_toys_10pct")


def main():
    log.info("Generating post-fit figures")
    plot_np_pulls()
    plot_mu_comparison()
    plot_gof_toys()
    log.info("All post-fit figures generated.")


if __name__ == "__main__":
    main()
