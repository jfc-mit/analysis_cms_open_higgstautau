"""
Phase 3 Fix: Train alternative BDT classifier (A1).

Trains a GradientBoostingClassifier as a comparison to the NN.
Reports AUC comparison.
"""
import logging
import json
import pickle
from pathlib import Path

from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, roc_curve
from scipy.stats import ks_2samp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep as mh
import hist

mh.style.use("CMS")

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"
FIG_DIR = OUTPUT_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

SIGNAL_SAMPLES = ["GluGluToHToTauTau", "VBF_HToTauTau"]
BKG_SAMPLES = ["DYJetsToLL", "TTbar", "W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu"]

FEATURES = [
    "mu_pt", "mu_eta", "tau_pt", "tau_eta", "met_pt", "met_significance",
    "mvis", "mt", "delta_r", "delta_phi_mutau",
    "njets", "lead_jet_pt", "lead_jet_eta", "nbjets",
]

SEED = 42


def load_and_prepare_data():
    """Load signal and background from OS SR npz files."""
    X_sig, w_sig, X_bkg, w_bkg = [], [], [], []

    for sn in SIGNAL_SAMPLES:
        path = OUTPUT_DIR / f"p3_{sn}_os_sr.npz"
        if not path.exists():
            continue
        d = dict(np.load(path, allow_pickle=True))
        if len(d["mu_pt"]) == 0:
            continue
        features = np.column_stack([d[f] for f in FEATURES])
        X_sig.append(features)
        w_sig.append(d["weight"])

    for sn in BKG_SAMPLES:
        path = OUTPUT_DIR / f"p3_{sn}_os_sr.npz"
        if not path.exists():
            continue
        d = dict(np.load(path, allow_pickle=True))
        if len(d["mu_pt"]) == 0:
            continue
        features = np.column_stack([d[f] for f in FEATURES])
        X_bkg.append(features)
        w_bkg.append(d["weight"])

    X_sig = np.vstack(X_sig) if X_sig else np.empty((0, len(FEATURES)))
    w_sig = np.concatenate(w_sig) if w_sig else np.array([])
    X_bkg = np.vstack(X_bkg) if X_bkg else np.empty((0, len(FEATURES)))
    w_bkg = np.concatenate(w_bkg) if w_bkg else np.array([])

    return X_sig, w_sig, X_bkg, w_bkg


def main():
    log.info("=" * 60)
    log.info("Fix A1: Training BDT Alternative Classifier")
    log.info("=" * 60)

    X_sig, w_sig, X_bkg, w_bkg = load_and_prepare_data()
    log.info("Signal: %d events, Background: %d events", len(X_sig), len(X_bkg))

    if len(X_sig) == 0 or len(X_bkg) == 0:
        log.error("No data available!")
        return

    # Combine
    X = np.vstack([X_sig, X_bkg])
    y = np.concatenate([np.ones(len(X_sig)), np.zeros(len(X_bkg))])
    w = np.concatenate([w_sig, w_bkg])

    # Remove NaN/Inf
    mask = np.isfinite(X).all(axis=1)
    if not np.all(mask):
        n_bad = int(np.sum(~mask))
        log.info("Removing %d events with NaN/Inf features", n_bad)
        X, y, w = X[mask], y[mask], w[mask]

    # Same 50/25/25 split as NN (same seed for fair comparison)
    X_train, X_temp, y_train, y_temp, w_train, w_temp = train_test_split(
        X, y, w, test_size=0.5, random_state=SEED, stratify=y
    )
    X_val, X_test, y_val, y_test, w_val, w_test = train_test_split(
        X_temp, y_temp, w_temp, test_size=0.5, random_state=SEED, stratify=y_temp
    )
    log.info("Train: %d, Val: %d, Test: %d", len(X_train), len(X_val), len(X_test))

    # Equalize signal and background total weight for training
    sig_mask_train = y_train == 1
    bkg_mask_train = y_train == 0
    total_sig_w = np.sum(w_train[sig_mask_train])
    total_bkg_w = np.sum(w_train[bkg_mask_train])
    train_weights = w_train.copy()
    if total_sig_w > 0 and total_bkg_w > 0:
        train_weights[sig_mask_train] *= (total_bkg_w / total_sig_w)

    # Train BDT
    log.info("Training GradientBoostingClassifier...")
    bdt = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=3,
        learning_rate=0.1,
        subsample=0.8,
        min_samples_leaf=50,
        random_state=SEED,
        verbose=0,
    )
    bdt.fit(X_train, y_train, sample_weight=train_weights)
    log.info("BDT training complete. %d estimators.", bdt.n_estimators)

    # Predictions
    score_train = bdt.predict_proba(X_train)[:, 1]
    score_val = bdt.predict_proba(X_val)[:, 1]
    score_test = bdt.predict_proba(X_test)[:, 1]

    # AUC
    auc_train = roc_auc_score(y_train, score_train, sample_weight=w_train)
    auc_val = roc_auc_score(y_val, score_val, sample_weight=w_val)
    auc_test = roc_auc_score(y_test, score_test, sample_weight=w_test)
    log.info("BDT AUC -- Train: %.4f, Val: %.4f, Test: %.4f", auc_train, auc_val, auc_test)

    # Overtraining check
    sig_train_scores = score_train[y_train == 1]
    sig_test_scores = score_test[y_test == 1]
    bkg_train_scores = score_train[y_train == 0]
    bkg_test_scores = score_test[y_test == 0]

    ks_sig, p_sig = ks_2samp(sig_train_scores, sig_test_scores)
    ks_bkg, p_bkg = ks_2samp(bkg_train_scores, bkg_test_scores)
    log.info("BDT Overtraining KS test:")
    log.info("  Signal: KS=%.4f, p=%.4f", ks_sig, p_sig)
    log.info("  Background: KS=%.4f, p=%.4f", ks_bkg, p_bkg)

    # Load NN results for comparison
    nn_results_path = OUTPUT_DIR / "nn_discriminant_results.json"
    nn_auc_test = None
    if nn_results_path.exists():
        with open(nn_results_path) as f:
            nn_results = json.load(f)
        nn_auc_test = nn_results["auc_test"]
        log.info("\n=== COMPARISON ===")
        log.info("NN AUC (test):  %.4f", nn_auc_test)
        log.info("BDT AUC (test): %.4f", auc_test)
        log.info("Difference:     %.4f (NN - BDT)", nn_auc_test - auc_test)

    # Save BDT results
    bdt_results = {
        "auc_train": auc_train,
        "auc_val": auc_val,
        "auc_test": auc_test,
        "ks_sig": ks_sig, "p_sig": p_sig,
        "ks_bkg": ks_bkg, "p_bkg": p_bkg,
        "n_estimators": bdt.n_estimators,
        "max_depth": bdt.max_depth,
        "learning_rate": bdt.learning_rate,
        "seed": SEED,
        "nn_auc_test": nn_auc_test,
    }
    with open(OUTPUT_DIR / "bdt_alternative_results.json", "w") as f:
        json.dump(bdt_results, f, indent=2)

    # Save model
    with open(OUTPUT_DIR / "bdt_alternative_model.pkl", "wb") as f:
        pickle.dump({"model": bdt, "features": FEATURES}, f)

    # --- ROC comparison plot ---
    fig, ax = plt.subplots(figsize=(10, 10))

    # BDT ROC
    fpr_bdt, tpr_bdt, _ = roc_curve(y_test, score_test, sample_weight=w_test)
    ax.plot(fpr_bdt, tpr_bdt, color="blue", linewidth=2,
            label=f"BDT (AUC = {auc_test:.4f})")

    # NN ROC (load NN model and recompute on same test set)
    nn_model_path = OUTPUT_DIR / "nn_discriminant_model.pkl"
    if nn_model_path.exists():
        with open(nn_model_path, "rb") as f:
            nn_data = pickle.load(f)
        nn_scaler = nn_data["scaler"]
        nn_model = nn_data["model"]
        X_test_scaled = nn_scaler.transform(X_test)
        nn_scores_test = nn_model.predict_proba(X_test_scaled)[:, 1]
        fpr_nn, tpr_nn, _ = roc_curve(y_test, nn_scores_test, sample_weight=w_test)
        nn_auc_recomputed = roc_auc_score(y_test, nn_scores_test, sample_weight=w_test)
        ax.plot(fpr_nn, tpr_nn, color="red", linewidth=2,
                label=f"NN (AUC = {nn_auc_recomputed:.4f})")

    ax.plot([0, 1], [0, 1], "k--", linewidth=0.5)
    ax.set_xlabel("False Positive Rate (Background Efficiency)")
    ax.set_ylabel("True Positive Rate (Signal Efficiency)")
    ax.legend(fontsize="x-small", loc="lower right")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    mh.label.exp_label(exp="CMS", data=True, llabel="Open Simulation",
                        rlabel=r"$\sqrt{s} = 8$ TeV", loc=0, ax=ax)

    fig.savefig(FIG_DIR / "bdt_vs_nn_roc.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig.savefig(FIG_DIR / "bdt_vs_nn_roc.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info("Saved BDT vs NN ROC comparison plot")

    # --- BDT overtraining plot using mh.histplot ---
    fig, ax = plt.subplots(figsize=(10, 10))
    bins = np.linspace(0, 1, 41)

    # Train histograms
    h_sig_train = hist.Hist(hist.axis.Variable(bins, name="score", label="BDT Score"))
    h_sig_train.fill(sig_train_scores)
    h_bkg_train = hist.Hist(hist.axis.Variable(bins, name="score", label="BDT Score"))
    h_bkg_train.fill(bkg_train_scores)

    # Normalize to density
    sig_train_norm = h_sig_train.values() / (h_sig_train.sum() * (bins[1] - bins[0]))
    bkg_train_norm = h_bkg_train.values() / (h_bkg_train.sum() * (bins[1] - bins[0]))

    # Use hist objects for mh.histplot (filled)
    h_sig_train_density = hist.Hist(hist.axis.Variable(bins, name="score", label="BDT Score"))
    h_sig_train_density.view()[:] = sig_train_norm
    h_bkg_train_density = hist.Hist(hist.axis.Variable(bins, name="score", label="BDT Score"))
    h_bkg_train_density.view()[:] = bkg_train_norm

    mh.histplot(h_sig_train_density, ax=ax, histtype="fill", alpha=0.3, color="blue",
                label="Signal (train)")
    mh.histplot(h_bkg_train_density, ax=ax, histtype="fill", alpha=0.3, color="red",
                label="Background (train)")

    # Test as error bars
    h_sig_test_raw, _ = np.histogram(sig_test_scores, bins=bins)
    h_bkg_test_raw, _ = np.histogram(bkg_test_scores, bins=bins)
    bw = bins[1] - bins[0]
    sig_test_norm = h_sig_test_raw / (len(sig_test_scores) * bw) if len(sig_test_scores) > 0 else h_sig_test_raw
    bkg_test_norm = h_bkg_test_raw / (len(bkg_test_scores) * bw) if len(bkg_test_scores) > 0 else h_bkg_test_raw
    sig_test_err = np.sqrt(h_sig_test_raw) / (len(sig_test_scores) * bw) if len(sig_test_scores) > 0 else np.zeros_like(h_sig_test_raw)
    bkg_test_err = np.sqrt(h_bkg_test_raw) / (len(bkg_test_scores) * bw) if len(bkg_test_scores) > 0 else np.zeros_like(h_bkg_test_raw)

    h_sig_test_density = hist.Hist(hist.axis.Variable(bins, name="score", label="BDT Score"))
    h_sig_test_density.view()[:] = sig_test_norm
    h_bkg_test_density = hist.Hist(hist.axis.Variable(bins, name="score", label="BDT Score"))
    h_bkg_test_density.view()[:] = bkg_test_norm

    centers = (bins[:-1] + bins[1:]) / 2
    mh.histplot(h_sig_test_density, ax=ax, histtype="errorbar", color="blue",
                yerr=sig_test_err, label="Signal (test)")
    mh.histplot(h_bkg_test_density, ax=ax, histtype="errorbar", color="red",
                yerr=bkg_test_err, label="Background (test)")

    ax.set_xlabel("BDT Score")
    ax.set_ylabel("Normalized")
    ax.legend(fontsize="x-small", loc="upper center")
    mh.label.exp_label(exp="CMS", data=True, llabel="Open Simulation",
                        rlabel=r"$\sqrt{s} = 8$ TeV", loc=0, ax=ax)

    fig.savefig(FIG_DIR / "bdt_overtraining.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig.savefig(FIG_DIR / "bdt_overtraining.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info("Saved BDT overtraining check plot")

    log.info("\nBDT alternative training complete.")


if __name__ == "__main__":
    main()
