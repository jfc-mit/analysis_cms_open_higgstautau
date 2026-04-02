"""Quick check of GoF results from observed_results.json."""
import json
import numpy as np

OUT = "phase4_inference/4c_observed/outputs"

with open(f"{OUT}/observed_results.json") as f:
    r = json.load(f)

for approach in ["nn_score", "mvis", "mcol"]:
    nn = r[approach]
    print(f"\n=== {approach} GoF ===")
    print(f"chi2 = {nn['chi2']:.2f}, ndf = {nn['ndf']}, ndf_simple = {nn['ndf_simple']}")
    print(f"chi2/ndf_simple = {nn['chi2_ndf_simple']:.4f}")
    print(f"GoF p-value = {nn['gof_pvalue']}")
    print(f"Toys: converged={nn['gof_n_converged']}, outliers={nn['gof_n_outliers']}, failed={nn['gof_n_failed']}")
    print(f"failure_rate = {nn['gof_failure_rate']:.1%}")
    print()
    print("Per-category GoF:")
    for cat, info in nn["per_category_gof"].items():
        print(f"  {cat}: chi2={info['chi2']:.2f}, nbins={info['nbins']}, chi2/bin={info['chi2_per_bin']:.3f}")
    print()
    toys = np.array(nn["gof_toy_chi2s"])
    clean = toys[toys < 1000]
    if len(clean) > 0:
        print(f"Toy chi2 range: [{clean.min():.1f}, {clean.max():.1f}]")
        print(f"Toy chi2 median: {np.median(clean):.1f}")
        print(f"Toy chi2 mean: {np.mean(clean):.1f}")
        print(f"Observed chi2: {nn['chi2']:.1f}")
        print(f"Fraction toys >= observed: {np.mean(clean >= nn['chi2']):.4f}")

# Check NP pulls for nn_score
print("\n=== NN score NP pulls (standard convention) ===")
nn = r["nn_score"]
for name, info in sorted(nn["np_pulls"].items(), key=lambda x: abs(x[1]["pull"]), reverse=True):
    print(f"  {name:30s}: bestfit={info['bestfit']:+.4f}, postfit_unc={info['uncertainty']:.4f}, "
          f"pull_std={info['pull']:+.3f}, pull_constr={info['pull_constraint']:+.3f}")

# Check expected sigma from 4a
print("\n=== Phase 4a expected sigma ===")
with open("phase4_inference/4a_expected/outputs/expected_results.json") as f:
    e = json.load(f)
for approach in ["nn_score", "mvis", "mcol"]:
    print(f"  {approach}: mu_err = {e[approach]['mu_err']:.4f}")
