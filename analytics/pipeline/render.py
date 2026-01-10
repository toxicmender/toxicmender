"""
Rendering pipeline stage.
Outputs analysis results in various formats (JSON, CSV, HTML).
"""
from typing import Dict, Any, List
from pathlib import Path
import json
import csv
import logging

logger = logging.getLogger(__name__)


class ResultRenderer:
    """Renders analysis results in multiple output formats."""

    SUPPORTED_FORMATS = {'.json', '.csv', '.txt'}

    def __init__(self, output_dir: Path):
        """
        Initialize result renderer.

        Args:
            output_dir: Directory to write rendered results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def render(self, results: Dict[str, Any], format: str = 'json') -> Path:
        """
        Render results to specified format.

        Args:
            results: Analysis results dictionary
            format: Output format (json, csv, txt)

        Returns:
            Path to rendered output file

        Raises:
            ValueError: If format is not supported
        """
        format_lower = format.lower()
        if not format_lower.startswith('.'):
            format_lower = f'.{format_lower}'

        if format_lower not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format: {format}. "
                f"Supported: {self.SUPPORTED_FORMATS}"
            )

        if format_lower == '.json':
            return self._render_json(results)
        elif format_lower == '.csv':
            return self._render_csv(results)
        elif format_lower == '.txt':
            return self._render_text(results)

    def _render_json(self, results: Dict[str, Any]) -> Path:
        """Render results as JSON."""
        output_path = self.output_dir / 'results.json'
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Rendered JSON results to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to render JSON: {e}")
            raise

    def _render_csv(self, results: Dict[str, Any]) -> Path:
        """Render results as CSV."""
        output_path = self.output_dir / 'results.csv'
        try:
            # Flatten results for CSV format
            rows = self._flatten_results(results)

            if not rows:
                logger.warning("No data to render as CSV")
                return output_path

            # Get all keys from all rows for CSV headers
            fieldnames = set()
            for row in rows:
                fieldnames.update(row.keys())
            fieldnames = sorted(list(fieldnames))

            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

            logger.info(f"Rendered CSV results to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to render CSV: {e}")
            raise

    def _render_text(self, results: Dict[str, Any]) -> Path:
        """Render results as formatted text."""
        output_path = self.output_dir / 'results.txt'
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("Analysis Results\n")
                f.write("=" * 80 + "\n\n")

                self._write_dict_to_file(f, results, indent=0)

            logger.info(f"Rendered text results to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to render text: {e}")
            raise

    def _flatten_results(self, obj: Any, prefix: str = '') -> List[Dict[str, Any]]:
        """Flatten nested results for CSV output."""
        rows = []

        if isinstance(obj, dict):
            # Check if this looks like a metric result with values
            if 'values' in obj and isinstance(obj['values'], dict):
                for key, value in obj['values'].items():
                    rows.append({
                        'metric': obj.get('name', prefix),
                        'key': key,
                        'value': value
                    })
            else:
                # Generic dict - create one row with all key-values
                row = {}
                for key, value in obj.items():
                    if isinstance(value, (dict, list)):
                        row[key] = json.dumps(value)
                    else:
                        row[key] = value
                if row:
                    rows.append(row)
        elif isinstance(obj, list):
            for item in obj:
                rows.extend(self._flatten_results(item, prefix))

        return rows

    def _write_dict_to_file(self, f, obj: Any, indent: int = 0) -> None:
        """Recursively write dictionary to file with formatting."""
        indent_str = "  " * indent

        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, dict):
                    f.write(f"{indent_str}{key}:\n")
                    self._write_dict_to_file(f, value, indent + 1)
                elif isinstance(value, list):
                    f.write(f"{indent_str}{key}:\n")
                    for item in value:
                        if isinstance(item, dict):
                            self._write_dict_to_file(f, item, indent + 1)
                        else:
                            f.write(f"{indent_str}  - {item}\n")
                else:
                    f.write(f"{indent_str}{key}: {value}\n")
        else:
            f.write(f"{indent_str}{obj}\n")
