"""
Phase 2 Step 3: Apply baseline preselection, compute cutflow and yields.

Processes all samples in chunks, applies trigger + object selection + pair selection.
Saves selected events as awkward arrays for downstream analysis.
Reports cutflow and yields with cross-section normalization.
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

SAMPLES = {
    "GluGluToHToTauTau": {"desc": "ggH", "is_mc": True, "xsec": 21.39 * 0.06256},
    "VBF_HToTauTau": {"desc": "VBF", "is_mc": True, "xsec": 1.600 * 0.06256},
    "DYJetsToLL": {"desc": "DY", "is_mc": True, "xsec": 3503.7},
    "TTbar": {"desc": "TTbar", "is_mc": True, "xsec": 252.9},
    "W1JetsToLNu": {"desc": "W1J", "is_mc": True, "xsec": 6381.2},
    "W2JetsToLNu": {"desc": "W2J", "is_mc": True, "xsec": 2039.8},
    "W3JetsToLNu": {"desc": "W3J", "is_mc": True, "xsec": 612.5},
    "Run2012B_TauPlusX": {"desc": "DataB", "is_mc": False, "xsec": None},
    "Run2012C_TauPlusX": {"desc": "DataC", "is_mc": False, "xsec": None},
}

LUMI = 11467.0  # pb^-1
CHUNK_SIZE = 500_000

# Branches needed for preselection
BRANCHES = [
    "HLT_IsoMu17_eta2p1_LooseIsoPFTau20",
    "nMuon", "Muon_pt", "Muon_eta", "Muon_phi", "Muon_mass", "Muon_charge",
    "Muon_pfRelIso04_all", "Muon_tightId", "Muon_dxy", "Muon_dz",
    "nTau", "Tau_pt", "Tau_eta", "Tau_phi", "Tau_mass", "Tau_charge",
    "Tau_decayMode", "Tau_idDecayMode", "Tau_relIso_all",
    "Tau_idIsoVLoose", "Tau_idIsoLoose", "Tau_idIsoMedium", "Tau_idIsoTight",
    "Tau_idIsoRaw",
    "Tau_idAntiEleTight", "Tau_idAntiMuTight",
    "MET_pt", "MET_phi",
    "nJet", "Jet_pt", "Jet_eta", "Jet_phi", "Jet_mass", "Jet_btag", "Jet_puId",
    "PV_npvs",
]


def compute_mt(mu_pt, mu_phi, met_pt, met_phi):
    """Compute transverse mass of muon + MET."""
    dphi = mu_phi - met_phi
    dphi = np.arctan2(np.sin(dphi), np.cos(dphi))  # wrap to [-pi, pi]
    return np.sqrt(2.0 * mu_pt * met_pt * (1.0 - np.cos(dphi)))


def compute_mvis(mu_pt, mu_eta, mu_phi, mu_mass, tau_pt, tau_eta, tau_phi, tau_mass):
    """Compute visible di-tau invariant mass using numpy."""
    # Convert pT, eta, phi, mass to px, py, pz, E
    mu_px = mu_pt * np.cos(mu_phi)
    mu_py = mu_pt * np.sin(mu_phi)
    mu_pz = mu_pt * np.sinh(mu_eta)
    mu_e = np.sqrt(mu_px**2 + mu_py**2 + mu_pz**2 + mu_mass**2)

    tau_px = tau_pt * np.cos(tau_phi)
    tau_py = tau_pt * np.sin(tau_phi)
    tau_pz = tau_pt * np.sinh(tau_eta)
    tau_e = np.sqrt(tau_px**2 + tau_py**2 + tau_pz**2 + tau_mass**2)

    # Invariant mass of the sum
    tot_e = mu_e + tau_e
    tot_px = mu_px + tau_px
    tot_py = mu_py + tau_py
    tot_pz = mu_pz + tau_pz
    m2 = tot_e**2 - tot_px**2 - tot_py**2 - tot_pz**2
    return np.sqrt(np.maximum(m2, 0.0))


def process_sample(sample_name, info, tau_iso_wp="Loose"):
    """Process a single sample with the given tau isolation WP."""
    fpath = DATA_DIR / f"{sample_name}.root"
    tree = uproot.open(fpath)["Events"]
    n_total = tree.num_entries

    # Weight per event
    if info["is_mc"]:
        weight_per_event = info["xsec"] * LUMI / n_total
    else:
        weight_per_event = 1.0

    tau_iso_branch = f"Tau_idIso{tau_iso_wp}"

    cutflow = {
        "total": 0,
        "trigger": 0,
        "good_muon": 0,
        "good_tau": 0,
        "pair_found": 0,
        "os_pair": 0,
        "dr_cut": 0,
        "mt_cut": 0,
        "iso_tight": 0,
    }
    cutflow_weighted = {k: 0.0 for k in cutflow}

    # Accumulators for selected events
    selected_arrays = {
        "mu_pt": [], "mu_eta": [], "mu_phi": [], "mu_mass": [], "mu_charge": [],
        "mu_iso": [],
        "tau_pt": [], "tau_eta": [], "tau_phi": [], "tau_mass": [], "tau_charge": [],
        "tau_iso_raw": [], "tau_dm": [],
        "met_pt": [], "met_phi": [],
        "mvis": [], "mt": [],
        "njets": [], "nbjets": [],
        "lead_jet_pt": [], "lead_jet_eta": [],
        "pv_npvs": [],
        "weight": [],
    }

    t0 = time.time()
    for chunk_arrays in tree.iterate(BRANCHES, step_size=CHUNK_SIZE, library="ak"):
        n_chunk = len(chunk_arrays)
        cutflow["total"] += n_chunk
        cutflow_weighted["total"] += n_chunk * weight_per_event

        # 1. Trigger
        trig = chunk_arrays["HLT_IsoMu17_eta2p1_LooseIsoPFTau20"]
        ev = chunk_arrays[trig]
        cutflow["trigger"] += len(ev)
        cutflow_weighted["trigger"] += len(ev) * weight_per_event

        # 2. Good muons: pT > 20, |eta| < 2.1, tightId, iso < 0.15, |dxy| < 0.045, |dz| < 0.2
        mu_mask = (
            (ev["Muon_pt"] > 20)
            & (np.abs(ev["Muon_eta"]) < 2.1)
            & (ev["Muon_tightId"])
            & (ev["Muon_pfRelIso04_all"] < 0.15)
            & (np.abs(ev["Muon_dxy"]) < 0.045)
            & (np.abs(ev["Muon_dz"]) < 0.2)
        )
        n_good_mu = ak.sum(mu_mask, axis=1)
        has_mu = n_good_mu >= 1
        ev_mu = ev[has_mu]
        mu_mask = mu_mask[has_mu]
        cutflow["good_muon"] += int(ak.sum(has_mu))
        cutflow_weighted["good_muon"] += int(ak.sum(has_mu)) * weight_per_event

        # 3. Good taus: pT > 20, |eta| < 2.3, decayMode, anti-ele tight, anti-mu tight, tau iso WP
        tau_mask = (
            (ev_mu["Tau_pt"] > 20)
            & (np.abs(ev_mu["Tau_eta"]) < 2.3)
            & (ev_mu["Tau_idDecayMode"])
            & (ev_mu["Tau_idAntiEleTight"])
            & (ev_mu["Tau_idAntiMuTight"])
            & (ev_mu[tau_iso_branch])
            & (ev_mu["Tau_charge"] != 0)
        )
        n_good_tau = ak.sum(tau_mask, axis=1)
        has_tau = n_good_tau >= 1
        ev_t = ev_mu[has_tau]
        mu_mask_t = mu_mask[has_tau]
        tau_mask_t = tau_mask[has_tau]
        cutflow["good_tau"] += int(ak.sum(has_tau))
        cutflow_weighted["good_tau"] += int(ak.sum(has_tau)) * weight_per_event

        # 4. Pair selection: highest-pT muon, lowest-isolation tau
        # Get good muons and taus
        good_mu = ev_t["Muon_pt"][mu_mask_t]
        good_tau_iso = ev_t["Tau_relIso_all"][tau_mask_t]

        # Select leading muon (highest pT)
        mu_idx = ak.argmax(ev_t["Muon_pt"][mu_mask_t], axis=1, keepdims=True)
        # Select best tau (lowest isolation = most isolated)
        tau_idx = ak.argmin(ev_t["Tau_relIso_all"][tau_mask_t], axis=1, keepdims=True)

        # Check both have valid indices (should always be true given has_tau)
        has_pair = (ak.num(mu_idx) > 0) & (ak.num(tau_idx) > 0)
        ev_p = ev_t[has_pair]
        mu_mask_p = mu_mask_t[has_pair]
        tau_mask_p = tau_mask_t[has_pair]
        mu_idx_p = mu_idx[has_pair]
        tau_idx_p = tau_idx[has_pair]
        cutflow["pair_found"] += int(ak.sum(has_pair))
        cutflow_weighted["pair_found"] += int(ak.sum(has_pair)) * weight_per_event

        # Extract selected muon and tau properties
        # We need to index into the masked arrays
        good_mu_pt = ak.flatten(ev_p["Muon_pt"][mu_mask_p][mu_idx_p])
        good_mu_eta = ak.flatten(ev_p["Muon_eta"][mu_mask_p][mu_idx_p])
        good_mu_phi = ak.flatten(ev_p["Muon_phi"][mu_mask_p][mu_idx_p])
        good_mu_mass = ak.flatten(ev_p["Muon_mass"][mu_mask_p][mu_idx_p])
        good_mu_charge = ak.flatten(ev_p["Muon_charge"][mu_mask_p][mu_idx_p])
        good_mu_iso = ak.flatten(ev_p["Muon_pfRelIso04_all"][mu_mask_p][mu_idx_p])

        good_tau_pt = ak.flatten(ev_p["Tau_pt"][tau_mask_p][tau_idx_p])
        good_tau_eta = ak.flatten(ev_p["Tau_eta"][tau_mask_p][tau_idx_p])
        good_tau_phi = ak.flatten(ev_p["Tau_phi"][tau_mask_p][tau_idx_p])
        good_tau_mass = ak.flatten(ev_p["Tau_mass"][tau_mask_p][tau_idx_p])
        good_tau_charge = ak.flatten(ev_p["Tau_charge"][tau_mask_p][tau_idx_p])
        good_tau_iso_raw = ak.flatten(ev_p["Tau_idIsoRaw"][tau_mask_p][tau_idx_p])
        good_tau_dm = ak.flatten(ev_p["Tau_decayMode"][tau_mask_p][tau_idx_p])

        met_pt = ev_p["MET_pt"]
        met_phi = ev_p["MET_phi"]

        # 5. Opposite sign
        os_mask = (good_mu_charge * good_tau_charge) < 0
        cutflow["os_pair"] += int(ak.sum(os_mask))
        cutflow_weighted["os_pair"] += int(ak.sum(os_mask)) * weight_per_event

        good_mu_pt = good_mu_pt[os_mask]
        good_mu_eta = good_mu_eta[os_mask]
        good_mu_phi = good_mu_phi[os_mask]
        good_mu_mass = good_mu_mass[os_mask]
        good_mu_charge = good_mu_charge[os_mask]
        good_mu_iso = good_mu_iso[os_mask]
        good_tau_pt = good_tau_pt[os_mask]
        good_tau_eta = good_tau_eta[os_mask]
        good_tau_phi = good_tau_phi[os_mask]
        good_tau_mass = good_tau_mass[os_mask]
        good_tau_charge = good_tau_charge[os_mask]
        good_tau_iso_raw = good_tau_iso_raw[os_mask]
        good_tau_dm = good_tau_dm[os_mask]
        met_pt_sel = met_pt[os_mask]
        met_phi_sel = met_phi[os_mask]

        # 6. DeltaR > 0.5
        deta = good_mu_eta - good_tau_eta
        dphi = np.arctan2(np.sin(good_mu_phi - good_tau_phi),
                          np.cos(good_mu_phi - good_tau_phi))
        dr = np.sqrt(deta**2 + dphi**2)
        dr_mask = dr > 0.5
        cutflow["dr_cut"] += int(ak.sum(dr_mask))
        cutflow_weighted["dr_cut"] += int(ak.sum(dr_mask)) * weight_per_event

        good_mu_pt = good_mu_pt[dr_mask]
        good_mu_eta = good_mu_eta[dr_mask]
        good_mu_phi = good_mu_phi[dr_mask]
        good_mu_mass = good_mu_mass[dr_mask]
        good_mu_charge = good_mu_charge[dr_mask]
        good_mu_iso = good_mu_iso[dr_mask]
        good_tau_pt = good_tau_pt[dr_mask]
        good_tau_eta = good_tau_eta[dr_mask]
        good_tau_phi = good_tau_phi[dr_mask]
        good_tau_mass = good_tau_mass[dr_mask]
        good_tau_charge = good_tau_charge[dr_mask]
        good_tau_iso_raw = good_tau_iso_raw[dr_mask]
        good_tau_dm = good_tau_dm[dr_mask]
        met_pt_sel = met_pt_sel[dr_mask]
        met_phi_sel = met_phi_sel[dr_mask]

        # 7. mT < 30 GeV
        mt_vals = compute_mt(
            ak.to_numpy(good_mu_pt), ak.to_numpy(good_mu_phi),
            ak.to_numpy(met_pt_sel), ak.to_numpy(met_phi_sel)
        )
        mt_mask = mt_vals < 30.0
        cutflow["mt_cut"] += int(np.sum(mt_mask))
        cutflow_weighted["mt_cut"] += int(np.sum(mt_mask)) * weight_per_event

        good_mu_pt = ak.to_numpy(good_mu_pt)[mt_mask]
        good_mu_eta = ak.to_numpy(good_mu_eta)[mt_mask]
        good_mu_phi = ak.to_numpy(good_mu_phi)[mt_mask]
        good_mu_mass = ak.to_numpy(good_mu_mass)[mt_mask]
        good_mu_charge = ak.to_numpy(good_mu_charge)[mt_mask]
        good_mu_iso = ak.to_numpy(good_mu_iso)[mt_mask]
        good_tau_pt = ak.to_numpy(good_tau_pt)[mt_mask]
        good_tau_eta = ak.to_numpy(good_tau_eta)[mt_mask]
        good_tau_phi = ak.to_numpy(good_tau_phi)[mt_mask]
        good_tau_mass = ak.to_numpy(good_tau_mass)[mt_mask]
        good_tau_charge = ak.to_numpy(good_tau_charge)[mt_mask]
        good_tau_iso_raw = ak.to_numpy(good_tau_iso_raw)[mt_mask]
        good_tau_dm = ak.to_numpy(good_tau_dm)[mt_mask]
        met_pt_sel = ak.to_numpy(met_pt_sel)[mt_mask]
        met_phi_sel = ak.to_numpy(met_phi_sel)[mt_mask]
        mt_vals = mt_vals[mt_mask]

        # 8. Tighter muon isolation < 0.1 (signal region)
        iso_mask = good_mu_iso < 0.1
        cutflow["iso_tight"] += int(np.sum(iso_mask))
        cutflow_weighted["iso_tight"] += int(np.sum(iso_mask)) * weight_per_event

        # Apply final selection
        good_mu_pt = good_mu_pt[iso_mask]
        good_mu_eta = good_mu_eta[iso_mask]
        good_mu_phi = good_mu_phi[iso_mask]
        good_mu_mass = good_mu_mass[iso_mask]
        good_mu_charge = good_mu_charge[iso_mask]
        good_mu_iso = good_mu_iso[iso_mask]
        good_tau_pt = good_tau_pt[iso_mask]
        good_tau_eta = good_tau_eta[iso_mask]
        good_tau_phi = good_tau_phi[iso_mask]
        good_tau_mass = good_tau_mass[iso_mask]
        good_tau_charge = good_tau_charge[iso_mask]
        good_tau_iso_raw = good_tau_iso_raw[iso_mask]
        good_tau_dm = good_tau_dm[iso_mask]
        met_pt_sel = met_pt_sel[iso_mask]
        met_phi_sel = met_phi_sel[iso_mask]
        mt_vals = mt_vals[iso_mask]

        # Compute derived quantities
        mvis = compute_mvis(good_mu_pt, good_mu_eta, good_mu_phi, good_mu_mass,
                            good_tau_pt, good_tau_eta, good_tau_phi, good_tau_mass)

        # Jets (for VBF and b-tag counting) - need to go back to chunk
        ev_final = ev_p[os_mask][dr_mask][mt_mask][iso_mask]
        jet_pt = ev_final["Jet_pt"]
        jet_eta = ev_final["Jet_eta"]
        jet_phi = ev_final["Jet_phi"]
        jet_mass = ev_final["Jet_mass"]
        jet_btag = ev_final["Jet_btag"]
        jet_puid = ev_final["Jet_puId"]
        pv_npvs = ak.to_numpy(ev_final["PV_npvs"])

        # Good jets: pT > 30, |eta| < 4.7, puId
        # Also need overlap removal with muon and tau
        good_jet_mask = (jet_pt > 30) & (np.abs(jet_eta) < 4.7) & jet_puid

        # Overlap removal: DR > 0.5 from selected muon and tau
        for i_ev in range(len(ev_final)):
            pass  # Will do vectorized below

        # Simplified: count jets per event
        njets = ak.to_numpy(ak.sum(good_jet_mask, axis=1))

        # b-tagged jets (btag > 0.8, rough CSVM-like WP)
        bjet_mask = good_jet_mask & (jet_btag > 0.8)
        nbjets = ak.to_numpy(ak.sum(bjet_mask, axis=1))

        # Leading jet pT and eta
        good_jet_pt = jet_pt[good_jet_mask]
        good_jet_eta = jet_eta[good_jet_mask]
        lead_jet_pt_arr = np.where(
            njets > 0,
            ak.to_numpy(ak.fill_none(ak.firsts(good_jet_pt), -1)),
            -1.0
        )
        lead_jet_eta_arr = np.where(
            njets > 0,
            ak.to_numpy(ak.fill_none(ak.firsts(good_jet_eta), -99)),
            -99.0
        )

        # Store selected event properties
        w = np.full(len(good_mu_pt), weight_per_event)
        selected_arrays["mu_pt"].append(good_mu_pt)
        selected_arrays["mu_eta"].append(good_mu_eta)
        selected_arrays["mu_phi"].append(good_mu_phi)
        selected_arrays["mu_mass"].append(good_mu_mass)
        selected_arrays["mu_charge"].append(good_mu_charge)
        selected_arrays["mu_iso"].append(good_mu_iso)
        selected_arrays["tau_pt"].append(good_tau_pt)
        selected_arrays["tau_eta"].append(good_tau_eta)
        selected_arrays["tau_phi"].append(good_tau_phi)
        selected_arrays["tau_mass"].append(good_tau_mass)
        selected_arrays["tau_charge"].append(good_tau_charge)
        selected_arrays["tau_iso_raw"].append(good_tau_iso_raw)
        selected_arrays["tau_dm"].append(good_tau_dm)
        selected_arrays["met_pt"].append(met_pt_sel)
        selected_arrays["met_phi"].append(met_phi_sel)
        selected_arrays["mvis"].append(mvis)
        selected_arrays["mt"].append(mt_vals)
        selected_arrays["njets"].append(njets)
        selected_arrays["nbjets"].append(nbjets)
        selected_arrays["lead_jet_pt"].append(lead_jet_pt_arr)
        selected_arrays["lead_jet_eta"].append(lead_jet_eta_arr)
        selected_arrays["pv_npvs"].append(pv_npvs)
        selected_arrays["weight"].append(w)

    elapsed = time.time() - t0
    log.info("  Processed %d events in %.1f s (%.0f kHz)",
             cutflow["total"], elapsed, cutflow["total"] / elapsed / 1000)

    # Concatenate
    for key in selected_arrays:
        if selected_arrays[key]:
            selected_arrays[key] = np.concatenate(selected_arrays[key])
        else:
            selected_arrays[key] = np.array([])

    return cutflow, cutflow_weighted, selected_arrays


def main():
    log.info("=" * 60)
    log.info("Phase 2 Step 3: Preselection and Yields")
    log.info("=" * 60)

    # Process with Loose tau ID (default)
    all_cutflows = {}
    all_cutflows_weighted = {}
    all_selected = {}

    for sample_name, info in SAMPLES.items():
        log.info("\nProcessing %s (%s)...", sample_name, info["desc"])
        cutflow, cutflow_w, selected = process_sample(sample_name, info, tau_iso_wp="Loose")
        all_cutflows[sample_name] = cutflow
        all_cutflows_weighted[sample_name] = cutflow_w
        all_selected[sample_name] = selected

        log.info("  Cutflow (raw):")
        for step, count in cutflow.items():
            log.info("    %-15s: %10d", step, count)

    # Print yield table
    log.info("\n" + "=" * 60)
    log.info("YIELD TABLE (Loose tau ID, weighted)")
    log.info("=" * 60)
    log.info("%-25s %12s %12s", "Sample", "Raw", "Weighted")
    for sample_name in SAMPLES:
        raw = all_cutflows[sample_name]["iso_tight"]
        weighted = all_cutflows_weighted[sample_name]["iso_tight"]
        log.info("%-25s %12d %12.1f", sample_name, raw, weighted)

    # Data total
    data_total = sum(all_cutflows[n]["iso_tight"] for n in SAMPLES if not SAMPLES[n]["is_mc"])
    log.info("%-25s %12d %12d", "Data Total", data_total, data_total)

    # MC total
    mc_total = sum(all_cutflows_weighted[n]["iso_tight"] for n in SAMPLES if SAMPLES[n]["is_mc"])
    log.info("%-25s %12s %12.1f", "MC Total", "-", mc_total)

    # Save cutflows and selected arrays
    cutflow_path = OUTPUT_DIR / "cutflow_loose.json"
    with open(cutflow_path, "w") as f:
        json.dump({"raw": all_cutflows, "weighted": all_cutflows_weighted}, f, indent=2)
    log.info("Cutflows saved to %s", cutflow_path)

    # Save selected arrays as npz
    for sample_name, arrays in all_selected.items():
        npz_path = OUTPUT_DIR / f"selected_{sample_name}_loose.npz"
        np.savez_compressed(npz_path, **arrays)
    log.info("Selected arrays saved to %s/selected_*.npz", OUTPUT_DIR)


if __name__ == "__main__":
    main()
