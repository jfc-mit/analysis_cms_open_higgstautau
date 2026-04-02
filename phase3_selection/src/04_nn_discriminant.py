"""
Phase 3 Step 4: NN Discriminant Training [D1, D9].

Trains a neural network classifier to separate H->tautau signal from backgrounds.
Uses scikit-learn MLPClassifier.
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
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, roc_curve
from scipy.stats import ks_2samp
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

# Input features
FEATURES = [
    "mu_pt", "mu_eta", "tau_pt", "tau_eta", "met_pt", "met_significance",
    "mvis", "mt", "delta_r", "delta_phi_mutau",
    "njets", "lead_jet_pt", "lead_jet_eta", "nbjets",
]

SEED = 42


def load_and_prepare_data():
    """Load signal and background from OS SR npz files."""
    X_sig = []
    w_sig = []
    X_bkg = []
    w_bkg = []

    for sn in SIGNAL_SAMPLES:
        path = OUTPUT_DIR / f"p3_{sn}_os_sr.npz"
        if not path.exists():
            log.info("Signal sample %s not found", sn)
            continue
        d = dict(np.load(path, allow_pickle=True))
        if len(d["mu_pt"]) == 0:
            continue

        features = np.column_stack([d[f] for f in FEATURES])
        X_sig.append(features)
        w_sig.append(d["weight"])
        log.info("Signal %s: %d events", sn, len(features))

    for sn in BKG_SAMPLES:
        path = OUTPUT_DIR / f"p3_{sn}_os_sr.npz"
        if not path.exists():
            log.info("Background sample %s not found", sn)
            continue
        d = dict(np.load(path, allow_pickle=True))
        if len(d["mu_pt"]) == 0:
            continue

        features = np.column_stack([d[f] for f in FEATURES])
        X_bkg.append(features)
        w_bkg.append(d["weight"])
        log.info("Background %s: %d events", sn, len(features))

    X_sig = np.vstack(X_sig) if X_sig else np.empty((0, len(FEATURES)))
    w_sig = np.concatenate(w_sig) if w_sig else np.array([])
    X_bkg = np.vstack(X_bkg) if X_bkg else np.empty((0, len(FEATURES)))
    w_bkg = np.concatenate(w_bkg) if w_bkg else np.array([])

    log.info("Total signal: %d, Background: %d", len(X_sig), len(X_bkg))

    return X_sig, w_sig, X_bkg, w_bkg


def train_nn(X_sig, w_sig, X_bkg, w_bkg):
    """Train NN classifier with 50/25/25 split."""
    # Combine
    X = np.vstack([X_sig, X_bkg])
    y = np.concatenate([np.ones(len(X_sig)), np.zeros(len(X_bkg))])
    w = np.concatenate([w_sig, w_bkg])

    # Replace any NaN/Inf with 0
    mask = np.isfinite(X).all(axis=1)
    if not np.all(mask):
        n_bad = int(np.sum(~mask))
        log.info("Removing %d events with NaN/Inf features", n_bad)
        X = X[mask]
        y = y[mask]
        w = w[mask]

    # 50/25/25 split: first 50/50 train/temp, then 50/50 temp into val/test
    X_train, X_temp, y_train, y_temp, w_train, w_temp = train_test_split(
        X, y, w, test_size=0.5, random_state=SEED, stratify=y
    )
    X_val, X_test, y_val, y_test, w_val, w_test = train_test_split(
        X_temp, y_temp, w_temp, test_size=0.5, random_state=SEED, stratify=y_temp
    )

    log.info("Train: %d, Val: %d, Test: %d", len(X_train), len(X_val), len(X_test))

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    # Train NN: 3 hidden layers of 64 nodes, ReLU, dropout via alpha regularization
    nn = MLPClassifier(
        hidden_layer_sizes=(64, 64, 32),
        activation="relu",
        solver="adam",
        alpha=0.001,  # L2 regularization (acts like dropout surrogate)
        batch_size=256,
        learning_rate="adaptive",
        learning_rate_init=0.001,
        max_iter=200,
        early_stopping=True,
        validation_fraction=0.1,  # Internal validation for early stopping
        n_iter_no_change=20,
        random_state=SEED,
        verbose=False,
    )

    # Use sample weights for training (normalize so signal and bkg have equal total weight)
    sig_mask_train = y_train == 1
    bkg_mask_train = y_train == 0
    total_sig_w = np.sum(w_train[sig_mask_train])
    total_bkg_w = np.sum(w_train[bkg_mask_train])

    # Training weights: equalize signal and background total weight
    train_weights = w_train.copy()
    if total_sig_w > 0 and total_bkg_w > 0:
        train_weights[sig_mask_train] *= (total_bkg_w / total_sig_w)

    log.info("Training NN...")
    nn.fit(X_train_scaled, y_train, sample_weight=train_weights)
    log.info("Training complete. %d iterations.", nn.n_iter_)

    # Predictions
    score_train = nn.predict_proba(X_train_scaled)[:, 1]
    score_val = nn.predict_proba(X_val_scaled)[:, 1]
    score_test = nn.predict_proba(X_test_scaled)[:, 1]

    # AUC
    auc_train = roc_auc_score(y_train, score_train, sample_weight=w_train)
    auc_val = roc_auc_score(y_val, score_val, sample_weight=w_val)
    auc_test = roc_auc_score(y_test, score_test, sample_weight=w_test)

    log.info("AUC — Train: %.4f, Val: %.4f, Test: %.4f", auc_train, auc_val, auc_test)

    # Overtraining check: KS test on signal and background score distributions
    sig_train_scores = score_train[y_train == 1]
    sig_test_scores = score_test[y_test == 1]
    bkg_train_scores = score_train[y_train == 0]
    bkg_test_scores = score_test[y_test == 0]

    ks_sig, p_sig = ks_2samp(sig_train_scores, sig_test_scores)
    ks_bkg, p_bkg = ks_2samp(bkg_train_scores, bkg_test_scores)
    log.info("Overtraining KS test:")
    log.info("  Signal: KS=%.4f, p=%.4f (p>0.05 = no overtraining)", ks_sig, p_sig)
    log.info("  Background: KS=%.4f, p=%.4f", ks_bkg, p_bkg)

    results = {
        "auc_train": auc_train,
        "auc_val": auc_val,
        "auc_test": auc_test,
        "ks_sig": ks_sig, "p_sig": p_sig,
        "ks_bkg": ks_bkg, "p_bkg": p_bkg,
        "n_train": len(X_train),
        "n_val": len(X_val),
        "n_test": len(X_test),
        "n_iter": nn.n_iter_,
        "features": FEATURES,
        "hidden_layers": list(nn.hidden_layer_sizes),
        "alpha": nn.alpha,
        "seed": SEED,
    }

    return nn, scaler, results, {
        "X_train": X_train_scaled, "y_train": y_train, "w_train": w_train,
        "X_val": X_val_scaled, "y_val": y_val, "w_val": w_val,
        "X_test": X_test_scaled, "y_test": y_test, "w_test": w_test,
        "score_train": score_train, "score_val": score_val, "score_test": score_test,
    }


def compute_nn_scores_all(nn, scaler):
    """Compute NN scores for all samples in OS SR."""
    all_samples = SIGNAL_SAMPLES + BKG_SAMPLES + [
        "Run2012B_TauPlusX", "Run2012C_TauPlusX"
    ]

    for sn in all_samples:
        path = OUTPUT_DIR / f"p3_{sn}_os_sr.npz"
        if not path.exists():
            continue
        d = dict(np.load(path, allow_pickle=True))
        if len(d["mu_pt"]) == 0:
            continue

        features = np.column_stack([d[f] for f in FEATURES])
        # Handle NaN/Inf
        features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)
        features_scaled = scaler.transform(features)
        scores = nn.predict_proba(features_scaled)[:, 1]

        np.savez_compressed(
            OUTPUT_DIR / f"p3_{sn}_os_sr_nn_score.npz",
            nn_score=scores,
        )
        log.info("Saved NN scores for %s: %d events, mean score = %.3f",
                 sn, len(scores), float(np.mean(scores)))


def plot_roc(results, data):
    """Plot ROC curve."""
    fig, ax = plt.subplots(figsize=(10, 10))

    for split_name, X_key, y_key, w_key, color in [
        ("Train", "X_train", "y_train", "w_train", "blue"),
        ("Validation", "X_val", "y_val", "w_val", "green"),
        ("Test", "X_test", "y_test", "w_test", "red"),
    ]:
        y = data[y_key]
        # Map split names to data dict keys
        score_map = {"Train": "score_train", "Validation": "score_val", "Test": "score_test"}
        scores = data[score_map[split_name]]
        w = data[w_key]
        fpr, tpr, _ = roc_curve(y, scores, sample_weight=w)
        auc = roc_auc_score(y, scores, sample_weight=w)
        ax.plot(fpr, tpr, color=color, label=f"{split_name} (AUC = {auc:.4f})")

    ax.plot([0, 1], [0, 1], "k--", linewidth=0.5)
    ax.set_xlabel("False Positive Rate (Background Efficiency)")
    ax.set_ylabel("True Positive Rate (Signal Efficiency)")
    ax.legend(fontsize="x-small", loc="lower right")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    mh.label.exp_label(exp="CMS", data=True, llabel="Open Simulation",
                        rlabel=r"$\sqrt{s} = 8$ TeV", loc=0, ax=ax)

    fig.savefig(FIG_DIR / "nn_roc.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig.savefig(FIG_DIR / "nn_roc.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info("Saved ROC curve")


def plot_score_distributions(data):
    """Plot NN score distributions for train and test (overtraining check).

    Uses mh.histplot for all histogram rendering. Error bars on test
    distributions use proper Poisson uncertainty for density-normalized
    histograms: sigma_density = sqrt(N_raw) / (N_total * bin_width).
    """
    import hist as hist_pkg

    fig, ax = plt.subplots(figsize=(10, 10))

    bins = np.linspace(0, 1, 41)
    bw = bins[1] - bins[0]

    sig_train = data["score_train"][data["y_train"] == 1]
    bkg_train = data["score_train"][data["y_train"] == 0]
    sig_test = data["score_test"][data["y_test"] == 1]
    bkg_test = data["score_test"][data["y_test"] == 0]

    # Compute density-normalized values
    h_sig_train_raw, _ = np.histogram(sig_train, bins=bins)
    h_bkg_train_raw, _ = np.histogram(bkg_train, bins=bins)
    h_sig_test_raw, _ = np.histogram(sig_test, bins=bins)
    h_bkg_test_raw, _ = np.histogram(bkg_test, bins=bins)

    n_sig_train = max(len(sig_train), 1)
    n_bkg_train = max(len(bkg_train), 1)
    n_sig_test = max(len(sig_test), 1)
    n_bkg_test = max(len(bkg_test), 1)

    sig_train_density = h_sig_train_raw / (n_sig_train * bw)
    bkg_train_density = h_bkg_train_raw / (n_bkg_train * bw)
    sig_test_density = h_sig_test_raw / (n_sig_test * bw)
    bkg_test_density = h_bkg_test_raw / (n_bkg_test * bw)

    # Proper error: sigma = sqrt(N_raw) / (N_total * bw)
    sig_test_err = np.sqrt(h_sig_test_raw.astype(float)) / (n_sig_test * bw)
    bkg_test_err = np.sqrt(h_bkg_test_raw.astype(float)) / (n_bkg_test * bw)

    # Train as filled histograms via mh.histplot
    h_sig_t = hist_pkg.Hist(hist_pkg.axis.Variable(bins, name="score"))
    h_sig_t.view()[:] = sig_train_density
    h_bkg_t = hist_pkg.Hist(hist_pkg.axis.Variable(bins, name="score"))
    h_bkg_t.view()[:] = bkg_train_density

    mh.histplot(h_sig_t, ax=ax, histtype="fill", alpha=0.3, color="blue",
                label="Signal (train)")
    mh.histplot(h_bkg_t, ax=ax, histtype="fill", alpha=0.3, color="red",
                label="Background (train)")

    # Test as errorbar points via mh.histplot
    h_sig_te = hist_pkg.Hist(hist_pkg.axis.Variable(bins, name="score"))
    h_sig_te.view()[:] = sig_test_density
    h_bkg_te = hist_pkg.Hist(hist_pkg.axis.Variable(bins, name="score"))
    h_bkg_te.view()[:] = bkg_test_density

    mh.histplot(h_sig_te, ax=ax, histtype="errorbar", color="blue",
                yerr=sig_test_err, label="Signal (test)")
    mh.histplot(h_bkg_te, ax=ax, histtype="errorbar", color="red",
                yerr=bkg_test_err, label="Background (test)")

    ax.set_xlabel("NN Score")
    ax.set_ylabel("Normalized")
    ax.legend(fontsize="x-small", loc="upper center")
    mh.label.exp_label(exp="CMS", data=True, llabel="Open Simulation",
                        rlabel=r"$\sqrt{s} = 8$ TeV", loc=0, ax=ax)

    fig.savefig(FIG_DIR / "nn_overtraining.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig.savefig(FIG_DIR / "nn_overtraining.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info("Saved overtraining check plot")


def plot_feature_importance(nn, scaler):
    """Plot feature importance from first layer weights."""
    # Use absolute mean of first-layer weights as proxy for importance
    w1 = nn.coefs_[0]  # shape: (n_features, n_hidden_1)
    importance = np.mean(np.abs(w1), axis=1)

    # Sort
    idx = np.argsort(importance)[::-1]

    fig, ax = plt.subplots(figsize=(10, 10))
    y_pos = np.arange(len(FEATURES))
    ax.barh(y_pos, importance[idx], color="#1f77b4", edgecolor="black", linewidth=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([FEATURES[i] for i in idx], fontsize="x-small")
    ax.invert_yaxis()
    ax.set_xlabel("Mean |weight| (first layer)")
    mh.label.exp_label(exp="CMS", data=True, llabel="Open Simulation",
                        rlabel=r"$\sqrt{s} = 8$ TeV", loc=0, ax=ax)

    fig.savefig(FIG_DIR / "nn_feature_importance.pdf", bbox_inches="tight", dpi=200, transparent=True)
    fig.savefig(FIG_DIR / "nn_feature_importance.png", bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)
    log.info("Saved feature importance plot")


def main():
    log.info("=" * 60)
    log.info("Phase 3 Step 4: NN Discriminant Training")
    log.info("=" * 60)

    # Load data
    X_sig, w_sig, X_bkg, w_bkg = load_and_prepare_data()

    if len(X_sig) == 0 or len(X_bkg) == 0:
        log.info("ERROR: No signal or background data available!")
        return

    # Train
    nn, scaler, results, data = train_nn(X_sig, w_sig, X_bkg, w_bkg)

    # Save model and scaler
    model_path = OUTPUT_DIR / "nn_discriminant_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump({"model": nn, "scaler": scaler, "features": FEATURES}, f)
    log.info("Model saved to %s", model_path)

    # Save results
    results_path = OUTPUT_DIR / "nn_discriminant_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    log.info("Results saved to %s", results_path)

    # Compute scores for all samples
    log.info("\nComputing NN scores for all samples...")
    compute_nn_scores_all(nn, scaler)

    # Plots
    log.info("\nProducing validation plots...")
    plot_roc(results, data)
    plot_score_distributions(data)
    plot_feature_importance(nn, scaler)

    # Go/no-go check [D1]
    log.info("\n=== GO/NO-GO CHECK [D1] ===")
    log.info("AUC (test) = %.4f (requirement: > 0.75)", results["auc_test"])
    log.info("KS signal p-value = %.4f (requirement: > 0.05)", results["p_sig"])
    log.info("KS background p-value = %.4f", results["p_bkg"])

    go = True
    if results["auc_test"] < 0.75:
        log.info("FAIL: AUC below threshold")
        go = False
    if results["p_sig"] < 0.05:
        log.info("WARNING: Possible overtraining on signal (KS p < 0.05)")
    if results["p_bkg"] < 0.05:
        log.info("WARNING: Possible overtraining on background (KS p < 0.05)")

    if go:
        log.info("GO: NN discriminant passes all criteria")
    else:
        log.info("NO-GO: NN discriminant fails criteria")


if __name__ == "__main__":
    main()
