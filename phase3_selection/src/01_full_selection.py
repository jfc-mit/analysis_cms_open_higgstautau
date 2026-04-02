"""
Phase 3 Step 1: Full event selection with DY decomposition, VBF categorization,
same-sign and high-mT control regions for background estimation.

Re-reads ROOT files to access per-jet arrays and GenPart for DY split.
Uses vectorized awkward-array operations for jet processing.
Saves extended npz files for all regions.
"""
import logging
import json
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
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SAMPLES = {
    "GluGluToHToTauTau": {"desc": "ggH", "is_mc": True, "xsec": 21.39 * 0.06256, "is_signal": True},
    "VBF_HToTauTau": {"desc": "VBF", "is_mc": True, "xsec": 1.600 * 0.06256, "is_signal": True},
    "DYJetsToLL": {"desc": "DY", "is_mc": True, "xsec": 3503.7, "is_signal": False},
    "TTbar": {"desc": "TTbar", "is_mc": True, "xsec": 252.9, "is_signal": False},
    "W1JetsToLNu": {"desc": "W1J", "is_mc": True, "xsec": 6381.2, "is_signal": False},
    "W2JetsToLNu": {"desc": "W2J", "is_mc": True, "xsec": 2039.8, "is_signal": False},
    "W3JetsToLNu": {"desc": "W3J", "is_mc": True, "xsec": 612.5, "is_signal": False},
    "Run2012B_TauPlusX": {"desc": "DataB", "is_mc": False, "xsec": None, "is_signal": False},
    "Run2012C_TauPlusX": {"desc": "DataC", "is_mc": False, "xsec": None, "is_signal": False},
}

LUMI = 11467.0  # pb^-1
CHUNK_SIZE = 500_000

BRANCHES_BASE = [
    "HLT_IsoMu17_eta2p1_LooseIsoPFTau20",
    "nMuon", "Muon_pt", "Muon_eta", "Muon_phi", "Muon_mass", "Muon_charge",
    "Muon_pfRelIso04_all", "Muon_tightId", "Muon_dxy", "Muon_dz",
    "nTau", "Tau_pt", "Tau_eta", "Tau_phi", "Tau_mass", "Tau_charge",
    "Tau_decayMode", "Tau_idDecayMode", "Tau_relIso_all",
    "Tau_idIsoVLoose", "Tau_idIsoLoose", "Tau_idIsoMedium", "Tau_idIsoTight",
    "Tau_idIsoRaw",
    "Tau_idAntiEleTight", "Tau_idAntiMuTight",
    "MET_pt", "MET_phi", "MET_significance",
    "nJet", "Jet_pt", "Jet_eta", "Jet_phi", "Jet_mass", "Jet_btag", "Jet_puId",
    "PV_npvs",
]

BRANCHES_GEN = [
    "nGenPart", "GenPart_pt", "GenPart_eta", "GenPart_phi",
    "GenPart_mass", "GenPart_pdgId", "GenPart_status",
]


def compute_mt(mu_pt, mu_phi, met_pt, met_phi):
    """Compute transverse mass of muon + MET."""
    dphi = mu_phi - met_phi
    dphi = np.arctan2(np.sin(dphi), np.cos(dphi))
    return np.sqrt(2.0 * mu_pt * met_pt * (1.0 - np.cos(dphi)))


def compute_mvis(mu_pt, mu_eta, mu_phi, mu_mass, tau_pt, tau_eta, tau_phi, tau_mass):
    """Compute visible di-tau invariant mass."""
    mu_px = mu_pt * np.cos(mu_phi)
    mu_py = mu_pt * np.sin(mu_phi)
    mu_pz = mu_pt * np.sinh(mu_eta)
    mu_e = np.sqrt(mu_px**2 + mu_py**2 + mu_pz**2 + mu_mass**2)
    tau_px = tau_pt * np.cos(tau_phi)
    tau_py = tau_pt * np.sin(tau_phi)
    tau_pz = tau_pt * np.sinh(tau_eta)
    tau_e = np.sqrt(tau_px**2 + tau_py**2 + tau_pz**2 + tau_mass**2)
    m2 = (mu_e + tau_e)**2 - (mu_px + tau_px)**2 - (mu_py + tau_py)**2 - (mu_pz + tau_pz)**2
    return np.sqrt(np.maximum(m2, 0.0))


def process_jets_vectorized(ev, sel_mu_eta, sel_mu_phi, sel_tau_eta, sel_tau_phi):
    """Process jets with vectorized overlap removal and VBF variable computation.

    Returns flat numpy arrays: njets, nbjets, lead_jet_pt/eta, sublead_jet_pt/eta,
    mjj, deta_jj, zeppenfeld.
    """
    jet_pt = ev["Jet_pt"]
    jet_eta = ev["Jet_eta"]
    jet_phi = ev["Jet_phi"]
    jet_mass = ev["Jet_mass"]
    jet_btag = ev["Jet_btag"]
    jet_puid = ev["Jet_puId"]

    n_ev = len(ev)

    # Base jet selection
    base_mask = (jet_pt > 30) & (np.abs(jet_eta) < 4.7) & jet_puid

    # Overlap removal: compute DR to muon and tau
    # Broadcast scalar mu/tau per event to jet shape
    mu_eta_bc = ak.ones_like(jet_eta) * ak.Array(sel_mu_eta[:, np.newaxis])
    mu_phi_bc = ak.ones_like(jet_phi) * ak.Array(sel_mu_phi[:, np.newaxis])
    tau_eta_bc = ak.ones_like(jet_eta) * ak.Array(sel_tau_eta[:, np.newaxis])
    tau_phi_bc = ak.ones_like(jet_phi) * ak.Array(sel_tau_phi[:, np.newaxis])

    deta_mu = jet_eta - mu_eta_bc
    dphi_mu = np.arctan2(np.sin(jet_phi - mu_phi_bc), np.cos(jet_phi - mu_phi_bc))
    dr_mu = np.sqrt(deta_mu**2 + dphi_mu**2)

    deta_tau = jet_eta - tau_eta_bc
    dphi_tau = np.arctan2(np.sin(jet_phi - tau_phi_bc), np.cos(jet_phi - tau_phi_bc))
    dr_tau = np.sqrt(deta_tau**2 + dphi_tau**2)

    good_jet_mask = base_mask & (dr_mu > 0.5) & (dr_tau > 0.5)

    # Count jets
    njets = ak.to_numpy(ak.sum(good_jet_mask, axis=1))

    # b-jets
    bjet_mask = good_jet_mask & (jet_btag > 0.8)
    nbjets = ak.to_numpy(ak.sum(bjet_mask, axis=1))

    # Get good jets sorted by pT (descending)
    good_jet_pt = jet_pt[good_jet_mask]
    good_jet_eta = jet_eta[good_jet_mask]
    good_jet_phi = jet_phi[good_jet_mask]
    good_jet_mass = jet_mass[good_jet_mask]

    # Sort by pT descending
    sort_idx = ak.argsort(good_jet_pt, axis=1, ascending=False)
    good_jet_pt = good_jet_pt[sort_idx]
    good_jet_eta = good_jet_eta[sort_idx]
    good_jet_phi = good_jet_phi[sort_idx]
    good_jet_mass = good_jet_mass[sort_idx]

    # Leading jet
    lead_pt = ak.to_numpy(ak.fill_none(ak.firsts(good_jet_pt), -1.0))
    lead_eta = ak.to_numpy(ak.fill_none(ak.firsts(good_jet_eta), -99.0))

    # Subleading jet (2nd element)
    has_2jets = njets >= 2
    sublead_pt_ak = ak.where(ak.num(good_jet_pt) >= 2, good_jet_pt[:, 1:2], ak.Array([[-1.0]] * n_ev))
    sublead_eta_ak = ak.where(ak.num(good_jet_eta) >= 2, good_jet_eta[:, 1:2], ak.Array([[-99.0]] * n_ev))

    # Simpler: use pad_none
    padded_pt = ak.pad_none(good_jet_pt, 2, clip=True)
    padded_eta = ak.pad_none(good_jet_eta, 2, clip=True)
    padded_phi = ak.pad_none(good_jet_phi, 2, clip=True)
    padded_mass = ak.pad_none(good_jet_mass, 2, clip=True)

    j1_pt = ak.to_numpy(ak.fill_none(padded_pt[:, 0], -1.0))
    j1_eta = ak.to_numpy(ak.fill_none(padded_eta[:, 0], -99.0))
    j1_phi = ak.to_numpy(ak.fill_none(padded_phi[:, 0], 0.0))
    j1_mass = ak.to_numpy(ak.fill_none(padded_mass[:, 0], 0.0))

    j2_pt = ak.to_numpy(ak.fill_none(padded_pt[:, 1], -1.0))
    j2_eta = ak.to_numpy(ak.fill_none(padded_eta[:, 1], -99.0))
    j2_phi = ak.to_numpy(ak.fill_none(padded_phi[:, 1], 0.0))
    j2_mass = ak.to_numpy(ak.fill_none(padded_mass[:, 1], 0.0))

    # Dijet mass for events with >= 2 jets
    j1_px = j1_pt * np.cos(j1_phi)
    j1_py = j1_pt * np.sin(j1_phi)
    j1_pz = j1_pt * np.sinh(j1_eta)
    j1_e = np.sqrt(j1_px**2 + j1_py**2 + j1_pz**2 + j1_mass**2)

    j2_px = j2_pt * np.cos(j2_phi)
    j2_py = j2_pt * np.sin(j2_phi)
    j2_pz = j2_pt * np.sinh(j2_eta)
    j2_e = np.sqrt(j2_px**2 + j2_py**2 + j2_pz**2 + j2_mass**2)

    m2 = (j1_e + j2_e)**2 - (j1_px + j2_px)**2 - (j1_py + j2_py)**2 - (j1_pz + j2_pz)**2
    mjj = np.where(has_2jets, np.sqrt(np.maximum(m2, 0.0)), -1.0)
    deta_jj = np.where(has_2jets, np.abs(j1_eta - j2_eta), -99.0)

    # Zeppenfeld centrality
    eta_mutau = (sel_mu_eta + sel_tau_eta) / 2.0
    zeppenfeld = np.where(has_2jets,
                          np.abs(eta_mutau - (j1_eta + j2_eta) / 2.0),
                          99.0)

    return {
        "njets": njets,
        "nbjets": nbjets,
        "lead_jet_pt": lead_pt,
        "lead_jet_eta": lead_eta,
        "sublead_jet_pt": j2_pt,
        "sublead_jet_eta": j2_eta,
        "mjj": mjj,
        "deta_jj": deta_jj,
        "zeppenfeld": zeppenfeld,
    }


def dy_truth_match_vectorized(genpart_pdgid, genpart_eta, genpart_phi,
                               tau_eta_sel, tau_phi_sel):
    """DY truth matching: check if selected tau matches a gen-level tau.
    Returns boolean array: True = Z->tautau, False = Z->ll.
    Uses per-event loop (unavoidable with jagged gen arrays).
    """
    gen_tau_mask = (np.abs(genpart_pdgid) == 15)
    gen_tau_eta = genpart_eta[gen_tau_mask]
    gen_tau_phi = genpart_phi[gen_tau_mask]

    n_events = len(tau_eta_sel)
    is_ztt = np.zeros(n_events, dtype=bool)

    for i in range(n_events):
        gt_eta = gen_tau_eta[i]
        if len(gt_eta) == 0:
            continue
        gt_eta_np = ak.to_numpy(gt_eta)
        gt_phi_np = ak.to_numpy(gen_tau_phi[i])
        deta = gt_eta_np - tau_eta_sel[i]
        dphi_val = np.arctan2(
            np.sin(gt_phi_np - tau_phi_sel[i]),
            np.cos(gt_phi_np - tau_phi_sel[i])
        )
        dr = np.sqrt(deta**2 + dphi_val**2)
        if np.any(dr < 0.3):
            is_ztt[i] = True

    return is_ztt


def process_sample(sample_name, info):
    """Process a single sample through the full selection.

    Saves events in multiple regions for background estimation.
    """
    fpath = DATA_DIR / f"{sample_name}.root"
    tree = uproot.open(fpath)["Events"]
    n_total = tree.num_entries

    if info["is_mc"]:
        weight_per_event = info["xsec"] * LUMI / n_total
    else:
        weight_per_event = 1.0

    branches = BRANCHES_BASE[:]
    if info["is_mc"]:
        branches += BRANCHES_GEN

    # Define regions to fill
    region_names = ["os_sr", "os_highmt", "os_midmt", "ss_sr",
                    "os_antiiso", "ss_antiiso", "os_no_mt_cut"]
    field_list = [
        "mu_pt", "mu_eta", "mu_phi", "mu_mass", "mu_charge", "mu_iso",
        "tau_pt", "tau_eta", "tau_phi", "tau_mass", "tau_charge",
        "tau_iso_raw", "tau_dm",
        "met_pt", "met_phi", "met_significance",
        "mvis", "mt", "delta_r", "delta_phi_mutau",
        "njets", "nbjets", "lead_jet_pt", "lead_jet_eta",
        "sublead_jet_pt", "sublead_jet_eta",
        "mjj", "deta_jj", "zeppenfeld",
        "pv_npvs", "weight",
    ]

    regions = {}
    for rn in region_names:
        regions[rn] = {f: [] for f in field_list}
        if sample_name == "DYJetsToLL":
            regions[rn]["is_ztt"] = []

    cutflow = {
        "total": 0, "trigger": 0, "good_muon": 0, "good_tau": 0,
        "pair_found": 0, "os_pair": 0, "dr_cut": 0, "mt_cut": 0,
        "iso_tight": 0,
    }
    cutflow_w = {k: 0.0 for k in cutflow}

    t0 = time.time()
    for chunk in tree.iterate(branches, step_size=CHUNK_SIZE, library="ak"):
        n_chunk = len(chunk)
        cutflow["total"] += n_chunk
        cutflow_w["total"] += n_chunk * weight_per_event

        # 1. Trigger
        trig = chunk["HLT_IsoMu17_eta2p1_LooseIsoPFTau20"]
        ev = chunk[trig]
        cutflow["trigger"] += len(ev)
        cutflow_w["trigger"] += len(ev) * weight_per_event
        if len(ev) == 0:
            continue

        # 2. Good muons
        mu_mask = (
            (ev["Muon_pt"] > 20) & (np.abs(ev["Muon_eta"]) < 2.1)
            & ev["Muon_tightId"] & (ev["Muon_pfRelIso04_all"] < 0.15)
            & (np.abs(ev["Muon_dxy"]) < 0.045) & (np.abs(ev["Muon_dz"]) < 0.2)
        )
        has_mu = ak.sum(mu_mask, axis=1) >= 1
        ev = ev[has_mu]; mu_mask = mu_mask[has_mu]
        cutflow["good_muon"] += int(ak.sum(has_mu))
        cutflow_w["good_muon"] += int(ak.sum(has_mu)) * weight_per_event
        if len(ev) == 0:
            continue

        # 3. Good taus (Loose ID)
        tau_mask = (
            (ev["Tau_pt"] > 20) & (np.abs(ev["Tau_eta"]) < 2.3)
            & ev["Tau_idDecayMode"] & ev["Tau_idAntiEleTight"]
            & ev["Tau_idAntiMuTight"] & ev["Tau_idIsoLoose"]
            & (ev["Tau_charge"] != 0)
        )
        has_tau = ak.sum(tau_mask, axis=1) >= 1
        ev = ev[has_tau]; mu_mask = mu_mask[has_tau]; tau_mask = tau_mask[has_tau]
        cutflow["good_tau"] += int(ak.sum(has_tau))
        cutflow_w["good_tau"] += int(ak.sum(has_tau)) * weight_per_event
        if len(ev) == 0:
            continue

        # 4. Pair selection
        mu_idx = ak.argmax(ev["Muon_pt"][mu_mask], axis=1, keepdims=True)
        tau_iso_sort = ak.fill_none(ak.nan_to_none(ev["Tau_relIso_all"][tau_mask]), 999.0)
        tau_idx = ak.argmin(tau_iso_sort, axis=1, keepdims=True)
        has_pair = (ak.num(mu_idx) > 0) & (ak.num(tau_idx) > 0)
        ev = ev[has_pair]
        mu_mask = mu_mask[has_pair]; tau_mask = tau_mask[has_pair]
        mu_idx = mu_idx[has_pair]; tau_idx = tau_idx[has_pair]
        cutflow["pair_found"] += int(ak.sum(has_pair))
        cutflow_w["pair_found"] += int(ak.sum(has_pair)) * weight_per_event
        if len(ev) == 0:
            continue

        # Extract selected lepton kinematics
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
        sel_tau_iso_raw = ak.to_numpy(ak.flatten(ev["Tau_idIsoRaw"][tau_mask][tau_idx]))
        sel_tau_dm = ak.to_numpy(ak.flatten(ev["Tau_decayMode"][tau_mask][tau_idx]))

        sel_met_pt = ak.to_numpy(ev["MET_pt"])
        sel_met_phi = ak.to_numpy(ev["MET_phi"])
        sel_met_sig = ak.to_numpy(ev["MET_significance"])
        sel_pv_npvs = ak.to_numpy(ev["PV_npvs"])

        # 5. DeltaR > 0.5
        deta_val = sel_mu_eta - sel_tau_eta
        dphi_val = np.arctan2(np.sin(sel_mu_phi - sel_tau_phi),
                              np.cos(sel_mu_phi - sel_tau_phi))
        dr_vals = np.sqrt(deta_val**2 + dphi_val**2)
        dr_mask = dr_vals > 0.5

        # Apply DR cut to all arrays
        def apply_mask(arrs, mask):
            return [a[mask] for a in arrs]

        (sel_mu_pt, sel_mu_eta, sel_mu_phi, sel_mu_mass, sel_mu_charge, sel_mu_iso,
         sel_tau_pt, sel_tau_eta, sel_tau_phi, sel_tau_mass, sel_tau_charge,
         sel_tau_iso_raw, sel_tau_dm, sel_met_pt, sel_met_phi, sel_met_sig,
         sel_pv_npvs) = apply_mask(
            [sel_mu_pt, sel_mu_eta, sel_mu_phi, sel_mu_mass, sel_mu_charge, sel_mu_iso,
             sel_tau_pt, sel_tau_eta, sel_tau_phi, sel_tau_mass, sel_tau_charge,
             sel_tau_iso_raw, sel_tau_dm, sel_met_pt, sel_met_phi, sel_met_sig,
             sel_pv_npvs], dr_mask)
        ev = ev[dr_mask]

        if len(sel_mu_pt) == 0:
            continue

        # Derived quantities
        mt_vals = compute_mt(sel_mu_pt, sel_mu_phi, sel_met_pt, sel_met_phi)
        mvis_vals = compute_mvis(sel_mu_pt, sel_mu_eta, sel_mu_phi, sel_mu_mass,
                                  sel_tau_pt, sel_tau_eta, sel_tau_phi, sel_tau_mass)
        dr_final = np.sqrt((sel_mu_eta - sel_tau_eta)**2 +
                           np.arctan2(np.sin(sel_mu_phi - sel_tau_phi),
                                      np.cos(sel_mu_phi - sel_tau_phi))**2)
        dphi_mutau = np.arctan2(np.sin(sel_mu_phi - sel_tau_phi),
                                np.cos(sel_mu_phi - sel_tau_phi))

        # Charge
        charge_prod = sel_mu_charge * sel_tau_charge
        is_os = charge_prod < 0
        is_ss = charge_prod > 0

        # Cutflow (OS path)
        cutflow["os_pair"] += int(np.sum(is_os))
        cutflow_w["os_pair"] += int(np.sum(is_os)) * weight_per_event
        cutflow["dr_cut"] += int(np.sum(is_os))
        cutflow_w["dr_cut"] += int(np.sum(is_os)) * weight_per_event
        cutflow["mt_cut"] += int(np.sum(is_os & (mt_vals < 30)))
        cutflow_w["mt_cut"] += int(np.sum(is_os & (mt_vals < 30))) * weight_per_event
        cutflow["iso_tight"] += int(np.sum(is_os & (mt_vals < 30) & (sel_mu_iso < 0.1)))
        cutflow_w["iso_tight"] += int(np.sum(is_os & (mt_vals < 30) & (sel_mu_iso < 0.1))) * weight_per_event

        # Jet processing (vectorized)
        jet_info = process_jets_vectorized(ev, sel_mu_eta, sel_mu_phi,
                                            sel_tau_eta, sel_tau_phi)

        # DY truth matching
        is_ztt = None
        if sample_name == "DYJetsToLL":
            is_ztt = dy_truth_match_vectorized(
                ev["GenPart_pdgId"], ev["GenPart_eta"], ev["GenPart_phi"],
                sel_tau_eta, sel_tau_phi
            )

        # Region masks
        region_masks = {
            "os_sr": is_os & (mt_vals < 30) & (sel_mu_iso < 0.1),
            "os_highmt": is_os & (mt_vals > 70) & (sel_mu_iso < 0.1),
            "os_midmt": is_os & (mt_vals >= 30) & (mt_vals <= 70) & (sel_mu_iso < 0.1),
            "ss_sr": is_ss & (mt_vals < 30) & (sel_mu_iso < 0.1),
            "os_antiiso": is_os & (mt_vals < 30) & (sel_mu_iso >= 0.1) & (sel_mu_iso < 0.3),
            "ss_antiiso": is_ss & (mt_vals < 30) & (sel_mu_iso >= 0.1) & (sel_mu_iso < 0.3),
            "os_no_mt_cut": is_os & (sel_mu_iso < 0.1),
        }

        for rname, rmask in region_masks.items():
            if np.sum(rmask) == 0:
                continue
            regions[rname]["mu_pt"].append(sel_mu_pt[rmask])
            regions[rname]["mu_eta"].append(sel_mu_eta[rmask])
            regions[rname]["mu_phi"].append(sel_mu_phi[rmask])
            regions[rname]["mu_mass"].append(sel_mu_mass[rmask])
            regions[rname]["mu_charge"].append(sel_mu_charge[rmask])
            regions[rname]["mu_iso"].append(sel_mu_iso[rmask])
            regions[rname]["tau_pt"].append(sel_tau_pt[rmask])
            regions[rname]["tau_eta"].append(sel_tau_eta[rmask])
            regions[rname]["tau_phi"].append(sel_tau_phi[rmask])
            regions[rname]["tau_mass"].append(sel_tau_mass[rmask])
            regions[rname]["tau_charge"].append(sel_tau_charge[rmask])
            regions[rname]["tau_iso_raw"].append(sel_tau_iso_raw[rmask])
            regions[rname]["tau_dm"].append(sel_tau_dm[rmask])
            regions[rname]["met_pt"].append(sel_met_pt[rmask])
            regions[rname]["met_phi"].append(sel_met_phi[rmask])
            regions[rname]["met_significance"].append(sel_met_sig[rmask])
            regions[rname]["mvis"].append(mvis_vals[rmask])
            regions[rname]["mt"].append(mt_vals[rmask])
            regions[rname]["delta_r"].append(dr_final[rmask])
            regions[rname]["delta_phi_mutau"].append(dphi_mutau[rmask])
            regions[rname]["njets"].append(jet_info["njets"][rmask])
            regions[rname]["nbjets"].append(jet_info["nbjets"][rmask])
            regions[rname]["lead_jet_pt"].append(jet_info["lead_jet_pt"][rmask])
            regions[rname]["lead_jet_eta"].append(jet_info["lead_jet_eta"][rmask])
            regions[rname]["sublead_jet_pt"].append(jet_info["sublead_jet_pt"][rmask])
            regions[rname]["sublead_jet_eta"].append(jet_info["sublead_jet_eta"][rmask])
            regions[rname]["mjj"].append(jet_info["mjj"][rmask])
            regions[rname]["deta_jj"].append(jet_info["deta_jj"][rmask])
            regions[rname]["zeppenfeld"].append(jet_info["zeppenfeld"][rmask])
            regions[rname]["pv_npvs"].append(sel_pv_npvs[rmask])
            regions[rname]["weight"].append(np.full(int(np.sum(rmask)), weight_per_event))
            if sample_name == "DYJetsToLL":
                regions[rname]["is_ztt"].append(is_ztt[rmask])

    elapsed = time.time() - t0
    log.info("  %s: %d events in %.1f s (%.0f kHz)",
             sample_name, cutflow["total"], elapsed,
             cutflow["total"] / max(elapsed, 0.01) / 1000)

    # Concatenate
    for rn in region_names:
        for key in regions[rn]:
            if regions[rn][key]:
                regions[rn][key] = np.concatenate(regions[rn][key])
            else:
                regions[rn][key] = np.array([])

    return cutflow, cutflow_w, regions


def main():
    log.info("=" * 60)
    log.info("Phase 3 Step 1: Full Selection with VBF and Control Regions")
    log.info("=" * 60)

    all_cutflows = {}
    all_cutflows_w = {}
    all_regions = {}

    for sample_name, info in SAMPLES.items():
        log.info("\nProcessing %s (%s)...", sample_name, info["desc"])
        cutflow, cutflow_w, regions = process_sample(sample_name, info)
        all_cutflows[sample_name] = cutflow
        all_cutflows_w[sample_name] = cutflow_w
        all_regions[sample_name] = regions

        log.info("  Cutflow (raw): %s",
                 ", ".join(f"{k}={v}" for k, v in cutflow.items()))
        n_sr = len(regions["os_sr"]["mu_pt"])
        w_sr = float(np.sum(regions["os_sr"]["weight"])) if n_sr > 0 else 0
        log.info("  OS SR: %d raw (%.1f weighted)", n_sr, w_sr)

    # Save
    cutflow_path = OUTPUT_DIR / "cutflow_phase3.json"
    with open(cutflow_path, "w") as f:
        json.dump({"raw": all_cutflows, "weighted": all_cutflows_w}, f, indent=2)
    log.info("\nCutflows saved to %s", cutflow_path)

    for sample_name in SAMPLES:
        for rname in ["os_sr", "os_highmt", "os_midmt", "ss_sr",
                       "os_antiiso", "ss_antiiso", "os_no_mt_cut"]:
            data = all_regions[sample_name][rname]
            if len(data["mu_pt"]) > 0:
                npz_path = OUTPUT_DIR / f"p3_{sample_name}_{rname}.npz"
                np.savez_compressed(npz_path, **data)

    log.info("Region arrays saved")

    # Summary
    log.info("\n" + "=" * 60)
    log.info("YIELD TABLE — OS Signal Region (mT < 30, iso < 0.1)")
    log.info("=" * 60)
    log.info("%-25s %10s %10s", "Sample", "Raw", "Weighted")
    mc_total = 0.0
    data_total = 0
    for sn, info in SAMPLES.items():
        n_raw = len(all_regions[sn]["os_sr"]["mu_pt"])
        w_sum = float(np.sum(all_regions[sn]["os_sr"]["weight"])) if n_raw > 0 else 0
        if info["is_mc"]:
            mc_total += w_sum
        else:
            data_total += n_raw
        log.info("%-25s %10d %10.1f", sn, n_raw, w_sum)
    log.info("%-25s %10s %10.1f", "MC Total", "-", mc_total)
    log.info("%-25s %10d %10d", "Data Total", data_total, data_total)

    # DY decomposition
    dy_sr = all_regions["DYJetsToLL"]["os_sr"]
    if len(dy_sr.get("is_ztt", [])) > 0:
        ztt_mask = dy_sr["is_ztt"].astype(bool)
        log.info("\nDY decomposition (OS SR):")
        log.info("  Z->tautau: %d raw (%.1f weighted)",
                 int(np.sum(ztt_mask)),
                 float(np.sum(dy_sr["weight"][ztt_mask])))
        log.info("  Z->ll:     %d raw (%.1f weighted)",
                 int(np.sum(~ztt_mask)),
                 float(np.sum(dy_sr["weight"][~ztt_mask])))

    # VBF categorization
    log.info("\n" + "=" * 60)
    log.info("VBF CATEGORIZATION (OS SR)")
    log.info("%-25s %10s %10s", "Sample", "Baseline", "VBF")
    for sn in SAMPLES:
        data = all_regions[sn]["os_sr"]
        if len(data["mjj"]) == 0:
            continue
        vbf = (data["njets"] >= 2) & (data["mjj"] > 200) & (np.abs(data["deta_jj"]) > 2.0)
        log.info("%-25s %10.1f %10.1f",
                 sn,
                 float(np.sum(data["weight"][~vbf])),
                 float(np.sum(data["weight"][vbf])))

    # Control region yields
    log.info("\n" + "=" * 60)
    log.info("CONTROL REGION YIELDS (weighted)")
    for rn in ["os_highmt", "os_midmt", "ss_sr", "os_antiiso", "ss_antiiso"]:
        log.info("\n--- %s ---", rn)
        for sn in SAMPLES:
            data = all_regions[sn][rn]
            n = len(data["mu_pt"])
            w = float(np.sum(data["weight"])) if n > 0 else 0
            if n > 0:
                log.info("  %-25s %8d raw %10.1f weighted", sn, n, w)


if __name__ == "__main__":
    main()
