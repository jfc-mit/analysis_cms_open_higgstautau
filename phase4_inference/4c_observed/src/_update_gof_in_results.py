"""Update observed_results.json with GoF investigation results."""
import json
from pathlib import Path

OUT = Path("phase4_inference/4c_observed/outputs")

with open(OUT / "observed_results.json") as f:
    results = json.load(f)

with open(OUT / "gof_investigation.json") as f:
    gof = json.load(f)

for approach in ["mvis", "nn_score", "mcol"]:
    g = gof[approach]
    results[approach]["gof_investigation"] = {
        "obs_pearson_chi2": g["obs_pearson_chi2"],
        "obs_llr": g["obs_llr"],
        "p_pearson": g["p_pearson"],
        "p_pearson_unc": g["p_pearson_unc"],
        "p_llr": g["p_llr"],
        "p_llr_unc": g["p_llr_unc"],
        "n_toys": g["n_toys"],
        "n_converged": g["n_converged"],
        "n_failed": g["n_failed"],
        "failure_rate": g["failure_rate"],
        "per_category": g["per_category"],
        "toy_pearson_stats": g["toy_pearson_stats"],
        "toy_llr_stats": g["toy_llr_stats"],
    }

with open(OUT / "observed_results.json", "w") as f:
    json.dump(results, f, indent=2)

print("Updated observed_results.json with GoF investigation results")
