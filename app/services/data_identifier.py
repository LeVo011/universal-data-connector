import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def identify_data_type(data: List[Dict]) -> str:
    """Look at the first record's keys to classify what kind of data this is."""
    if not data:
        return "empty"
    first = data[0]
    if "date" in first and "metric" in first:
        return "time_series"
    if "ticket_id" in first:
        return "tabular_support"
    if "customer_id" in first:
        return "tabular_crm"
    return "unknown"