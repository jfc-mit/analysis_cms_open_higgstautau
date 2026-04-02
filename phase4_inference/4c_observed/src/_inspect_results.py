"""Quick inspection of updated observed results."""
import json

with open("phase4_inference/4c_observed/outputs/observed_results.json") as f:
    r = json.load(f)

nn = r["nn_score"]
print("=== NN Score Results ===")
print(f"mu_hat = {nn['mu_hat']:.4f} +/- {nn['mu_err']:.4f}")
print(f"chi2 = {nn['chi2']:.2f}, ndf(full) = {nn['ndf']}, ndf_simple = {nn['ndf_simple']}")
print(f"chi2/ndf(simple) = {nn['chi2_ndf_simple']:.4f}")
print(f"GoF p-value = {nn['gof_pvalue']}")
print(f"GoF toys: {nn['gof_n_converged']} converged, {nn['gof_n_failed']} failed, rate = {nn['gof_failure_rate']:.1%}")

print("\nPer-category GoF:")
for ch, info in nn["per_category_gof"].items():
    print(f"  {ch}: chi2 = {info['chi2']:.2f}, nbins = {info['nbins']}, chi2/bin = {info['chi2_per_bin']:.3f}")

print("\nNP pulls (standard convention, sorted by |pull|):")
for name, info in sorted(nn["np_pulls"].items(), key=lambda x: abs(x[1]["pull"]), reverse=True):
    pull = info["pull"]
    flag = " ***" if abs(pull) > 2.0 else " **" if abs(pull) > 1.5 else ""
    print(f"  {name:30s}: bestfit={info['bestfit']:+.4f}, unc={info['uncertainty']:.4f}, pull_std={pull:+.4f}, pull_constr={info['pull_constraint']:+.4f}{flag}")

print("\n=== All Approaches GoF Summary ===")
for approach in ["mvis", "nn_score", "mcol"]:
    a = r[approach]
    print(f"\n{approach}:")
    print(f"  mu_hat = {a['mu_hat']:.4f} +/- {a['mu_err']:.4f}")
    print(f"  chi2 = {a['chi2']:.2f}, ndf_simple = {a['ndf_simple']}, chi2/ndf = {a['chi2_ndf_simple']:.4f}")
    print(f"  GoF p-value = {a['gof_pvalue']}")
    print(f"  GoF: {a['gof_n_converged']} converged, {a['gof_n_failed']} failed ({a['gof_failure_rate']:.1%})")
    print(f"  Per-category GoF:")
    for ch, info in a["per_category_gof"].items():
        print(f"    {ch}: chi2 = {info['chi2']:.2f}, nbins = {info['nbins']}, chi2/bin = {info['chi2_per_bin']:.3f}")

print("\n=== Expected sigma comparison ===")
with open("phase4_inference/4a_expected/outputs/expected_results.json") as f:
    e = json.load(f)
print(f"4a expected sigma(mu) for nn_score = {e['nn_score']['mu_err']:.4f}")
print(f"4c observed sigma(mu) for nn_score = {r['nn_score']['mu_err']:.4f}")
