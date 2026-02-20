from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseConnector(ABC):
    """Abstract base class — all connectors must implement fetch()"""

    @abstractmethod
    def fetch(self, **kwargs) -> List[Dict[str, Any]]:
        pass