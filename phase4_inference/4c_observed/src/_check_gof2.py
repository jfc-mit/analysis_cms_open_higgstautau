"""Check GoF investigation results."""
import json

with open("phase4_inference/4c_observed/outputs/observed_results.json") as f:
    r = json.load(f)

nn = r["nn_score"]
gi = nn.get("gof_investigation", {})
print("GoF investigation present:", bool(gi))
if gi:
    for k, v in gi.items():
        if isinstance(v, dict):
            print(f"  {k}:")
            for kk, vv in v.items():
                if not isinstance(vv, (list, dict)):
                    print(f"    {kk}: {vv}")
        elif not isinstance(v, list):
            print(f"  {k}: {v}")
else:
    print("No gof_investigation field found")
    # Check gof_investigation.json instead
    try:
        with open("phase4_inference/4c_observed/outputs/gof_investigation.json") as f:
            gi = json.load(f)
        print("\nFrom gof_investigation.json:")
        for approach in ["nn_score", "mvis", "mcol"]:
            if approach in gi:
                a = gi[approach]
                print(f"\n  {approach}:")
                for k, v in a.items():
                    if not isinstance(v, (list, dict)):
                        print(f"    {k}: {v}")
                if "per_category" in a:
                    for cat, info in a["per_category"].items():
                        print(f"    {cat}:")
                        for kk, vv in info.items():
                            if not isinstance(vv, (list, dict)):
                                print(f"      {kk}: {vv}")
    except FileNotFoundError:
        print("gof_investigation.json not found either")
