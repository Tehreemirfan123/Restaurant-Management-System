"""Loader for the per-client profile (client.config.yaml).

This exposes the CONFIGURABLE surface described in docs/ARCHITECTURE.md — brand,
terminology, enabled modules and feature flags. It is client data, never
secrets (those stay in the environment / Kubernetes Secrets).

Path resolution:
  1. CLIENT_CONFIG_PATH env var, if set (this is how a Kubernetes ConfigMap
     mount points the container at the file);
  2. otherwise the repo-root client.config.yaml, resolved from this file's
     location so it works no matter what the current working directory is.

If the file is missing the loader returns a minimal default instead of
crashing, so the API always boots.
"""

import os
from functools import lru_cache
from pathlib import Path

import yaml


_DEFAULT_PROFILE = {
    "client": {"id": "default", "vertical": "generic"},
    "brand": {"name": "Management System"},
    "locale": {"language": "en"},
    "terminology": {"customer": "Customer", "staff": "Staff", "order": "Order"},
    "modules": {},
    "features": {},
}


def _config_path() -> Path:
    override = os.getenv("CLIENT_CONFIG_PATH")
    if override:
        return Path(override)
    # backend/core/client_config.py -> parents[2] is the repo root.
    return Path(__file__).resolve().parents[2] / "client.config.yaml"


@lru_cache(maxsize=1)
def get_client_config() -> dict:
    """The full parsed profile (cached). Server-side use only."""
    try:
        with open(_config_path(), "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or dict(_DEFAULT_PROFILE)
    except FileNotFoundError:
        return dict(_DEFAULT_PROFILE)


def public_profile() -> dict:
    """The non-secret subset safe to send to the browser.

    Deliberately excludes `roles` and the numeric `payments`/`delivery` rule
    params — those drive server-side behaviour and belong in the API/DB, not in
    a public config document.
    """
    cfg = get_client_config()
    payments = cfg.get("payments", {}) or {}
    return {
        "client": cfg.get("client", {}),
        "brand": cfg.get("brand", {}),
        "locale": cfg.get("locale", {}),
        "terminology": cfg.get("terminology", {}),
        "modules": cfg.get("modules", {}),
        "features": cfg.get("features", {}),
        # Only which methods are offered — not the amounts/thresholds.
        "payment_methods": payments.get("methods", []),
    }
