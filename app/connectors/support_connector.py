import json
import logging
from pathlib import Path
from .base import BaseConnector

logger = logging.getLogger(__name__)


class SupportConnector(BaseConnector):
    def fetch(self, status=None, priority=None, category=None, customer_id=None, **kwargs):
        logger.info("SupportConnector: fetching tickets")
        with open(Path("data/support_tickets.json")) as f:
            tickets = json.load(f)

        if status:
            tickets = [t for t in tickets if t.get("status") == status]
        if priority:
            tickets = [t for t in tickets if t.get("priority") == priority]
        if category:
            tickets = [t for t in tickets if t.get("category") == category]
        if customer_id:
            tickets = [t for t in tickets if t.get("customer_id") == customer_id]

        tickets.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        logger.info("SupportConnector: returning %d records", len(tickets))
        return tickets