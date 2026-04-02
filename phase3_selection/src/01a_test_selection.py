"""Quick prototype: test the selection on ggH signal (small sample)."""
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

DATA_DIR = Path("/eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool")


def compute_mt(mu_pt, mu_phi, met_pt, met_phi):
    dphi = mu_phi - met_phi
    dphi = np.arctan2(np.sin(dphi), np.cos(dphi))
    return np.sqrt(2.0 * mu_pt * met_pt * (1.0 - np.cos(dphi)))


def compute_mvis(mu_pt, mu_eta, mu_phi, mu_mass, tau_pt, tau_eta, tau_phi, tau_mass):
    mu_px = mu_pt * np.cos(mu_phi)
    mu_py = mu_pt * np.sin(mu_phi)
    mu_pz = mu_pt * np.sinh(mu_eta)
    mu_e = np.sqrt(mu_px**2 + mu_py**2 + mu_pz**2 + mu_mass**2)
    tau_px = tau_pt * np.cos(tau_phi)
    tau_py = tau_pt * np.sin(tau_phi)
    tau_pz = tau_pt * np.sinh(tau_eta)
    tau_e = np.sqrt(tau_px**2 + tau_py**2 + tau_pz**2 + tau_mass**2)
    tot_e = mu_e + tau_e
    tot_px = mu_px + tau_px
    tot_py = mu_py + tau_py
    tot_pz = mu_pz + tau_pz
    m2 = tot_e**2 - tot_px**2 - tot_py**2 - tot_pz**2
    return np.sqrt(np.maximum(m2, 0.0))


def compute_delta_r(eta1, phi1, eta2, phi2):
    deta = eta1 - eta2
    dphi = np.arctan2(np.sin(phi1 - phi2), np.cos(phi1 - phi2))
    return np.sqrt(deta**2 + dphi**2)


def main():
    fpath = DATA_DIR / "GluGluToHToTauTau.root"
    tree = uproot.open(fpath)["Events"]
    n_total = tree.num_entries
    log.info("Total events: %d", n_total)

    branches = [
        "HLT_IsoMu17_eta2p1_LooseIsoPFTau20",
        "nMuon", "Muon_pt", "Muon_eta", "Muon_phi", "Muon_mass", "Muon_charge",
        "Muon_pfRelIso04_all", "Muon_tightId", "Muon_dxy", "Muon_dz",
        "nTau", "Tau_pt", "Tau_eta", "Tau_phi", "Tau_mass", "Tau_charge",
        "Tau_decayMode", "Tau_idDecayMode", "Tau_relIso_all",
        "Tau_idIsoLoose", "Tau_idIsoRaw",
        "Tau_idAntiEleTight", "Tau_idAntiMuTight",
        "MET_pt", "MET_phi", "MET_significance",
        "nJet", "Jet_pt", "Jet_eta", "Jet_phi", "Jet_mass", "Jet_btag", "Jet_puId",
        "PV_npvs",
        "nGenPart", "GenPart_pt", "GenPart_eta", "GenPart_phi",
        "GenPart_mass", "GenPart_pdgId", "GenPart_status",
    ]

    weight_per_event = 21.39 * 0.06256 * 11467.0 / n_total
    log.info("Weight per event: %.6f", weight_per_event)

    t0 = time.time()
    # Process just first 50K events for testing
    selected_count = 0
    vbf_count = 0

    for chunk in tree.iterate(branches, step_size=50000, library="ak",
                              entry_stop=100000):
        n_chunk = len(chunk)
        log.info("Chunk: %d events", n_chunk)

        # Trigger
        trig = chunk["HLT_IsoMu17_eta2p1_LooseIsoPFTau20"]
        ev = chunk[trig]
        log.info("  After trigger: %d", len(ev))

        # Good muons
        mu_mask = (
            (ev["Muon_pt"] > 20) & (np.abs(ev["Muon_eta"]) < 2.1)
            & ev["Muon_tightId"] & (ev["Muon_pfRelIso04_all"] < 0.15)
            & (np.abs(ev["Muon_dxy"]) < 0.045) & (np.abs(ev["Muon_dz"]) < 0.2)
        )
        has_mu = ak.sum(mu_mask, axis=1) >= 1
        ev = ev[has_mu]
        mu_mask = mu_mask[has_mu]
        log.info("  After good muon: %d", len(ev))

        # Good taus
        tau_mask = (
            (ev["Tau_pt"] > 20) & (np.abs(ev["Tau_eta"]) < 2.3)
            & ev["Tau_idDecayMode"] & ev["Tau_idAntiEleTight"]
            & ev["Tau_idAntiMuTight"] & ev["Tau_idIsoLoose"]
            & (ev["Tau_charge"] != 0)
        )
        has_tau = ak.sum(tau_mask, axis=1) >= 1
        ev = ev[has_tau]
        mu_mask = mu_mask[has_tau]
        tau_mask = tau_mask[has_tau]
        log.info("  After good tau: %d", len(ev))

        # Pair selection
        mu_idx = ak.argmax(ev["Muon_pt"][mu_mask], axis=1, keepdims=True)
        tau_iso_sort = ak.fill_none(ak.nan_to_none(ev["Tau_relIso_all"][tau_mask]), 999.0)
        tau_idx = ak.argmin(tau_iso_sort, axis=1, keepdims=True)

        has_pair = (ak.num(mu_idx) > 0) & (ak.num(tau_idx) > 0)
        ev = ev[has_pair]
        mu_mask = mu_mask[has_pair]
        tau_mask = tau_mask[has_pair]
        mu_idx = mu_idx[has_pair]
        tau_idx = tau_idx[has_pair]

        sel_mu_pt = ak.to_numpy(ak.flatten(ev["Muon_pt"][mu_mask][mu_idx]))
        sel_mu_eta = ak.to_numpy(ak.flatten(ev["Muon_eta"][mu_mask][mu_idx]))
        sel_mu_phi = ak.to_numpy(ak.flatten(ev["Muon_phi"][mu_mask][mu_idx]))
        sel_mu_mass = ak.to_numpy(ak.flatten(ev["Muon_mass"][mu_mask][mu_idx]))
        sel_mu_charge = ak.to_numpy(ak.flatten(ev["Muon_charge"][mu_mask][mu_idx]))
        sel_mu_iso = ak.to_numpy(ak.flatten(ev["Muon_pfRelIso04_all"][mu_mask][mu_idx]))

        sel_tau_pt = ak.to_numpy(ak.flatten(ev["Tau_pt"][tau_mask][tau_idx]))
        sel_tau_eta = ak.to_numpy(ak.flatten(ev["Tau_eta"][tau_mask][tau_idx]))
        sel_tau_phi = ak.to_numpy(ak.flatten(ev["Tau_phi"][tau_mask][tau_idx]))
        sel_tau_mass = ak.to_numpy(ak.flatten(ev["Tau_mass"][tau_mask][tau_idx]))
        sel_tau_charge = ak.to_numpy(ak.flatten(ev["Tau_charge"][tau_mask][tau_idx]))

        sel_met_pt = ak.to_numpy(ev["MET_pt"])
        sel_met_phi = ak.to_numpy(ev["MET_phi"])

        # DR
        dr = compute_delta_r(sel_mu_eta, sel_mu_phi, sel_tau_eta, sel_tau_phi)
        dr_mask = dr > 0.5

        # Apply DR
        sel_mu_pt = sel_mu_pt[dr_mask]
        sel_mu_eta = sel_mu_eta[dr_mask]
        sel_mu_phi = sel_mu_phi[dr_mask]
        sel_mu_charge = sel_mu_charge[dr_mask]
        sel_mu_iso = sel_mu_iso[dr_mask]
        sel_tau_pt = sel_tau_pt[dr_mask]
        sel_tau_eta = sel_tau_eta[dr_mask]
        sel_tau_phi = sel_tau_phi[dr_mask]
        sel_tau_charge = sel_tau_charge[dr_mask]
        sel_met_pt = sel_met_pt[dr_mask]
        sel_met_phi = sel_met_phi[dr_mask]
        ev_dr = ev[dr_mask]
        log.info("  After DR: %d", len(sel_mu_pt))

        # OS
        is_os = (sel_mu_charge * sel_tau_charge) < 0
        mt_vals = compute_mt(sel_mu_pt, sel_mu_phi, sel_met_pt, sel_met_phi)

        sr_mask = is_os & (mt_vals < 30) & (sel_mu_iso < 0.1)
        log.info("  OS SR: %d", int(np.sum(sr_mask)))

        # VBF jets per event
        jet_pt = ev_dr["Jet_pt"]
        jet_eta = ev_dr["Jet_eta"]
        jet_phi = ev_dr["Jet_phi"]
        jet_mass = ev_dr["Jet_mass"]
        jet_puid = ev_dr["Jet_puId"]

        n_ev = len(ev_dr)
        njets = np.zeros(n_ev, dtype=int)
        mjj_arr = np.full(n_ev, -1.0)
        deta_arr = np.full(n_ev, -99.0)

        for i in range(n_ev):
            jpt = ak.to_numpy(jet_pt[i])
            jeta = ak.to_numpy(jet_eta[i])
            jphi = ak.to_numpy(jet_phi[i])
            jm = ak.to_numpy(jet_mass[i])
            jpid = ak.to_numpy(jet_puid[i])

            if len(jpt) == 0:
                continue

            mask = (jpt > 30) & (np.abs(jeta) < 4.7) & jpid
            # Overlap removal
            mu_dr = compute_delta_r(jeta, jphi,
                                     np.full(len(jeta), sel_mu_eta[i]),
                                     np.full(len(jphi), sel_mu_phi[i]))
            tau_dr = compute_delta_r(jeta, jphi,
                                      np.full(len(jeta), sel_tau_eta[i]),
                                      np.full(len(jphi), sel_tau_phi[i]))
            mask = mask & (mu_dr > 0.5) & (tau_dr > 0.5)

            good_idx = np.where(mask)[0]
            njets[i] = len(good_idx)

            if len(good_idx) >= 2:
                sorted_idx = good_idx[np.argsort(jpt[good_idx])[::-1]]
                j1_pt, j1_eta, j1_phi, j1_m = jpt[sorted_idx[0]], jeta[sorted_idx[0]], jphi[sorted_idx[0]], jm[sorted_idx[0]]
                j2_pt, j2_eta, j2_phi, j2_m = jpt[sorted_idx[1]], jeta[sorted_idx[1]], jphi[sorted_idx[1]], jm[sorted_idx[1]]

                j1_px = j1_pt * np.cos(j1_phi)
                j1_py = j1_pt * np.sin(j1_phi)
                j1_pz = j1_pt * np.sinh(j1_eta)
                j1_e = np.sqrt(j1_px**2 + j1_py**2 + j1_pz**2 + j1_m**2)
                j2_px = j2_pt * np.cos(j2_phi)
                j2_py = j2_pt * np.sin(j2_phi)
                j2_pz = j2_pt * np.sinh(j2_eta)
                j2_e = np.sqrt(j2_px**2 + j2_py**2 + j2_pz**2 + j2_m**2)
                m2 = (j1_e+j2_e)**2 - (j1_px+j2_px)**2 - (j1_py+j2_py)**2 - (j1_pz+j2_pz)**2
                mjj_arr[i] = np.sqrt(max(m2, 0))
                deta_arr[i] = abs(j1_eta - j2_eta)

        # VBF in SR
        vbf_in_sr = sr_mask & (njets >= 2) & (mjj_arr > 200) & (np.abs(deta_arr) > 2.0)
        log.info("  VBF in SR: %d", int(np.sum(vbf_in_sr)))
        selected_count += int(np.sum(sr_mask))
        vbf_count += int(np.sum(vbf_in_sr))

        # Test gen MET
        genpart_pdgid = ev_dr["GenPart_pdgId"]
        genpart_pt = ev_dr["GenPart_pt"]
        genpart_phi = ev_dr["GenPart_phi"]
        genpart_status = ev_dr["GenPart_status"]

        nu_mask = (
            ((np.abs(genpart_pdgid) == 12) |
             (np.abs(genpart_pdgid) == 14) |
             (np.abs(genpart_pdgid) == 16))
            & (genpart_status == 1)
        )
        nu_px = genpart_pt[nu_mask] * np.cos(genpart_phi[nu_mask])
        nu_py = genpart_pt[nu_mask] * np.sin(genpart_phi[nu_mask])
        gen_met_px = ak.sum(nu_px, axis=1)
        gen_met_py = ak.sum(nu_py, axis=1)
        gen_met_pt = np.sqrt(gen_met_px**2 + gen_met_py**2)

        log.info("  Gen MET mean: %.1f, Reco MET mean: %.1f",
                 float(ak.mean(gen_met_pt)), float(np.mean(sel_met_pt)))

    log.info("\n=== TOTALS (first 100K events) ===")
    log.info("OS SR: %d, VBF: %d", selected_count, vbf_count)
    log.info("Elapsed: %.1f s", time.time() - t0)


if __name__ == "__main__":
    main()
