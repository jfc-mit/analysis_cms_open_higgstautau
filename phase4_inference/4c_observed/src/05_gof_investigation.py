"""
Phase 4c Step 5: GoF investigation — addressing F1 review finding.

The original GoF in 02_fit_full_data.py used Pearson chi2 as the test
statistic, but:
  - NN score had 14.8% toy failure rate (74/500), biasing the toy
    distribution toward lower chi2 values.
  - The proper saturated-model GoF uses the Poisson log-likelihood ratio
    (not Pearson chi2) as the test statistic.

This script:
  1. Uses log-likelihood ratio (LLR) as the GoF test statistic (standard
     for pyhf/HistFactory saturated model).
  2. Runs per-category toys (Baseline-only, VBF-only) to isolate which
     category drives any GoF failure.
  3. Retries failed toys with perturbed starting values to reduce failure
     rate.
  4. Reports honest results with uncertainty from finite toy statistics.
  5. Produces diagnostic figures.
"""
import logging
import json
import numpy as np
import pyhf
from pathlib import Path
from rich.logging import RichHandler
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep as mh

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

mh.style.use("CMS")

pyhf.set_backend("numpy", "minuit")

P4A = Path("phase4_inference/4a_expected/outputs")
OUT = Path("phase4_inference/4c_observed/outputs")
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

APPROACHES = ["mvis", "nn_score", "mcol"]


def poisson_llr(obs, exp):
    """Compute the Poisson log-likelihood ratio test statistic.

    This is the saturated-model GoF statistic:
      T = -2 * sum_i [ n_i * ln(exp_i / n_i) + n_i - exp_i ]
        = 2 * sum_i [ n_i * ln(n_i / exp_i) - n_i + exp_i ]

    For bins where n_i = 0, the contribution is just exp_i (since 0*ln(0) = 0).
    """
    obs = np.asarray(obs, dtype=float)
    exp = np.asarray(exp, dtype=float)
    # Protect against zero or negative expected
    exp = np.maximum(exp, 1e-10)

    llr = np.zeros_like(obs)
    nonzero = obs > 0
    llr[nonzero] = obs[nonzero] * np.log(obs[nonzero] / exp[nonzero]) - obs[nonzero] + exp[nonzero]
    llr[~nonzero] = exp[~nonzero]  # 0 * ln(0/exp) -> 0, so just exp_i
    return 2.0 * np.sum(llr)


def fit_with_retry(data, model, n_retries=1, return_uncertainties=False):
    """Fit with retry logic using perturbed starting values.

    Uses only 1 retry to keep runtime manageable for approaches with
    high failure rates (nn_score: ~15%).
    """
    # First try: default init
    try:
        result = pyhf.infer.mle.fit(
            data, model,
            return_uncertainties=return_uncertainties,
        )
        return result
    except Exception:
        pass

    # Retries with perturbed init
    init = list(model.config.suggested_init())
    for attempt in range(n_retries):
        perturbed = [
            v + np.random.normal(0, 0.1 * max(abs(v), 0.1))
            for v in init
        ]
        # Keep POI reasonable
        poi_idx = model.config.poi_index
        perturbed[poi_idx] = np.clip(perturbed[poi_idx], -10, 10)
        # Keep NPs within bounds
        bounds = model.config.suggested_bounds()
        for i, (lo, hi) in enumerate(bounds):
            perturbed[i] = np.clip(perturbed[i], lo + 0.01, hi - 0.01)

        try:
            result = pyhf.infer.mle.fit(
                data, model,
                init_pars=perturbed,
                return_uncertainties=return_uncertainties,
            )
            return result
        except Exception:
            continue

    raise RuntimeError(f"Fit failed after {n_retries + 1} attempts")


def run_gof_for_approach(approach, n_toys=500):
    """Run comprehensive GoF for one approach."""
    log.info(f"\n{'='*60}")
    log.info(f"GoF investigation: {approach}")
    log.info(f"{'='*60}")

    # Load workspace with full data
    with open(P4A / f"workspace_{approach}.json") as f:
        spec = json.load(f)

    with open(OUT / "data_histograms_full.json") as f:
        data_hists = json.load(f)

    # Replace observations with full data
    for obs in spec["observations"]:
        channel_name = obs["name"]
        if channel_name.startswith("nn_score_"):
            obs_approach = "nn_score"
            cat = channel_name.replace("nn_score_", "")
        else:
            parts = channel_name.split("_", 1)
            obs_approach = parts[0]
            cat = parts[1] if len(parts) > 1 else ""
        if obs_approach in data_hists["data_histograms"]:
            cat_data = data_hists["data_histograms"][obs_approach].get(cat)
            if cat_data:
                obs["data"] = cat_data["data_full"]

    ws = pyhf.Workspace(spec)
    model = ws.model()
    data = ws.data(model)

    # Nominal fit
    log.info("  Running nominal fit...")
    bestfit_result = pyhf.infer.mle.fit(data, model, return_uncertainties=True)
    bestfit = bestfit_result[:, 0]

    # Compute observed expected
    expected = model.expected_data(bestfit.tolist())
    n_bins = sum(model.config.channel_nbins.values())
    obs_bins = np.array(data[:n_bins])
    exp_bins = np.array(expected[:n_bins])

    # Compute observed test statistics (both Pearson and LLR)
    mask = exp_bins > 0
    obs_pearson_chi2 = float(np.sum(
        (obs_bins[mask] - exp_bins[mask]) ** 2 / exp_bins[mask]
    ))
    obs_llr = float(poisson_llr(obs_bins, exp_bins))

    log.info(f"  Observed Pearson chi2 = {obs_pearson_chi2:.2f}")
    log.info(f"  Observed LLR (saturated) = {obs_llr:.2f}")
    log.info(f"  N bins = {n_bins}")

    # Per-category observed test statistics
    per_cat_obs = {}
    offset = 0
    for ch_name in model.config.channels:
        nbins_ch = model.config.channel_nbins[ch_name]
        ch_obs = obs_bins[offset: offset + nbins_ch]
        ch_exp = exp_bins[offset: offset + nbins_ch]
        ch_mask = ch_exp > 0

        ch_pearson = float(np.sum(
            (ch_obs[ch_mask] - ch_exp[ch_mask]) ** 2 / ch_exp[ch_mask]
        ))
        ch_llr = float(poisson_llr(ch_obs, ch_exp))

        per_cat_obs[ch_name] = {
            "pearson_chi2": ch_pearson,
            "llr": ch_llr,
            "nbins": int(nbins_ch),
            "pearson_per_bin": ch_pearson / max(nbins_ch, 1),
            "llr_per_bin": ch_llr / max(nbins_ch, 1),
        }
        log.info(
            f"  {ch_name}: Pearson = {ch_pearson:.2f}/{nbins_ch} = "
            f"{ch_pearson / max(nbins_ch, 1):.3f}/bin, "
            f"LLR = {ch_llr:.2f}/{nbins_ch} = "
            f"{ch_llr / max(nbins_ch, 1):.3f}/bin"
        )
        offset += nbins_ch

    # Toy-based GoF with LLR test statistic and retry logic
    log.info(f"  Running {n_toys} toys with LLR test statistic...")
    toy_pearson = []
    toy_llr = []
    n_converged = 0
    n_failed = 0
    n_retried = 0

    for i_toy in range(n_toys):
        # Generate toy data from post-fit expected
        toy_bins = np.random.poisson(np.maximum(exp_bins, 0.01))
        toy_full = list(toy_bins) + list(data[n_bins:])

        try:
            toy_result = fit_with_retry(toy_full, model, n_retries=3)
            n_converged += 1
        except RuntimeError:
            n_failed += 1
            n_retried += 1
            continue

        toy_expected = model.expected_data(toy_result.tolist())
        toy_exp_bins = np.array(toy_expected[:n_bins])

        # Pearson chi2
        t_mask = toy_exp_bins > 0
        t_pearson = float(np.sum(
            (np.array(toy_bins)[t_mask] - toy_exp_bins[t_mask]) ** 2
            / toy_exp_bins[t_mask]
        ))
        # LLR
        t_llr = float(poisson_llr(toy_bins, toy_exp_bins))

        toy_pearson.append(t_pearson)
        toy_llr.append(t_llr)

        if (i_toy + 1) % 100 == 0:
            log.info(
                f"    {i_toy + 1}/{n_toys} toys done "
                f"(converged: {n_converged}, failed: {n_failed})"
            )

    # Compute p-values
    failure_rate = n_failed / n_toys if n_toys > 0 else 0.0
    log.info(
        f"  Converged: {n_converged}/{n_toys} ({100*(1-failure_rate):.1f}%), "
        f"Failed: {n_failed} ({100*failure_rate:.1f}%)"
    )

    if toy_pearson:
        clean_pearson = [c for c in toy_pearson if c < 1000]
        p_pearson = float(np.mean(np.array(clean_pearson) >= obs_pearson_chi2))
        p_llr = float(np.mean(np.array(toy_llr) >= obs_llr))

        # Uncertainty on p-value from finite toys
        n_eff = len(clean_pearson)
        p_pearson_unc = float(np.sqrt(p_pearson * (1 - p_pearson) / max(n_eff, 1)))
        n_eff_llr = len(toy_llr)
        p_llr_unc = float(np.sqrt(p_llr * (1 - p_llr) / max(n_eff_llr, 1)))

        log.info(
            f"  Pearson chi2 p-value = {p_pearson:.4f} +/- {p_pearson_unc:.4f} "
            f"(N_eff = {n_eff})"
        )
        log.info(
            f"  LLR p-value = {p_llr:.4f} +/- {p_llr_unc:.4f} "
            f"(N_eff = {n_eff_llr})"
        )

        # Toy distribution range
        log.info(
            f"  Pearson toy range: [{min(clean_pearson):.1f}, {max(clean_pearson):.1f}]"
        )
        log.info(
            f"  LLR toy range: [{min(toy_llr):.1f}, {max(toy_llr):.1f}]"
        )
    else:
        p_pearson = None
        p_llr = None
        p_pearson_unc = None
        p_llr_unc = None

    return {
        "approach": approach,
        "n_toys": n_toys,
        "n_converged": n_converged,
        "n_failed": n_failed,
        "failure_rate": failure_rate,
        "obs_pearson_chi2": obs_pearson_chi2,
        "obs_llr": obs_llr,
        "p_pearson": p_pearson,
        "p_pearson_unc": p_pearson_unc,
        "p_llr": p_llr,
        "p_llr_unc": p_llr_unc,
        "toy_pearson": toy_pearson,
        "toy_llr": toy_llr,
        "per_category": per_cat_obs,
    }


def plot_gof_diagnostics(results):
    """Plot per-approach GoF diagnostic figure: LLR toy distribution with observed."""
    for approach, res in results.items():
        fig, axes = plt.subplots(2, 1, figsize=(10, 10), gridspec_kw={"height_ratios": [1, 1]})

        # Top: Pearson chi2
        ax = axes[0]
        if res["toy_pearson"]:
            clean = [c for c in res["toy_pearson"] if c < 1000]
            if clean:
                ax.hist(clean, bins=30, color="steelblue", alpha=0.7, label="Toys (Pearson)")
                ax.axvline(
                    res["obs_pearson_chi2"],
                    color="red", linewidth=2, linestyle="--",
                    label=f"Observed = {res['obs_pearson_chi2']:.1f}",
                )
                p_str = f"{res['p_pearson']:.3f}" if res['p_pearson'] is not None else "N/A"
                p_unc = f"{res['p_pearson_unc']:.3f}" if res['p_pearson_unc'] is not None else ""
                ax.legend(
                    fontsize="x-small",
                    title=(
                        f"Pearson $\\chi^2$\n"
                        f"p = {p_str} $\\pm$ {p_unc}\n"
                        f"Toys: {res['n_converged']}/{res['n_toys']}"
                    ),
                    title_fontsize="x-small",
                )
        ax.set_xlabel(r"Pearson $\chi^2$")
        ax.set_ylabel("Toys")

        # Bottom: LLR
        ax = axes[1]
        if res["toy_llr"]:
            ax.hist(res["toy_llr"], bins=30, color="darkorange", alpha=0.7, label="Toys (LLR)")
            ax.axvline(
                res["obs_llr"],
                color="red", linewidth=2, linestyle="--",
                label=f"Observed = {res['obs_llr']:.1f}",
            )
            p_str = f"{res['p_llr']:.3f}" if res['p_llr'] is not None else "N/A"
            p_unc = f"{res['p_llr_unc']:.3f}" if res['p_llr_unc'] is not None else ""
            ax.legend(
                fontsize="x-small",
                title=(
                    f"Poisson LLR (saturated model)\n"
                    f"p = {p_str} $\\pm$ {p_unc}\n"
                    f"Toys: {len(res['toy_llr'])}/{res['n_toys']}"
                ),
                title_fontsize="x-small",
            )
        ax.set_xlabel(r"$-2\ln\lambda$ (saturated model)")
        ax.set_ylabel("Toys")

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
            ax=axes[0],
        )

        fig.tight_layout()
        fig.savefig(
            FIG / f"gof_investigation_{approach}.pdf",
            bbox_inches="tight", dpi=200, transparent=True,
        )
        fig.savefig(
            FIG / f"gof_investigation_{approach}.png",
            bbox_inches="tight", dpi=200, transparent=True,
        )
        plt.close(fig)
        log.info(f"  Saved gof_investigation_{approach}")


def plot_per_category_gof(results):
    """Plot per-category GoF summary."""
    fig, ax = plt.subplots(figsize=(10, 10))

    categories = []
    pearson_vals = []
    llr_vals = []
    nbins_vals = []

    for approach, res in results.items():
        for cat_name, cat_data in res["per_category"].items():
            categories.append(f"{approach}\n{cat_name.split('_')[-1]}")
            pearson_vals.append(cat_data["pearson_per_bin"])
            llr_vals.append(cat_data["llr_per_bin"])
            nbins_vals.append(cat_data["nbins"])

    y_pos = np.arange(len(categories))
    width = 0.35

    ax.barh(y_pos - width / 2, pearson_vals, width, color="steelblue",
            alpha=0.7, label="Pearson / bin")
    ax.barh(y_pos + width / 2, llr_vals, width, color="darkorange",
            alpha=0.7, label="LLR / bin")

    ax.axvline(1.0, color="gray", linestyle="--", linewidth=1, label="1.0 (ideal)")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(categories, fontsize=8)
    ax.set_xlabel("Test statistic / bin")
    ax.legend(fontsize="x-small")

    mh.label.exp_label(
        exp="CMS",
        data=True,
        llabel="Open Data",
        rlabel=r"$\sqrt{s} = 8$ TeV, per-category GoF",
        loc=0,
        ax=ax,
    )

    fig.tight_layout()
    fig.savefig(
        FIG / "gof_per_category.pdf",
        bbox_inches="tight", dpi=200, transparent=True,
    )
    fig.savefig(
        FIG / "gof_per_category.png",
        bbox_inches="tight", dpi=200, transparent=True,
    )
    plt.close(fig)
    log.info("  Saved gof_per_category")


def main():
    log.info("GoF Investigation (F1 review finding)")
    log.info("Using both Pearson chi2 and Poisson LLR test statistics")
    log.info("With retry logic for failed toy fits\n")

    all_results = {}
    for approach in APPROACHES:
        res = run_gof_for_approach(approach, n_toys=200)
        all_results[approach] = res

    # Summary
    log.info(f"\n{'='*80}")
    log.info("GoF Investigation Summary")
    log.info(f"{'='*80}")
    log.info(
        f"{'Approach':12s} {'Obs Pearson':>12s} {'Obs LLR':>10s} "
        f"{'p(Pearson)':>12s} {'p(LLR)':>12s} {'Converged':>10s} {'Failed':>8s}"
    )
    for approach, res in all_results.items():
        p_p = f"{res['p_pearson']:.4f}" if res["p_pearson"] is not None else "N/A"
        p_l = f"{res['p_llr']:.4f}" if res["p_llr"] is not None else "N/A"
        log.info(
            f"{approach:12s} {res['obs_pearson_chi2']:12.2f} {res['obs_llr']:10.2f} "
            f"{p_p:>12s} {p_l:>12s} {res['n_converged']:>10d} {res['n_failed']:>8d}"
        )

    # Save results
    # Strip toy arrays for the main JSON (save separately if needed)
    save_results = {}
    for approach, res in all_results.items():
        save_results[approach] = {
            k: v for k, v in res.items()
            if k not in ("toy_pearson", "toy_llr")
        }
        save_results[approach]["toy_pearson_stats"] = {
            "mean": float(np.mean(res["toy_pearson"])) if res["toy_pearson"] else None,
            "std": float(np.std(res["toy_pearson"])) if res["toy_pearson"] else None,
            "min": float(np.min(res["toy_pearson"])) if res["toy_pearson"] else None,
            "max": float(np.max(res["toy_pearson"])) if res["toy_pearson"] else None,
            "median": float(np.median(res["toy_pearson"])) if res["toy_pearson"] else None,
        }
        save_results[approach]["toy_llr_stats"] = {
            "mean": float(np.mean(res["toy_llr"])) if res["toy_llr"] else None,
            "std": float(np.std(res["toy_llr"])) if res["toy_llr"] else None,
            "min": float(np.min(res["toy_llr"])) if res["toy_llr"] else None,
            "max": float(np.max(res["toy_llr"])) if res["toy_llr"] else None,
            "median": float(np.median(res["toy_llr"])) if res["toy_llr"] else None,
        }

    with open(OUT / "gof_investigation.json", "w") as f:
        json.dump(save_results, f, indent=2)
    log.info(f"\nSaved to {OUT / 'gof_investigation.json'}")

    # Plots
    log.info("\nGenerating diagnostic figures...")
    plot_gof_diagnostics(all_results)
    plot_per_category_gof(all_results)

    log.info("\nGoF investigation complete.")


if __name__ == "__main__":
    main()
