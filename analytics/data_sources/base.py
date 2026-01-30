from abc import ABC, abstractmethod
from typing import Any


class DataSource(ABC):
    @abstractmethod
    def fetch(self) -> Any:
        """Return raw data"""
        pass
