"""
Phase 4c Step 2: Fit FULL data for signal strength.

For each approach (m_vis, nn_score, m_col):
- Load the pyhf workspace from Phase 4a
- Replace Asimov observations with actual full data
- Fit for mu -> report mu_hat, sigma(mu)
- Compute NP pulls, GoF (chi2 + toy-based), significance
- Compare to BOTH expected (4a) AND 10% (4b)
"""
import logging
import json
import numpy as np
import pyhf
from pathlib import Path
from rich.logging import RichHandler
from scipy.stats import norm

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

pyhf.set_backend("numpy", "minuit")

P4A = Path("phase4_inference/4a_expected/outputs")
P4B = Path("phase4_inference/4b_partial/outputs")
OUT = Path("phase4_inference/4c_observed/outputs")

APPROACHES = ["mvis", "nn_score", "mcol"]


def load_workspace_with_full_data(approach):
    """Load 4a workspace and replace Asimov data with full real data."""
    # Load workspace
    with open(P4A / f"workspace_{approach}.json") as f:
        spec = json.load(f)

    # Load full data histograms
    with open(OUT / "data_histograms_full.json") as f:
        data_hists = json.load(f)

    # Replace observations with full data
    for obs in spec["observations"]:
        channel_name = obs["name"]
        # Parse approach and category from channel name
        if channel_name.startswith("nn_score_"):
            obs_approach = "nn_score"
            cat = channel_name.replace("nn_score_", "")
        else:
            parts = channel_name.split("_", 1)
            obs_approach = parts[0]
            cat = parts[1] if len(parts) > 1 else ""

        # Get the full data
        if obs_approach in data_hists["data_histograms"]:
            cat_data = data_hists["data_histograms"][obs_approach].get(cat)
            if cat_data:
                full_data = cat_data["data_full"]
                log.info(
                    f"  {channel_name}: replacing Asimov with full data "
                    f"(sum={sum(full_data):.0f})"
                )
                obs["data"] = full_data

    return spec


def fit_data(approach):
    """Fit full data for one approach."""
    log.info(f"\n{'='*60}")
    log.info(f"=== Fitting {approach} on FULL data ===")
    log.info(f"{'='*60}")

    spec = load_workspace_with_full_data(approach)

    ws = pyhf.Workspace(spec)
    model = ws.model()
    data = ws.data(model)

    log.info(f"  Model: {model.config.npars} parameters")
    log.info(f"  Data length: {len(data)}")
    log.info(f"  Channels: {model.config.channels}")

    # Maximum likelihood fit
    log.info("  Running MLE fit...")
    result = pyhf.infer.mle.fit(
        data, model, return_uncertainties=True,
    )
    bestfit = result[:, 0]
    uncertainties = result[:, 1]

    mu_idx = model.config.poi_index
    mu_hat = float(bestfit[mu_idx])
    mu_err = float(uncertainties[mu_idx])
    log.info(f"  mu_hat = {mu_hat:.4f} +/- {mu_err:.4f}")

    # NP pulls — standard convention: pull = (bestfit - prefit) / prefit_unc
    # For Gaussian-constrained NPs, prefit_unc = 1.0, so pull = bestfit - init.
    # Also store the "constraint" definition: (bestfit - init) / postfit_unc.
    par_names = model.config.par_names
    np_pulls = {}
    for i, name in enumerate(par_names):
        if name == "mu":
            continue
        if "staterror" in name:
            continue
        init_val = model.config.suggested_init()[i]
        prefit_unc = 1.0  # standard Gaussian constraint
        pull_standard = float(bestfit[i] - init_val) / prefit_unc
        pull_constraint = (
            float((bestfit[i] - init_val) / uncertainties[i])
            if uncertainties[i] > 1e-10
            else 0.0
        )
        np_pulls[name] = {
            "bestfit": float(bestfit[i]),
            "uncertainty": float(uncertainties[i]),
            "pull": pull_standard,
            "pull_constraint": pull_constraint,
        }

    # Log NP pulls (standard convention)
    log.info("  NP pulls — standard convention: (bestfit - prefit) / prefit_unc:")
    for name, info in sorted(
        np_pulls.items(), key=lambda x: abs(x[1]["pull"]), reverse=True
    ):
        pull = info["pull"]
        flag = " *** " if abs(pull) > 2.0 else " ** " if abs(pull) > 1.5 else ""
        log.info(
            f"    {name:30s}: {info['bestfit']:+.4f} +/- {info['uncertainty']:.4f} "
            f"(pull_std = {pull:+.3f}, pull_constr = {info['pull_constraint']:+.3f}){flag}"
        )

    # Goodness of fit: chi2
    expected = model.expected_data(bestfit.tolist())
    n_bins = sum(model.config.channel_nbins.values())
    obs_bins = np.array(data[:n_bins])
    exp_bins = np.array(expected[:n_bins])

    mask = exp_bins > 0
    chi2_val = np.sum((obs_bins[mask] - exp_bins[mask]) ** 2 / exp_bins[mask])
    ndf_full = int(mask.sum()) - model.config.npars
    # Alternative chi2/ndf using only free parameters that are actually
    # constrained by data (exclude staterror gammas from ndf count for
    # a simpler interpretable metric)
    n_free_nps = sum(
        1 for nm in par_names
        if nm != "mu" and "staterror" not in nm
    )
    ndf_simple = int(mask.sum()) - n_free_nps - 1  # -1 for mu
    chi2_ndf_simple = chi2_val / max(ndf_simple, 1)
    log.info(
        f"  chi2 = {chi2_val:.2f}, ndf(full) = {ndf_full}, "
        f"ndf(NPs+mu only) = {ndf_simple}, chi2/ndf(simple) = {chi2_ndf_simple:.4f}"
    )

    # Per-category chi2 (for GoF investigation)
    per_cat_gof = {}
    offset = 0
    for ch_name in model.config.channels:
        nbins_ch = model.config.channel_nbins[ch_name]
        ch_obs = obs_bins[offset : offset + nbins_ch]
        ch_exp = exp_bins[offset : offset + nbins_ch]
        ch_mask = ch_exp > 0
        ch_chi2 = float(np.sum(
            (ch_obs[ch_mask] - ch_exp[ch_mask]) ** 2 / ch_exp[ch_mask]
        ))
        ch_ndf = int(ch_mask.sum())
        per_cat_gof[ch_name] = {
            "chi2": ch_chi2,
            "nbins": ch_ndf,
            "chi2_per_bin": ch_chi2 / max(ch_ndf, 1),
        }
        log.info(
            f"  Per-category GoF: {ch_name}: chi2 = {ch_chi2:.2f}, "
            f"nbins = {ch_ndf}, chi2/bin = {ch_chi2 / max(ch_ndf, 1):.3f}"
        )
        offset += nbins_ch

    # Toy-based GoF p-value (500 toys for better statistics)
    n_toys = 500
    log.info(f"  Running {n_toys} toys for GoF...")
    toy_chi2s = []
    n_converged = 0
    n_outlier = 0
    n_failed = 0

    for i_toy in range(n_toys):
        toy_bins = np.random.poisson(np.maximum(exp_bins, 0.01))
        toy_full = list(toy_bins) + list(data[n_bins:])
        try:
            toy_result = pyhf.infer.mle.fit(
                toy_full, model, return_uncertainties=False,
            )
            toy_expected = model.expected_data(toy_result.tolist())
            toy_exp_bins = np.array(toy_expected[:n_bins])
            toy_mask = toy_exp_bins > 0
            toy_chi2 = np.sum(
                (np.array(toy_bins)[toy_mask] - toy_exp_bins[toy_mask]) ** 2
                / toy_exp_bins[toy_mask]
            )
            if toy_chi2 > 1000:
                n_outlier += 1
            else:
                n_converged += 1
            toy_chi2s.append(float(toy_chi2))
        except Exception:
            n_failed += 1

        if (i_toy + 1) % 100 == 0:
            log.info(f"    {i_toy + 1}/{n_toys} toys done")

    clean_chi2s = [c for c in toy_chi2s if c < 1000]
    p_value = (
        float(np.mean(np.array(clean_chi2s) >= chi2_val)) if clean_chi2s else None
    )
    failure_rate = n_failed / n_toys if n_toys > 0 else 0.0
    log.info(
        f"  GoF p-value = {p_value} "
        f"(converged={n_converged}, outliers={n_outlier}, failed={n_failed}, "
        f"failure_rate={failure_rate:.1%})"
    )
    if failure_rate > 0.05:
        log.warning(
            f"  WARNING: {failure_rate:.1%} toy convergence failure rate. "
            f"This may bias the toy distribution."
        )

    # Significance (observed)
    log.info("  Computing observed significance...")
    try:
        obs_pval, exp_pvals = pyhf.infer.hypotest(
            0.0,
            data,
            model,
            test_stat="q0",
            return_expected_set=True,
        )
        obs_sig = float(norm.isf(obs_pval))
        exp_sig = float(norm.isf(exp_pvals[2]))
        log.info(f"  Observed significance: {obs_sig:.3f} sigma")
        log.info(f"  Expected significance: {exp_sig:.3f} sigma")
    except Exception as e:
        log.warning(f"  Significance failed: {e}")
        obs_sig = None
        exp_sig = None

    # CLs upper limit
    log.info("  Computing CLs upper limit...")
    try:
        poi_values = np.linspace(0.0, 15.0, 61)
        cls_scan = []
        for poi_val in poi_values:
            try:
                obs_cls, exp_cls = pyhf.infer.hypotest(
                    poi_val,
                    data,
                    model,
                    test_stat="qtilde",
                    return_expected_set=True,
                )
                cls_scan.append(
                    {
                        "poi": float(poi_val),
                        "obs_cls": float(obs_cls),
                        "exp_cls": [float(x) for x in exp_cls],
                    }
                )
            except Exception:
                pass

        # Find 95% CL crossing
        obs_limit_95 = None
        exp_limit_95 = None
        if cls_scan:
            poi_arr = np.array([r["poi"] for r in cls_scan])
            obs_arr = np.array([r["obs_cls"] for r in cls_scan])
            exp_med_arr = np.array([r["exp_cls"][2] for r in cls_scan])
            for i in range(len(poi_arr) - 1):
                if obs_arr[i] >= 0.05 >= obs_arr[i + 1]:
                    frac = (0.05 - obs_arr[i]) / (obs_arr[i + 1] - obs_arr[i])
                    obs_limit_95 = float(
                        poi_arr[i] + frac * (poi_arr[i + 1] - poi_arr[i])
                    )
                if exp_med_arr[i] >= 0.05 >= exp_med_arr[i + 1]:
                    frac = (0.05 - exp_med_arr[i]) / (
                        exp_med_arr[i + 1] - exp_med_arr[i]
                    )
                    exp_limit_95 = float(
                        poi_arr[i] + frac * (poi_arr[i + 1] - poi_arr[i])
                    )

        log.info(f"  Observed 95% CL limit: {obs_limit_95}")
        log.info(f"  Expected 95% CL limit: {exp_limit_95}")
    except Exception as e:
        log.warning(f"  CLs scan failed: {e}")
        obs_limit_95 = None
        exp_limit_95 = None
        cls_scan = []

    # Post-fit expected yields per channel
    postfit_yields = {}
    offset = 0
    for ch_name in model.config.channels:
        nbins = model.config.channel_nbins[ch_name]
        ch_obs = obs_bins[offset : offset + nbins]
        ch_exp = exp_bins[offset : offset + nbins]
        postfit_yields[ch_name] = {
            "observed": ch_obs.tolist(),
            "expected_postfit": ch_exp.tolist(),
        }
        offset += nbins

    return {
        "approach": approach,
        "mu_hat": mu_hat,
        "mu_err": mu_err,
        "obs_significance": obs_sig,
        "exp_significance": exp_sig,
        "obs_limit_95": obs_limit_95,
        "exp_limit_95": exp_limit_95,
        "chi2": float(chi2_val),
        "ndf": ndf_full,
        "ndf_simple": ndf_simple,
        "chi2_ndf_simple": float(chi2_ndf_simple),
        "gof_pvalue": p_value,
        "gof_n_toys": n_toys,
        "gof_n_converged": n_converged,
        "gof_n_outliers": n_outlier,
        "gof_n_failed": n_failed,
        "gof_failure_rate": failure_rate,
        "gof_toy_chi2s": toy_chi2s,
        "per_category_gof": per_cat_gof,
        "np_pulls": np_pulls,
        "cls_scan": cls_scan,
        "postfit_yields": postfit_yields,
        "bestfit_pars": bestfit.tolist(),
    }


def main():
    # Load expected and 10% results for comparison
    with open(P4A / "expected_results.json") as f:
        expected = json.load(f)

    with open(P4B / "partial_data_results.json") as f:
        partial = json.load(f)

    results = {}
    for approach in APPROACHES:
        res = fit_data(approach)
        results[approach] = res

    # Three-way comparison summary
    log.info(f"\n{'='*80}")
    log.info("=== THREE-WAY COMPARISON: Expected vs 10% vs Full ===")
    log.info(f"{'='*80}")
    log.info(
        f"{'Approach':12s} {'mu_exp':>10s} {'sig_exp':>10s} "
        f"{'mu_10%':>10s} {'sig_10%':>10s} "
        f"{'mu_full':>10s} {'sig_full':>10s} {'Pull':>8s} {'GoF p':>8s}"
    )
    for approach in APPROACHES:
        r = results[approach]
        e = expected[approach]
        p = partial[approach]
        pull = (r["mu_hat"] - 1.0) / r["mu_err"] if r["mu_err"] > 0 else 0.0
        gof_p = r["gof_pvalue"] if r["gof_pvalue"] is not None else -1
        log.info(
            f"{approach:12s} {e['mu_hat']:+10.3f} {e['mu_err']:10.3f} "
            f"{p['mu_hat']:+10.3f} {p['mu_err']:10.3f} "
            f"{r['mu_hat']:+10.3f} {r['mu_err']:10.3f} {pull:+8.3f} "
            f"{gof_p:8.4f}"
        )

    # Consistency checks
    log.info("\n=== Consistency Checks ===")
    for approach in APPROACHES:
        r = results[approach]
        e = expected[approach]
        p = partial[approach]

        # Pull of full data mu from SM (mu=1)
        pull_from_sm = (r["mu_hat"] - 1.0) / r["mu_err"] if r["mu_err"] > 0 else 0.0

        # Pull of full from 10% result
        combined_err = np.sqrt(r["mu_err"] ** 2 + p["mu_err"] ** 2)
        pull_from_10pct = (
            (r["mu_hat"] - p["mu_hat"]) / combined_err if combined_err > 0 else 0.0
        )

        log.info(f"  {approach}:")
        log.info(f"    mu_full = {r['mu_hat']:.3f} +/- {r['mu_err']:.3f}")
        log.info(f"    Pull from SM: {pull_from_sm:.2f} sigma")
        log.info(f"    Pull from 10%: {pull_from_10pct:.2f} sigma")
        log.info(f"    sigma(mu) ratio full/expected: {r['mu_err']/e['mu_err']:.3f}")
        log.info(f"    GoF p-value: {r['gof_pvalue']}")

    # Flag any issues
    log.info("\n=== Flags ===")
    any_flag = False
    for approach in APPROACHES:
        r = results[approach]
        pull_mu = (r["mu_hat"] - 1.0) / r["mu_err"] if r["mu_err"] > 0 else 0.0
        if abs(pull_mu) > 3.0:
            log.warning(f"  {approach}: mu pull = {pull_mu:.2f} (> 3 sigma from SM)")
            any_flag = True
        if r["gof_pvalue"] is not None and r["gof_pvalue"] < 0.05:
            log.warning(
                f"  {approach}: GoF p-value = {r['gof_pvalue']:.4f} (< 0.05)"
            )
            any_flag = True
        if r["gof_failure_rate"] > 0.05:
            log.warning(
                f"  {approach}: GoF toy failure rate = {r['gof_failure_rate']:.1%} "
                f"(> 5%, may bias toy distribution)"
            )
            any_flag = True
        for np_name, np_info in r["np_pulls"].items():
            # Flag using standard convention (pull = bestfit for init=0)
            if abs(np_info["pull"]) > 2.0:
                log.warning(
                    f"  {approach}: NP {np_name} standard pull = "
                    f"{np_info['pull']:.2f} (> 2 sigma)"
                )
                any_flag = True

    if not any_flag:
        log.info("  No flags raised. All results look healthy.")

    # Save
    with open(OUT / "observed_results.json", "w") as f:
        json.dump(results, f, indent=2)
    log.info(f"\nSaved to {OUT / 'observed_results.json'}")


if __name__ == "__main__":
    main()
