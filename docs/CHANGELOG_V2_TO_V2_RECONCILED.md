# MANGAN-AI — v2 Reconciliation / Packaging Changelog

## What was wrong in the earlier package

The earlier backend ZIP contained the original backend checkpoint, while the v2 MOIL documents described additional files that were not actually in that archive. In particular, the earlier archive lacked the v2 Grade/Production reference model implementations, MOIL provider, mine routes and canonical MOIL reference data.

## What is now included

- MOIL Grade v001 reference implementation
- MOIL historical Production v001 reference implementation
- canonical MOIL site/grade/production datasets
- MOIL source workbook retained under `data/external/`
- NGDR 2022 lease GeoJSON
- `services/providers/moil_reference.py`
- `GET /mines`
- `GET /mines/{site_id}/leases`
- registry `input_mode`
- registry-driven input building for feature vectors, site references and scenarios
- explicit `pipelines/preprocessing/` layer
- model-service facade
- updated tests and model contract coverage
- reconciled API/frontend and architecture handoff documentation

## What remains intentionally DEMO

Equipment, Recovery, Blast and Weather are still DEMO simulations.

## What remains a future true-ML task

Grade spatial regression and chronological production forecasting require data and validation that are not established by the supplied MOIL package.
