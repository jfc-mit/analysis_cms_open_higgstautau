"""
Phase 3 Step 2: Data-driven background estimation.

W+jets: high-mT sideband normalization [D3]
QCD: same-sign control region with measured OS/SS ratio [D4]
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

SAMPLES_MC = {
    "GluGluToHToTauTau": {"label": "ggH", "color": "#d62728"},
    "VBF_HToTauTau": {"label": "VBF", "color": "#ff7f0e"},
    "DYJetsToLL": {"label": "DY", "color": "#f0c571"},
    "TTbar": {"label": r"$t\bar{t}$", "color": "#9467bd"},
    "W1JetsToLNu": {"label": "W+1j", "color": "#8c564b"},
    "W2JetsToLNu": {"label": "W+2j", "color": "#a67c6b"},
    "W3JetsToLNu": {"label": "W+3j", "color": "#c49a8b"},
}

DATA_SAMPLES = ["Run2012B_TauPlusX", "Run2012C_TauPlusX"]
W_SAMPLES = ["W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu"]
NON_W_MC = ["GluGluToHToTauTau", "VBF_HToTauTau", "DYJetsToLL", "TTbar"]


def load_region(sample, region):
    """Load npz file for a sample/region, return dict of arrays or None."""
    path = OUTPUT_DIR / f"p3_{sample}_{region}.npz"
    if not path.exists():
        return None
    return dict(np.load(path, allow_pickle=True))


def weighted_sum(data):
    """Sum of weights for a region."""
    if data is None or len(data["weight"]) == 0:
        return 0.0
    return float(np.sum(data["weight"]))


def compute_wjets_sf():
    """Compute W+jets scale factor from high-mT sideband [D3].

    SF_W = (N_data - N_non-W_MC) / N_W_MC  in mT > 70 GeV region.
    """
    log.info("\n=== W+jets Scale Factor (high-mT sideband) ===")

    # Data in high-mT
    data_highmt = 0.0
    for ds in DATA_SAMPLES:
        d = load_region(ds, "os_highmt")
        data_highmt += weighted_sum(d)
    log.info("Data (mT > 70): %.1f", data_highmt)

    # Non-W MC in high-mT (with sum of weights squared for proper uncertainty)
    non_w_mc = 0.0
    non_w_mc_w2 = 0.0  # sum(w_i^2) for weighted MC stat uncertainty
    for sn in NON_W_MC:
        d = load_region(sn, "os_highmt")
        w = weighted_sum(d)
        non_w_mc += w
        if d is not None and len(d["weight"]) > 0:
            non_w_mc_w2 += float(np.sum(d["weight"]**2))
        log.info("  %s (mT > 70): %.1f", sn, w)
    log.info("Non-W MC total (mT > 70): %.1f", non_w_mc)

    # W+jets MC in high-mT
    w_mc = 0.0
    w_mc_w2 = 0.0
    for sn in W_SAMPLES:
        d = load_region(sn, "os_highmt")
        w = weighted_sum(d)
        w_mc += w
        if d is not None and len(d["weight"]) > 0:
            w_mc_w2 += float(np.sum(d["weight"]**2))
        log.info("  %s (mT > 70): %.1f", sn, w)
    log.info("W+jets MC total (mT > 70): %.1f", w_mc)

    if w_mc == 0:
        log.info("WARNING: No W+jets MC in high-mT region!")
        return 1.0, 0.0

    sf_w = (data_highmt - non_w_mc) / w_mc
    # B4 fix: proper uncertainty propagation with weighted MC statistics
    # sigma^2(SF) = (sigma^2(data) + sigma^2(non_W_MC)) / N_W_MC^2
    # + (data - non_W_MC)^2 * sigma^2(W_MC) / N_W_MC^4
    # where sigma^2(MC) = sum(w_i^2) (not sum(w_i))
    numerator_var = data_highmt + non_w_mc_w2  # Poisson data + weighted MC
    denominator_var = w_mc_w2  # weighted W+jets MC variance
    sf_w_err = sf_w * np.sqrt(numerator_var / max((data_highmt - non_w_mc)**2, 1)
                               + denominator_var / max(w_mc**2, 1))

    log.info("SF_W = (%.1f - %.1f) / %.1f = %.3f +/- %.3f",
             data_highmt, non_w_mc, w_mc, sf_w, sf_w_err)

    # Validation in intermediate mT (30-70 GeV)
    log.info("\n--- Validation in intermediate mT (30-70 GeV) ---")
    data_midmt = 0.0
    for ds in DATA_SAMPLES:
        d = load_region(ds, "os_midmt")
        data_midmt += weighted_sum(d)

    mc_midmt = 0.0
    for sn in NON_W_MC:
        d = load_region(sn, "os_midmt")
        mc_midmt += weighted_sum(d)

    w_mc_midmt = 0.0
    for sn in W_SAMPLES:
        d = load_region(sn, "os_midmt")
        w_mc_midmt += weighted_sum(d)

    pred_midmt = mc_midmt + sf_w * w_mc_midmt
    log.info("Data (30 < mT < 70): %.1f", data_midmt)
    log.info("MC pred (non-W + SF*W): %.1f (non-W: %.1f, W*SF: %.1f)",
             pred_midmt, mc_midmt, sf_w * w_mc_midmt)
    if pred_midmt > 0:
        log.info("Data/Pred = %.3f", data_midmt / pred_midmt)

    return sf_w, sf_w_err


def compute_qcd_osss():
    """Compute QCD from same-sign control region [D4].

    1. Measure OS/SS ratio in anti-isolated control region.
    2. Subtract MC from SS data.
    3. Apply OS/SS ratio.
    """
    log.info("\n=== QCD Estimation (Same-Sign Method) ===")

    # Step 1: Measure OS/SS ratio in anti-isolated CR
    log.info("\n--- OS/SS ratio from anti-isolated CR ---")

    # Data in anti-iso regions
    os_antiiso_data = 0.0
    ss_antiiso_data = 0.0
    for ds in DATA_SAMPLES:
        d_os = load_region(ds, "os_antiiso")
        d_ss = load_region(ds, "ss_antiiso")
        os_antiiso_data += weighted_sum(d_os)
        ss_antiiso_data += weighted_sum(d_ss)

    log.info("Data OS anti-iso: %.1f", os_antiiso_data)
    log.info("Data SS anti-iso: %.1f", ss_antiiso_data)

    # MC in anti-iso regions (to subtract)
    all_mc = list(SAMPLES_MC.keys())
    os_antiiso_mc = 0.0
    ss_antiiso_mc = 0.0
    for sn in all_mc:
        d_os = load_region(sn, "os_antiiso")
        d_ss = load_region(sn, "ss_antiiso")
        os_antiiso_mc += weighted_sum(d_os)
        ss_antiiso_mc += weighted_sum(d_ss)

    log.info("MC OS anti-iso: %.1f", os_antiiso_mc)
    log.info("MC SS anti-iso: %.1f", ss_antiiso_mc)

    qcd_os_antiiso = os_antiiso_data - os_antiiso_mc
    qcd_ss_antiiso = ss_antiiso_data - ss_antiiso_mc
    log.info("QCD OS anti-iso: %.1f", qcd_os_antiiso)
    log.info("QCD SS anti-iso: %.1f", qcd_ss_antiiso)

    if qcd_ss_antiiso > 0:
        r_osss = qcd_os_antiiso / qcd_ss_antiiso
        r_osss_err = r_osss * np.sqrt(1.0 / max(qcd_os_antiiso, 1) +
                                       1.0 / max(qcd_ss_antiiso, 1))
    else:
        log.info("WARNING: QCD SS anti-iso <= 0, using default OS/SS = 1.06")
        r_osss = 1.06
        r_osss_err = 0.5

    log.info("OS/SS ratio = %.3f +/- %.3f", r_osss, r_osss_err)
    log.info("  (Tutorial: 0.80, Published: 1.06)")

    # Step 2: QCD in SS signal region
    log.info("\n--- QCD from SS signal region ---")
    ss_sr_data = 0.0
    for ds in DATA_SAMPLES:
        d = load_region(ds, "ss_sr")
        ss_sr_data += weighted_sum(d)
    log.info("Data SS SR: %.1f", ss_sr_data)

    ss_sr_mc = 0.0
    for sn in all_mc:
        d = load_region(sn, "ss_sr")
        w = weighted_sum(d)
        ss_sr_mc += w
        log.info("  %s SS SR: %.1f", sn, w)
    log.info("MC SS SR total: %.1f", ss_sr_mc)

    qcd_ss = ss_sr_data - ss_sr_mc
    log.info("QCD SS (data - MC): %.1f", qcd_ss)

    qcd_os = r_osss * qcd_ss
    qcd_os_err = qcd_os * np.sqrt((r_osss_err / r_osss)**2 +
                                    1.0 / max(abs(qcd_ss), 1))
    log.info("QCD OS estimate: %.1f +/- %.1f", qcd_os, qcd_os_err)

    return r_osss, r_osss_err, qcd_os, qcd_os_err


def get_qcd_template_binned(var_name, bins, r_osss, sf_w=1.0):
    """Get QCD template histogram from SS data - SS MC.

    Returns bin contents and errors for the QCD template.
    """
    all_mc = list(SAMPLES_MC.keys())

    # SS SR data histogram
    data_vals = []
    for ds in DATA_SAMPLES:
        d = load_region(ds, "ss_sr")
        if d is not None and len(d[var_name]) > 0:
            data_vals.append(d[var_name])
    if data_vals:
        data_vals = np.concatenate(data_vals)
    else:
        data_vals = np.array([])

    h_data, _ = np.histogram(data_vals, bins=bins)

    # SS SR MC histogram (subtract from data)
    h_mc = np.zeros_like(h_data, dtype=float)
    for sn in all_mc:
        d = load_region(sn, "ss_sr")
        if d is None or len(d[var_name]) == 0:
            continue
        w = d["weight"]
        if sn in W_SAMPLES:
            w = w * sf_w
        h_tmp, _ = np.histogram(d[var_name], bins=bins, weights=w)
        h_mc += h_tmp

    h_qcd = r_osss * (h_data.astype(float) - h_mc)

    # Handle negative bins: set to 0 and note
    n_neg = int(np.sum(h_qcd < 0))
    if n_neg > 0:
        log.info("  QCD template: %d negative bins (set to 0)", n_neg)
        h_qcd = np.maximum(h_qcd, 0.0)

    return h_qcd


def plot_wjets_validation(sf_w):
    """Plot W+jets normalization validation in intermediate mT region."""
    bins = np.linspace(0, 200, 26)

    # Data
    data_vals = []
    for ds in DATA_SAMPLES:
        d = load_region(ds, "os_midmt")
        if d is not None and len(d["mvis"]) > 0:
            data_vals.append(d["mvis"])
    data_vals = np.concatenate(data_vals) if data_vals else np.array([])
    h_data, _ = np.histogram(data_vals, bins=bins)

    # MC stacks
    stack_labels = []
    stack_histos = []
    stack_colors = []

    # DY
    d = load_region("DYJetsToLL", "os_midmt")
    if d is not None and len(d["mvis"]) > 0:
        h, _ = np.histogram(d["mvis"], bins=bins, weights=d["weight"])
        stack_histos.append(h)
        stack_labels.append("DY")
        stack_colors.append("#f0c571")

    # TTbar
    d = load_region("TTbar", "os_midmt")
    if d is not None and len(d["mvis"]) > 0:
        h, _ = np.histogram(d["mvis"], bins=bins, weights=d["weight"])
        stack_histos.append(h)
        stack_labels.append(r"$t\bar{t}$")
        stack_colors.append("#9467bd")

    # W+jets with SF
    h_wjets = np.zeros(len(bins) - 1)
    for sn in W_SAMPLES:
        d = load_region(sn, "os_midmt")
        if d is not None and len(d["mvis"]) > 0:
            h, _ = np.histogram(d["mvis"], bins=bins, weights=d["weight"] * sf_w)
            h_wjets += h
    stack_histos.append(h_wjets)
    stack_labels.append(f"W+jets (SF={sf_w:.2f})")
    stack_colors.append("#8c564b")

    # Plot
    fig, (ax, rax) = plt.subplots(2, 1, figsize=(10, 10),
                                   gridspec_kw={"height_ratios": [3, 1]},
                                   sharex=True)
    fig.subplots_adjust(hspace=0)

    # Stack using mh.histplot
    mc_total = np.sum(stack_histos, axis=0)
    centers = (bins[:-1] + bins[1:]) / 2

    # Build hist objects for mh.histplot
    hist_objs = []
    for h_arr in stack_histos:
        h_obj = hist.Hist(hist.axis.Variable(bins, name="x"))
        h_obj.view()[:] = h_arr
        hist_objs.append(h_obj)

    mh.histplot(hist_objs, ax=ax, stack=True, histtype="fill",
                 label=stack_labels, color=stack_colors,
                 edgecolor="black", linewidth=0.5)

    # Data points using mh.histplot
    h_data_obj = hist.Hist(hist.axis.Variable(bins, name="x"))
    h_data_obj.view()[:] = h_data.astype(float)
    mh.histplot(h_data_obj, ax=ax, histtype="errorbar", color="black",
                 yerr=np.sqrt(h_data.astype(float)),
                 label="Data", markersize=4)

    ax.set_ylabel("Events / 8 GeV")
    ax.legend(fontsize="x-small", loc="upper right")
    mh.label.exp_label(exp="CMS", data=True, llabel="Open Data",
                        rlabel=r"$\sqrt{s} = 8$ TeV", loc=0, ax=ax)

    # Ratio
    ratio = np.divide(h_data, mc_total, where=mc_total > 0, out=np.ones_like(mc_total))
    ratio_err = np.divide(np.sqrt(h_data.astype(float)), mc_total, where=mc_total > 0, out=np.zeros_like(mc_total))
    rax.errorbar(centers, ratio, yerr=ratio_err, fmt="ko", markersize=4)
    rax.axhline(1, color="gray", linestyle="--", linewidth=1)
    rax.set_ylim(0.5, 1.5)
    rax.set_xlabel(r"$m_{\mathrm{vis}}$ [GeV]")
    rax.set_ylabel("Data / MC")

    fig.savefig(FIG_DIR / "wjets_validation_midmt.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig.savefig(FIG_DIR / "wjets_validation_midmt.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info("Saved W+jets validation plot")


def plot_mt_distribution():
    """Plot mT distribution with all regions marked."""
    bins = np.linspace(0, 150, 31)

    # Load OS no-mT-cut data
    data_vals = []
    for ds in DATA_SAMPLES:
        d = load_region(ds, "os_no_mt_cut")
        if d is not None and len(d["mt"]) > 0:
            data_vals.append(d["mt"])
    data_vals = np.concatenate(data_vals) if data_vals else np.array([])
    h_data, _ = np.histogram(data_vals, bins=bins)

    # MC
    mc_histos = {}
    for sn in SAMPLES_MC:
        d = load_region(sn, "os_no_mt_cut")
        if d is not None and len(d["mt"]) > 0:
            h, _ = np.histogram(d["mt"], bins=bins, weights=d["weight"])
            mc_histos[sn] = h
        else:
            mc_histos[sn] = np.zeros(len(bins) - 1)

    fig, (ax, rax) = plt.subplots(2, 1, figsize=(10, 10),
                                   gridspec_kw={"height_ratios": [3, 1]},
                                   sharex=True)
    fig.subplots_adjust(hspace=0)

    centers = (bins[:-1] + bins[1:]) / 2
    width = bins[1] - bins[0]

    # Stack order: DY, TTbar, W+jets
    stack_order = [("DYJetsToLL", "DY", "#f0c571"),
                   ("TTbar", r"$t\bar{t}$", "#9467bd"),
                   ("W1JetsToLNu", "W+1j", "#8c564b"),
                   ("W2JetsToLNu", "W+2j", "#a67c6b"),
                   ("W3JetsToLNu", "W+3j", "#c49a8b")]

    mc_total = np.zeros(len(bins) - 1)

    # Build hist objects for mh.histplot
    mt_hist_objs = []
    mt_labels = []
    mt_colors = []
    for sn, label, color in stack_order:
        h_arr = mc_histos.get(sn, np.zeros(len(bins) - 1))
        if np.sum(h_arr) > 0:
            h_obj = hist.Hist(hist.axis.Variable(bins, name="x"))
            h_obj.view()[:] = h_arr
            mt_hist_objs.append(h_obj)
            mt_labels.append(label)
            mt_colors.append(color)
        mc_total += h_arr

    if mt_hist_objs:
        mh.histplot(mt_hist_objs, ax=ax, stack=True, histtype="fill",
                     label=mt_labels, color=mt_colors,
                     edgecolor="black", linewidth=0.5)

    # Data points using mh.histplot
    h_data_mt_obj = hist.Hist(hist.axis.Variable(bins, name="x"))
    h_data_mt_obj.view()[:] = h_data.astype(float)
    mh.histplot(h_data_mt_obj, ax=ax, histtype="errorbar", color="black",
                 yerr=np.sqrt(h_data.astype(float)),
                 label="Data", markersize=4)

    # Mark regions
    ax.axvline(30, color="red", linestyle="--", linewidth=1.5, label="SR / mid-mT boundary")
    ax.axvline(70, color="blue", linestyle="--", linewidth=1.5, label="mid-mT / high-mT boundary")

    ax.set_ylabel("Events / 5 GeV")
    ax.set_yscale("log")
    ax.set_ylim(1, ax.get_ylim()[1] * 5)
    ax.legend(fontsize="x-small", loc="upper right")
    mh.label.exp_label(exp="CMS", data=True, llabel="Open Data",
                        rlabel=r"$\sqrt{s} = 8$ TeV", loc=0, ax=ax)

    ratio = np.divide(h_data, mc_total, where=mc_total > 0, out=np.ones_like(mc_total))
    ratio_err = np.divide(np.sqrt(h_data), mc_total, where=mc_total > 0, out=np.zeros_like(mc_total))
    rax.errorbar(centers, ratio, yerr=ratio_err, fmt="ko", markersize=4)
    rax.axhline(1, color="gray", linestyle="--", linewidth=1)
    rax.axvline(30, color="red", linestyle="--", linewidth=1.5)
    rax.axvline(70, color="blue", linestyle="--", linewidth=1.5)
    rax.set_ylim(0.5, 1.5)
    rax.set_xlabel(r"$m_T(\mu, E_T^{\mathrm{miss}})$ [GeV]")
    rax.set_ylabel("Data / MC")

    fig.savefig(FIG_DIR / "mt_regions.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig.savefig(FIG_DIR / "mt_regions.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info("Saved mT regions plot")


def main():
    log.info("=" * 60)
    log.info("Phase 3 Step 2: Background Estimation")
    log.info("=" * 60)

    # W+jets scale factor
    sf_w, sf_w_err = compute_wjets_sf()

    # QCD estimation
    r_osss, r_osss_err, qcd_os, qcd_os_err = compute_qcd_osss()

    # Save results
    results = {
        "sf_w": sf_w,
        "sf_w_err": sf_w_err,
        "r_osss": r_osss,
        "r_osss_err": r_osss_err,
        "qcd_os_yield": qcd_os,
        "qcd_os_yield_err": qcd_os_err,
    }

    results_path = OUTPUT_DIR / "background_estimation.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    log.info("\nResults saved to %s", results_path)

    # Plots
    plot_wjets_validation(sf_w)
    plot_mt_distribution()

    # Summary
    log.info("\n=== SUMMARY ===")
    log.info("W+jets SF = %.3f +/- %.3f", sf_w, sf_w_err)
    log.info("QCD OS/SS ratio = %.3f +/- %.3f", r_osss, r_osss_err)
    log.info("QCD OS yield = %.1f +/- %.1f", qcd_os, qcd_os_err)

    # Expected total after corrections
    mc_total = 0.0
    for sn in SAMPLES_MC:
        d = load_region(sn, "os_sr")
        w = weighted_sum(d)
        if sn in W_SAMPLES:
            w *= sf_w
        mc_total += w

    data_total = 0.0
    for ds in DATA_SAMPLES:
        d = load_region(ds, "os_sr")
        data_total += weighted_sum(d)

    log.info("\nCorrected yields (OS SR):")
    log.info("  MC (with W SF): %.1f", mc_total)
    log.info("  QCD: %.1f", qcd_os)
    log.info("  Total prediction: %.1f", mc_total + qcd_os)
    log.info("  Data: %.1f", data_total)
    log.info("  Data/Pred = %.3f", data_total / (mc_total + qcd_os) if (mc_total + qcd_os) > 0 else 0)


if __name__ == "__main__":
    main()
