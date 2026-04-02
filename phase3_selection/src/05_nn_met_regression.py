"""
Phase 3 Step 5: NN MET Regression [D1, D13].

NEGATIVE RESULT: Gen-level neutrinos are not available in the reduced NanoAOD
GenPart collection. The NanoAOD reduction tool stripped neutrinos entirely.

Without gen-level neutrino information, there is no truth target to train an
NN MET regressor. This approach (c) is dropped per [D13]:
"If >15% MET resolution improvement is not met by end of Phase 3,
approach (c) is dropped."

The criterion cannot be evaluated because the necessary gen-level information
is missing. This is documented as a negative result arising from the
data format limitation.
"""
import logging
import json
from pathlib import Path

from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"


def main():
    log.info("=" * 60)
    log.info("Phase 3 Step 5: NN MET Regression Assessment")
    log.info("=" * 60)

    log.info("\nGenPart investigation:")
    log.info("  Available PDG IDs in GenPart: {-15, -13, -11, 11, 13, 15}")
    log.info("  Missing: neutrinos (pdgId 12, 14, 16)")
    log.info("  The NanoAOD reduction tool stripped all neutrinos from GenPart.")
    log.info("  Only tau leptons (pdgId +/-15), muons (pdgId +/-13),")
    log.info("  and electrons/positrons (pdgId +/-11) are stored.")

    log.info("\nConsequence:")
    log.info("  Gen-level MET cannot be computed from GenPart neutrinos.")
    log.info("  The NN MET regression approach requires gen-level MET")
    log.info("  as training target. Without it, the approach is infeasible.")

    log.info("\n[D13] Decision: Approach (c) DROPPED")
    log.info("  Criterion: >15%% MET resolution improvement on MC test set")
    log.info("  Status: CANNOT EVALUATE (no gen-level neutrino information)")
    log.info("  Action: Document as negative result, drop approach (c)")

    results = {
        "approach": "NN-regressed MET (approach c)",
        "status": "DROPPED",
        "reason": "Gen-level neutrinos not available in reduced NanoAOD GenPart. "
                  "Only PDG IDs {-15, -13, -11, 11, 13, 15} found. "
                  "No training target for MET regression.",
        "d13_criterion": ">15% MET resolution improvement on MC test set",
        "d13_evaluation": "Cannot evaluate - no gen-level neutrino truth",
        "gen_pdg_ids_found": [-15, -13, -11, 11, 13, 15],
        "gen_pdg_ids_missing": [12, -12, 14, -14, 16, -16],
    }

    with open(OUTPUT_DIR / "nn_met_regression_results.json", "w") as f:
        json.dump(results, f, indent=2)
    log.info("\nResults saved to nn_met_regression_results.json")


if __name__ == "__main__":
    main()
