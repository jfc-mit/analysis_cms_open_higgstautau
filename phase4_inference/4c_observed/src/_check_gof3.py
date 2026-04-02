"""Check per-category GoF results."""
import json

with open("phase4_inference/4c_observed/outputs/gof_investigation.json") as f:
    gi = json.load(f)

for approach in ["nn_score", "mvis", "mcol"]:
    a = gi[approach]
    print(approach + ":")
    obs_chi2 = a["obs_pearson_chi2"]
    obs_llr = a["obs_llr"]
    print("  obs_chi2=%.1f, obs_llr=%.1f" % (obs_chi2, obs_llr))
    print("  p_pearson=%s, p_llr=%s" % (a["p_pearson"], a["p_llr"]))
    print("  failure_rate=%.1f%%" % (a["failure_rate"] * 100))
    if "per_category" in a:
        for cat, info in a["per_category"].items():
            print("  %s: keys=%s" % (cat, list(info.keys())))
            # Print all non-list values
            for k, v in info.items():
                if not isinstance(v, (list, dict)):
                    print("    %s: %s" % (k, v))
    print()
