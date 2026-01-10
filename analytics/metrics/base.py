from abc import ABC, abstractmethod

class Metric(ABC):
    name: str

    @abstractmethod
    def compute(self, data):
        """Return numeric metric"""
        pass
