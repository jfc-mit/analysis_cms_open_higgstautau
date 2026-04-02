"""
Phase 2 Step 4: Tau ID working point comparison.

Compares VLoose, Loose, Medium tau isolation working points for data/MC
agreement in the Z peak region (60-120 GeV visible mass).
Determines the optimal WP for [D7].

Processes all samples at three WPs with a single pass through the data,
using chunk-based processing.
"""
import logging
import time
from pathlib import Path

from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

import uproot
import awkward as ak
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplhep as mh

mh.style.use("CMS")

DATA_DIR = Path("/eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool")
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"
FIG_DIR = OUTPUT_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

SAMPLES = {
    "GluGluToHToTauTau": {"desc": "ggH", "is_mc": True, "xsec": 21.39 * 0.06256, "color": "#d62728"},
    "VBF_HToTauTau": {"desc": "VBF", "is_mc": True, "xsec": 1.600 * 0.06256, "color": "#ff7f0e"},
    "DYJetsToLL": {"desc": "DY", "is_mc": True, "xsec": 3503.7, "color": "#1f77b4"},
    "TTbar": {"desc": r"$t\bar{t}$", "is_mc": True, "xsec": 252.9, "color": "#2ca02c"},
    "W1JetsToLNu": {"desc": "W+1j", "is_mc": True, "xsec": 6381.2, "color": "#9467bd"},
    "W2JetsToLNu": {"desc": "W+2j", "is_mc": True, "xsec": 2039.8, "color": "#8c564b"},
    "W3JetsToLNu": {"desc": "W+3j", "is_mc": True, "xsec": 612.5, "color": "#e377c2"},
    "Run2012B_TauPlusX": {"desc": "DataB", "is_mc": False, "xsec": None, "color": "black"},
    "Run2012C_TauPlusX": {"desc": "DataC", "is_mc": False, "xsec": None, "color": "black"},
}

LUMI = 11467.0
CHUNK_SIZE = 500_000

BRANCHES = [
    "HLT_IsoMu17_eta2p1_LooseIsoPFTau20",
    "nMuon", "Muon_pt", "Muon_eta", "Muon_phi", "Muon_mass", "Muon_charge",
    "Muon_pfRelIso04_all", "Muon_tightId", "Muon_dxy", "Muon_dz",
    "nTau", "Tau_pt", "Tau_eta", "Tau_phi", "Tau_mass", "Tau_charge",
    "Tau_idDecayMode", "Tau_relIso_all",
    "Tau_idIsoVLoose", "Tau_idIsoLoose", "Tau_idIsoMedium",
    "Tau_idAntiEleTight", "Tau_idAntiMuTight",
    "MET_pt", "MET_phi",
]

WPS = ["VLoose", "Loose", "Medium"]
Z_MASS_RANGE = (60, 120)  # GeV
MVIS_BINS = np.linspace(0, 200, 29)  # 28 bins from 0-200 GeV


def process_sample_3wp(sample_name, info):
    """Process a single sample collecting mvis histograms at all three WPs."""
    fpath = DATA_DIR / f"{sample_name}.root"
    tree = uproot.open(fpath)["Events"]
    n_total = tree.num_entries

    if info["is_mc"]:
        w_per_event = info["xsec"] * LUMI / n_total
    else:
        w_per_event = 1.0

    # Histograms per WP
    hists = {wp: np.zeros(len(MVIS_BINS) - 1) for wp in WPS}
    yields = {wp: 0.0 for wp in WPS}
    raw_counts = {wp: 0 for wp in WPS}

    t0 = time.time()
    for chunk in tree.iterate(BRANCHES, step_size=CHUNK_SIZE, library="ak"):
        # Trigger
        trig = chunk["HLT_IsoMu17_eta2p1_LooseIsoPFTau20"]
        ev = chunk[trig]

        # Good muons
        mu_mask = (
            (ev["Muon_pt"] > 20)
            & (np.abs(ev["Muon_eta"]) < 2.1)
            & (ev["Muon_tightId"])
            & (ev["Muon_pfRelIso04_all"] < 0.15)
            & (np.abs(ev["Muon_dxy"]) < 0.045)
            & (np.abs(ev["Muon_dz"]) < 0.2)
        )
        has_mu = ak.sum(mu_mask, axis=1) >= 1
        ev = ev[has_mu]
        mu_mask = mu_mask[has_mu]

        # Base tau selection (without iso WP)
        tau_base = (
            (ev["Tau_pt"] > 20)
            & (np.abs(ev["Tau_eta"]) < 2.3)
            & (ev["Tau_idDecayMode"])
            & (ev["Tau_idAntiEleTight"])
            & (ev["Tau_idAntiMuTight"])
            & (ev["Tau_charge"] != 0)
        )

        for wp in WPS:
            tau_mask = tau_base & ev[f"Tau_idIso{wp}"]
            has_tau = ak.sum(tau_mask, axis=1) >= 1

            ev_sel = ev[has_tau]
            mu_m = mu_mask[has_tau]
            tau_m = tau_mask[has_tau]

            if len(ev_sel) == 0:
                continue

            # Pick leading muon
            mu_idx = ak.argmax(ev_sel["Muon_pt"][mu_m], axis=1, keepdims=True)
            # Pick most isolated tau
            tau_iso_vals = ev_sel["Tau_relIso_all"][tau_m]
            # Replace NaN with large values for argmin
            tau_iso_safe = ak.fill_none(ak.nan_to_none(tau_iso_vals), 999.0)
            tau_idx = ak.argmin(tau_iso_safe, axis=1, keepdims=True)

            sel_mu_pt = ak.flatten(ev_sel["Muon_pt"][mu_m][mu_idx])
            sel_mu_eta = ak.flatten(ev_sel["Muon_eta"][mu_m][mu_idx])
            sel_mu_phi = ak.flatten(ev_sel["Muon_phi"][mu_m][mu_idx])
            sel_mu_mass = ak.flatten(ev_sel["Muon_mass"][mu_m][mu_idx])
            sel_mu_charge = ak.flatten(ev_sel["Muon_charge"][mu_m][mu_idx])
            sel_mu_iso = ak.flatten(ev_sel["Muon_pfRelIso04_all"][mu_m][mu_idx])

            sel_tau_pt = ak.flatten(ev_sel["Tau_pt"][tau_m][tau_idx])
            sel_tau_eta = ak.flatten(ev_sel["Tau_eta"][tau_m][tau_idx])
            sel_tau_phi = ak.flatten(ev_sel["Tau_phi"][tau_m][tau_idx])
            sel_tau_mass = ak.flatten(ev_sel["Tau_mass"][tau_m][tau_idx])
            sel_tau_charge = ak.flatten(ev_sel["Tau_charge"][tau_m][tau_idx])

            met_pt = ev_sel["MET_pt"]
            met_phi = ev_sel["MET_phi"]

            # OS
            os_mask = (sel_mu_charge * sel_tau_charge) < 0

            # DR > 0.5
            deta = sel_mu_eta - sel_tau_eta
            dphi = np.arctan2(np.sin(sel_mu_phi - sel_tau_phi),
                              np.cos(sel_mu_phi - sel_tau_phi))
            dr = np.sqrt(deta**2 + dphi**2)
            dr_mask = dr > 0.5

            # mT < 30
            mt = np.sqrt(2.0 * ak.to_numpy(sel_mu_pt) * ak.to_numpy(met_pt) *
                         (1.0 - np.cos(ak.to_numpy(sel_mu_phi) - ak.to_numpy(met_phi))))
            mt_mask = mt < 30.0

            # Tight muon iso
            iso_mask = ak.to_numpy(sel_mu_iso) < 0.1

            full_mask = ak.to_numpy(os_mask) & ak.to_numpy(dr_mask) & mt_mask & iso_mask

            # Compute mvis
            mu_pt_np = ak.to_numpy(sel_mu_pt)[full_mask]
            mu_eta_np = ak.to_numpy(sel_mu_eta)[full_mask]
            mu_phi_np = ak.to_numpy(sel_mu_phi)[full_mask]
            mu_mass_np = ak.to_numpy(sel_mu_mass)[full_mask]
            tau_pt_np = ak.to_numpy(sel_tau_pt)[full_mask]
            tau_eta_np = ak.to_numpy(sel_tau_eta)[full_mask]
            tau_phi_np = ak.to_numpy(sel_tau_phi)[full_mask]
            tau_mass_np = ak.to_numpy(sel_tau_mass)[full_mask]

            mu_px = mu_pt_np * np.cos(mu_phi_np)
            mu_py = mu_pt_np * np.sin(mu_phi_np)
            mu_pz = mu_pt_np * np.sinh(mu_eta_np)
            mu_e = np.sqrt(mu_px**2 + mu_py**2 + mu_pz**2 + mu_mass_np**2)

            tau_px = tau_pt_np * np.cos(tau_phi_np)
            tau_py = tau_pt_np * np.sin(tau_phi_np)
            tau_pz = tau_pt_np * np.sinh(tau_eta_np)
            tau_e = np.sqrt(tau_px**2 + tau_py**2 + tau_pz**2 + tau_mass_np**2)

            mvis = np.sqrt(np.maximum(
                (mu_e + tau_e)**2 - (mu_px + tau_px)**2 -
                (mu_py + tau_py)**2 - (mu_pz + tau_pz)**2, 0.0
            ))

            h, _ = np.histogram(mvis, bins=MVIS_BINS, weights=np.full(len(mvis), w_per_event))
            hists[wp] += h
            yields[wp] += len(mvis) * w_per_event
            raw_counts[wp] += len(mvis)

    elapsed = time.time() - t0
    log.info("  %s: %.1f s (%.0f kHz), yields: VLoose=%.0f Loose=%.0f Medium=%.0f",
             sample_name, elapsed, n_total / elapsed / 1000,
             yields["VLoose"], yields["Loose"], yields["Medium"])

    return hists, yields, raw_counts


def main():
    log.info("=" * 60)
    log.info("Phase 2 Step 4: Tau ID Working Point Study")
    log.info("=" * 60)

    # Accumulate per sample
    all_hists = {}
    all_yields = {}
    all_raw = {}

    for sample_name, info in SAMPLES.items():
        log.info("Processing %s...", sample_name)
        hists, yields, raw = process_sample_3wp(sample_name, info)
        all_hists[sample_name] = hists
        all_yields[sample_name] = yields
        all_raw[sample_name] = raw

    # Combine data
    data_hists = {wp: np.zeros(len(MVIS_BINS) - 1) for wp in WPS}
    for s in ["Run2012B_TauPlusX", "Run2012C_TauPlusX"]:
        for wp in WPS:
            data_hists[wp] += all_hists[s][wp]

    # Combine MC backgrounds
    bkg_order = ["DYJetsToLL", "W1JetsToLNu", "W2JetsToLNu", "W3JetsToLNu", "TTbar"]
    bkg_labels = ["DY", "W+1j", "W+2j", "W+3j", r"$t\bar{t}$"]
    bkg_colors = ["#1f77b4", "#9467bd", "#8c564b", "#e377c2", "#2ca02c"]

    bin_centers = 0.5 * (MVIS_BINS[:-1] + MVIS_BINS[1:])

    # Make comparison plots for each WP
    for wp in WPS:
        fig, (ax_main, ax_ratio) = plt.subplots(
            2, 1, figsize=(10, 10), gridspec_kw={"height_ratios": [3, 1]},
            sharex=True
        )
        fig.subplots_adjust(hspace=0)

        bkg_h = [all_hists[s][wp] for s in bkg_order]
        total_mc = sum(bkg_h)

        mh.histplot(
            bkg_h, bins=MVIS_BINS, stack=True, histtype="fill",
            label=bkg_labels, color=bkg_colors, ax=ax_main,
        )

        # Data
        h_data = data_hists[wp]
        data_err = np.sqrt(np.maximum(h_data, 0))
        ax_main.errorbar(bin_centers, h_data, yerr=data_err, fmt="ko",
                         markersize=4, label="Data", zorder=5)

        # Ratio
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = np.where(total_mc > 0, h_data / total_mc, 0)
            ratio_err = np.where(total_mc > 0, data_err / total_mc, 0)
        ax_ratio.errorbar(bin_centers, ratio, yerr=ratio_err, fmt="ko", markersize=4)
        ax_ratio.axhline(1.0, color="gray", linestyle="--", linewidth=1)
        ax_ratio.set_ylim(0.5, 1.5)

        # Chi2 in Z peak region
        z_mask = (MVIS_BINS[:-1] >= Z_MASS_RANGE[0]) & (MVIS_BINS[1:] <= Z_MASS_RANGE[1])
        with np.errstate(divide="ignore", invalid="ignore"):
            chi2_bins = np.where(
                (total_mc[z_mask] > 0) & (h_data[z_mask] > 0),
                (h_data[z_mask] - total_mc[z_mask])**2 / (data_err[z_mask]**2 + 0.01 * total_mc[z_mask]**2),
                0
            )
        chi2 = np.sum(chi2_bins)
        ndf = np.sum(z_mask) - 1
        chi2_ndf = chi2 / ndf if ndf > 0 else 0

        # Data/MC ratio in Z peak
        z_data = np.sum(h_data[z_mask])
        z_mc = np.sum(total_mc[z_mask])
        z_ratio = z_data / z_mc if z_mc > 0 else 0

        ax_main.set_ylabel("Events / 7.1 GeV")
        ax_ratio.set_xlabel(r"$m_\mathrm{vis}(\mu, \tau_h)$ [GeV]")
        ax_ratio.set_ylabel("Data/MC")
        ax_main.legend(fontsize="x-small", ncol=2)
        ax_main.set_xlim(0, 200)

        mh.label.exp_label(
            exp="CMS", data=True,
            llabel="Open Data",
            rlabel=r"$\sqrt{s} = 8$ TeV, 11.5 fb$^{-1}$",
            loc=0, ax=ax_main,
        )

        # Annotate with chi2 info
        ax_main.text(0.95, 0.70,
                     f"Tau Iso WP: {wp}\n"
                     f"Z peak (60-120 GeV):\n"
                     f"  Data/MC = {z_ratio:.3f}\n"
                     f"  $\\chi^2$/ndf = {chi2:.1f}/{ndf} = {chi2_ndf:.2f}",
                     transform=ax_main.transAxes, ha="right", va="top",
                     fontsize="x-small",
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

        for ext in ["pdf", "png"]:
            fig.savefig(FIG_DIR / f"tau_id_wp_{wp}.{ext}",
                        bbox_inches="tight", dpi=200, transparent=True)
        plt.close(fig)
        log.info("Saved tau_id_wp_%s.pdf/png", wp)

    # Summary table
    log.info("\n" + "=" * 60)
    log.info("TAU ID WP COMPARISON SUMMARY")
    log.info("=" * 60)
    log.info("%-10s %10s %10s %10s %10s", "WP", "Data", "MC Total", "Data/MC", "chi2/ndf (Z peak)")

    for wp in WPS:
        z_mask = (MVIS_BINS[:-1] >= Z_MASS_RANGE[0]) & (MVIS_BINS[1:] <= Z_MASS_RANGE[1])
        h_data = data_hists[wp]
        total_mc = sum(all_hists[s][wp] for s in bkg_order)

        z_data = np.sum(h_data[z_mask])
        z_mc = np.sum(total_mc[z_mask])
        z_ratio = z_data / z_mc if z_mc > 0 else 0

        data_err_z = np.sqrt(np.maximum(h_data[z_mask], 0))
        with np.errstate(divide="ignore", invalid="ignore"):
            chi2_bins = np.where(
                (total_mc[z_mask] > 0) & (h_data[z_mask] > 0),
                (h_data[z_mask] - total_mc[z_mask])**2 / (data_err_z**2 + 0.01 * total_mc[z_mask]**2),
                0
            )
        chi2 = np.sum(chi2_bins)
        ndf = np.sum(z_mask) - 1

        total_data = np.sum(h_data)
        total_mc_all = np.sum(total_mc)

        log.info("%-10s %10.0f %10.0f %10.3f %10.2f/%d = %.2f",
                 wp, total_data, total_mc_all, z_ratio, chi2, ndf, chi2 / ndf if ndf > 0 else 0)

    # Per-sample yields
    log.info("\nYields per sample (Z peak 60-120 GeV, weighted):")
    log.info("%-25s %10s %10s %10s", "Sample", "VLoose", "Loose", "Medium")
    for sample_name in SAMPLES:
        log.info("%-25s %10.1f %10.1f %10.1f",
                 sample_name,
                 all_yields[sample_name]["VLoose"],
                 all_yields[sample_name]["Loose"],
                 all_yields[sample_name]["Medium"])


if __name__ == "__main__":
    main()
