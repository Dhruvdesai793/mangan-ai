# MANGAN-AI — Current Model Live Status

| ID | Version | Status | Type | Source | Scope |
|---|---|---|---|---|---|
| prospectivity | v001 | LIVE | ML | `PUBLIC_DATA_SYNTHETIC_FALLBACK` | Existing frozen ML model |
| grade | v001 | LIVE | REFERENCE | `MOIL_VERIFIED_PRODUCT_ASSAYS` | Product-grade reference, not spatial in-situ prediction |
| production | v001 | LIVE | REFERENCE | `MOIL_HISTORICAL_2012` | Historical FY2012 reference, not future forecast |
| equipment | demo_v001 | DEMO | SIMULATION | `SYNTHETIC_SCENARIO` | Synthetic scenario |
| recovery | demo_v001 | DEMO | SIMULATION | `SYNTHETIC_SCENARIO` | Synthetic scenario |
| blast | demo_v001 | DEMO | SIMULATION | `SYNTHETIC_SCENARIO` | Synthetic scenario |
| weather | demo_v001 | DEMO | SIMULATION | `SYNTHETIC_SCENARIO` | Synthetic scenario |

### Important distinction

`LIVE` means the implementation is repository-owned and available through the production contract. It does not mean every LIVE component is a scientifically validated predictive ML model.

The only current `LIVE` ML component is Prospectivity v001.
