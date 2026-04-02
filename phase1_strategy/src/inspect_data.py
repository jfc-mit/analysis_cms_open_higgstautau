"""Inspect the CMS Open Data NanoAOD files: branch structure, event counts, basic kinematics."""
import logging
from pathlib import Path

from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

import uproot
import numpy as np

DATA_DIR = Path("/eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool")

SAMPLES = {
    "GluGluToHToTauTau": "ggH signal",
    "VBF_HToTauTau": "VBF signal",
    "DYJetsToLL": "Drell-Yan",
    "TTbar": "ttbar",
    "W1JetsToLNu": "W+1jet",
    "W2JetsToLNu": "W+2jets",
    "W3JetsToLNu": "W+3jets",
    "Run2012B_TauPlusX": "Data Run2012B",
    "Run2012C_TauPlusX": "Data Run2012C",
}


def main():
    log.info("=== CMS Open Data NanoAOD Inspection ===")

    for sample_name, description in SAMPLES.items():
        fpath = DATA_DIR / f"{sample_name}.root"
        if not fpath.exists():
            log.warning("File not found: %s", fpath)
            continue

        f = uproot.open(fpath)
        tree = f["Events"]
        n_events = tree.num_entries
        log.info("%s (%s): %d events", sample_name, description, n_events)

        if sample_name == "GluGluToHToTauTau":
            log.info("  Branches:")
            for b in sorted(tree.keys()):
                log.info("    %s", b)

    # Detailed check of branch types for signal sample
    log.info("\n=== Detailed branch check (GluGluToHToTauTau) ===")
    f = uproot.open(DATA_DIR / "GluGluToHToTauTau.root")
    tree = f["Events"]

    # Read a small sample to check ranges
    branches_to_check = [
        "nMuon", "Muon_pt", "Muon_eta", "Muon_phi", "Muon_charge",
        "Muon_pfRelIso03_all", "Muon_pfRelIso04_all", "Muon_tightId",
        "Muon_dxy", "Muon_dz",
        "nTau", "Tau_pt", "Tau_eta", "Tau_phi", "Tau_charge",
        "Tau_decayMode", "Tau_relIso_all",
        "Tau_idDecayMode", "Tau_idIsoRaw", "Tau_idIsoVLoose",
        "Tau_idIsoLoose", "Tau_idIsoMedium", "Tau_idIsoTight",
        "Tau_idAntiEleLoose", "Tau_idAntiEleMedium", "Tau_idAntiEleTight",
        "Tau_idAntiMuLoose", "Tau_idAntiMuTight",
        "nJet", "Jet_pt", "Jet_eta", "Jet_phi", "Jet_mass", "Jet_btag", "Jet_puId",
        "MET_pt", "MET_phi", "MET_sumet", "MET_significance",
        "MET_CovXX", "MET_CovXY", "MET_CovYY",
        "nGenPart", "GenPart_pt", "GenPart_eta", "GenPart_phi",
        "GenPart_mass", "GenPart_pdgId", "GenPart_status",
        "PV_npvs",
        "HLT_IsoMu17_eta2p1_LooseIsoPFTau20",
        "HLT_IsoMu24_eta2p1", "HLT_IsoMu24",
    ]

    available = tree.keys()
    for b in branches_to_check:
        if b in available:
            log.info("  FOUND: %s", b)
        else:
            log.info("  MISSING: %s", b)

    # Check a few basic distributions on a small sample
    log.info("\n=== Quick kinematic check (first 10000 events of ggH) ===")
    arrays = tree.arrays(["nMuon", "nTau", "nJet", "MET_pt", "PV_npvs"],
                         entry_stop=10000, library="np")

    for key, arr in arrays.items():
        if hasattr(arr, '__len__') and not isinstance(arr, np.ndarray):
            # Jagged array
            flat = np.concatenate([np.asarray(a) for a in arr]) if len(arr) > 0 else np.array([])
            log.info("  %s: mean=%.2f, min=%s, max=%s", key, np.mean(flat), np.min(flat), np.max(flat))
        else:
            log.info("  %s: mean=%.2f, min=%s, max=%s", key, np.mean(arr), np.min(arr), np.max(arr))


if __name__ == "__main__":
    main()
