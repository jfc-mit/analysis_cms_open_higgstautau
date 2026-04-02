"""
Phase 4b Step 1: Select 10% data subsample.

Uses a fixed random seed (42) for reproducibility.
Selects 10% of data events from Run2012B and Run2012C.
Saves subsampled arrays for downstream use.
"""
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
OUT = Path("phase4_inference/4b_partial/outputs")
OUT.mkdir(parents=True, exist_ok=True)

DATA_SAMPLES = ["Run2012B_TauPlusX", "Run2012C_TauPlusX"]
FRACTION = 0.10
SEED = 42


def subsample_npz(input_path, output_path, rng, fraction=0.10):
    """Load an npz file, select a random fraction, save."""
    d = np.load(input_path, allow_pickle=True)
    arrays = {k: d[k] for k in d.keys()}

    n_total = len(arrays["weight"])
    mask = rng.random(n_total) < fraction
    n_selected = mask.sum()

    sub = {k: v[mask] for k, v in arrays.items()}
    np.savez_compressed(output_path, **sub)

    log.info(
        f"  {input_path.name}: {n_selected}/{n_total} events "
        f"({100.0 * n_selected / n_total:.2f}%)"
    )
    return n_total, n_selected


def main():
    log.info("Selecting 10% data subsample (seed=42)")

    rng = np.random.RandomState(SEED)

    summary = {}

    for tag in DATA_SAMPLES:
        summary[tag] = {}
        for region in ["os_sr", "ss_sr"]:
            # Main arrays
            in_path = P3 / f"p3_{tag}_{region}.npz"
            out_path = OUT / f"p3_{tag}_{region}_10pct.npz"
            n_total, n_sel = subsample_npz(in_path, out_path, rng, FRACTION)
            summary[tag][region] = {
                "n_total": int(n_total),
                "n_selected": int(n_sel),
            }

            # NN scores
            nn_in = P3 / f"p3_{tag}_{region}_nn_score.npz"
            nn_out = OUT / f"p3_{tag}_{region}_nn_score_10pct.npz"
            # Must use the SAME mask — reload and apply
            d_main = np.load(in_path, allow_pickle=True)
            n_main = len(d_main["weight"])
            # Regenerate the same mask
            rng2 = np.random.RandomState(SEED)
            # Need to consume the same random numbers as above
            # to get the same mask. But we used a single rng above
            # which advances state across samples/regions.
            # Solution: save the masks explicitly.

    # Start over with a cleaner approach: generate all masks first, then apply
    log.info("\n--- Generating masks for all files ---")
    rng = np.random.RandomState(SEED)
    masks = {}

    for tag in DATA_SAMPLES:
        for region in ["os_sr", "ss_sr"]:
            in_path = P3 / f"p3_{tag}_{region}.npz"
            d = np.load(in_path, allow_pickle=True)
            n = len(d["weight"])
            mask = rng.random(n) < FRACTION
            masks[(tag, region)] = mask
            log.info(f"  {tag} {region}: {mask.sum()}/{n} events")

    # Now apply masks to all files
    log.info("\n--- Applying masks ---")
    total_os_full = 0
    total_os_sel = 0
    total_ss_full = 0
    total_ss_sel = 0

    for tag in DATA_SAMPLES:
        for region in ["os_sr", "ss_sr"]:
            mask = masks[(tag, region)]

            # Main arrays
            in_path = P3 / f"p3_{tag}_{region}.npz"
            out_path = OUT / f"p3_{tag}_{region}_10pct.npz"
            d = np.load(in_path, allow_pickle=True)
            sub = {k: d[k][mask] for k in d.keys()}
            np.savez_compressed(out_path, **sub)
            log.info(f"  Saved {out_path.name}: {mask.sum()} events")

            # NN scores
            nn_in = P3 / f"p3_{tag}_{region}_nn_score.npz"
            nn_out = OUT / f"p3_{tag}_{region}_nn_score_10pct.npz"
            nn_d = np.load(nn_in, allow_pickle=True)
            nn_sub = {k: nn_d[k][mask] for k in nn_d.keys()}
            np.savez_compressed(nn_out, **nn_sub)

            # Collinear mass
            col_in = P3 / f"p3_{tag}_{region}_collinear.npz"
            col_out = OUT / f"p3_{tag}_{region}_collinear_10pct.npz"
            col_d = np.load(col_in, allow_pickle=True)
            col_sub = {k: col_d[k][mask] for k in col_d.keys()}
            np.savez_compressed(col_out, **col_sub)

            if "os" in region:
                total_os_full += len(d["weight"])
                total_os_sel += mask.sum()
            else:
                total_ss_full += len(d["weight"])
                total_ss_sel += mask.sum()

    log.info(f"\n=== Summary ===")
    log.info(f"OS SR: {total_os_sel}/{total_os_full} "
             f"({100.0 * total_os_sel / total_os_full:.2f}%)")
    log.info(f"SS SR: {total_ss_sel}/{total_ss_full} "
             f"({100.0 * total_ss_sel / total_ss_full:.2f}%)")
    log.info(f"Total: {total_os_sel + total_ss_sel}/{total_os_full + total_ss_full}")


if __name__ == "__main__":
    main()
