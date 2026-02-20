import logging
from typing import Dict, List

logger = logging.getLogger(__name__)
SUMMARIZE_THRESHOLD = 10


def summarize_if_large(data: List[Dict]) -> List[Dict]:
    """If dataset is too large for voice, replace with one summary sentence."""
    if len(data) <= SUMMARIZE_THRESHOLD:
        return data

    if data and "metric" in data[0]:
        values = [r.get("value", 0) for r in data]
        summary = (f"{len(data)} metric records. "
                   f"Latest: {data[0].get('metric')} = {data[0].get('value')} "
                   f"on {data[0].get('date')}. "
                   f"Average: {sum(values)/len(values):.0f}.")
    elif data and "ticket_id" in data[0]:
        open_n = sum(1 for r in data if r.get("status") == "open")
        summary = f"{len(data)} tickets found. {open_n} are open."
    elif data and "customer_id" in data[0]:
        active = sum(1 for r in data if r.get("status") == "active")
        summary = f"{len(data)} customers found. {active} are active."
    else:
        summary = f"{len(data)} records found."

    return [{"summary": summary}]


def build_voice_summary(data: List[Dict], data_type: str, total: int) -> str:
    """Build a one-sentence summary the LLM can speak aloud."""
    shown = len(data)

    if data_type == "time_series" and data and "value" in data[0]:
        values = [r["value"] for r in data if "value" in r]
        avg = sum(values) / len(values)
        latest = data[0]
        return (f"Latest {latest.get('metric')} on {latest.get('date')} "
                f"was {latest.get('value')}. "
                f"Average over the last {shown} days: {avg:.0f}.")

    if data_type == "tabular_support":
        open_c = sum(1 for r in data if r.get("status") == "open")
        high_c = sum(1 for r in data if r.get("priority") == "high")
        return (f"Showing {shown} of {total} tickets. "
                f"{open_c} open, {high_c} high priority.")

    if data_type == "tabular_crm":
        active = sum(1 for r in data if r.get("status") == "active")
        return f"Showing {shown} of {total} customers. {active} are active."

    return f"Showing {shown} of {total} results."