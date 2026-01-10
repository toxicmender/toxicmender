from abc import ABC, abstractmethod

class DataSource(ABC):
    @abstractmethod
    def fetch(self):
        """Return raw data"""
        pass
