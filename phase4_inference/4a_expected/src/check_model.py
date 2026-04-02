"""Quick check of the NN model structure."""
import pickle
import json
import numpy as np

model_data = pickle.load(open("phase3_selection/outputs/nn_discriminant_model.pkl", "rb"))
print("Type:", type(model_data))

if isinstance(model_data, dict):
    print("Keys:", list(model_data.keys()))
    for k, v in model_data.items():
        if isinstance(v, np.ndarray):
            print(f"  {k}: array shape={v.shape}")
        elif isinstance(v, list):
            print(f"  {k}: list len={len(v)}, first={v[:3]}")
        elif hasattr(v, "__class__"):
            print(f"  {k}: {type(v).__name__}")
        else:
            print(f"  {k}: {v}")

    # Check if there's a model inside
    if "model" in model_data:
        m = model_data["model"]
        print("\nModel type:", type(m))
        if hasattr(m, "n_features_in_"):
            print("N features:", m.n_features_in_)
        if hasattr(m, "hidden_layer_sizes"):
            print("Hidden layers:", m.hidden_layer_sizes)
        if hasattr(m, "feature_names_in_"):
            print("Feature names:", list(m.feature_names_in_))

# Also check NN results JSON
with open("phase3_selection/outputs/nn_discriminant_results.json") as f:
    nn_res = json.load(f)
print("\nNN results keys:", list(nn_res.keys()))
for k, v in nn_res.items():
    if isinstance(v, list):
        print(f"  {k}: {v[:5]}...")
    elif isinstance(v, dict):
        print(f"  {k}: {v}")
    else:
        print(f"  {k}: {v}")
