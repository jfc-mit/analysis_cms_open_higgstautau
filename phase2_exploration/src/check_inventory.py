"""Quick check of inventory JSON."""
import json
with open("phase2_exploration/outputs/sample_inventory.json") as f:
    data = json.load(f)
for name in data:
    r = data[name]
    print(f"=== {name} ({r['num_events']} events, {r['num_branches']} branches) ===")
    for key in ["branch_PSWeight", "branch_LHEPdfWeight", "branch_LHEScaleWeight", "branch_genWeight", "branch_LHEWeight_originalXWGTUP"]:
        if key in r:
            print(f"  {key}: {r[key]}")
    for key in r:
        if key.startswith("hlt_"):
            print(f"  {key}: {r[key]}")
    if "genpart_pdgids" in r:
        print(f"  GenPart PDG IDs: {r['genpart_pdgids']}")
    if "genpart_n_higgs" in r:
        print(f"  GenPart: Higgs={r['genpart_n_higgs']}, Taus={r['genpart_n_taus']}, Muons={r['genpart_n_muons']}")
    if "tau_decay_modes" in r:
        print(f"  Tau_decayMode: {r['tau_decay_modes']}")
    if "expected_events_xsec_lumi" in r:
        print(f"  xsec*lumi={r['expected_events_xsec_lumi']:.0f}, N_gen={r['num_events']}, ratio={r['ngen_over_expected']:.3f}")
    if "genpart_status_values" in r:
        print(f"  GenPart_status values: {r['genpart_status_values']}")
    # Multiplicities
    for key in ["mult_nMuon", "mult_nTau", "mult_nJet", "mult_nGenPart"]:
        if key in r:
            print(f"  {key}: {r[key]}")
    print()
