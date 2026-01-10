from abc import ABC, abstractmethod
import os
from pathlib import Path

from analytics.exceptions import ChartError

class Chart(ABC):
    @abstractmethod
    def render(self, output: Path) -> None:
        pass

    def _validate_path(self, output_path: Path):
        if output_path.suffix not in {".svg", ".png"}:
            raise ChartError("Chart output must be SVG or PNG")
        if not output_path.parent.exists():
            raise ChartError("Output directory does not exist")
        if not output_path.parent.is_dir():
            raise ChartError("Output path parent is not a directory")
        if not os.access(output_path.parent, os.W_OK):
            raise ChartError("Output directory is not writable")
        return True