# MANGAN-AI Security Notes

This repository contains a prototype backend boundary, not an enterprise security implementation.

## Implemented prototype controls

- Models can only be imported through `schemas/model_registry.json`; HTTP requests never provide an import path.
- Scenario filenames are restricted to existing JSON files under `scenarios/`.
- Prospectivity feature inputs have bounded numeric ranges and reject unknown fields.
- Request IDs are generated or validated and returned in `X-Request-ID`.
- Prediction endpoints use an in-process rate limiter.
- CORS is restricted to configured frontend origins.
- Logs are structured and do not include raw feature payloads by default.
- Request body size is bounded by middleware.

## Prototype role concept

The application may be presented with the following deployment roles:

- Exploration Geologist
- Operations User
- Management
- Administrator

These are architectural role labels only; this checkpoint does **not** implement enterprise authentication or authorization.

## Secrets

Real secrets belong in environment variables or a deployment secret manager. Never commit `.env` or real API keys.

## Deployment hardening still required

Production deployment would need institutional authentication/authorization, secret management, network policy, audit retention, dependency scanning, TLS termination, persistent rate limiting, and security review.
