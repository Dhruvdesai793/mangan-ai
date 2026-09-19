# MANGAN-AI — Model/Data + Preprocessing Handoff v3

## Why preprocessing is explicit

The model layer must consume canonical, validated inputs. API code is not the preprocessing layer.

```text
Raw source
  ↓
Ingestion
  ↓
Validation
  ↓
Preprocessing
  ↓
Feature/reference layer
  ↓
Model input
  ↓
predict()
```

## Current MOIL preprocessing

The source workbook is:

```text
data/external/MOIL_v12.xlsx
```

The runtime canonical outputs are:

```text
data/external/moil_site_catalog.csv
data/external/moil_grade_reference.csv
data/external/moil_production_reference.csv
```

The lease geometry is:

```text
data/external/geometries/ngdr_moil_major_mining_leases_2022.geojson
```

The manifest is:

```text
data/external/moil_reference_manifest.json
```

Validation utility:

```text
pipelines/preprocessing/moil_reference.py
```

Run:

```bash
python pipelines/preprocessing/moil_reference.py
```

## Identity rules

Canonical runtime site IDs are the 10 verified operational site IDs used by the reference datasets:

```text
MOIL-BAL-001
MOIL-UKW-001
MOIL-TIR-001
MOIL-SIT-001
MOIL-CHI-001
MOIL-DON-001
MOIL-KAN-001
MOIL-MAN-001
MOIL-GUM-001
MOIL-BEL-001
```

Plant-only and user-target records are not included in the runtime mine selector.

## Grade preprocessing

Source tabs:

```text
USER_SOURCE_Assays
USER_SOURCE_Ore Products
```

Canonicalization includes:

- stable site ID
- assay/product identifiers
- numeric Mn/Fe/SiO₂/P/MnO₂ fields where supplied
- grade interval from product range
- source/year/provenance
- explicit product-grade verification status

No target-derived spatial feature is created.

## Production preprocessing

Source tab:

```text
HISTORICAL_MOIL_2012
```

Canonicalization includes:

- site ID normalization
- historical year
- production tonnes
- grade label
- reserve/resource values
- interpretation status

The grouped Sitapatore/Sukli measurement is kept as a grouped interpretation rather than being represented as an independent mine-only observation.

## Prospectivity preprocessing

Prospectivity retains the existing feature pipeline and frozen model contract:

```text
Sentinel-2 bands
NDVI
NDMI
Elevation
Slope
Curvature
Geology class
```

The API must receive these as an explicit validated feature vector. It must not invent them from a mine profile or grade reference.

## Future true-ML preprocessing

### Grade v002

```text
assays
 + geology
 + terrain
 + satellite
 + spatial context
       ↓
as-of / leakage audit
       ↓
spatial train/validation/test split
       ↓
feature pipeline
       ↓
trained artifact
```

### Production v002

```text
production history
 + lags/rolling features
 + operational state
 + material quality
 + weather forecast available at origin
       ↓
chronological split
       ↓
forecast model
```

The audit specifically warns against training on future observed rainfall and then calling the result forecast-validated.
