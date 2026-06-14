"""
Settings / API-key management routes.

Lets the frontend read which keys are configured (masked) and save new keys
entered by the user at runtime. See backend/app/secrets_store.py for storage.
"""

import logging
from typing import Dict, Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .. import secrets_store
from ..settings import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/settings", tags=["settings"])


class SecretsUpdate(BaseModel):
    """Map of setting key -> value. Empty string clears a key."""
    updates: Dict[str, Optional[str]]


def _reload_clients() -> None:
    """Apply freshly saved settings to the running process."""
    settings.refresh()
    # Re-initialise the OpenAI client used by the stocks router so a newly
    # entered key takes effect without a server restart.
    try:
        from ..openai_client import OpenAIClient
        from ..routers import stocks

        if settings.OPENAI_API_KEY:
            stocks.set_openai_client(OpenAIClient(settings.OPENAI_API_KEY))
    except Exception as e:  # never let a reload error break the save
        logger.warning(f"Client reload after settings save failed: {e}")


@router.get("/secrets")
async def get_secrets_status():
    """Return masked status of all known API keys + non-secret config."""
    return secrets_store.status()


@router.post("/secrets")
async def update_secrets(payload: SecretsUpdate):
    """Persist user-entered keys/config and apply them live."""
    changed = secrets_store.save(payload.updates)
    _reload_clients()
    logger.info(f"Settings updated: {changed}")
    return {"changed": changed, **secrets_store.status()}


@router.post("/test/{provider}")
async def test_provider(provider: str):
    """Lightweight connectivity check for a provider's configured key."""
    provider = provider.lower()

    if provider == "openai":
        key = settings.OPENAI_API_KEY
        if not key or key.startswith("sk-your-"):
            return {"provider": provider, "ok": False, "message": "API 키가 설정되지 않았습니다."}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {key}"},
                )
            if resp.status_code == 200:
                return {"provider": provider, "ok": True, "message": "연결 성공"}
            if resp.status_code == 401:
                return {"provider": provider, "ok": False, "message": "유효하지 않은 API 키"}
            return {"provider": provider, "ok": False, "message": f"오류 {resp.status_code}"}
        except Exception as e:
            return {"provider": provider, "ok": False, "message": f"연결 실패: {e}"}

    # Broker providers: real order-API validation arrives with the broker
    # adapter phase (see docs/ARCHITECTURE_KRX.md). For now report key presence.
    presence = {
        "toss": bool(settings.TOSS_CLIENT_ID and settings.TOSS_CLIENT_SECRET),
        "kis": bool(settings.KIS_APP_KEY and settings.KIS_APP_SECRET),
    }
    if provider in presence:
        ok = presence[provider]
        return {
            "provider": provider,
            "ok": None,
            "message": (
                "키 입력됨 — 실제 연결 검증은 브로커 연동 단계에서 수행됩니다."
                if ok
                else "키가 아직 입력되지 않았습니다."
            ),
        }

    raise HTTPException(status_code=404, detail=f"Unknown provider: {provider}")
