"""Interactive one-time Earth Engine OAuth bootstrap."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import get_settings


if __name__ == "__main__":
    import ee
    settings = get_settings()
    if settings.gee_auth_method.lower() != "oauth":
        raise SystemExit("This helper supports GEE_AUTH_METHOD=oauth only")
    ee.Authenticate()
    ee.Initialize(project=settings.gee_project_id)
    print(f"Earth Engine authentication verified for project {settings.gee_project_id}.")
