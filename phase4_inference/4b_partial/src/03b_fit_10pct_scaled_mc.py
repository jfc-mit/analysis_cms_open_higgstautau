"""
Phase 4b Step 3b: Fit 10% data with MC templates scaled by 0.1.

Instead of scaling data by 10 (which creates non-Poisson data),
we scale the MC templates by 0.1 to match the 10% data statistics.
This preserves the Poisson nature of the data.

For each approach:
- Rebuild workspace with templates * 0.1
- Use raw 10% data as observations
- Fit for mu
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
OUT = Path("phase4_inference/4b_partial/outputs")

APPROACHES = ["mvis", "nn_score", "mcol"]
SCALE = 0.1  # Scale MC by this factor to match 10% data


def build_scaled_workspace(approach):
    """Build a workspace with MC templates scaled by 0.1."""
    with open(P4A / f"workspace_{approach}.json") as f:
        spec = json.load(f)

    # Scale all sample data by 0.1
    for channel in spec["channels"]:
        for sample in channel["samples"]:
            # Scale nominal data
            sample["data"] = [x * SCALE for x in sample["data"]]

            # Scale modifiers that have absolute data
            for mod in sample["modifiers"]:
                if mod["type"] == "histosys":
                    mod["data"]["hi_data"] = [x * SCALE for x in mod["data"]["hi_data"]]
                    mod["data"]["lo_data"] = [x * SCALE for x in mod["data"]["lo_data"]]
                elif mod["type"] == "staterror":
                    # staterror data are absolute uncertainties, scale them too
                    mod["data"] = [x * SCALE for x in mod["data"]]

    # Replace observations with raw 10% data
    with open(OUT / "data_histograms_10pct.json") as f:
        data_hists = json.load(f)

    for obs in spec["observations"]:
        channel_name = obs["name"]
        # Parse approach and category
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
                raw_data = cat_data["data_10pct"]
                log.info(
                    f"  {channel_name}: raw 10% data sum={sum(raw_data):.0f}"
                )
                obs["data"] = raw_data

    return spec


def fit_data(approach):
    """Fit 10% data with scaled MC for one approach."""
    log.info(f"\n=== Fitting {approach} (scaled MC x0.1) ===")

    spec = build_scaled_workspace(approach)

    ws = pyhf.Workspace(spec)
    model = ws.model()
    data = ws.data(model)

    log.info(f"  Model: {model.config.npars} parameters")

    # MLE fit
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

    # NP pulls
    par_names = model.config.par_names
    np_pulls = {}
    for i, name in enumerate(par_names):
        if name == "mu":
            continue
        if "staterror" in name:
            continue
        init_val = model.config.suggested_init()[i]
        np_pulls[name] = {
            "bestfit": float(bestfit[i]),
            "uncertainty": float(uncertainties[i]),
            "pull": float((bestfit[i] - init_val) / uncertainties[i])
            if uncertainties[i] > 1e-10
            else 0.0,
        }

    log.info("  NP pulls (sorted by |pull|):")
    for name, info in sorted(
        np_pulls.items(), key=lambda x: abs(x[1]["pull"]), reverse=True
    ):
        pull = info["pull"]
        flag = " *** " if abs(pull) > 2.0 else " ** " if abs(pull) > 1.5 else ""
        log.info(
            f"    {name:30s}: {info['bestfit']:+.4f} +/- {info['uncertainty']:.4f} "
            f"(pull = {pull:+.3f}){flag}"
        )

    # GoF chi2
    expected = model.expected_data(bestfit.tolist())
    n_bins = sum(model.config.channel_nbins.values())
    obs_bins = np.array(data[:n_bins])
    exp_bins = np.array(expected[:n_bins])

    mask = exp_bins > 0
    chi2_val = np.sum((obs_bins[mask] - exp_bins[mask]) ** 2 / exp_bins[mask])
    ndf = int(mask.sum()) - model.config.npars
    chi2_ndf = chi2_val / max(ndf, 1)
    log.info(f"  chi2 = {chi2_val:.2f}, ndf = {ndf}, chi2/ndf = {chi2_ndf:.4f}")

    # Toy-based GoF
    log.info("  Running 200 toys for GoF...")
    toy_chi2s = []
    n_converged = 0
    n_outlier = 0
    n_failed = 0

    for i_toy in range(200):
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

        if (i_toy + 1) % 50 == 0:
            log.info(f"    {i_toy + 1}/200 toys done")

    clean_chi2s = [c for c in toy_chi2s if c < 1000]
    p_value = (
        float(np.mean(np.array(clean_chi2s) >= chi2_val)) if clean_chi2s else None
    )
    log.info(
        f"  GoF p-value = {p_value} "
        f"(converged={n_converged}, outliers={n_outlier}, failed={n_failed})"
    )

    # Significance
    log.info("  Computing significance...")
    try:
        obs_pval, exp_pvals = pyhf.infer.hypotest(
            0.0, data, model, test_stat="q0", return_expected_set=True,
        )
        obs_sig = float(norm.isf(obs_pval))
        exp_sig = float(norm.isf(exp_pvals[2]))
        log.info(f"  Observed significance: {obs_sig:.3f} sigma")
    except Exception as e:
        log.warning(f"  Significance failed: {e}")
        obs_sig = None
        exp_sig = None

    # CLs upper limit scan
    log.info("  Computing CLs scan...")
    cls_scan = []
    obs_limit_95 = None
    exp_limit_95 = None
    try:
        poi_values = np.linspace(0.0, 15.0, 61)
        for poi_val in poi_values:
            try:
                obs_cls, exp_cls = pyhf.infer.hypotest(
                    poi_val, data, model,
                    test_stat="qtilde",
                    return_expected_set=True,
                )
                cls_scan.append({
                    "poi": float(poi_val),
                    "obs_cls": float(obs_cls),
                    "exp_cls": [float(x) for x in exp_cls],
                })
            except Exception:
                pass

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

    return {
        "approach": approach,
        "mu_hat": mu_hat,
        "mu_err": mu_err,
        "obs_significance": obs_sig,
        "exp_significance": exp_sig,
        "obs_limit_95": obs_limit_95,
        "exp_limit_95": exp_limit_95,
        "chi2": float(chi2_val),
        "ndf": ndf,
        "chi2_ndf": float(chi2_ndf),
        "gof_pvalue": p_value,
        "gof_n_converged": n_converged,
        "gof_n_outliers": n_outlier,
        "gof_n_failed": n_failed,
        "gof_toy_chi2s": toy_chi2s,
        "np_pulls": np_pulls,
        "cls_scan": cls_scan,
        "method": "scaled_mc_0p1",
    }


def main():
    with open(P4A / "expected_results.json") as f:
        expected = json.load(f)

    results = {}
    for approach in APPROACHES:
        res = fit_data(approach)
        results[approach] = res

    # Summary
    log.info("\n=== 10% Data Results (MC scaled x0.1) ===")
    log.info(
        f"{'Approach':12s} {'mu_10%':>10s} {'sig(mu)':>10s} "
        f"{'mu_exp':>10s} {'sig_exp':>10s} {'Pull':>8s} {'GoF p':>8s}"
    )
    for approach in APPROACHES:
        r = results[approach]
        e = expected[approach]
        pull = (r["mu_hat"] - 1.0) / r["mu_err"] if r["mu_err"] > 0 else 0.0
        gof_p = r["gof_pvalue"] if r["gof_pvalue"] is not None else -1
        log.info(
            f"{approach:12s} {r['mu_hat']:+10.3f} {r['mu_err']:10.3f} "
            f"{e['mu_hat']:10.3f} {e['mu_err']:10.3f} {pull:+8.3f} "
            f"{gof_p:8.4f}"
        )

    # Flags
    log.info("\n=== Flags ===")
    any_flag = False
    for approach in APPROACHES:
        r = results[approach]
        pull_mu = (r["mu_hat"] - 1.0) / r["mu_err"] if r["mu_err"] > 0 else 0.0
        if abs(pull_mu) > 2.0:
            log.warning(f"  {approach}: mu pull = {pull_mu:.2f} (> 2 sigma)")
            any_flag = True
        if r["gof_pvalue"] is not None and r["gof_pvalue"] < 0.05:
            log.warning(
                f"  {approach}: GoF p-value = {r['gof_pvalue']:.4f} (< 0.05)"
            )
            any_flag = True
        for np_name, np_info in r["np_pulls"].items():
            if abs(np_info["pull"]) > 2.0:
                log.warning(
                    f"  {approach}: NP {np_name} pull = {np_info['pull']:.2f}"
                )
                any_flag = True

    if not any_flag:
        log.info("  No flags raised.")

    # Save
    with open(OUT / "partial_data_results.json", "w") as f:
        json.dump(results, f, indent=2)
    log.info(f"\nSaved to {OUT / 'partial_data_results.json'}")


if __name__ == "__main__":
    main()
