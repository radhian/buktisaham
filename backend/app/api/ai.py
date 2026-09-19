from __future__ import annotations

from fastapi import APIRouter

from app.schemas import AiReviewRequest
from app.services.ollama_client import OllamaClient

router = APIRouter(prefix="/v1/ai", tags=["ai"])


@router.post("/review")
def review(request: AiReviewRequest) -> dict:
    return OllamaClient().review(request.analysis)
