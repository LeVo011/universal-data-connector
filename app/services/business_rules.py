import logging
from typing import Dict, List
from app.config import settings

logger = logging.getLogger(__name__)

PRIORITY_WEIGHT = {"high": 3, "medium": 2, "low": 1}


def apply_voice_limits(data: List[Dict], limit: int = None) -> List[Dict]:
    """Cap results to voice-friendly size (default 10)."""
    max_n = limit if limit is not None else settings.MAX_RESULTS
    result = data[:max_n]
    logger.info("apply_voice_limits: %d → %d records", len(data), len(result))
    return result


def prioritize_open_tickets(tickets: List[Dict]) -> List[Dict]:
    """Sort tickets: open + high priority come first."""
    def sort_key(t):
        return (
            1 if t.get("status") == "open" else 0,
            PRIORITY_WEIGHT.get(t.get("priority", "low"), 0)
        )
    return sorted(tickets, key=sort_key, reverse=True)


def filter_active_customers(customers: List[Dict]) -> List[Dict]:
    """Sort customers: active high-MRR accounts first."""
    active = sorted(
        [c for c in customers if c.get("status") == "active"],
        key=lambda x: x.get("mrr", 0),
        reverse=True
    )
    inactive = [c for c in customers if c.get("status") != "active"]
    return active + inactive