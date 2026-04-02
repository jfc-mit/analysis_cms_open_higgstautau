"""
Phase 3 Step 7: Data/MC comparison plots for all discriminants and categories.

Produces stacked MC + data overlay plots with ratio panels for:
- m_vis, NN score, collinear mass
- In Baseline and VBF categories
- Kinematic variables in Baseline and VBF categories

Uses mh.histplot for all histogram rendering (no ax.bar/ax.step).
QCD template included for ALL discriminant plots (NN score and collinear
mass use actual SS-region values, not proxies).
"""
import logging
import json
from pathlib import Path

from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep as mh
import hist

mh.style.use("CMS")

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"
FIG_DIR = OUTPUT_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

DATA_SAMPLES = ["Run2012B_TauPlusX", "Run2012C_TauPlusX"]
W_SAMPLES = ["W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu"]
BKG_SAMPLES = ["DYJetsToLL", "TTbar", "W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu"]
SIGNAL_SAMPLES = ["GluGluToHToTauTau", "VBF_HToTauTau"]


def load_sr(sample):
    path = OUTPUT_DIR / f"p3_{sample}_os_sr.npz"
    if not path.exists():
        return None
    return dict(np.load(path, allow_pickle=True))


def load_nn_score(sample, region="os_sr"):
    path = OUTPUT_DIR / f"p3_{sample}_{region}_nn_score.npz"
    if not path.exists():
        return None
    return dict(np.load(path, allow_pickle=True))


def load_collinear(sample, region="os_sr"):
    path = OUTPUT_DIR / f"p3_{sample}_{region}_collinear.npz"
    if not path.exists():
        return None
    return dict(np.load(path, allow_pickle=True))


def get_category_mask(d, category):
    """Get mask for Baseline or VBF category."""
    if category == "inclusive":
        return np.ones(len(d["mu_pt"]), dtype=bool)
    elif category == "vbf":
        return (d["njets"] >= 2) & (d["mjj"] > 200) & (np.abs(d["deta_jj"]) > 2.0)
    elif category == "baseline":
        vbf = (d["njets"] >= 2) & (d["mjj"] > 200) & (np.abs(d["deta_jj"]) > 2.0)
        return ~vbf
    return np.ones(len(d["mu_pt"]), dtype=bool)


def make_hist_obj(bins, values):
    """Create a hist object with given bin edges and fill from values array."""
    h = hist.Hist(hist.axis.Variable(bins, name="x"))
    h.view()[:] = values
    return h


def make_data_mc_plot(variable_name, xlabel, bins, category, get_vals_fn,
                       sf_w=1.0, qcd_template=None, signal_scale=10.0,
                       logy=False):
    """Generic data/MC comparison plot with ratio panel using mh.histplot."""
    fig, (ax, rax) = plt.subplots(2, 1, figsize=(10, 10),
                                   gridspec_kw={"height_ratios": [3, 1]},
                                   sharex=True)
    fig.subplots_adjust(hspace=0)

    # Data histogram
    data_vals = []
    for ds in DATA_SAMPLES:
        d = load_sr(ds)
        if d is None or len(d["mu_pt"]) == 0:
            continue
        cat_mask = get_category_mask(d, category)
        vals = get_vals_fn(d, ds)
        if vals is not None:
            data_vals.append(vals[cat_mask])

    if data_vals:
        data_all = np.concatenate(data_vals)
    else:
        data_all = np.array([])
    h_data_arr, _ = np.histogram(data_all, bins=bins)

    # MC stacks: DY (split into ZTT and ZLL), TTbar, W+jets combined
    dy_d = load_sr("DYJetsToLL")
    dy_cat = get_category_mask(dy_d, category) if dy_d is not None else np.array([], dtype=bool)

    h_ztt = np.zeros(len(bins) - 1)
    h_zll = np.zeros(len(bins) - 1)
    if dy_d is not None and len(dy_d["mu_pt"]) > 0 and "is_ztt" in dy_d:
        ztt_mask = dy_d["is_ztt"].astype(bool) & dy_cat
        zll_mask = (~dy_d["is_ztt"].astype(bool)) & dy_cat
        vals = get_vals_fn(dy_d, "DYJetsToLL")
        if vals is not None:
            h_ztt, _ = np.histogram(vals[ztt_mask], bins=bins, weights=dy_d["weight"][ztt_mask])
            h_zll, _ = np.histogram(vals[zll_mask], bins=bins, weights=dy_d["weight"][zll_mask])
    elif dy_d is not None and len(dy_d["mu_pt"]) > 0:
        vals = get_vals_fn(dy_d, "DYJetsToLL")
        if vals is not None:
            h_ztt, _ = np.histogram(vals[dy_cat], bins=bins, weights=dy_d["weight"][dy_cat])

    h_tt = np.zeros(len(bins) - 1)
    d = load_sr("TTbar")
    if d is not None and len(d["mu_pt"]) > 0:
        cat_mask = get_category_mask(d, category)
        vals = get_vals_fn(d, "TTbar")
        if vals is not None:
            h_tt, _ = np.histogram(vals[cat_mask], bins=bins, weights=d["weight"][cat_mask])

    h_wjets = np.zeros(len(bins) - 1)
    for sn in W_SAMPLES:
        d = load_sr(sn)
        if d is not None and len(d["mu_pt"]) > 0:
            cat_mask = get_category_mask(d, category)
            vals = get_vals_fn(d, sn)
            if vals is not None:
                h, _ = np.histogram(vals[cat_mask], bins=bins,
                                     weights=d["weight"][cat_mask] * sf_w)
                h_wjets += h

    h_qcd = np.zeros(len(bins) - 1)
    if qcd_template is not None:
        h_qcd = qcd_template

    # Build hist objects for mh.histplot stacking
    stack_data = []
    stack_labels = []
    stack_colors = []

    for h_arr, label, color in [
        (h_qcd, "QCD", "#aec7e8"),
        (h_wjets, "W+jets", "#8c564b"),
        (h_tt, r"$t\bar{t}$", "#9467bd"),
        (h_zll, r"$Z \to \ell\ell$", "#98df8a"),
        (h_ztt, r"$Z \to \tau\tau$", "#f0c571"),
    ]:
        if np.sum(h_arr) > 0:
            stack_data.append(make_hist_obj(bins, h_arr))
            stack_labels.append(label)
            stack_colors.append(color)

    mc_total = h_qcd + h_wjets + h_tt + h_zll + h_ztt

    if stack_data:
        mh.histplot(stack_data, ax=ax, stack=True, histtype="fill",
                     label=stack_labels, color=stack_colors,
                     edgecolor="black", linewidth=0.5)

    # Signal (scaled) using mh.histplot step
    for sn, label, color in [("GluGluToHToTauTau", f"ggH (x{signal_scale:.0f})", "#d62728"),
                               ("VBF_HToTauTau", f"VBF (x{signal_scale:.0f})", "#ff7f0e")]:
        d = load_sr(sn)
        if d is None or len(d["mu_pt"]) == 0:
            continue
        cat_mask = get_category_mask(d, category)
        vals = get_vals_fn(d, sn)
        if vals is not None:
            h_sig_arr, _ = np.histogram(vals[cat_mask], bins=bins,
                                         weights=d["weight"][cat_mask] * signal_scale)
            h_sig = make_hist_obj(bins, h_sig_arr)
            mh.histplot(h_sig, ax=ax, histtype="step", color=color,
                         linewidth=2, linestyle="--", label=label)

    # Data points using mh.histplot errorbar
    h_data_obj = make_hist_obj(bins, h_data_arr.astype(float))
    mh.histplot(h_data_obj, ax=ax, histtype="errorbar", color="black",
                 yerr=np.sqrt(np.maximum(h_data_arr, 0).astype(float)),
                 label="Data", markersize=4)

    width = bins[1] - bins[0]
    ax.set_ylabel(f"Events / {width:.0f}" if width >= 1 else f"Events / {width:.2f}")
    ax.legend(fontsize="x-small", loc="upper right", ncol=2)
    if logy:
        ax.set_yscale("log")
        ax.set_ylim(0.1, ax.get_ylim()[1] * 5)
    else:
        ax.set_ylim(0, ax.get_ylim()[1] * 1.4)

    cat_label = {"baseline": "Baseline", "vbf": "VBF", "inclusive": "Inclusive"}.get(category, category)
    mh.label.exp_label(exp="CMS", data=True, llabel=f"Open Data, {cat_label}",
                        rlabel=r"$\sqrt{s} = 8$ TeV", loc=0, ax=ax)

    # Ratio panel
    centers = (bins[:-1] + bins[1:]) / 2
    ratio = np.divide(h_data_arr.astype(float), mc_total,
                       where=mc_total > 0, out=np.ones_like(mc_total))
    ratio_err = np.divide(np.sqrt(np.maximum(h_data_arr, 0).astype(float)), mc_total,
                           where=mc_total > 0, out=np.zeros_like(mc_total))
    rax.errorbar(centers, ratio, yerr=ratio_err, fmt="ko", markersize=4)
    rax.axhline(1, color="gray", linestyle="--", linewidth=1)
    rax.set_ylim(0.5, 1.5)
    rax.set_xlabel(xlabel)
    rax.set_ylabel("Data / MC")

    fname = f"{variable_name}_{category}"
    fig.savefig(FIG_DIR / f"{fname}.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig.savefig(FIG_DIR / f"{fname}.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info("Saved %s", fname)


def make_qcd_template(var_name, bins, sf_w, r_osss, get_vals_fn, category):
    """Build QCD template from SS data - SS MC, scaled by OS/SS ratio."""
    all_mc = list(set(BKG_SAMPLES + SIGNAL_SAMPLES))

    data_vals = []
    for ds in DATA_SAMPLES:
        path = OUTPUT_DIR / f"p3_{ds}_ss_sr.npz"
        if not path.exists():
            continue
        d = dict(np.load(path, allow_pickle=True))
        if len(d["mu_pt"]) == 0:
            continue
        cat_mask = get_category_mask(d, category)
        vals = get_vals_fn(d, ds)
        if vals is not None:
            data_vals.append(vals[cat_mask])

    if not data_vals:
        return np.zeros(len(bins) - 1)
    data_all = np.concatenate(data_vals)
    h_data, _ = np.histogram(data_all, bins=bins)

    h_mc = np.zeros(len(bins) - 1)
    for sn in all_mc:
        path = OUTPUT_DIR / f"p3_{sn}_ss_sr.npz"
        if not path.exists():
            continue
        d = dict(np.load(path, allow_pickle=True))
        if len(d["mu_pt"]) == 0:
            continue
        cat_mask = get_category_mask(d, category)
        w = d["weight"]
        if sn in W_SAMPLES:
            w = w * sf_w
        vals = get_vals_fn(d, sn)
        if vals is not None:
            h, _ = np.histogram(vals[cat_mask], bins=bins, weights=w[cat_mask])
            h_mc += h

    h_qcd = r_osss * (h_data.astype(float) - h_mc)
    h_qcd = np.maximum(h_qcd, 0.0)
    return h_qcd


def make_qcd_template_nn(bins, sf_w, r_osss, category):
    """Build QCD template for NN score from SS SR NN score files."""
    all_mc = list(set(BKG_SAMPLES + SIGNAL_SAMPLES))

    data_vals = []
    for ds in DATA_SAMPLES:
        ss_path = OUTPUT_DIR / f"p3_{ds}_ss_sr.npz"
        nn_path = OUTPUT_DIR / f"p3_{ds}_ss_sr_nn_score.npz"
        if not ss_path.exists() or not nn_path.exists():
            continue
        d = dict(np.load(ss_path, allow_pickle=True))
        nn = dict(np.load(nn_path, allow_pickle=True))
        if len(d["mu_pt"]) == 0:
            continue
        cat_mask = get_category_mask(d, category)
        data_vals.append(nn["nn_score"][cat_mask])

    if not data_vals:
        return np.zeros(len(bins) - 1)
    data_all = np.concatenate(data_vals)
    h_data, _ = np.histogram(data_all, bins=bins)

    h_mc = np.zeros(len(bins) - 1)
    for sn in all_mc:
        ss_path = OUTPUT_DIR / f"p3_{sn}_ss_sr.npz"
        nn_path = OUTPUT_DIR / f"p3_{sn}_ss_sr_nn_score.npz"
        if not ss_path.exists() or not nn_path.exists():
            continue
        d = dict(np.load(ss_path, allow_pickle=True))
        nn = dict(np.load(nn_path, allow_pickle=True))
        if len(d["mu_pt"]) == 0:
            continue
        cat_mask = get_category_mask(d, category)
        w = d["weight"]
        if sn in W_SAMPLES:
            w = w * sf_w
        h, _ = np.histogram(nn["nn_score"][cat_mask], bins=bins, weights=w[cat_mask])
        h_mc += h

    h_qcd = r_osss * (h_data.astype(float) - h_mc)
    h_qcd = np.maximum(h_qcd, 0.0)
    return h_qcd


def make_qcd_template_mcol(bins, sf_w, r_osss, category):
    """Build QCD template for collinear mass from SS SR collinear mass files."""
    all_mc = list(set(BKG_SAMPLES + SIGNAL_SAMPLES))

    data_vals = []
    for ds in DATA_SAMPLES:
        ss_path = OUTPUT_DIR / f"p3_{ds}_ss_sr.npz"
        col_path = OUTPUT_DIR / f"p3_{ds}_ss_sr_collinear.npz"
        if not ss_path.exists() or not col_path.exists():
            continue
        d = dict(np.load(ss_path, allow_pickle=True))
        col = dict(np.load(col_path, allow_pickle=True))
        if len(d["mu_pt"]) == 0:
            continue
        cat_mask = get_category_mask(d, category)
        data_vals.append(col["m_col"][cat_mask])

    if not data_vals:
        return np.zeros(len(bins) - 1)
    data_all = np.concatenate(data_vals)
    h_data, _ = np.histogram(data_all, bins=bins)

    h_mc = np.zeros(len(bins) - 1)
    for sn in all_mc:
        ss_path = OUTPUT_DIR / f"p3_{sn}_ss_sr.npz"
        col_path = OUTPUT_DIR / f"p3_{sn}_ss_sr_collinear.npz"
        if not ss_path.exists() or not col_path.exists():
            continue
        d = dict(np.load(ss_path, allow_pickle=True))
        col = dict(np.load(col_path, allow_pickle=True))
        if len(d["mu_pt"]) == 0:
            continue
        cat_mask = get_category_mask(d, category)
        w = d["weight"]
        if sn in W_SAMPLES:
            w = w * sf_w
        h, _ = np.histogram(col["m_col"][cat_mask], bins=bins, weights=w[cat_mask])
        h_mc += h

    h_qcd = r_osss * (h_data.astype(float) - h_mc)
    h_qcd = np.maximum(h_qcd, 0.0)
    return h_qcd


def main():
    log.info("=" * 60)
    log.info("Phase 3 Step 7: Data/MC Comparison Plots (fixed)")
    log.info("=" * 60)

    # Load background estimation
    bkg_path = OUTPUT_DIR / "background_estimation.json"
    sf_w = 1.0
    r_osss = 1.06
    if bkg_path.exists():
        with open(bkg_path) as f:
            bkg = json.load(f)
        sf_w = bkg["sf_w"]
        r_osss = bkg["r_osss"]
    log.info("W+jets SF = %.3f, OS/SS = %.3f", sf_w, r_osss)

    # --- m_vis plots ---
    mvis_bins = np.linspace(0, 200, 26)
    def get_mvis(d, sn):
        return d["mvis"]

    for cat in ["baseline", "vbf"]:
        qcd = make_qcd_template("mvis", mvis_bins, sf_w, r_osss, get_mvis, cat)
        make_data_mc_plot("mvis", r"$m_{\mathrm{vis}}$ [GeV]", mvis_bins,
                          cat, get_mvis, sf_w=sf_w, qcd_template=qcd)

    # --- NN score plots (A3 fix: now includes QCD from SS NN scores) ---
    nn_bins = np.linspace(0, 1, 21)
    def get_nn_score(d, sn):
        nn = load_nn_score(sn, "os_sr")
        if nn is None:
            return None
        return nn["nn_score"]

    for cat in ["baseline", "vbf"]:
        qcd_nn = make_qcd_template_nn(nn_bins, sf_w, r_osss, cat)
        make_data_mc_plot("nn_score", "NN Score", nn_bins,
                          cat, get_nn_score, sf_w=sf_w, qcd_template=qcd_nn,
                          signal_scale=10.0)

    # --- Collinear mass plots (B2 fix: uses actual collinear mass for QCD) ---
    mcol_bins = np.linspace(0, 300, 31)
    def get_mcol(d, sn):
        col = load_collinear(sn, "os_sr")
        if col is None:
            return None
        return col["m_col"]

    for cat in ["baseline", "vbf"]:
        qcd_mcol = make_qcd_template_mcol(mcol_bins, sf_w, r_osss, cat)
        make_data_mc_plot("mcol", r"$m_{\mathrm{col}}$ [GeV]", mcol_bins,
                          cat, get_mcol, sf_w=sf_w, qcd_template=qcd_mcol)

    # --- Kinematic plots for BOTH Baseline and VBF (B5 fix: adds VBF) ---
    kinematic_vars = [
        ("tau_pt", r"$\tau_h$ $p_T$ [GeV]", np.linspace(20, 120, 21)),
        ("mu_pt", r"$\mu$ $p_T$ [GeV]", np.linspace(20, 120, 21)),
        ("met_pt", r"$E_T^{\mathrm{miss}}$ [GeV]", np.linspace(0, 100, 21)),
        ("njets", r"$N_{\mathrm{jets}}$", np.arange(-0.5, 7.5, 1)),
        ("delta_r", r"$\Delta R(\mu, \tau_h)$", np.linspace(0.5, 5.0, 19)),
    ]

    for cat in ["baseline", "vbf"]:
        for var_name, xlabel, bins_var in kinematic_vars:
            def get_var(d, sn, vn=var_name):
                return d[vn]
            qcd = make_qcd_template(var_name, bins_var, sf_w, r_osss, get_var, cat)
            make_data_mc_plot(var_name, xlabel, bins_var,
                              cat, get_var, sf_w=sf_w, qcd_template=qcd)

    log.info("\nAll plots saved to %s", FIG_DIR)


if __name__ == "__main__":
    main()
