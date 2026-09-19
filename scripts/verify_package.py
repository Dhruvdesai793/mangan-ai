from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("PYTHONPATH", str(ROOT))
sys.path.insert(0, str(ROOT))

print("== registry ==")
registry = json.loads((ROOT / "schemas/model_registry.json").read_text())
print("models:", len(registry))
print("live:", sum(v["status"] == "LIVE" for v in registry.values()))
print("demo:", sum(v["status"] == "DEMO" for v in registry.values()))

print("== preprocessing ==")
from pipelines.preprocessing.moil_reference import validate
print(json.dumps(validate(), indent=2))

print("== tests ==")
raise SystemExit(subprocess.call([sys.executable, "-m", "unittest", "discover", "-v"], cwd=ROOT))
