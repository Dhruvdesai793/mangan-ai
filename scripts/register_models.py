"""
Regenerates schemas/model_registry.json by scanning models/*/*/config.yaml.
Never hand-edit model_registry.json -- run this instead, or it will drift
from what actually exists on disk.
"""
import yaml, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / "models"


def scan() -> dict:
    registry = {}
    for model_dir in sorted(MODELS_DIR.iterdir()):
        if not model_dir.is_dir() or model_dir.name.startswith("_"):
            continue
        versions = [v for v in model_dir.iterdir() if v.is_dir()]
        if not versions:
            continue
        # prefer a non-demo (real) version if present, else the demo folder
        chosen = sorted(versions, key=lambda v: v.name.startswith("demo"))[0]
        cfg_path = chosen / "config.yaml"
        if not cfg_path.exists():
            continue
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f)
        registry[model_dir.name] = {
            "version": cfg.get("version", chosen.name),
            "status": cfg.get("status", "UNAVAILABLE"),
            "type": cfg.get("type", "ML" if "demo" not in chosen.name else "SIMULATION"),
            "source": cfg.get("data_source_label", cfg.get("note", "")),
            "predict_module": f"models.{model_dir.name}.{chosen.name}.predict",
            "input_mode": cfg.get("input_mode", "scenario"),
        }
    return registry


if __name__ == "__main__":
    reg = scan()
    out_path = ROOT / "schemas" / "model_registry.json"
    with open(out_path, "w") as f:
        json.dump(reg, f, indent=2)
    print(json.dumps(reg, indent=2))
    print("wrote ->", out_path)
