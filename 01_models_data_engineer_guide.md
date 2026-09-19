# MANGAN-AI — Models & Data Engineering Guide
**Owner of this scope:** Nishant (Team 3) — models, data pipelines, model registry
**Consumed by:** the API/Frontend engineer (see the companion document)
**Governing document:** Audit 3.4 final architecture — nothing below contradicts it

---

## 0. What this document is for

This is the build manual for everything under `models/`, `pipelines/`, `data/`, `scenarios/`, and the shared `schemas/`. It tells you, in order, which files and folders to create, what goes in each, and how the whole thing stays consistent so that:

1. Tomorrow's demo runs on one real model (prospectivity) plus several honestly-labeled simulation modules.
2. When Team 1 and Team 2 eventually deliver real verified data, you swap it in **without changing the contract** the API/frontend depends on.
3. Nothing you hand off requires the API/frontend engineer to know anything about ML, GEE, or spatial validation — they only ever talk to a fixed interface.

Do not fabricate accuracy numbers for demo modules. Do not claim synthetic data is MOIL data. Every model output carries a `status` field (`LIVE`, `DEMO`, or `UNAVAILABLE`) and that field is the single source of truth for what's real.

---

## 1. Architecture recap (so every file you create has a reason)

```
DATA SOURCES (public / MOIL / synthetic)
        ↓
DATA CONTRACT (schema validation)
        ↓
VALIDATION LAYER (Team 2's job today, your fallback pipeline until then)
        ↓
FEATURE LAYER (spatial features, per model)
        ↓
SPECIALIST MODELS  → prospectivity (LIVE), grade/production/equipment/
                      recovery/blast/weather (DEMO, simulation-backed)
        ↓
ORCHESTRATOR (API/frontend owns this — calls your models uniformly)
        ↓
DECISION ENGINE → OPTIMIZER → API → FRONTEND (all API/frontend scope)
```

Your job stops at "specialist models return a `ModelResult`." Everything after the orchestrator is not your concern — don't build it, don't duplicate it.

---

## 2. Full repository tree (your folders marked, everyone else's for context)

```
mangan-ai/
├── apps/frontend/                        [API/FRONTEND — not yours]
├── services/                             [API/FRONTEND — not yours]
│   ├── api/
│   ├── orchestrator/
│   ├── decision_engine/
│   └── optimization/
│
├── models/                               ★ YOURS ★
│   ├── prospectivity/
│   │   └── v001/
│   │       ├── model.pkl
│   │       ├── predict.py
│   │       ├── feature_schema.json
│   │       ├── config.yaml
│   │       ├── metrics.json
│   │       ├── training_metadata.json
│   │       └── README.md
│   ├── grade/demo_v001/{predict.py, config.yaml, README.md}
│   ├── production/demo_v001/{predict.py, config.yaml, README.md}
│   ├── equipment/demo_v001/{predict.py, config.yaml, README.md}
│   ├── recovery/demo_v001/{predict.py, config.yaml, README.md}
│   ├── blast/demo_v001/{predict.py, config.yaml, README.md}
│   └── weather/demo_v001/{predict.py, config.yaml, README.md}
│
├── pipelines/                            ★ YOURS ★
│   ├── ingestion/
│   │   ├── schema_validation.py
│   │   └── quarantine.py
│   ├── geospatial/
│   │   ├── gee_extraction.py
│   │   ├── feature_engineering.py
│   │   └── spatial_validation.py
│   └── training/prospectivity/
│       ├── train_baseline.py
│       ├── train_lr.py
│       ├── train_rf.py
│       ├── train_xgb.py
│       └── evaluate_spatial_cv.py
│
├── data/                                 ★ YOURS ★
│   ├── public/                           (raw public geology/satellite/occurrence pulls)
│   ├── prospectivity/
│   │   ├── raw/
│   │   ├── processed/
│   │   └── verified/                     (this is where Team 2's output lands, once it exists)
│   ├── synthetic/
│   │   ├── mine_demo.csv
│   │   ├── production_demo.csv
│   │   ├── equipment_demo.csv
│   │   ├── recovery_demo.csv
│   │   ├── blast_demo.csv
│   │   └── weather_demo.csv
│   └── external/.gitkeep
│
├── scenarios/                            ★ YOURS ★ (consumed by frontend)
│   ├── scenario_01_normal.json
│   ├── scenario_02_rainfall.json
│   └── scenario_03_equipment_failure.json
│
├── schemas/                              ★ SHARED — you create, both sides read ★
│   ├── prediction_contract.json
│   ├── model_registry.json
│   └── ingestion_contracts/
│       ├── team1_parquet_schema.json
│       └── team2_verified_schema.json
│
├── configs/
│   ├── app.yaml                          [API/FRONTEND]
│   ├── models.yaml                       ★ YOURS ★
│   └── demo.yaml                         ★ SHARED ★
│
├── tests/
│   ├── unit/                             ★ YOURS ★
│   └── model_contract/                   ★ SHARED ★
│
├── docs/
│   ├── model_cards/{prospectivity,grade,production,...}.md   ★ YOURS ★
│   ├── data_card.md                      ★ YOURS ★
│   ├── architecture.md                   [SHARED — write together]
│   ├── demo_disclosure.md                [SHARED — write together]
│   └── judge_qa.md                       [SHARED — write together]
│
├── scripts/
│   ├── generate_demo_data.py             ★ YOURS ★
│   ├── seed_demo_scenario.py             ★ YOURS ★
│   └── register_models.py                ★ YOURS ★
│
├── requirements.txt
├── .env.example
├── docker-compose.yml
├── README.md
└── SECURITY.md
```

Create the skeleton first — every folder above, even empty ones with a `.gitkeep` — before writing a single model. This is what lets the API/frontend engineer start wiring the orchestrator against stub files on day one instead of waiting on you.

---

## 3. Build order (do this in sequence)

### Step 1 — Repo skeleton
Create every directory above. Add a one-line `README.md` stub in each `models/*/` folder so the tree isn't empty. Commit this first — it's the map the other engineer works from.

### Step 2 — Data contracts (before any pipeline code)
Write these three files. They are what makes Team 1/Team 2 replaceable later without breaking anything downstream.

`schemas/ingestion_contracts/team1_parquet_schema.json` — the exact columns Team 1's Parquet must have: coordinates, Sentinel-2 bands, NDVI, NDMI, elevation, slope, curvature, geology class, label/occurrence flag, spatial metadata (tile/grid id, acquisition date). Include dtype and nullability for every column.

`schemas/ingestion_contracts/team2_verified_schema.json` — same columns plus verification metadata: `leakage_check_passed`, `duplicate_check_passed`, `spatial_fold_id`, `verification_report_id`, `verified_timestamp`.

`schemas/prediction_contract.json` — the single output shape **every** model in this repo must return, real or demo:

```json
{
  "model_id": "string",
  "model_version": "string",
  "status": "LIVE | DEMO | UNAVAILABLE",
  "prediction": "any | null",
  "uncertainty": "number | null",
  "data_source": "string",
  "prediction_timestamp": "ISO-8601 string",
  "reason": "string | null  (required when status = UNAVAILABLE)"
}
```

Mirror this as a Pydantic model in `pipelines/` (or a shared `schemas/contracts.py`) so both your training code and the demo modules import the same class instead of hand-rolling dicts.

### Step 3 — Public-data fallback pipeline (this is what de-risks you today)
Build `pipelines/ingestion/schema_validation.py` and `pipelines/geospatial/*` so the prospectivity pipeline has **two entry points**, both producing a dataframe that matches `team2_verified_schema.json`:

```
Route A: data/public/  → schema_validation → feature_engineering → spatial_validation → data/prospectivity/processed/
Route B: data/prospectivity/verified/ (Team 2's real output, when it exists) → same downstream code
```

Both routes must emit the *same schema*. This is the entire point — your model training code never needs to know which route produced its input. If Team 1/Team 2 are late tomorrow, Route A alone gets you a working LIVE model. When Team 2 delivers, you just point at Route B and retrain — no code changes elsewhere.

### Step 4 — Train the real prospectivity model
In `pipelines/training/prospectivity/`, run in order and keep every intermediate result:
1. `train_baseline.py` — prevalence/geology-type baseline
2. `train_lr.py`, `train_rf.py`, `train_xgb.py`
3. `evaluate_spatial_cv.py` — spatial group k-fold, **not** a random split; also run an ablation (features on/off) and a robustness check

Freeze the best model. Package it into `models/prospectivity/v001/`:
- `model.pkl` — the frozen artifact
- `feature_schema.json` — exact input feature names, order, dtypes
- `config.yaml` — preprocessing steps, thresholds
- `metrics.json` — spatial-CV metrics only (never a random-split number presented as final)
- `training_metadata.json` — training date, data version, algorithm, hyperparameters, geographic scope
- `README.md` — plain-language model card
- `predict.py` — exposes one function:

```python
def predict(input: dict) -> ModelResult:
    # loads model.pkl once (cache at module load), validates input
    # against feature_schema.json, returns a ModelResult with status="LIVE"
```

This `predict(input) -> ModelResult` signature is the contract every model folder implements — real or demo. The orchestrator (API/frontend side) never imports `model.pkl` directly; it only ever calls `predict()`.

### Step 5 — Demo/simulation models
For `grade`, `production`, `equipment`, `recovery`, `blast`, `weather`: each gets a `demo_vXXX/predict.py` with the same signature, returning `status="DEMO"` and `data_source="SYNTHETIC_SCENARIO"`. These are **not** ML models — they're small, honest functions (rule-based + randomized-but-bounded) that read from `data/synthetic/*.csv` or the active scenario file and return a plausible, internally-consistent number. Do not attach a fabricated accuracy metric to any of these.

Critical: make the six demo outputs tell **one coherent story**, not six independent random numbers. Build this by writing `scripts/generate_demo_data.py` to generate correlated synthetic data for a single fictional "Mine A" scenario (e.g., if the scenario says heavy rainfall, equipment availability drops, which drops production, which raises shortfall risk). Save the finished narrative as the three files in `scenarios/`.

### Step 6 — Model registry
Write `schemas/model_registry.json`. This is the file the orchestrator reads to know what exists and what to call:

```json
{
  "prospectivity": {"version": "v001", "status": "LIVE",  "type": "ML",         "source": "PUBLIC_DATA"},
  "grade":         {"version": "demo_v001", "status": "DEMO", "type": "SIMULATION"},
  "production":    {"version": "demo_v001", "status": "DEMO", "type": "SIMULATION"},
  "equipment":     {"version": "demo_v001", "status": "DEMO", "type": "SIMULATION"},
  "recovery":      {"version": "demo_v001", "status": "DEMO", "type": "SIMULATION"},
  "blast":         {"version": "demo_v001", "status": "DEMO", "type": "SIMULATION"},
  "weather":       {"version": "demo_v001", "status": "DEMO", "type": "SIMULATION"}
}
```

`scripts/register_models.py` should regenerate this file automatically by scanning `models/*/*/config.yaml` — don't hand-maintain it once it exists, or it will drift from reality.

### Step 7 — Model-contract tests
In `tests/model_contract/`, write one test that imports every `predict.py` under `models/`, calls it with a fixture input, and asserts the output matches `prediction_contract.json` exactly (right keys, right types, `status` is one of the three allowed values, `reason` present when `UNAVAILABLE`). This is what stops a broken demo module from crashing the whole orchestrator during the live demo.

### Step 8 — Documentation handoff
- `docs/model_cards/*.md` — one per model, plain language, states LIVE or DEMO up front
- `docs/data_card.md` — what data exists, what's public, what's synthetic, what's pending from Team 1/2

---

## 4. Exactly what you hand to the API/frontend engineer

Once the above exists, they need only these paths — nothing else, no ML knowledge required:

1. `schemas/model_registry.json`
2. `schemas/prediction_contract.json`
3. `models/<model_name>/<version>/predict.py` (importable, same signature everywhere)
4. `scenarios/*.json`
5. `docs/model_cards/*.md` (for the judge Q&A / "model trace" panel)

Tell them: "call `predict(input)` on whichever model the registry lists — you never touch `.pkl` files or training code directly."

---

## 5. When Team 1 / Team 2 actually deliver data

1. Team 1's real Parquet lands in `data/prospectivity/raw/` — run it through `schema_validation.py` against `team1_parquet_schema.json`. Anything failing goes to `pipelines/ingestion/quarantine.py`, not silently dropped.
2. Team 2's verified output lands in `data/prospectivity/verified/` — validate against `team2_verified_schema.json`.
3. Re-run `pipelines/training/prospectivity/` Route B instead of Route A.
4. Freeze as `models/prospectivity/v002/` — **do not overwrite v001**. Keep the old version archived.
5. Update `schemas/model_registry.json` (via `register_models.py`) to point to v002.
6. Nothing in `services/` or `apps/` changes. That's the entire reason this structure exists.

The same swap procedure applies later for grade/production/equipment/etc. once their real data sources exist — `demo_v001` becomes `v001`, `status` flips from `DEMO` to `LIVE`, contract stays identical.

---

## 6. Non-negotiables (repeat before you present)

- Never report a random-split accuracy as your headline metric — spatial CV only.
- Never label synthetic output as MOIL-derived.
- Every model, real or fake, returns `status`. If something can't run, return `UNAVAILABLE` with a `reason` — never fabricate a number to avoid an empty field.
- `predict()` signature is identical across every model folder. This uniformity is what you'll point to when a judge asks about scalability.
