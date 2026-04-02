"""Estimate timing for full selection run."""
import logging
import time
from pathlib import Path
from rich.logging import RichHandler

logging.basicConfig(level=logging.INFO, format="%(message)s",
                    handlers=[RichHandler(rich_tracebacks=True)])
log = logging.getLogger(__name__)

import uproot
import numpy as np

DATA_DIR = Path("/eos/opendata/cms/derived-data/AOD2NanoAODOutreachTool")

# Test ggH: 477K events took ~2.4s for 100K, so ~12s total
# The bottleneck is the per-event jet loop.
# DY has 30M events. Most are rejected at trigger (~16% pass = ~4.8M).
# After muon+tau: ~78K. Per-event jet loop on 78K events in ~2s? No, it
# took 2.4s for 1741 events (after tau). The jet loop is per-event.
# For DY: after trigger+muon+tau we'd have ~78K events, per-event loop
# would be slow.

# Let's benchmark: how fast is the per-event jet loop?
fpath = DATA_DIR / "GluGluToHToTauTau.root"
tree = uproot.open(fpath)["Events"]

# Read 50K events and measure how long the jet loop takes
branches = [
    "nJet", "Jet_pt", "Jet_eta", "Jet_phi", "Jet_mass", "Jet_btag", "Jet_puId",
]
import awkward as ak

ev = tree.arrays(branches, entry_stop=50000, library="ak")
t0 = time.time()

# Simulate overlap removal on all events (not just selected)
n = len(ev)
njets_arr = np.zeros(n, dtype=int)
dummy_mu_eta = np.zeros(n)
dummy_mu_phi = np.zeros(n)

for i in range(n):
    jpt = ev["Jet_pt"][i]
    if len(jpt) == 0:
        continue
    jpt_np = ak.to_numpy(jpt)
    jeta_np = ak.to_numpy(ev["Jet_eta"][i])
    jphi_np = ak.to_numpy(ev["Jet_phi"][i])
    jpuid = ak.to_numpy(ev["Jet_puId"][i])
    mask = (jpt_np > 30) & (np.abs(jeta_np) < 4.7) & jpuid
    njets_arr[i] = int(np.sum(mask))

t1 = time.time()
log.info("Per-event jet loop on %d events: %.2f s (%.1f kHz)", n, t1 - t0, n / (t1 - t0) / 1000)
log.info("But after selection, only ~2%% of events remain")

# After trigger+muon+tau selection, we'd have ~8K/477K events = 1.7%
# For DY: ~78K/30M = 0.26% remain
# So for DY: per-event loop on ~78K events
# Estimate: ~78K events / 50K * (t1-t0) seconds
rate_per_sec = n / (t1 - t0)
for sample, n_after_sel in [("ggH", 8000), ("DY", 78000),
                             ("TTbar", 50000), ("W1J", 40000),
                             ("DataB", 40000), ("DataC", 55000)]:
    est = n_after_sel / rate_per_sec
    log.info("%s: ~%d events after tau selection, jet loop ~%.1f s", sample, n_after_sel, est)
