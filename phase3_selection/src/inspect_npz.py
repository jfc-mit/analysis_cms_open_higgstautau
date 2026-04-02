"""Inspect the Phase 2 npz files to understand available arrays."""
import numpy as np
import sys

files = [
    "phase2_exploration/outputs/selected_GluGluToHToTauTau_loose.npz",
    "phase2_exploration/outputs/selected_Run2012B_TauPlusX_loose.npz",
]

for fpath in files:
    print(f"\n=== {fpath} ===")
    d = np.load(fpath, allow_pickle=True)
    print(f"Keys: {sorted(d.files)}")
    for k in sorted(d.files):
        arr = d[k]
        info = f"  {k}: shape={arr.shape}, dtype={arr.dtype}"
        if arr.ndim == 1 and arr.size > 0:
            info += f", min={arr.min():.4f}, max={arr.max():.4f}, mean={arr.mean():.4f}"
        elif arr.ndim == 2 and arr.size > 0:
            info += f", min={arr.min():.4f}, max={arr.max():.4f}"
        print(info)
