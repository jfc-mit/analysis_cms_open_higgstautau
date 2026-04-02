"""
Phase 4a Step 4: Compute expected results on Asimov data.

For each approach (m_vis, NN score, m_col):
- Asimov fit: best-fit mu + uncertainty
- Expected 95% CL upper limit (CLs)
- Expected significance
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

OUT = Path("phase4_inference/4a_expected/outputs")

APPROACHES = ["mvis", "nn_score", "mcol"]


def fit_asimov(approach):
    """Perform Asimov fit for one approach."""
    log.info(f"\n=== Fitting {approach} ===")

    with open(OUT / f"workspace_{approach}.json") as f:
        spec = json.load(f)

    ws = pyhf.Workspace(spec)
    model = ws.model()

    # Asimov data (generated at mu=1 with nominal NPs)
    data = ws.data(model)

    log.info(f"  Model: {model.config.npars} parameters")
    log.info(f"  Data length: {len(data)}")

    # Maximum likelihood fit
    log.info("  Running MLE fit...")
    result = pyhf.infer.mle.fit(
        data,
        model,
        return_uncertainties=True,
    )
    bestfit = result[:, 0]
    uncertainties = result[:, 1]

    # Extract mu
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
        np_pulls[name] = {
            "bestfit": float(bestfit[i]),
            "uncertainty": float(uncertainties[i]),
        }

    # Expected upper limit (CLs)
    log.info("  Computing expected upper limit...")
    try:
        obs_limit, exp_limits = pyhf.infer.hypotest(
            1.0,  # test mu=1
            data,
            model,
            test_stat="qtilde",
            return_expected_set=True,
        )
        # For upper limit, we need to scan mu values
        poi_values = np.linspace(0.0, 10.0, 41)
        results_scan = []
        for poi_val in poi_values:
            try:
                obs_cls, exp_cls = pyhf.infer.hypotest(
                    poi_val,
                    data,
                    model,
                    test_stat="qtilde",
                    return_expected_set=True,
                )
                results_scan.append({
                    "poi": float(poi_val),
                    "obs_cls": float(obs_cls),
                    "exp_cls": [float(x) for x in exp_cls],
                })
            except Exception as e:
                log.warning(f"    Failed at mu={poi_val}: {e}")

        # Find 95% CL crossing (CLs = 0.05)
        exp_limit_95 = None
        obs_limit_95 = None
        if results_scan:
            poi_arr = np.array([r["poi"] for r in results_scan])
            obs_arr = np.array([r["obs_cls"] for r in results_scan])
            exp_med_arr = np.array([r["exp_cls"][2] for r in results_scan])

            # Find crossing with 0.05
            for i in range(len(poi_arr) - 1):
                if obs_arr[i] >= 0.05 >= obs_arr[i + 1]:
                    # Linear interpolation
                    frac = (0.05 - obs_arr[i]) / (obs_arr[i + 1] - obs_arr[i])
                    obs_limit_95 = poi_arr[i] + frac * (poi_arr[i + 1] - poi_arr[i])
                if exp_med_arr[i] >= 0.05 >= exp_med_arr[i + 1]:
                    frac = (0.05 - exp_med_arr[i]) / (exp_med_arr[i + 1] - exp_med_arr[i])
                    exp_limit_95 = poi_arr[i] + frac * (poi_arr[i + 1] - poi_arr[i])

        log.info(f"  Expected 95% CL limit: {exp_limit_95}")
        log.info(f"  Observed 95% CL limit: {obs_limit_95}")

    except Exception as e:
        log.error(f"  Upper limit computation failed: {e}")
        exp_limit_95 = None
        obs_limit_95 = None
        results_scan = []

    # Expected significance
    log.info("  Computing expected significance...")
    try:
        obs_pval, exp_pvals = pyhf.infer.hypotest(
            0.0,  # test mu=0 (background-only)
            data,
            model,
            test_stat="q0",
            return_expected_set=True,
        )
        from scipy.stats import norm
        obs_sig = float(norm.isf(obs_pval))
        exp_sig = float(norm.isf(exp_pvals[2]))  # median expected
        log.info(f"  Expected significance (median): {exp_sig:.3f} sigma")
        log.info(f"  Observed significance (Asimov): {obs_sig:.3f} sigma")
    except Exception as e:
        log.warning(f"  Significance computation failed: {e}")
        obs_sig = None
        exp_sig = None

    return {
        "approach": approach,
        "mu_hat": mu_hat,
        "mu_err": mu_err,
        "exp_limit_95": float(exp_limit_95) if exp_limit_95 is not None else None,
        "obs_limit_95_asimov": float(obs_limit_95) if obs_limit_95 is not None else None,
        "exp_significance": exp_sig,
        "obs_significance_asimov": obs_sig,
        "np_pulls": np_pulls,
        "cls_scan": results_scan,
        "n_parameters": model.config.npars,
    }


def main():
    results = {}

    for approach in APPROACHES:
        res = fit_asimov(approach)
        results[approach] = res

    # Summary
    log.info("\n=== Expected Results Summary ===")
    log.info(f"{'Approach':12s} {'mu_hat':>10s} {'mu_err':>10s} {'Exp Limit':>10s} {'Exp Sig':>10s}")
    for approach in APPROACHES:
        r = results[approach]
        lim = f"{r['exp_limit_95']:.2f}" if r["exp_limit_95"] else "N/A"
        sig = f"{r['exp_significance']:.3f}" if r["exp_significance"] else "N/A"
        log.info(f"{approach:12s} {r['mu_hat']:10.4f} {r['mu_err']:10.4f} {lim:>10s} {sig:>10s}")

    # Save
    with open(OUT / "expected_results.json", "w") as f:
        json.dump(results, f, indent=2)
    log.info(f"\nSaved to {OUT / 'expected_results.json'}")


if __name__ == "__main__":
    main()
