"""
Phase 4c Step 3: Diagnostic checks on full data.

- Per-category fit (Baseline-only, VBF-only)
- Pre-fit data/MC chi2 per discriminant per category
- Impact ranking of NPs on mu
"""
import logging
import json
import numpy as np
import pyhf
from pathlib import Path
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

pyhf.set_backend("numpy", "minuit")

P4A = Path("phase4_inference/4a_expected/outputs")
OUT = Path("phase4_inference/4c_observed/outputs")

APPROACHES = ["mvis", "nn_score", "mcol"]


def prefit_data_mc_chi2():
    """Compute pre-fit data/MC chi2 per approach per category."""
    log.info("\n=== Pre-fit Data/MC chi2 ===")

    with open(P4A / "nominal_templates.json") as f:
        nominal = json.load(f)

    with open(OUT / "data_histograms_full.json") as f:
        data_hists = json.load(f)

    results = {}
    for approach in APPROACHES:
        results[approach] = {}
        for cat in ["baseline", "vbf"]:
            # Full data
            data_full = np.array(
                data_hists["data_histograms"][approach][cat]["data_full"]
            )

            # Sum all MC processes
            mc_total = None
            for proc_name, proc_data in nominal[approach][cat]["processes"].items():
                h = np.array(proc_data["nominal"])
                if mc_total is None:
                    mc_total = h.copy()
                else:
                    mc_total += h

            # Chi2 (bins where MC > 0)
            mask = mc_total > 0
            chi2 = np.sum(
                (data_full[mask] - mc_total[mask]) ** 2 / mc_total[mask]
            )
            ndf = int(mask.sum()) - 1  # -1 for normalization
            chi2_ndf = chi2 / max(ndf, 1)

            results[approach][cat] = {
                "chi2": float(chi2),
                "ndf": ndf,
                "chi2_ndf": float(chi2_ndf),
                "data_total": float(data_full.sum()),
                "mc_total": float(mc_total.sum()),
                "ratio": float(data_full.sum() / mc_total.sum()),
            }

            log.info(
                f"  {approach:10s} {cat:10s}: chi2/ndf = {chi2:.1f}/{ndf} = {chi2_ndf:.2f}, "
                f"data/MC = {data_full.sum():.0f}/{mc_total.sum():.0f} = "
                f"{data_full.sum() / mc_total.sum():.3f}"
            )

    return results


def per_category_fit():
    """Fit mu separately in Baseline and VBF categories."""
    log.info("\n=== Per-Category Fit (Full Data) ===")

    with open(OUT / "data_histograms_full.json") as f:
        data_hists = json.load(f)

    results = {}

    for approach in APPROACHES:
        results[approach] = {}

        with open(P4A / f"workspace_{approach}.json") as f:
            spec = json.load(f)

        for target_cat in ["baseline", "vbf"]:
            target_channel = f"{approach}_{target_cat}"

            # Build single-channel workspace
            single_spec = {
                "channels": [
                    ch
                    for ch in spec["channels"]
                    if ch["name"] == target_channel
                ],
                "observations": [],
                "measurements": spec["measurements"],
                "version": "1.0.0",
            }

            # Set observation for this channel
            cat_data = data_hists["data_histograms"][approach].get(target_cat)
            if cat_data:
                single_spec["observations"].append(
                    {
                        "name": target_channel,
                        "data": cat_data["data_full"],
                    }
                )
            else:
                log.warning(f"  No data for {target_channel}")
                continue

            try:
                single_ws = pyhf.Workspace(single_spec)
                single_model = single_ws.model()
                single_data = single_ws.data(single_model)

                result = pyhf.infer.mle.fit(
                    single_data,
                    single_model,
                    return_uncertainties=True,
                )
                mu_idx = single_model.config.poi_index
                mu_hat = float(result[mu_idx, 0])
                mu_err = float(result[mu_idx, 1])

                results[approach][target_cat] = {
                    "mu_hat": mu_hat,
                    "mu_err": mu_err,
                    "pull_from_1": float((mu_hat - 1.0) / mu_err)
                    if mu_err > 0
                    else 0.0,
                }
                log.info(
                    f"  {approach:10s} {target_cat:10s}: "
                    f"mu = {mu_hat:.3f} +/- {mu_err:.3f} "
                    f"(pull from 1 = {(mu_hat - 1.0) / mu_err:.2f})"
                )
            except Exception as e:
                log.warning(f"  {approach} {target_cat} fit failed: {e}")
                results[approach][target_cat] = {
                    "mu_hat": None,
                    "mu_err": None,
                    "pull_from_1": None,
                    "error": str(e),
                }

    return results


def impact_ranking():
    """Compute NP impact ranking on mu for the NN score approach."""
    log.info("\n=== NP Impact Ranking (NN score, full data) ===")

    with open(OUT / "observed_results.json") as f:
        obs_results = json.load(f)

    # Load workspace and fit with full data
    with open(P4A / "workspace_nn_score.json") as f:
        spec = json.load(f)

    with open(OUT / "data_histograms_full.json") as f:
        data_hists = json.load(f)

    # Replace observations
    for obs in spec["observations"]:
        channel_name = obs["name"]
        if channel_name.startswith("nn_score_"):
            cat = channel_name.replace("nn_score_", "")
        else:
            continue
        cat_data = data_hists["data_histograms"]["nn_score"].get(cat)
        if cat_data:
            obs["data"] = cat_data["data_full"]

    ws = pyhf.Workspace(spec)
    model = ws.model()
    data = ws.data(model)

    # Nominal fit
    bestfit_full = pyhf.infer.mle.fit(data, model, return_uncertainties=True)
    mu_nom = float(bestfit_full[model.config.poi_index, 0])

    par_names = model.config.par_names
    impacts = {}

    # Read NP pulls to use bestfit +/- postfit_unc for impact (standard method)
    np_pulls = obs_results.get("nn_score", {}).get("np_pulls", {})

    for i, name in enumerate(par_names):
        if name == "mu":
            continue
        if "staterror" in name:
            continue

        # Standard impact: fix NP to bestfit +/- 1*postfit_unc, refit
        # This avoids the zero-impact artifact that occurs when the
        # pre-fit +1 sigma value happens to coincide with the best-fit value.
        np_info = np_pulls.get(name)
        bestfit_val = float(bestfit_full[i, 0])
        postfit_unc = float(bestfit_full[i, 1]) if np_info is None else np_info["uncertainty"]

        init = list(model.config.suggested_init())
        fixed = list(model.config.suggested_fixed())

        # +1 postfit sigma from bestfit
        init_up = init.copy()
        fixed_up = fixed.copy()
        init_up[i] = bestfit_val + postfit_unc
        fixed_up[i] = True

        try:
            result_up = pyhf.infer.mle.fit(
                data,
                model,
                init_pars=init_up,
                fixed_params=fixed_up,
                return_uncertainties=False,
            )
            mu_up = float(result_up[model.config.poi_index])
        except Exception:
            mu_up = mu_nom

        # -1 postfit sigma from bestfit
        init_down = init.copy()
        fixed_down = fixed.copy()
        init_down[i] = bestfit_val - postfit_unc
        fixed_down[i] = True

        try:
            result_down = pyhf.infer.mle.fit(
                data,
                model,
                init_pars=init_down,
                fixed_params=fixed_down,
                return_uncertainties=False,
            )
            mu_down = float(result_down[model.config.poi_index])
        except Exception:
            mu_down = mu_nom

        impact_up = mu_up - mu_nom
        impact_down = mu_down - mu_nom
        impact_sym = (abs(impact_up) + abs(impact_down)) / 2.0

        impacts[name] = {
            "impact_up": impact_up,
            "impact_down": impact_down,
            "impact_sym": impact_sym,
            "bestfit": bestfit_val,
            "postfit_unc": postfit_unc,
        }

        log.info(
            f"  {name:30s}: bestfit={bestfit_val:+.4f}, "
            f"+1s -> dmu={impact_up:+.4f}, "
            f"-1s -> dmu={impact_down:+.4f}, sym={impact_sym:.4f}"
        )

    # Sort by symmetric impact
    sorted_impacts = dict(
        sorted(impacts.items(), key=lambda x: x[1]["impact_sym"], reverse=True)
    )

    log.info("\n  Top 10 impacts:")
    for i, (name, imp) in enumerate(sorted_impacts.items()):
        if i >= 10:
            break
        log.info(f"    {i+1}. {name}: {imp['impact_sym']:.4f}")

    return sorted_impacts


def vbf_process_decomposition():
    """Decompose VBF deficit by MC process for the NN score approach."""
    log.info("\n=== VBF Process Decomposition (NN score) ===")

    with open(P4A / "nominal_templates.json") as f:
        nominal = json.load(f)

    with open(OUT / "data_histograms_full.json") as f:
        data_hists = json.load(f)

    approach = "nn_score"
    cat = "vbf"

    data_full = np.array(data_hists["data_histograms"][approach][cat]["data_full"])
    data_total = float(data_full.sum())

    results = {"data_total": data_total, "processes": {}}
    mc_total = 0.0

    for proc_name, proc_data in nominal[approach][cat]["processes"].items():
        h = np.array(proc_data["nominal"])
        proc_total = float(h.sum())
        mc_total += proc_total
        results["processes"][proc_name] = {
            "yield": proc_total,
        }

    results["mc_total"] = mc_total
    results["data_mc_ratio"] = data_total / mc_total if mc_total > 0 else 0.0
    results["deficit"] = mc_total - data_total
    results["deficit_fraction"] = (mc_total - data_total) / mc_total if mc_total > 0 else 0.0

    # Compute each process's fraction of total MC
    for proc_name in results["processes"]:
        proc_yield = results["processes"][proc_name]["yield"]
        results["processes"][proc_name]["fraction_of_mc"] = (
            proc_yield / mc_total if mc_total > 0 else 0.0
        )
        results["processes"][proc_name]["fraction_of_deficit"] = (
            proc_yield / (mc_total - data_total) if (mc_total - data_total) > 0 else 0.0
        )

    log.info(f"  VBF data total: {data_total:.0f}")
    log.info(f"  VBF MC total:   {mc_total:.0f}")
    log.info(f"  Data/MC ratio:  {results['data_mc_ratio']:.3f}")
    log.info(f"  Deficit:        {results['deficit']:.0f} events ({results['deficit_fraction']:.1%})")
    log.info("  Process breakdown:")
    for proc_name, info in sorted(
        results["processes"].items(),
        key=lambda x: x[1]["yield"],
        reverse=True,
    ):
        log.info(
            f"    {proc_name:15s}: {info['yield']:8.1f} events "
            f"({info['fraction_of_mc']:.1%} of MC)"
        )

    return results


def main():
    diagnostics = {}

    # Pre-fit chi2
    diagnostics["prefit_chi2"] = prefit_data_mc_chi2()

    # Per-category fit
    diagnostics["per_category_fit"] = per_category_fit()

    # Impact ranking
    diagnostics["impact_ranking"] = impact_ranking()

    # VBF process decomposition (F5)
    diagnostics["vbf_process_decomposition"] = vbf_process_decomposition()

    # Save
    with open(OUT / "diagnostics_full.json", "w") as f:
        json.dump(diagnostics, f, indent=2)
    log.info(f"\nSaved diagnostics to {OUT / 'diagnostics_full.json'}")


if __name__ == "__main__":
    main()
