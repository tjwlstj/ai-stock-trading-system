"""
Tier policy (free vs paid) capability context.

Loads config/tiers.yaml — a single declarative place that decides what each tier
is allowed to do. The rest of the app reads capabilities from here instead of
hard-coding "free can't trade" logic in many places.

Rule of thumb:
- free  -> analysis & advice only; ordering/purchasing is conservatively blocked.
- paid  -> analysis & advice + ordering/live trading under RiskGuard safeguards.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "tiers.yaml"

# Safe built-in defaults used if config/tiers.yaml is missing or unreadable.
_DEFAULTS: Dict[str, Any] = {
    "default_tier": "free",
    "tiers": {
        "free": {
            "label": "무료 (Free)",
            "description": "분석과 조언만 제공합니다. 실제 주문·실거래는 비활성화됩니다.",
            "capabilities": {
                "analyze": True,
                "advise": True,
                "place_orders": False,
                "live_trading": False,
                "brokers": ["paper"],
                "max_order_amount_krw": 0,
            },
            "ai_providers": ["gemini_free"],
            "notes": [],
        },
        "paid": {
            "label": "유료 (Paid)",
            "description": "분석·조언 + 안전장치 하에서 모의/실거래가 가능합니다.",
            "capabilities": {
                "analyze": True,
                "advise": True,
                "place_orders": True,
                "live_trading": True,
                "brokers": ["paper", "kis", "toss"],
                "max_order_amount_krw": 100000,
            },
            "ai_providers": ["openai", "gemini_free"],
            "notes": [],
        },
    },
}


def _load_policy() -> Dict[str, Any]:
    try:
        import yaml  # PyYAML is a project dependency

        if _CONFIG_PATH.exists():
            data = yaml.safe_load(_CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("tiers"):
                return data
    except Exception as e:  # never let a config issue crash the app
        logger.warning(f"Failed to load tiers.yaml, using defaults: {e}")
    return _DEFAULTS


# Loaded once at import; cheap and rarely changes.
_POLICY = _load_policy()


def reload() -> None:
    """Re-read the policy file (e.g., after editing config/tiers.yaml)."""
    global _POLICY
    _POLICY = _load_policy()


def default_tier() -> str:
    return _POLICY.get("default_tier", "free")


def current_tier() -> str:
    """Active tier from APP_TIER env, falling back to the policy default."""
    name = (os.getenv("APP_TIER") or default_tier()).lower()
    return name if name in _POLICY.get("tiers", {}) else default_tier()


def tier(name: str | None = None) -> Dict[str, Any]:
    name = (name or current_tier()).lower()
    tiers = _POLICY.get("tiers", {})
    return tiers.get(name, tiers.get(default_tier(), {}))


def capabilities(name: str | None = None) -> Dict[str, Any]:
    return dict(tier(name).get("capabilities", {}))


def can(action: str, name: str | None = None) -> bool:
    """True if the given tier permits an action (e.g. 'place_orders')."""
    return bool(capabilities(name).get(action, False))


def allowed_brokers(name: str | None = None) -> list:
    return list(capabilities(name).get("brokers", ["paper"]))


def public_view() -> Dict[str, Any]:
    """Tier info safe to expose to the frontend."""
    name = current_tier()
    t = tier(name)
    return {
        "current": name,
        "label": t.get("label", name),
        "description": t.get("description", ""),
        "capabilities": capabilities(name),
        "notes": t.get("notes", []),
        "available": [
            {"value": k, "label": v.get("label", k)}
            for k, v in _POLICY.get("tiers", {}).items()
        ],
    }
