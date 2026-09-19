from app.api.ai import router as ai_router
from app.api.health import router as health_router
from app.api.market import router as market_router
from app.api.research import router as research_router

__all__ = ["ai_router", "health_router", "market_router", "research_router"]
