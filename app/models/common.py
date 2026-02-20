from pydantic import BaseModel
from typing import Any, List, Optional


class Metadata(BaseModel):
    total_results: int
    returned_results: int
    data_freshness: str
    data_type: str = "unknown"
    voice_summary: Optional[str] = None
    context_hint: Optional[str] = None


class DataResponse(BaseModel):
    data: List[Any]
    metadata: Metadata