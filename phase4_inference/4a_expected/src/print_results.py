"""Print validation results summary."""
import json

with open("phase4_inference/4a_expected/outputs/validation_results.json") as f:
    v = json.load(f)

print("=== Signal Injection (nn_score) ===")
for d in v["signal_injection"]:
    if d["mu_hat"] is not None:
        print(f"  mu_inj={d['mu_inject']:.1f}: mu_hat={d['mu_hat']:.4f} +/- {d['mu_err']:.4f} (pull={d['pull']:.4f})")

print()
print("=== Signal Injection (mvis) ===")
for d in v["signal_injection_mvis"]:
    if d["mu_hat"] is not None:
        print(f"  mu_inj={d['mu_inject']:.1f}: mu_hat={d['mu_hat']:.4f} +/- {d['mu_err']:.4f} (pull={d['pull']:.4f})")

print()
print("=== Top 15 NP Impacts ===")
for i, imp in enumerate(v["impact_ranking"][:15], 1):
    print(f"  {i:2d}. {imp['name']:30s}  up={imp['impact_up']:+.4f}  down={imp['impact_down']:+.4f}  total={imp['total_impact']:.4f}")

print()
print("=== GoF ===")
for key in ["gof", "gof_mvis", "gof_mcol"]:
    gof = v.get(key, {})
    print(f"  {key}: chi2={gof.get('chi2', 0):.4f}, ndf={gof.get('ndf', 0)}, chi2/ndf={gof.get('chi2_ndf', 0):.4f}, p-value={gof.get('p_value_toys', 'N/A')}")

# Expected results
with open("phase4_inference/4a_expected/outputs/expected_results.json") as f:
    r = json.load(f)

print()
print("=== Expected Results ===")
for approach in ["mvis", "nn_score", "mcol"]:
    ra = r[approach]
    print(f"  {approach:10s}: mu={ra['mu_hat']:.4f}+/-{ra['mu_err']:.4f}, limit={ra.get('exp_limit_95', 'N/A')}, sig={ra.get('exp_significance', 'N/A')}")
