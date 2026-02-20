import json
import logging
from pathlib import Path
from .base import BaseConnector

logger = logging.getLogger(__name__)


class AnalyticsConnector(BaseConnector):
    def fetch(self, metric=None, date_from=None, date_to=None, **kwargs):
        logger.info("AnalyticsConnector: fetching metrics")
        with open(Path("data/analytics.json")) as f:
            records = json.load(f)

        if metric:
            records = [r for r in records if r.get("metric") == metric]
        if date_from:
            records = [r for r in records if r.get("date", "") >= date_from]
        if date_to:
            records = [r for r in records if r.get("date", "") <= date_to]

        records.sort(key=lambda x: x.get("date", ""), reverse=True)
        logger.info("AnalyticsConnector: returning %d records", len(records))
        return records