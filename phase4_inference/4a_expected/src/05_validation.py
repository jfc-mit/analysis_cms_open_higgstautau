"""
Phase 4a Step 5: Validation checks.

- Signal injection: mu = 0, 1, 2, 5 -> recover injected mu
- Nuisance parameter pulls on Asimov
- Impact ranking: top 15 NPs by impact on mu
- Goodness-of-fit: chi2/ndf + toy-based p-value
"""
import logging
import json
import numpy as np
import pyhf
from pathlib import Path
from rich.logging import RichHandler
from scipy.stats import norm, chi2 as chi2_dist

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

pyhf.set_backend("numpy", "minuit")

OUT = Path("phase4_inference/4a_expected/outputs")

# Use NN score as primary approach for detailed validation
PRIMARY_APPROACH = "nn_score"


def signal_injection_test(approach="nn_score"):
    """Inject signal at various mu values and check recovery."""
    log.info(f"\n=== Signal Injection Test ({approach}) ===")

    with open(OUT / f"workspace_{approach}.json") as f:
        spec = json.load(f)

    ws = pyhf.Workspace(spec)
    model = ws.model()

    mu_inject_values = [0.0, 1.0, 2.0, 5.0]
    results = []

    for mu_inject in mu_inject_values:
        log.info(f"  Injecting mu = {mu_inject}")

        # Generate Asimov data at mu_inject
        pars = model.config.suggested_init()
        pars[model.config.poi_index] = mu_inject
        data = model.expected_data(pars).tolist()

        # Fit
        try:
            result = pyhf.infer.mle.fit(
                data,
                model,
                return_uncertainties=True,
            )
            mu_hat = float(result[model.config.poi_index, 0])
            mu_err = float(result[model.config.poi_index, 1])
            pull = (mu_hat - mu_inject) / mu_err if mu_err > 0 else 0.0
            log.info(f"    mu_hat = {mu_hat:.4f} +/- {mu_err:.4f} (pull = {pull:.3f})")

            results.append({
                "mu_inject": mu_inject,
                "mu_hat": mu_hat,
                "mu_err": mu_err,
                "pull": pull,
            })
        except Exception as e:
            log.error(f"    Fit failed: {e}")
            results.append({
                "mu_inject": mu_inject,
                "mu_hat": None,
                "mu_err": None,
                "pull": None,
            })

    return results


def np_impact_ranking(approach="nn_score"):
    """Compute impact of each NP on mu via profile likelihood."""
    log.info(f"\n=== NP Impact Ranking ({approach}) ===")

    with open(OUT / f"workspace_{approach}.json") as f:
        spec = json.load(f)

    ws = pyhf.Workspace(spec)
    model = ws.model()
    data = ws.data(model)

    # Nominal fit
    result = pyhf.infer.mle.fit(
        data, model, return_uncertainties=True,
    )
    mu_nom = float(result[model.config.poi_index, 0])
    bestfit = result[:, 0]
    uncertainties = result[:, 1]

    par_names = model.config.par_names
    poi_idx = model.config.poi_index

    impacts = []

    for i, name in enumerate(par_names):
        if name == "mu":
            continue
        if "staterror" in name:
            continue

        theta_hat = float(bestfit[i])
        theta_err = float(uncertainties[i])

        if theta_err < 1e-10:
            continue

        # Impact: shift NP by +/-1 sigma, profile mu
        for direction in [+1, -1]:
            fixed_val = theta_hat + direction * theta_err

            # Create fixed parameter set
            init = bestfit.copy()
            init[i] = fixed_val

            # Fix this NP and fit mu
            fixed_params = {name: fixed_val}
            try:
                # Use pyhf fixed_poi approach
                # Simpler: compute impact as the shift in mu
                pars_fixed = model.config.suggested_init()
                pars_fixed[i] = fixed_val

                # Profile fit with NP fixed
                fixed_pars = [False] * model.config.npars
                fixed_pars[i] = True

                result_fixed = pyhf.infer.mle.fit(
                    data, model,
                    init_pars=init.tolist(),
                    fixed_params=fixed_pars,
                    return_uncertainties=True,
                )
                mu_shifted = float(result_fixed[poi_idx, 0])

                if direction == 1:
                    impact_up = mu_shifted - mu_nom
                else:
                    impact_down = mu_shifted - mu_nom
            except Exception as e:
                log.warning(f"  Impact failed for {name} dir={direction}: {e}")
                if direction == 1:
                    impact_up = 0.0
                else:
                    impact_down = 0.0

        total_impact = np.sqrt((impact_up ** 2 + impact_down ** 2) / 2.0)
        impacts.append({
            "name": name,
            "impact_up": impact_up,
            "impact_down": impact_down,
            "total_impact": total_impact,
            "bestfit": theta_hat,
            "uncertainty": theta_err,
            "pull": (theta_hat - model.config.suggested_init()[i]) / theta_err if theta_err > 0 else 0.0,
        })

    # Sort by total impact
    impacts.sort(key=lambda x: x["total_impact"], reverse=True)

    log.info(f"\nTop 15 NP impacts on mu:")
    log.info(f"{'Rank':>4s} {'Name':30s} {'Impact Up':>10s} {'Impact Dn':>10s} {'Total':>10s} {'Pull':>8s}")
    for rank, imp in enumerate(impacts[:15], 1):
        log.info(
            f"{rank:4d} {imp['name']:30s} {imp['impact_up']:+10.4f} {imp['impact_down']:+10.4f} "
            f"{imp['total_impact']:10.4f} {imp['pull']:+8.3f}"
        )

    return impacts


def goodness_of_fit(approach="nn_score", n_toys=200):
    """Compute goodness-of-fit: chi2/ndf and toy-based p-value."""
    log.info(f"\n=== Goodness of Fit ({approach}) ===")

    with open(OUT / f"workspace_{approach}.json") as f:
        spec = json.load(f)

    ws = pyhf.Workspace(spec)
    model = ws.model()
    data = ws.data(model)

    # Fit
    result = pyhf.infer.mle.fit(
        data, model, return_uncertainties=True,
    )
    bestfit = result[:, 0]

    # Compute chi2 from Asimov data vs post-fit prediction
    expected = model.expected_data(bestfit.tolist())

    # Only use actual bin data (not aux data)
    n_bins = sum(model.config.channel_nbins.values())
    obs_bins = np.array(data[:n_bins])
    exp_bins = np.array(expected[:n_bins])

    # Chi2 (Pearson)
    mask = exp_bins > 0
    chi2_val = np.sum((obs_bins[mask] - exp_bins[mask]) ** 2 / exp_bins[mask])
    ndf = int(mask.sum()) - model.config.npars
    chi2_ndf = chi2_val / max(ndf, 1)

    log.info(f"  chi2 = {chi2_val:.4f}")
    log.info(f"  ndf = {ndf}")
    log.info(f"  chi2/ndf = {chi2_ndf:.4f}")

    # For Asimov data, chi2 should be ~0 (by construction)
    # This validates the framework works correctly

    # Toy-based GoF using saturated model
    # [FIX F17: added convergence monitoring — log minimizer status
    #  and report non-convergence fraction]
    log.info(f"  Running {n_toys} toys for saturated model GoF...")
    toy_chi2s = []
    n_converged = 0
    n_failed = 0
    n_outlier = 0
    try:
        for i_toy in range(n_toys):
            # Generate toy from post-fit model
            toy_bins = np.random.poisson(np.maximum(exp_bins, 0.01))
            # Refit toy
            toy_full = list(toy_bins) + list(data[n_bins:])  # keep aux data
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

                # Flag catastrophic outliers (chi2 > 1000)
                if toy_chi2 > 1000:
                    n_outlier += 1
                    log.warning(f"    Toy {i_toy}: outlier chi2={toy_chi2:.1f}")
                else:
                    n_converged += 1

                toy_chi2s.append(float(toy_chi2))
            except Exception as e:
                n_failed += 1
                log.warning(f"    Toy {i_toy}: fit failed ({e})")

            if (i_toy + 1) % 50 == 0:
                log.info(f"    Completed {i_toy + 1}/{n_toys} toys "
                         f"(converged={n_converged}, outliers={n_outlier}, failed={n_failed})")

        # p-value: fraction of toys with chi2 > observed chi2
        # Exclude catastrophic outliers from p-value calculation
        clean_chi2s = [c for c in toy_chi2s if c < 1000]
        if clean_chi2s:
            p_value_clean = np.mean(np.array(clean_chi2s) >= chi2_val)
            p_value_all = np.mean(np.array(toy_chi2s) >= chi2_val)
            log.info(f"  Convergence: {n_converged} clean, {n_outlier} outliers, {n_failed} failed "
                     f"out of {n_toys} toys")
            log.info(f"  Toy-based p-value (clean): {p_value_clean:.4f} ({len(clean_chi2s)} toys)")
            log.info(f"  Toy-based p-value (all):   {p_value_all:.4f} ({len(toy_chi2s)} toys)")
        else:
            p_value_clean = None
            p_value_all = None
    except Exception as e:
        log.error(f"  Toy GoF failed: {e}")
        p_value_clean = None
        p_value_all = None
        toy_chi2s = []

    return {
        "chi2": float(chi2_val),
        "ndf": ndf,
        "chi2_ndf": float(chi2_ndf),
        "p_value_toys": float(p_value_clean) if p_value_clean is not None else None,
        "p_value_toys_all": float(p_value_all) if p_value_all is not None else None,
        "n_toys": len(toy_chi2s),
        "n_converged": n_converged,
        "n_outliers": n_outlier,
        "n_failed": n_failed,
        "convergence_fraction": float(n_converged / max(n_toys, 1)),
        "toy_chi2s": toy_chi2s,  # save all for diagnostics
    }


def main():
    validation = {}

    # Signal injection
    injection_results = signal_injection_test(PRIMARY_APPROACH)
    validation["signal_injection"] = injection_results

    # Also run for other approaches
    for approach in ["mvis", "mcol"]:
        inj = signal_injection_test(approach)
        validation[f"signal_injection_{approach}"] = inj

    # Impact ranking (primary approach only)
    impacts = np_impact_ranking(PRIMARY_APPROACH)
    validation["impact_ranking"] = impacts

    # Goodness of fit (primary approach)
    gof = goodness_of_fit(PRIMARY_APPROACH, n_toys=200)
    validation["gof"] = gof

    # Also GoF for other approaches
    for approach in ["mvis", "mcol"]:
        gof_other = goodness_of_fit(approach, n_toys=100)
        validation[f"gof_{approach}"] = gof_other

    # Save
    with open(OUT / "validation_results.json", "w") as f:
        json.dump(validation, f, indent=2)
    log.info(f"\nSaved validation results to {OUT / 'validation_results.json'}")


if __name__ == "__main__":
    main()
