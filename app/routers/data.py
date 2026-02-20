import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.connectors.analytics_connector import AnalyticsConnector
from app.connectors.crm_connector import CRMConnector
from app.connectors.support_connector import SupportConnector
from app.models.common import DataResponse, Metadata
from app.services.business_rules import (
    apply_voice_limits,
    filter_active_customers,
    prioritize_open_tickets,
)
from app.services.data_identifier import identify_data_type
from app.services.voice_optimizer import build_voice_summary, summarize_if_large

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/data", tags=["Data"])

CONNECTOR_MAP = {
    "crm": CRMConnector(),
    "support": SupportConnector(),
    "analytics": AnalyticsConnector(),
}


@router.get("/{source}", response_model=DataResponse, summary="Query a data source")
def get_data(
    source: str,
    limit: int = Query(10, ge=1, le=50),
    status: Optional[str] = Query(None),
    plan: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    customer_id: Optional[int] = Query(None),
    metric: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
):
    logger.info("GET /data/%s  limit=%d", source, limit)

    connector = CONNECTOR_MAP.get(source)
    if not connector:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown source '{source}'. Valid: {list(CONNECTOR_MAP.keys())}",
        )

    raw_data = connector.fetch(
        status=status, plan=plan, priority=priority,
        category=category, customer_id=customer_id,
        metric=metric, date_from=date_from, date_to=date_to,
    )

    total = len(raw_data)

    # Apply business rules
    if source == "support":
        raw_data = prioritize_open_tickets(raw_data)
    elif source == "crm":
        raw_data = filter_active_customers(raw_data)

    limited = apply_voice_limits(raw_data, limit=limit)
    optimized = summarize_if_large(limited)
    data_type = identify_data_type(raw_data)
    voice_summary = build_voice_summary(optimized, data_type, total)
    freshness = f"Data as of {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"

    metadata = Metadata(
        total_results=total,
        returned_results=len(optimized),
        data_freshness=freshness,
        data_type=data_type,
        voice_summary=voice_summary,
        context_hint=f"Showing {len(optimized)} of {total} results.",
    )

    return DataResponse(data=optimized, metadata=metadata)


@router.get("/schema/functions", tags=["LLM Integration"])
def get_function_schemas():
    """OpenAI-compatible function definitions — feed this to an LLM."""
    return {
        "functions": [
            {
                "name": "query_crm",
                "description": "Query CRM customer data. Use for questions about customers, accounts, subscriptions, or revenue.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["active", "inactive"]},
                        "plan": {"type": "string", "enum": ["basic", "pro", "enterprise"]},
                        "limit": {"type": "integer", "default": 10},
                    },
                },
            },
            {
                "name": "query_support",
                "description": "Query support tickets. Use for questions about issues, bugs, complaints, or open tickets.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["open", "closed"]},
                        "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                        "category": {"type": "string", "enum": ["bug", "billing", "integration", "security", "feature_request", "performance"]},
                        "customer_id": {"type": "integer"},
                        "limit": {"type": "integer", "default": 10},
                    },
                },
            },
            {
                "name": "query_analytics",
                "description": "Query time-series metrics. Use for questions about usage trends, daily active users, or date-based data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "metric": {"type": "string", "description": "e.g. 'daily_active_users'"},
                        "date_from": {"type": "string", "description": "YYYY-MM-DD"},
                        "date_to": {"type": "string", "description": "YYYY-MM-DD"},
                        "limit": {"type": "integer", "default": 10},
                    },
                },
            },
        ]
    }


class ChatRequest(BaseModel):
    query: str


@router.post("/chat", tags=["LLM Integration"])
def chat_query(request: ChatRequest):
    """Natural language query — routes to the right data source automatically."""
    query = request.query.lower()
    logger.info("chat_query: %r", request.query)

    if any(kw in query for kw in ["customer", "crm", "account", "subscription", "mrr", "plan"]):
        source = "crm"
        filters: Dict[str, Any] = {}
        if "active" in query: filters["status"] = "active"
        if "enterprise" in query: filters["plan"] = "enterprise"
        if "inactive" in query: filters["status"] = "inactive"

    elif any(kw in query for kw in ["ticket", "issue", "bug", "support", "open", "complaint"]):
        source = "support"
        filters = {}
        if "open" in query: filters["status"] = "open"
        if "closed" in query: filters["status"] = "closed"
        if "high" in query: filters["priority"] = "high"
        if "billing" in query: filters["category"] = "billing"
        if "security" in query: filters["category"] = "security"

    elif any(kw in query for kw in ["analytics", "metric", "dau", "trend", "usage", "active user"]):
        source = "analytics"
        filters = {}
        if "active user" in query or "dau" in query:
            filters["metric"] = "daily_active_users"

    else:
        return {
            "answer": "I'm not sure which data source to query. Try asking about customers, support tickets, or analytics.",
            "routed_to": None,
            "source": None,
        }

    connector = CONNECTOR_MAP[source]
    raw_data = connector.fetch(**filters)
    total = len(raw_data)

    if source == "support":
        raw_data = prioritize_open_tickets(raw_data)
    elif source == "crm":
        raw_data = filter_active_customers(raw_data)

    limited = apply_voice_limits(raw_data)
    data_type = identify_data_type(raw_data)
    voice_summary = build_voice_summary(limited, data_type, total)

    return {
        "query": request.query,
        "routed_to": source,
        "answer": voice_summary,
        "data": limited,
        "metadata": {
            "total_results": total,
            "returned_results": len(limited),
            "data_type": data_type,
            "data_freshness": f"Data as of {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        },
    }