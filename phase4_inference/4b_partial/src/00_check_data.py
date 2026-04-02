"""Check data file contents and event counts."""
import logging
import numpy as np
from pathlib import Path
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

P3 = Path("phase3_selection/outputs")

for tag in ["Run2012B_TauPlusX", "Run2012C_TauPlusX"]:
    for region in ["os_sr", "ss_sr"]:
        d = np.load(P3 / f"p3_{tag}_{region}.npz", allow_pickle=True)
        log.info(f"{tag} {region}: {len(d['weight'])} events, keys={list(d.keys())}")

# Also check nn_score and collinear files
for tag in ["Run2012B_TauPlusX", "Run2012C_TauPlusX"]:
    for region in ["os_sr", "ss_sr"]:
        nn = np.load(P3 / f"p3_{tag}_{region}_nn_score.npz", allow_pickle=True)
        log.info(f"{tag} {region} nn_score: {len(nn['nn_score'])} entries")
        col = np.load(P3 / f"p3_{tag}_{region}_collinear.npz", allow_pickle=True)
        log.info(f"{tag} {region} collinear: {len(col['m_col'])} entries")
