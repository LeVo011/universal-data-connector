from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health, data
from app.utils.logging import configure_logging
from app.config import settings

configure_logging()

app = FastAPI(
    title=settings.APP_NAME,
    description="Unified LLM-ready data connector for CRM, support tickets, and analytics. Voice-optimized.",
    version="1.0.0",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(health.router)
app.include_router(data.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "service": settings.APP_NAME,
        "data_sources": ["crm", "support", "analytics"],
        "try": {
            "crm": "/data/crm?status=active",
            "support": "/data/support?status=open&priority=high",
            "analytics": "/data/analytics?metric=daily_active_users",
            "chat": "POST /data/chat  {query: 'show me open tickets'}",
            "llm_schemas": "/data/schema/functions",
            "docs": "/docs",
        },
    }