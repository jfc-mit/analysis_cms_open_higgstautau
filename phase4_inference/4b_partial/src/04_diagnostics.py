"""
Phase 4b Step 4: Diagnostic checks on 10% data.

- Per-category fit (Baseline-only, VBF-only)
- Data/MC chi2 per discriminant per category (pre-fit)
- Per-observable consistency checks
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
OUT = Path("phase4_inference/4b_partial/outputs")

APPROACHES = ["mvis", "nn_score", "mcol"]


def prefit_data_mc_chi2():
    """Compute pre-fit data/MC chi2 per approach per category."""
    log.info("\n=== Pre-fit Data/MC chi2 ===")

    with open(P4A / "nominal_templates.json") as f:
        nominal = json.load(f)

    with open(OUT / "data_histograms_10pct.json") as f:
        data_hists = json.load(f)

    results = {}
    for approach in APPROACHES:
        results[approach] = {}
        for cat in ["baseline", "vbf"]:
            # Scaled 10% data
            data_scaled = np.array(
                data_hists["data_histograms"][approach][cat]["data_10pct_scaled"]
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
                (data_scaled[mask] - mc_total[mask]) ** 2 / mc_total[mask]
            )
            ndf = int(mask.sum()) - 1  # -1 for normalization
            chi2_ndf = chi2 / max(ndf, 1)

            results[approach][cat] = {
                "chi2": float(chi2),
                "ndf": ndf,
                "chi2_ndf": float(chi2_ndf),
                "data_total": float(data_scaled.sum()),
                "mc_total": float(mc_total.sum()),
                "ratio": float(data_scaled.sum() / mc_total.sum()),
            }

            log.info(
                f"  {approach:10s} {cat:10s}: chi2/ndf = {chi2:.1f}/{ndf} = {chi2_ndf:.2f}, "
                f"data/MC = {data_scaled.sum():.0f}/{mc_total.sum():.0f} = "
                f"{data_scaled.sum() / mc_total.sum():.3f}"
            )

    return results


def per_category_fit():
    """Fit mu separately in Baseline and VBF categories."""
    log.info("\n=== Per-Category Fit ===")

    with open(OUT / "data_histograms_10pct.json") as f:
        data_hists = json.load(f)

    results = {}

    for approach in APPROACHES:
        results[approach] = {}

        with open(P4A / f"workspace_{approach}.json") as f:
            spec = json.load(f)

        ws = pyhf.Workspace(spec)
        model = ws.model()

        # Get channel names
        channels = model.config.channels
        log.info(f"  Channels: {channels}")

        for target_cat in ["baseline", "vbf"]:
            target_channel = f"{approach}_{target_cat}"

            # Build single-channel workspace by modifying the spec
            single_spec = {
                "channels": [
                    ch for ch in spec["channels"]
                    if ch["name"] == target_channel
                ],
                "observations": [],
                "measurements": spec["measurements"],
                "version": "1.0.0",
            }

            # Set observation for this channel
            cat_data = data_hists["data_histograms"][approach].get(target_cat)
            if cat_data:
                single_spec["observations"].append({
                    "name": target_channel,
                    "data": cat_data["data_10pct_scaled"],
                })
            else:
                log.warning(f"  No data for {target_channel}")
                continue

            try:
                single_ws = pyhf.Workspace(single_spec)
                single_model = single_ws.model()
                single_data = single_ws.data(single_model)

                result = pyhf.infer.mle.fit(
                    single_data, single_model, return_uncertainties=True,
                )
                mu_idx = single_model.config.poi_index
                mu_hat = float(result[mu_idx, 0])
                mu_err = float(result[mu_idx, 1])

                results[approach][target_cat] = {
                    "mu_hat": mu_hat,
                    "mu_err": mu_err,
                    "pull_from_1": float((mu_hat - 1.0) / mu_err) if mu_err > 0 else 0.0,
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


def main():
    diagnostics = {}

    # Pre-fit chi2
    diagnostics["prefit_chi2"] = prefit_data_mc_chi2()

    # Per-category fit
    diagnostics["per_category_fit"] = per_category_fit()

    # Save
    with open(OUT / "diagnostics_10pct.json", "w") as f:
        json.dump(diagnostics, f, indent=2)
    log.info(f"\nSaved diagnostics to {OUT / 'diagnostics_10pct.json'}")


if __name__ == "__main__":
    main()
