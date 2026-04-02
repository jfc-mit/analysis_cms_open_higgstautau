"""
Phase 2 Step 7: VBF category optimization.

Scans mjj and Delta_eta thresholds to optimize S/sqrt(B).
Evaluates Zeppenfeld centrality requirement [P2-3, P2-4].
"""
import logging
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

MC_SAMPLES = {
    "GluGluToHToTauTau": {"label": "ggH", "is_signal": True},
    "VBF_HToTauTau": {"label": "VBF", "is_signal": True},
    "DYJetsToLL": {"label": "DY", "is_signal": False},
    "TTbar": {"label": r"$t\bar{t}$", "is_signal": False},
    "W1JetsToLNu": {"label": "W+1j", "is_signal": False},
    "W2JetsToLNu": {"label": "W+2j", "is_signal": False},
    "W3JetsToLNu": {"label": "W+3j", "is_signal": False},
}

DATA_SAMPLES = ["Run2012B_TauPlusX", "Run2012C_TauPlusX"]

# Need to reprocess with full jet information for VBF study.
# For now, use the saved npz which has njets, lead_jet_pt, lead_jet_eta.
# We need to do a separate pass for the dijet quantities.

import uproot
import awkward as ak

DATA_DIR = Path("/eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool")
LUMI = 11467.0

XSECS = {
    "GluGluToHToTauTau": 21.39 * 0.06256,
    "VBF_HToTauTau": 1.600 * 0.06256,
    "DYJetsToLL": 3503.7,
    "TTbar": 252.9,
    "W1JetsToLNu": 6381.2,
    "W2JetsToLNu": 2039.8,
    "W3JetsToLNu": 612.5,
}


def load_sample(sample_name):
    """Load selected events from npz file."""
    npz_path = OUTPUT_DIR / f"selected_{sample_name}_loose.npz"
    if not npz_path.exists():
        return None
    return dict(np.load(npz_path))


def get_vbf_jets_from_file(sample_name, selected_events_npz):
    """
    For VBF study, we need dijet variables. Since we only stored njets and
    leading jet in the preselection, we'll use the saved info to estimate.

    For proper optimization, we need a dedicated pass. Here we use a simplified
    approach: events with njets >= 2 get approximate VBF variables from the
    preselection output. For a proper study, we'd reprocess.

    For now, return events with njets >= 2 and their weights.
    """
    d = selected_events_npz
    if d is None or len(d["mu_pt"]) == 0:
        return None

    # We only have njets, nbjets, lead_jet_pt, lead_jet_eta
    # We need a dedicated reprocessing for mjj and delta_eta_jj
    # For now, just count yields for njets >= 2
    mask_2j = d["njets"] >= 2
    return {
        "mask_2j": mask_2j,
        "n_2j": int(np.sum(mask_2j)),
        "weight_2j": np.sum(d["weight"][mask_2j]),
        "weight_total": np.sum(d["weight"]),
        "n_total": len(d["weight"]),
        "lead_jet_pt": d["lead_jet_pt"],
        "lead_jet_eta": d["lead_jet_eta"],
        "njets": d["njets"],
        "nbjets": d["nbjets"],
        "mvis": d["mvis"],
        "weight": d["weight"],
    }


def main():
    log.info("=" * 60)
    log.info("Phase 2 Step 7: VBF Optimization and Jet Studies")
    log.info("=" * 60)

    # Load all samples
    all_data = {}
    for sample_name in list(MC_SAMPLES.keys()) + DATA_SAMPLES:
        d = load_sample(sample_name)
        if d is not None:
            vbf_info = get_vbf_jets_from_file(sample_name, d)
            all_data[sample_name] = vbf_info

    # Jet multiplicity distribution
    log.info("\n--- Jet Multiplicity (weighted yields) ---")
    log.info("%-25s %10s %10s %10s %10s %10s", "Sample", "0-jet", "1-jet", ">=2-jet", "Total", ">=2/Total")

    for sample_name in list(MC_SAMPLES.keys()) + DATA_SAMPLES:
        if sample_name not in all_data or all_data[sample_name] is None:
            continue
        d = all_data[sample_name]
        nj = d["njets"]
        w = d["weight"]
        n0 = np.sum(w[nj == 0])
        n1 = np.sum(w[nj == 1])
        n2p = np.sum(w[nj >= 2])
        ntot = np.sum(w)
        frac = n2p / ntot if ntot > 0 else 0
        log.info("%-25s %10.1f %10.1f %10.1f %10.1f %10.3f",
                 sample_name, n0, n1, n2p, ntot, frac)

    # VBF-like yields (njets >= 2)
    log.info("\n--- VBF-like yields (njets >= 2) ---")
    sig_2j = 0
    bkg_2j = 0
    for sample_name, info in MC_SAMPLES.items():
        if sample_name in all_data and all_data[sample_name] is not None:
            w2j = all_data[sample_name]["weight_2j"]
            if info["is_signal"]:
                sig_2j += w2j
            else:
                bkg_2j += w2j
            log.info("  %-25s: %.1f events (2j)", sample_name, w2j)

    if bkg_2j > 0:
        log.info("\n  S (signal, 2j):    %.2f", sig_2j)
        log.info("  B (background, 2j): %.2f", bkg_2j)
        log.info("  S/sqrt(B) (2j):    %.3f", sig_2j / np.sqrt(bkg_2j))

    # We need dijet mass and delta_eta for proper VBF optimization.
    # Do a dedicated reprocessing for events with >= 2 jets.
    log.info("\n--- Dedicated VBF dijet study (requires full jet info) ---")
    log.info("Running targeted pass for dijet variables on signal and DY...")

    # Quick targeted pass to get dijet variables
    vbf_results = {}
    BRANCHES = [
        "HLT_IsoMu17_eta2p1_LooseIsoPFTau20",
        "nMuon", "Muon_pt", "Muon_eta", "Muon_phi", "Muon_mass", "Muon_charge",
        "Muon_pfRelIso04_all", "Muon_tightId", "Muon_dxy", "Muon_dz",
        "nTau", "Tau_pt", "Tau_eta", "Tau_phi", "Tau_mass", "Tau_charge",
        "Tau_idDecayMode", "Tau_relIso_all",
        "Tau_idIsoLoose", "Tau_idAntiEleTight", "Tau_idAntiMuTight",
        "nJet", "Jet_pt", "Jet_eta", "Jet_phi", "Jet_mass", "Jet_puId",
        "MET_pt", "MET_phi",
    ]

    # Only process key samples for VBF study
    vbf_study_samples = {
        "VBF_HToTauTau": XSECS["VBF_HToTauTau"],
        "GluGluToHToTauTau": XSECS["GluGluToHToTauTau"],
        "DYJetsToLL": XSECS["DYJetsToLL"],
        "TTbar": XSECS["TTbar"],
    }

    for sample_name, xsec in vbf_study_samples.items():
        fpath = DATA_DIR / f"{sample_name}.root"
        tree = uproot.open(fpath)["Events"]
        n_total = tree.num_entries
        w_per = xsec * LUMI / n_total

        mjj_list = []
        deta_list = []
        zep_mu_list = []
        zep_tau_list = []
        mvis_list = []
        weight_list = []

        for chunk in tree.iterate(BRANCHES, step_size=500_000, library="ak"):
            # Apply full preselection inline
            trig = chunk["HLT_IsoMu17_eta2p1_LooseIsoPFTau20"]
            ev = chunk[trig]

            mu_mask = (
                (ev["Muon_pt"] > 20) & (np.abs(ev["Muon_eta"]) < 2.1) &
                ev["Muon_tightId"] & (ev["Muon_pfRelIso04_all"] < 0.15) &
                (np.abs(ev["Muon_dxy"]) < 0.045) & (np.abs(ev["Muon_dz"]) < 0.2)
            )
            has_mu = ak.sum(mu_mask, axis=1) >= 1
            ev = ev[has_mu]
            mu_mask = mu_mask[has_mu]

            tau_mask = (
                (ev["Tau_pt"] > 20) & (np.abs(ev["Tau_eta"]) < 2.3) &
                ev["Tau_idDecayMode"] & ev["Tau_idAntiEleTight"] &
                ev["Tau_idAntiMuTight"] & ev["Tau_idIsoLoose"] &
                (ev["Tau_charge"] != 0)
            )
            has_tau = ak.sum(tau_mask, axis=1) >= 1
            ev = ev[has_tau]
            mu_mask = mu_mask[has_tau]
            tau_mask = tau_mask[has_tau]

            if len(ev) == 0:
                continue

            # Select leading muon and best tau
            mu_idx = ak.argmax(ev["Muon_pt"][mu_mask], axis=1, keepdims=True)
            tau_iso = ev["Tau_relIso_all"][tau_mask]
            tau_iso_safe = ak.fill_none(ak.nan_to_none(tau_iso), 999.0)
            tau_idx = ak.argmin(tau_iso_safe, axis=1, keepdims=True)

            sel_mu_eta = ak.to_numpy(ak.flatten(ev["Muon_eta"][mu_mask][mu_idx]))
            sel_mu_phi = ak.to_numpy(ak.flatten(ev["Muon_phi"][mu_mask][mu_idx]))
            sel_mu_pt = ak.to_numpy(ak.flatten(ev["Muon_pt"][mu_mask][mu_idx]))
            sel_mu_mass = ak.to_numpy(ak.flatten(ev["Muon_mass"][mu_mask][mu_idx]))
            sel_mu_charge = ak.to_numpy(ak.flatten(ev["Muon_charge"][mu_mask][mu_idx]))
            sel_mu_iso = ak.to_numpy(ak.flatten(ev["Muon_pfRelIso04_all"][mu_mask][mu_idx]))

            sel_tau_eta = ak.to_numpy(ak.flatten(ev["Tau_eta"][tau_mask][tau_idx]))
            sel_tau_phi = ak.to_numpy(ak.flatten(ev["Tau_phi"][tau_mask][tau_idx]))
            sel_tau_pt = ak.to_numpy(ak.flatten(ev["Tau_pt"][tau_mask][tau_idx]))
            sel_tau_mass = ak.to_numpy(ak.flatten(ev["Tau_mass"][tau_mask][tau_idx]))
            sel_tau_charge = ak.to_numpy(ak.flatten(ev["Tau_charge"][tau_mask][tau_idx]))

            met_pt_arr = ak.to_numpy(ev["MET_pt"])
            met_phi_arr = ak.to_numpy(ev["MET_phi"])

            # OS, DR, mT, iso cuts
            os_mask = sel_mu_charge * sel_tau_charge < 0
            deta_pair = sel_mu_eta - sel_tau_eta
            dphi_pair = np.arctan2(np.sin(sel_mu_phi - sel_tau_phi),
                                   np.cos(sel_mu_phi - sel_tau_phi))
            dr = np.sqrt(deta_pair**2 + dphi_pair**2)
            dr_mask = dr > 0.5
            mt = np.sqrt(2 * sel_mu_pt * met_pt_arr * (1 - np.cos(sel_mu_phi - met_phi_arr)))
            mt_mask = mt < 30
            iso_mask = sel_mu_iso < 0.1
            full = os_mask & dr_mask & mt_mask & iso_mask

            # Now jets for VBF
            jet_pt = ev["Jet_pt"]
            jet_eta = ev["Jet_eta"]
            jet_phi = ev["Jet_phi"]
            jet_mass = ev["Jet_mass"]
            jet_puid = ev["Jet_puId"]

            good_jet = (jet_pt > 30) & (np.abs(jet_eta) < 4.7) & jet_puid
            njets = ak.to_numpy(ak.sum(good_jet, axis=1))

            # >= 2 jets AND preselection
            vbf_mask = full & (njets >= 2)
            idx_vbf = np.where(vbf_mask)[0]

            if len(idx_vbf) == 0:
                continue

            for i in idx_vbf:
                gj_pt = ak.to_numpy(jet_pt[i][good_jet[i]])
                gj_eta = ak.to_numpy(jet_eta[i][good_jet[i]])
                gj_phi = ak.to_numpy(jet_phi[i][good_jet[i]])
                gj_mass = ak.to_numpy(jet_mass[i][good_jet[i]])

                if len(gj_pt) < 2:
                    continue

                # Leading and subleading by pT
                sort_idx = np.argsort(-gj_pt)
                j1_idx, j2_idx = sort_idx[0], sort_idx[1]

                j1_pt, j1_eta, j1_phi, j1_mass = gj_pt[j1_idx], gj_eta[j1_idx], gj_phi[j1_idx], gj_mass[j1_idx]
                j2_pt, j2_eta, j2_phi, j2_mass = gj_pt[j2_idx], gj_eta[j2_idx], gj_phi[j2_idx], gj_mass[j2_idx]

                # Dijet mass
                j1_px = j1_pt * np.cos(j1_phi)
                j1_py = j1_pt * np.sin(j1_phi)
                j1_pz = j1_pt * np.sinh(j1_eta)
                j1_e = np.sqrt(j1_px**2 + j1_py**2 + j1_pz**2 + j1_mass**2)

                j2_px = j2_pt * np.cos(j2_phi)
                j2_py = j2_pt * np.sin(j2_phi)
                j2_pz = j2_pt * np.sinh(j2_eta)
                j2_e = np.sqrt(j2_px**2 + j2_py**2 + j2_pz**2 + j2_mass**2)

                mjj = np.sqrt(max((j1_e + j2_e)**2 - (j1_px + j2_px)**2 -
                                  (j1_py + j2_py)**2 - (j1_pz + j2_pz)**2, 0))
                deta_jj = abs(j1_eta - j2_eta)

                # Zeppenfeld centrality
                eta_avg = (j1_eta + j2_eta) / 2
                zep_mu = abs(sel_mu_eta[i] - eta_avg) / deta_jj if deta_jj > 0 else 999
                zep_tau = abs(sel_tau_eta[i] - eta_avg) / deta_jj if deta_jj > 0 else 999

                # mvis
                mu_px = sel_mu_pt[i] * np.cos(sel_mu_phi[i])
                mu_py = sel_mu_pt[i] * np.sin(sel_mu_phi[i])
                mu_pz = sel_mu_pt[i] * np.sinh(sel_mu_eta[i])
                mu_e = np.sqrt(mu_px**2 + mu_py**2 + mu_pz**2 + sel_mu_mass[i]**2)
                tau_px_v = sel_tau_pt[i] * np.cos(sel_tau_phi[i])
                tau_py_v = sel_tau_pt[i] * np.sin(sel_tau_phi[i])
                tau_pz_v = sel_tau_pt[i] * np.sinh(sel_tau_eta[i])
                tau_e = np.sqrt(tau_px_v**2 + tau_py_v**2 + tau_pz_v**2 + sel_tau_mass[i]**2)
                mvis_val = np.sqrt(max((mu_e + tau_e)**2 - (mu_px + tau_px_v)**2 -
                                       (mu_py + tau_py_v)**2 - (mu_pz + tau_pz_v)**2, 0))

                mjj_list.append(mjj)
                deta_list.append(deta_jj)
                zep_mu_list.append(zep_mu)
                zep_tau_list.append(zep_tau)
                mvis_list.append(mvis_val)
                weight_list.append(w_per)

        vbf_results[sample_name] = {
            "mjj": np.array(mjj_list),
            "deta_jj": np.array(deta_list),
            "zep_mu": np.array(zep_mu_list),
            "zep_tau": np.array(zep_tau_list),
            "mvis": np.array(mvis_list),
            "weight": np.array(weight_list),
        }
        log.info("  %s: %d events with >= 2 jets after preselection",
                 sample_name, len(mjj_list))

    # VBF optimization: scan mjj and deta thresholds
    log.info("\n--- VBF Threshold Scan ---")
    log.info("%-10s %-10s %10s %10s %10s %10s",
             "mjj_cut", "deta_cut", "S(VBF)", "S(ggH)", "B", "S/sqrt(B)")

    best_ssqrtb = 0
    best_cuts = (0, 0)

    for mjj_cut in [200, 300, 400, 500, 700]:
        for deta_cut in [2.0, 2.5, 3.0, 3.5, 4.0]:
            sig_vbf = 0
            sig_ggh = 0
            bkg = 0
            for sample_name, r in vbf_results.items():
                mask = (r["mjj"] > mjj_cut) & (r["deta_jj"] > deta_cut)
                w_sum = np.sum(r["weight"][mask])
                if sample_name == "VBF_HToTauTau":
                    sig_vbf = w_sum
                elif sample_name == "GluGluToHToTauTau":
                    sig_ggh = w_sum
                else:
                    bkg += w_sum
            s_total = sig_vbf + sig_ggh
            ssqrtb = s_total / np.sqrt(bkg) if bkg > 0 else 0
            log.info("%-10d %-10.1f %10.2f %10.2f %10.1f %10.4f",
                     mjj_cut, deta_cut, sig_vbf, sig_ggh, bkg, ssqrtb)
            if ssqrtb > best_ssqrtb:
                best_ssqrtb = ssqrtb
                best_cuts = (mjj_cut, deta_cut)

    log.info("\nBest VBF cuts: mjj > %d GeV, |deta| > %.1f (S/sqrt(B) = %.4f)",
             best_cuts[0], best_cuts[1], best_ssqrtb)

    # Zeppenfeld centrality study
    log.info("\n--- Zeppenfeld Centrality Study ---")
    mjj_cut, deta_cut = best_cuts
    for zep_cut in [None, 1.0, 0.5]:
        sig_vbf = 0
        bkg = 0
        for sample_name, r in vbf_results.items():
            mask = (r["mjj"] > mjj_cut) & (r["deta_jj"] > deta_cut)
            if zep_cut is not None:
                mask = mask & (r["zep_mu"] < zep_cut) & (r["zep_tau"] < zep_cut)
            w_sum = np.sum(r["weight"][mask])
            if sample_name in ["VBF_HToTauTau", "GluGluToHToTauTau"]:
                sig_vbf += w_sum
            else:
                bkg += w_sum
        ssqrtb = sig_vbf / np.sqrt(bkg) if bkg > 0 else 0
        n_events = sum(np.sum((r["mjj"] > mjj_cut) & (r["deta_jj"] > deta_cut) &
                              ((r["zep_mu"] < zep_cut) & (r["zep_tau"] < zep_cut) if zep_cut is not None else True))
                       for r in vbf_results.values())
        log.info("  Zep cut=%-5s: S=%.2f, B=%.1f, S/sqrt(B)=%.4f, N_total=%d",
                 str(zep_cut) if zep_cut else "None", sig_vbf, bkg, ssqrtb, n_events)

    # Plot mjj distribution for VBF events
    fig, ax = plt.subplots(figsize=(10, 10))
    bins_mjj = np.linspace(0, 1000, 26)
    for sample_name in ["VBF_HToTauTau", "GluGluToHToTauTau", "DYJetsToLL", "TTbar"]:
        if sample_name in vbf_results:
            r = vbf_results[sample_name]
            label = MC_SAMPLES[sample_name]["label"]
            # Normalize for shape comparison
            h, _ = np.histogram(r["mjj"], bins=bins_mjj, weights=r["weight"])
            if np.sum(h) > 0:
                h = h / np.sum(h)
            mh.histplot(h, bins=bins_mjj, histtype="step", label=label,
                        linewidth=2, ax=ax)

    ax.set_xlabel(r"$m_{jj}$ [GeV]")
    ax.set_ylabel("Normalized")
    ax.legend(fontsize="x-small")
    mh.label.exp_label(
        exp="CMS", data=True,
        llabel="Open Simulation",
        rlabel=r"$\sqrt{s} = 8$ TeV",
        loc=0, ax=ax,
    )
    for ext in ["pdf", "png"]:
        fig.savefig(FIG_DIR / f"vbf_mjj.{ext}",
                    bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)

    # Plot delta_eta distribution
    fig, ax = plt.subplots(figsize=(10, 10))
    bins_deta = np.linspace(0, 8, 26)
    for sample_name in ["VBF_HToTauTau", "GluGluToHToTauTau", "DYJetsToLL", "TTbar"]:
        if sample_name in vbf_results:
            r = vbf_results[sample_name]
            label = MC_SAMPLES[sample_name]["label"]
            h, _ = np.histogram(r["deta_jj"], bins=bins_deta, weights=r["weight"])
            if np.sum(h) > 0:
                h = h / np.sum(h)
            mh.histplot(h, bins=bins_deta, histtype="step", label=label,
                        linewidth=2, ax=ax)

    ax.set_xlabel(r"$|\Delta\eta_{jj}|$")
    ax.set_ylabel("Normalized")
    ax.legend(fontsize="x-small")
    mh.label.exp_label(
        exp="CMS", data=True,
        llabel="Open Simulation",
        rlabel=r"$\sqrt{s} = 8$ TeV",
        loc=0, ax=ax,
    )
    for ext in ["pdf", "png"]:
        fig.savefig(FIG_DIR / f"vbf_deta.{ext}",
                    bbox_inches="tight", dpi=200, transparent=True)
    plt.close(fig)

    log.info("\nSaved VBF plots: vbf_mjj.pdf/png, vbf_deta.pdf/png")


if __name__ == "__main__":
    main()
