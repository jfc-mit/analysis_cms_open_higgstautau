"""Check GenPart content in signal sample for gen-level MET."""
import logging
from pathlib import Path
from rich.logging import RichHandler

logging.basicConfig(level=logging.INFO, format="%(message)s",
                    handlers=[RichHandler(rich_tracebacks=True)])
log = logging.getLogger(__name__)

import uproot
import awkward as ak
import numpy as np

DATA_DIR = Path("/eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool")

tree = uproot.open(DATA_DIR / "GluGluToHToTauTau.root")["Events"]

# Read first 1000 events
ev = tree.arrays(["GenPart_pdgId", "GenPart_status", "GenPart_pt",
                   "GenPart_eta", "GenPart_phi"],
                  entry_stop=1000, library="ak")

# Unique PDG IDs
all_pdgids = ak.flatten(ev["GenPart_pdgId"])
unique_ids = sorted(set(ak.to_numpy(all_pdgids)))
log.info("Unique PDG IDs: %s", unique_ids)

# Unique statuses
all_status = ak.flatten(ev["GenPart_status"])
unique_status = sorted(set(ak.to_numpy(all_status)))
log.info("Unique statuses: %s", unique_status)

# Check for neutrinos
for pdgid in [12, 14, 16]:
    mask = np.abs(ak.flatten(ev["GenPart_pdgId"])) == pdgid
    count = int(ak.sum(mask))
    log.info("PDG ID +/-%d: %d particles", pdgid, count)

# Check per event - are there neutrinos?
for i in range(min(5, len(ev))):
    pdgids = ak.to_numpy(ev["GenPart_pdgId"][i])
    statuses = ak.to_numpy(ev["GenPart_status"][i])
    pts = ak.to_numpy(ev["GenPart_pt"][i])
    log.info("\nEvent %d: %d GenPart", i, len(pdgids))
    for j in range(len(pdgids)):
        log.info("  GenPart[%d]: pdgId=%d, status=%d, pT=%.2f",
                 j, pdgids[j], statuses[j], pts[j])

# Check neutrinos with any status
for status_val in unique_status:
    for pdgid in [12, 14, 16]:
        mask_ev = ev["GenPart_pdgId"]
        nu_mask = (np.abs(mask_ev) == pdgid) & (ev["GenPart_status"] == status_val)
        count = int(ak.sum(ak.sum(nu_mask, axis=1)))
        if count > 0:
            log.info("Status %d, PDG +/-%d: %d particles (in 1000 events)",
                     status_val, pdgid, count)
