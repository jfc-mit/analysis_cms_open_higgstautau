"""Quick script to print summary of observed results."""
import json

with open("phase4_inference/4c_observed/outputs/observed_results.json") as f:
    r = json.load(f)

with open("phase4_inference/4a_expected/outputs/expected_results.json") as f:
    e = json.load(f)

with open("phase4_inference/4b_partial/outputs/partial_data_results.json") as f:
    p = json.load(f)

print("=" * 80)
print("FULL DATA RESULTS (Phase 4c)")
print("=" * 80)
for a in ["mvis", "nn_score", "mcol"]:
    d = r[a]
    print(
        f"\n{a}:"
        f"\n  mu = {d['mu_hat']:.3f} +/- {d['mu_err']:.3f}"
        f"\n  obs_significance = {d.get('obs_significance', 'N/A')}"
        f"\n  chi2 = {d['chi2']:.1f}, ndf = {d['ndf']}, chi2/ndf = {d['chi2_ndf']:.3f}"
        f"\n  GoF p-value = {d['gof_pvalue']}"
        f"\n  obs 95% CL = {d.get('obs_limit_95', 'N/A')}"
        f"\n  exp 95% CL = {d.get('exp_limit_95', 'N/A')}"
    )

print("\n" + "=" * 80)
print("THREE-WAY COMPARISON")
print("=" * 80)
header = f"{'Approach':12s} {'mu_exp':>10s} {'sig_exp':>10s} {'mu_10%':>10s} {'sig_10%':>10s} {'mu_full':>10s} {'sig_full':>10s}"
print(header)
for a in ["mvis", "nn_score", "mcol"]:
    print(
        f"{a:12s} "
        f"{e[a]['mu_hat']:+10.3f} {e[a]['mu_err']:10.3f} "
        f"{p[a]['mu_hat']:+10.3f} {p[a]['mu_err']:10.3f} "
        f"{r[a]['mu_hat']:+10.3f} {r[a]['mu_err']:10.3f}"
    )

print("\nNP PULLS (nn_score, full data):")
np_pulls = r["nn_score"]["np_pulls"]
for name, info in sorted(np_pulls.items(), key=lambda x: abs(x[1]["pull"]), reverse=True):
    pull = info["pull"]
    flag = " ***" if abs(pull) > 2.0 else " **" if abs(pull) > 1.5 else ""
    print(f"  {name:30s}: pull = {pull:+.3f}{flag}")
