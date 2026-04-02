"""
Produce the flagship comparison figure: our NN score result vs published CMS
result (Nature 2014) and the SM prediction.

Published CMS H->tautau result (mu-tau channel, 8 TeV):
  mu = 0.78 +/- 0.27
  Source: CMS Collaboration, JHEP 05 (2014) 104; Nature 515 (2014) 510
  Dataset: 19.7 fb^{-1} at 8 TeV (full Run 1)

This analysis (CMS Open Data, mu-tau channel, 8 TeV):
  mu = 0.635 +/- 1.079  (NN score approach, primary result)
  Dataset: 11.5 fb^{-1} at 8 TeV (partial Run 1, open data)

SM prediction: mu = 1.0 (by definition)
"""

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import mplhep as mh
import numpy as np
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

mh.style.use("CMS")

# ── Results ──────────────────────────────────────────────────────────────────
# Our three approaches (full data, Phase 4c)
results = {
    "NN score\n(this analysis)": {"mu": 0.635, "err": 1.079},
    r"$m_\mathrm{vis}$" + "\n(this analysis)": {"mu": -6.700, "err": 2.926},
    r"$m_\mathrm{col}$" + "\n(this analysis)": {"mu": -10.745, "err": 3.412},
}

# Published CMS result
# CMS Collaboration, "Evidence for the 125 GeV Higgs boson decaying to a pair
# of tau leptons", JHEP 05 (2014) 104.  Combined mu-tau + e-tau + e-mu + tau-tau,
# full Run 1: mu = 0.78 +/- 0.27.
cms_published = {"mu": 0.78, "err": 0.27}

# SM prediction
sm_mu = 1.0

outdir = Path("phase5_documentation/outputs/figures")
outdir.mkdir(parents=True, exist_ok=True)

# ── Figure 1: Flagship comparison (NN score vs CMS published vs SM) ─────────
fig, ax = plt.subplots(figsize=(10, 10))

labels = []
mus = []
errs = []
colors = []
markers = []

# Our primary result (NN score)
labels.append("This analysis\n(NN score, 11.5 fb$^{-1}$)")
mus.append(0.635)
errs.append(1.079)
colors.append("#d62728")  # red
markers.append("o")

# Published CMS result
labels.append("CMS published\n(combined, 19.7 fb$^{-1}$)")
mus.append(0.78)
errs.append(0.27)
colors.append("#1f77b4")  # blue
markers.append("s")

y_positions = np.array([1.0, 0.0])

for i, (label, mu, err, color, marker) in enumerate(
    zip(labels, mus, errs, colors, markers)
):
    ax.errorbar(
        mu,
        y_positions[i],
        xerr=err,
        fmt=marker,
        color=color,
        markersize=12,
        capsize=8,
        capthick=2,
        elinewidth=2.5,
        label=label,
        zorder=10,
    )

# SM prediction line
ax.axvline(x=sm_mu, color="gray", linestyle="--", linewidth=1.5, label=r"SM ($\mu = 1$)", zorder=5)

# Shading for SM = 0 (no Higgs)
ax.axvline(x=0.0, color="gray", linestyle=":", linewidth=1.0, alpha=0.5, zorder=3)

ax.set_yticks(y_positions)
ax.set_yticklabels(labels, fontsize=16)
ax.set_xlabel(r"Signal strength $\hat{\mu}$", fontsize=18)
ax.set_xlim(-2.5, 3.5)
ax.set_ylim(-0.7, 1.7)

ax.legend(loc="upper right", fontsize="x-small", frameon=True)

mh.label.exp_label(
    exp="CMS",
    data=True,
    llabel="Open Data",
    rlabel=r"$\sqrt{s} = 8$ TeV, 11.5 fb$^{-1}$",
    loc=0,
    ax=ax,
)

fig.savefig(outdir / "mu_comparison_published.pdf", bbox_inches="tight", dpi=200, transparent=True)
fig.savefig(outdir / "mu_comparison_published.png", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig)
log.info("Saved mu_comparison_published.pdf/png")


# ── Figure 2: All approaches + published CMS ────────────────────────────────
fig2, ax2 = plt.subplots(figsize=(10, 10))

all_labels = [
    "This analysis: NN score\n(11.5 fb$^{-1}$)",
    "This analysis: $m_{\\mathrm{vis}}$\n(11.5 fb$^{-1}$)",
    "This analysis: $m_{\\mathrm{col}}$\n(11.5 fb$^{-1}$)",
    "CMS published\n(19.7 fb$^{-1}$)",
]
all_mus = [0.635, -6.700, -10.745, 0.78]
all_errs = [1.079, 2.926, 3.412, 0.27]
all_colors = ["#d62728", "#ff7f0e", "#2ca02c", "#1f77b4"]
all_markers = ["o", "D", "^", "s"]
y_pos_all = np.array([3.0, 2.0, 1.0, 0.0])

for i in range(len(all_labels)):
    ax2.errorbar(
        all_mus[i],
        y_pos_all[i],
        xerr=all_errs[i],
        fmt=all_markers[i],
        color=all_colors[i],
        markersize=12,
        capsize=8,
        capthick=2,
        elinewidth=2.5,
        label=all_labels[i],
        zorder=10,
    )

# SM prediction line
ax2.axvline(x=sm_mu, color="gray", linestyle="--", linewidth=1.5, label=r"SM ($\mu = 1$)", zorder=5)
ax2.axvline(x=0.0, color="gray", linestyle=":", linewidth=1.0, alpha=0.5, zorder=3)

ax2.set_yticks(y_pos_all)
ax2.set_yticklabels(all_labels, fontsize=14)
ax2.set_xlabel(r"Signal strength $\hat{\mu}$", fontsize=18)
ax2.set_xlim(-16, 6)
ax2.set_ylim(-0.7, 3.7)

# Add a horizontal line separating our results from the published one
ax2.axhline(y=-0.5 + 1.0 * 0.5, color="lightgray", linestyle="-", linewidth=0.8, alpha=0.5)

ax2.legend(loc="upper left", fontsize="x-small", frameon=True)

mh.label.exp_label(
    exp="CMS",
    data=True,
    llabel="Open Data",
    rlabel=r"$\sqrt{s} = 8$ TeV, 11.5 fb$^{-1}$",
    loc=0,
    ax=ax2,
)

fig2.savefig(outdir / "mu_comparison_all_vs_published.pdf", bbox_inches="tight", dpi=200, transparent=True)
fig2.savefig(outdir / "mu_comparison_all_vs_published.png", bbox_inches="tight", dpi=200, transparent=True)
plt.close(fig2)
log.info("Saved mu_comparison_all_vs_published.pdf/png")


# ── Verify all expected figure paths ─────────────────────────────────────────
log.info("--- Figure inventory ---")
expected_figures = [
    # Phase 2 exploration
    "collinear_mass.pdf",
    "collinear_mass_physical.pdf",
    "delta_phi.pdf",
    "delta_r.pdf",
    "met_pt.pdf",
    "mt.pdf",
    "mu_eta.pdf",
    "mu_pt.pdf",
    "mvis.pdf",
    "nbjets.pdf",
    "njets.pdf",
    "pv_npvs.pdf",
    "separation_power.pdf",
    "tau_dm.pdf",
    "tau_eta.pdf",
    "tau_id_wp_Loose.pdf",
    "tau_id_wp_Medium.pdf",
    "tau_id_wp_VLoose.pdf",
    "tau_pt.pdf",
    "vbf_deta.pdf",
    "vbf_mjj.pdf",
    # Phase 3 selection
    "approach_comparison.pdf",
    "bdt_overtraining.pdf",
    "bdt_vs_nn_roc.pdf",
    "nn_feature_importance.pdf",
    "nn_overtraining.pdf",
    "nn_roc.pdf",
    "nn_score_baseline.pdf",
    "nn_score_vbf.pdf",
    "mt_regions.pdf",
    "wjets_validation_midmt.pdf",
    # Phase 3 per-category distributions
    "mcol_baseline.pdf",
    "mcol_vbf.pdf",
    "mvis_baseline.pdf",
    "mvis_vbf.pdf",
    "met_pt_baseline.pdf",
    "met_pt_vbf.pdf",
    "mu_pt_baseline.pdf",
    "mu_pt_vbf.pdf",
    "tau_pt_baseline.pdf",
    "tau_pt_vbf.pdf",
    "delta_r_baseline.pdf",
    "delta_r_vbf.pdf",
    "njets_baseline.pdf",
    "njets_vbf.pdf",
    # Phase 4a expected
    "template_nn_score_baseline.pdf",
    "template_nn_score_vbf.pdf",
    "template_mvis_baseline.pdf",
    "template_mvis_vbf.pdf",
    "template_mcol_baseline.pdf",
    "template_mcol_vbf.pdf",
    "cls_scan.pdf",
    "gof_toys.pdf",
    "impact_ranking.pdf",
    "np_pulls.pdf",
    "signal_injection.pdf",
    "syst_shift_jes.pdf",
    "syst_shift_mes.pdf",
    "syst_shift_met_uncl.pdf",
    "syst_shift_tes.pdf",
    # Phase 4b partial
    "data_mc_nn_score_baseline.pdf",
    "data_mc_nn_score_vbf.pdf",
    "data_mc_mvis_baseline.pdf",
    "data_mc_mvis_vbf.pdf",
    "data_mc_mcol_baseline.pdf",
    "data_mc_mcol_vbf.pdf",
    "data_mc_ratio_summary.pdf",
    "gof_toys_10pct.pdf",
    "mu_comparison_10pct.pdf",
    "mu_per_category_10pct.pdf",
    "np_pulls_10pct.pdf",
    # Phase 4c observed
    "data_mc_postfit_nn_score_baseline.pdf",
    "data_mc_postfit_nn_score_vbf.pdf",
    "data_mc_postfit_mvis_baseline.pdf",
    "data_mc_postfit_mvis_vbf.pdf",
    "data_mc_postfit_mcol_baseline.pdf",
    "data_mc_postfit_mcol_vbf.pdf",
    "data_mc_prefit_nn_score_baseline.pdf",
    "data_mc_prefit_nn_score_vbf.pdf",
    "data_mc_prefit_mvis_baseline.pdf",
    "data_mc_prefit_mvis_vbf.pdf",
    "data_mc_prefit_mcol_baseline.pdf",
    "data_mc_prefit_mcol_vbf.pdf",
    "gof_toys_full_nn_score.pdf",
    "gof_toys_full_mvis.pdf",
    "gof_toys_full_mcol.pdf",
    "gof_investigation_nn_score.pdf",
    "gof_investigation_mvis.pdf",
    "gof_investigation_mcol.pdf",
    "gof_per_category.pdf",
    "impact_ranking_full.pdf",
    "mu_comparison_three_way.pdf",
    "np_pulls_full.pdf",
    "per_category_mu_full.pdf",
    # Phase 5 new figures
    "mu_comparison_published.pdf",
    "mu_comparison_all_vs_published.pdf",
]

missing = []
present = []
for fig_name in expected_figures:
    path = outdir / fig_name
    if path.exists() or path.is_symlink():
        present.append(fig_name)
    else:
        missing.append(fig_name)

log.info("Total expected: %d", len(expected_figures))
log.info("Present: %d", len(present))
log.info("Missing: %d", len(missing))
if missing:
    for m in missing:
        log.warning("MISSING: %s", m)
else:
    log.info("All expected figures are present.")

# Also list any figures in the directory not in our expected list
all_pdfs = sorted(p.name for p in outdir.glob("*.pdf"))
unexpected = [f for f in all_pdfs if f not in expected_figures]
if unexpected:
    log.info("Additional figures (not in expected list): %d", len(unexpected))
    for u in unexpected:
        log.info("  EXTRA: %s", u)

log.info("Figure aggregation complete.")
