"""
Filesystem-based data source for reading repository data from local files.
Supports JSON, YAML, and CSV formats.
"""
from analytics.data_sources.base import DataSource
from analytics.exceptions import DataSourceError
from pathlib import Path
from typing import Any, List, Dict
import json
import csv


class FilesystemDataSource(DataSource):
    """Fetches repository data from local filesystem files."""

    def __init__(self, file_path: Path) -> None:
        """
        Initialize filesystem data source.

        Args:
            file_path: Path to data file (JSON, CSV, or YAML)

        Raises:
            DataSourceError: If file does not exist or format is unsupported
        """
        self.file_path: Path = Path(file_path)

        if not self.file_path.exists():
            raise DataSourceError(f"Data file not found: {file_path}")

        supported_formats = {'.json', '.csv', '.yml', '.yaml'}
        if self.file_path.suffix not in supported_formats:
            raise DataSourceError(
                f"Unsupported file format: {self.file_path.suffix}. "
                f"Supported: {supported_formats}"
            )

    def fetch(self) -> Any:
        """
        Fetch data from filesystem.

        Returns:
            Parsed data from file

        Raises:
            DataSourceError: If file parsing fails
        """
        try:
            if self.file_path.suffix == '.json':
                return self._fetch_json()
            elif self.file_path.suffix == '.csv':
                return self._fetch_csv()
            elif self.file_path.suffix in {'.yml', '.yaml'}:
                return self._fetch_yaml()
        except Exception as e:
            raise DataSourceError(
                f"Failed to fetch data from {self.file_path}"
            ) from e

    def _fetch_json(self) -> Any:
        """Parse and return JSON file."""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _fetch_csv(self) -> List[Dict[str, Any]]:
        """Parse and return CSV file as list of dictionaries."""
        data: List[Dict[str, Any]] = []
        with open(self.file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(dict(row))
        return data

    def _fetch_yaml(self) -> Any:
        """Parse and return YAML file."""
        try:
            import yaml
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except ImportError:
            raise DataSourceError("PyYAML not installed - cannot parse YAML files")
        except Exception as e:
            raise DataSourceError(f"Failed to parse YAML file: {e}")
