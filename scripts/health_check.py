"""Developer/demo health check for the MANGAN-AI API."""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request


def get_json(url: str) -> tuple[int, dict]:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=10) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    base = args.url.rstrip("/")

    try:
        status, health = get_json(f"{base}/health")
        if status != 200 or health.get("status") != "ok":
            raise RuntimeError(f"unexpected /health response: {status} {health}")

        status, mines = get_json(f"{base}/mines")
        if status != 200 or not mines:
            raise RuntimeError(f"unexpected /mines response: {status} {mines}")

    except (OSError, urllib.error.URLError, json.JSONDecodeError, RuntimeError) as exc:
        print(f"health check failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps({"health": health, "mine_catalog_ok": True}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
