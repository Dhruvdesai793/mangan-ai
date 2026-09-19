# Backend Security Boundary

The backend prototype intentionally establishes a narrow trust boundary:

1. API requests provide data, not code paths.
2. `ModelRegistry` loads the repository-owned registry and validates every entry.
3. The trusted importer only resolves modules beneath `models/` recorded in that registry.
4. Model failures are contained as `UNAVAILABLE` `ModelResult` objects.
5. Scenario access is confined to known repository scenario files.
6. Request IDs, structured logs, CORS restrictions, body-size limits, and an in-process prediction rate limiter are enabled.

The role labels `Exploration Geologist`, `Operations User`, `Management`, and `Administrator` describe the intended authorization model but are not enterprise IAM in this prototype.
