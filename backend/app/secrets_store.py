"""
Runtime secrets store.

Lets the user enter API keys / tokens from the running app (Settings UI) instead
of hand-editing .env. Values are persisted to a git-ignored JSON file under
``data/`` and applied to the process environment so the app picks them up live.

Security notes:
- ``data/`` is git-ignored, so secrets are never committed.
- Secret values are only ever returned to clients in masked form (see ``status``).
- Intended for local / single-user deployments. For multi-user or hosted setups,
  use a real secret manager (see docs/SECURITY_GUIDE.md).
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from threading import Lock
from typing import Dict, List

logger = logging.getLogger(__name__)

# Keys whose VALUES are sensitive — masked in any read response.
SECRET_KEYS: List[str] = [
    "OPENAI_API_KEY",
    "STOCK_API_KEY",
    "TOSS_CLIENT_ID",
    "TOSS_CLIENT_SECRET",
    "TOSS_ACCOUNT_NO",
    "KIS_APP_KEY",
    "KIS_APP_SECRET",
    "KIS_ACCOUNT_NO",
]

# Non-sensitive config that the UI may also set — returned in clear text.
CONFIG_KEYS: List[str] = [
    "OPENAI_MODEL",
    "BROKER",
    "MARKET",
    "ALLOW_LIVE_TRADING",
    "KIS_PAPER",
]

ALLOWED_KEYS = set(SECRET_KEYS) | set(CONFIG_KEYS)

# repo_root/data/secrets.json  (data/ is git-ignored)
_STORE_PATH = Path(__file__).resolve().parents[2] / "data" / "secrets.json"
_lock = Lock()


def _load_raw() -> Dict[str, str]:
    if _STORE_PATH.exists():
        try:
            return json.loads(_STORE_PATH.read_text(encoding="utf-8"))
        except Exception as e:  # corrupt file shouldn't crash the app
            logger.warning(f"Failed to read secrets store: {e}")
    return {}


def apply_to_env() -> None:
    """Load persisted secrets into ``os.environ`` (call once at startup).

    Persisted values win over .env so the user's in-app edits take effect.
    """
    data = _load_raw()
    applied = 0
    for key, value in data.items():
        if key in ALLOWED_KEYS and value not in (None, ""):
            os.environ[key] = str(value)
            applied += 1
    if applied:
        logger.info(f"Applied {applied} stored secret(s)/config from {_STORE_PATH.name}")


def save(updates: Dict[str, object]) -> List[str]:
    """Persist allowed key updates and apply them to the environment.

    An empty string clears (removes) a key. Unknown keys are ignored.
    Returns the list of keys that were changed.
    """
    with _lock:
        data = _load_raw()
        changed: List[str] = []
        for key, value in updates.items():
            if key not in ALLOWED_KEYS:
                logger.debug(f"Ignoring unknown settings key: {key}")
                continue
            if value is None or value == "":
                data.pop(key, None)
                os.environ.pop(key, None)
            else:
                str_value = str(value)
                data[key] = str_value
                os.environ[key] = str_value
            changed.append(key)

        _STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _STORE_PATH.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        try:  # best effort; no-op on most Windows filesystems
            os.chmod(_STORE_PATH, 0o600)
        except OSError:
            pass
        return changed


def _mask(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "•" * len(value)
    return f"{value[:4]}…{value[-4:]}"


def status() -> Dict[str, object]:
    """Return masked secret status + clear config, read from current env."""
    secrets = {
        key: {"set": bool(os.getenv(key)), "preview": _mask(os.getenv(key, ""))}
        for key in SECRET_KEYS
    }
    config = {key: os.getenv(key, "") for key in CONFIG_KEYS}
    return {"secrets": secrets, "config": config}
