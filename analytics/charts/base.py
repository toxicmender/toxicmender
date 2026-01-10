from abc import ABC, abstractmethod

class Chart(ABC):
    @abstractmethod
    def render(self, output_path: str):
        pass
