"""
Phase 3 Step 6: Selection approach comparison [D9].

Compares cut-based (m_vis template) vs MVA (NN discriminant) approaches.
Reports S/sqrt(B), AUC, and expected significance for each.
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

mh.style.use("CMS")

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"
FIG_DIR = OUTPUT_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

SIGNAL_SAMPLES = ["GluGluToHToTauTau", "VBF_HToTauTau"]
BKG_SAMPLES = ["DYJetsToLL", "TTbar", "W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu"]
DATA_SAMPLES = ["Run2012B_TauPlusX", "Run2012C_TauPlusX"]


def load_sr(sample):
    path = OUTPUT_DIR / f"p3_{sample}_os_sr.npz"
    if not path.exists():
        return None
    return dict(np.load(path, allow_pickle=True))


def load_nn_score(sample):
    path = OUTPUT_DIR / f"p3_{sample}_os_sr_nn_score.npz"
    if not path.exists():
        return None
    return dict(np.load(path, allow_pickle=True))


def load_collinear(sample):
    path = OUTPUT_DIR / f"p3_{sample}_os_sr_collinear.npz"
    if not path.exists():
        return None
    return dict(np.load(path, allow_pickle=True))


def compute_significance(s_hist, b_hist):
    """Compute expected significance as sum_bins sqrt(2*((s+b)*ln(1+s/b) - s))."""
    sig2 = 0.0
    for s, b in zip(s_hist, b_hist):
        if b > 0 and s > 0:
            sig2 += 2.0 * ((s + b) * np.log(1 + s / b) - s)
    return np.sqrt(max(sig2, 0.0))


def get_qcd_template(var_name, bins, sf_w, r_osss, get_vals_fn):
    """Build QCD template from SS data - SS MC, scaled by OS/SS ratio.

    Provides consistent QCD treatment across all approaches (B6 fix).
    """
    all_mc = list(set(BKG_SAMPLES + SIGNAL_SAMPLES))
    w_samples = ["W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu"]

    data_vals = []
    for ds in DATA_SAMPLES:
        path = OUTPUT_DIR / f"p3_{ds}_ss_sr.npz"
        if not path.exists():
            continue
        d = dict(np.load(path, allow_pickle=True))
        if len(d["mu_pt"]) > 0:
            vals = get_vals_fn(d, ds)
            if vals is not None:
                data_vals.append(vals)

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
        w = d["weight"]
        if sn in w_samples:
            w = w * sf_w
        vals = get_vals_fn(d, sn)
        if vals is not None:
            h, _ = np.histogram(vals, bins=bins, weights=w)
            h_mc += h

    h_qcd = r_osss * (h_data.astype(float) - h_mc)
    h_qcd = np.maximum(h_qcd, 0.0)
    return h_qcd


def evaluate_cutbased():
    """Evaluate cut-based approach: S/sqrt(B) in m_vis 100-150 GeV window."""
    log.info("\n=== Cut-based Approach (m_vis template) ===")

    # Load background estimation for SF
    bkg_path = OUTPUT_DIR / "background_estimation.json"
    sf_w = 1.0
    r_osss = 1.06
    if bkg_path.exists():
        with open(bkg_path) as f:
            bkg = json.load(f)
        sf_w = bkg["sf_w"]
        r_osss = bkg["r_osss"]

    mvis_bins = np.linspace(0, 250, 26)  # 10 GeV bins
    higgs_window = (mvis_bins[:-1] >= 100) & (mvis_bins[1:] <= 150)

    # Signal in Higgs window
    s_total = 0.0
    for sn in SIGNAL_SAMPLES:
        d = load_sr(sn)
        if d is None:
            continue
        h, _ = np.histogram(d["mvis"], bins=mvis_bins, weights=d["weight"])
        s_total += float(np.sum(h[higgs_window]))

    # Background in Higgs window
    b_total = 0.0
    w_samples = ["W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu"]
    for sn in BKG_SAMPLES:
        d = load_sr(sn)
        if d is None:
            continue
        w = d["weight"]
        if sn in w_samples:
            w = w * sf_w
        h, _ = np.histogram(d["mvis"], bins=mvis_bins, weights=w)
        b_total += float(np.sum(h[higgs_window]))

    # Add actual QCD template in window (B6 fix: use actual QCD shape)
    qcd_template = get_qcd_template("mvis", mvis_bins, sf_w, r_osss,
                                      lambda d, sn: d["mvis"])
    b_total += float(np.sum(qcd_template[higgs_window]))

    s_over_sqrtb = s_total / np.sqrt(max(b_total, 1))

    log.info("Signal (100-150 GeV): %.2f weighted events", s_total)
    log.info("Background (100-150 GeV): %.2f weighted events", b_total)
    log.info("S/sqrt(B) = %.4f", s_over_sqrtb)

    # Full template significance (includes QCD)
    s_hist = np.zeros(len(mvis_bins) - 1)
    b_hist = np.zeros(len(mvis_bins) - 1)

    for sn in SIGNAL_SAMPLES:
        d = load_sr(sn)
        if d is None:
            continue
        h, _ = np.histogram(d["mvis"], bins=mvis_bins, weights=d["weight"])
        s_hist += h

    for sn in BKG_SAMPLES:
        d = load_sr(sn)
        if d is None:
            continue
        w = d["weight"]
        if sn in w_samples:
            w = w * sf_w
        h, _ = np.histogram(d["mvis"], bins=mvis_bins, weights=w)
        b_hist += h

    b_hist += qcd_template  # Add QCD to background

    expected_sig = compute_significance(s_hist, b_hist)
    log.info("Expected significance (full m_vis template): %.4f sigma", expected_sig)

    return {
        "approach": "cut-based (m_vis template)",
        "s_window": s_total,
        "b_window": b_total,
        "s_over_sqrtb": s_over_sqrtb,
        "expected_significance": expected_sig,
    }


def evaluate_nn():
    """Evaluate NN discriminant approach (with QCD template)."""
    log.info("\n=== NN Discriminant Approach ===")

    # Load NN results
    nn_path = OUTPUT_DIR / "nn_discriminant_results.json"
    if not nn_path.exists():
        log.info("NN results not found")
        return None

    with open(nn_path) as f:
        nn_results = json.load(f)

    auc = nn_results["auc_test"]
    log.info("AUC (test) = %.4f", auc)

    # Load background estimation
    bkg_path = OUTPUT_DIR / "background_estimation.json"
    sf_w = 1.0
    r_osss = 1.06
    if bkg_path.exists():
        with open(bkg_path) as f:
            bkg = json.load(f)
        sf_w = bkg["sf_w"]
        r_osss = bkg["r_osss"]

    # Build NN score histograms
    nn_bins = np.linspace(0, 1, 21)

    s_hist = np.zeros(len(nn_bins) - 1)
    b_hist = np.zeros(len(nn_bins) - 1)
    w_samples = ["W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu"]

    for sn in SIGNAL_SAMPLES:
        d = load_sr(sn)
        nn = load_nn_score(sn)
        if d is None or nn is None:
            continue
        h, _ = np.histogram(nn["nn_score"], bins=nn_bins, weights=d["weight"])
        s_hist += h

    for sn in BKG_SAMPLES:
        d = load_sr(sn)
        nn = load_nn_score(sn)
        if d is None or nn is None:
            continue
        w = d["weight"]
        if sn in w_samples:
            w = w * sf_w
        h, _ = np.histogram(nn["nn_score"], bins=nn_bins, weights=w)
        b_hist += h

    # Add QCD template from SS NN scores (B6 fix)
    def get_nn_ss(d, sn):
        nn_path = OUTPUT_DIR / f"p3_{sn}_ss_sr_nn_score.npz"
        if not nn_path.exists():
            return None
        nn = dict(np.load(nn_path, allow_pickle=True))
        return nn["nn_score"]

    qcd_nn = get_qcd_template("nn_score", nn_bins, sf_w, r_osss, get_nn_ss)
    b_hist += qcd_nn

    expected_sig = compute_significance(s_hist, b_hist)
    log.info("Expected significance (NN score template, with QCD): %.4f sigma", expected_sig)

    # S/sqrt(B) in high NN score region (> 0.8)
    high_score_mask = nn_bins[:-1] >= 0.8
    s_high = float(np.sum(s_hist[high_score_mask]))
    b_high = float(np.sum(b_hist[high_score_mask]))
    s_over_sqrtb = s_high / np.sqrt(max(b_high, 1))
    log.info("S/sqrt(B) (NN > 0.8) = %.4f", s_over_sqrtb)

    return {
        "approach": "NN discriminant",
        "auc_test": auc,
        "s_over_sqrtb_high_score": s_over_sqrtb,
        "expected_significance": expected_sig,
    }


def evaluate_collinear():
    """Evaluate collinear mass approach (with QCD template)."""
    log.info("\n=== Collinear Mass Approach ===")

    bkg_path = OUTPUT_DIR / "background_estimation.json"
    sf_w = 1.0
    r_osss = 1.06
    if bkg_path.exists():
        with open(bkg_path) as f:
            bkg = json.load(f)
        sf_w = bkg["sf_w"]
        r_osss = bkg["r_osss"]

    mcol_bins = np.linspace(0, 300, 31)
    higgs_window = (mcol_bins[:-1] >= 110) & (mcol_bins[1:] <= 160)

    s_hist = np.zeros(len(mcol_bins) - 1)
    b_hist = np.zeros(len(mcol_bins) - 1)
    w_samples = ["W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu"]

    for sn in SIGNAL_SAMPLES:
        d = load_sr(sn)
        col = load_collinear(sn)
        if d is None or col is None:
            continue
        h, _ = np.histogram(col["m_col"], bins=mcol_bins, weights=d["weight"])
        s_hist += h

    for sn in BKG_SAMPLES:
        d = load_sr(sn)
        col = load_collinear(sn)
        if d is None or col is None:
            continue
        w = d["weight"]
        if sn in w_samples:
            w = w * sf_w
        h, _ = np.histogram(col["m_col"], bins=mcol_bins, weights=w)
        b_hist += h

    # Add QCD template from SS collinear mass (B6 fix)
    def get_mcol_ss(d, sn):
        col_path = OUTPUT_DIR / f"p3_{sn}_ss_sr_collinear.npz"
        if not col_path.exists():
            return None
        col = dict(np.load(col_path, allow_pickle=True))
        return col["m_col"]

    qcd_mcol = get_qcd_template("mcol", mcol_bins, sf_w, r_osss, get_mcol_ss)
    b_hist += qcd_mcol

    s_window = float(np.sum(s_hist[higgs_window]))
    b_window = float(np.sum(b_hist[higgs_window]))
    s_over_sqrtb = s_window / np.sqrt(max(b_window, 1))

    expected_sig = compute_significance(s_hist, b_hist)

    log.info("Signal (110-160 GeV): %.2f", s_window)
    log.info("Background (110-160 GeV): %.2f", b_window)
    log.info("S/sqrt(B) = %.4f", s_over_sqrtb)
    log.info("Expected significance (m_col template, with QCD): %.4f sigma", expected_sig)

    return {
        "approach": "collinear mass template",
        "s_window": s_window,
        "b_window": b_window,
        "s_over_sqrtb": s_over_sqrtb,
        "expected_significance": expected_sig,
    }


def plot_comparison(results):
    """Plot approach comparison."""
    approaches = [r["approach"] for r in results if r is not None]
    sigs = [r["expected_significance"] for r in results if r is not None]

    fig, ax = plt.subplots(figsize=(10, 10))
    y_pos = np.arange(len(approaches))
    ax.barh(y_pos, sigs, color=["#1f77b4", "#ff7f0e", "#2ca02c"][:len(approaches)],
            edgecolor="black", linewidth=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(approaches, fontsize="x-small")
    ax.set_xlabel("Expected Significance [$\\sigma$]")
    ax.invert_yaxis()
    mh.label.exp_label(exp="CMS", data=True, llabel="Open Data",
                        rlabel=r"$\sqrt{s} = 8$ TeV", loc=0, ax=ax)

    fig.savefig(FIG_DIR / "approach_comparison.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig.savefig(FIG_DIR / "approach_comparison.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info("Saved approach comparison plot")


def main():
    log.info("=" * 60)
    log.info("Phase 3 Step 6: Approach Comparison")
    log.info("=" * 60)

    results = []

    # Cut-based
    r_cut = evaluate_cutbased()
    results.append(r_cut)

    # NN
    r_nn = evaluate_nn()
    if r_nn is not None:
        results.append(r_nn)

    # Collinear mass
    r_col = evaluate_collinear()
    results.append(r_col)

    # Comparison
    log.info("\n" + "=" * 60)
    log.info("APPROACH COMPARISON SUMMARY")
    log.info("=" * 60)
    log.info("%-35s %15s", "Approach", "Expected Sig")
    for r in results:
        if r is not None:
            log.info("%-35s %15.4f sigma", r["approach"], r["expected_significance"])

    # Best approach
    best = max([r for r in results if r is not None],
               key=lambda x: x["expected_significance"])
    log.info("\nBest approach: %s (%.4f sigma)", best["approach"], best["expected_significance"])

    # Save
    with open(OUTPUT_DIR / "approach_comparison.json", "w") as f:
        json.dump(results, f, indent=2)
    log.info("Results saved to approach_comparison.json")

    # Plot
    plot_comparison(results)


if __name__ == "__main__":
    main()
