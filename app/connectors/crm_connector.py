import json
import logging
from pathlib import Path
from .base import BaseConnector

logger = logging.getLogger(__name__)


class CRMConnector(BaseConnector):
    def fetch(self, status=None, plan=None, sort_by="created_at", **kwargs):
        logger.info("CRMConnector: fetching customers")
        with open(Path("data/customers.json")) as f:
            customers = json.load(f)

        if status:
            customers = [c for c in customers if c.get("status") == status]
        if plan:
            customers = [c for c in customers if c.get("plan") == plan]

        customers.sort(key=lambda x: x.get(sort_by, ""), reverse=True)
        logger.info("CRMConnector: returning %d records", len(customers))
        return customers