"""
Base abstraction for pipeline steps.
Provides a standardized interface for all pipeline stages.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
import logging

logger = logging.getLogger(__name__)


class PipelineStep(ABC):
    """
    Abstract base class for pipeline steps.

    Each pipeline step should implement the execute() method to perform
    its specific operation. The class provides common functionality for
    logging, validation, and error handling.
    """

    def __init__(self, name: str):
        """
        Initialize pipeline step.

        Args:
            name: Human-readable name for this pipeline step
        """
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        Execute the pipeline step.

        Args:
            **kwargs: Step-specific parameters

        Returns:
            Result of the pipeline step execution

        Raises:
            Exception: If the step execution fails
        """
        pass

    def run(self, **kwargs) -> Any:
        """
        Run the pipeline step with logging and error handling.

        Args:
            **kwargs: Step-specific parameters

        Returns:
            Result of the pipeline step execution
        """
        self.logger.info(f"Starting {self.name} step")
        try:
            result = self.execute(**kwargs)
            self.logger.info(f"Completed {self.name} step successfully")
            return result
        except Exception as e:
            self.logger.error(f"Failed {self.name} step: {e}")
            raise

    def validate_path(self, path: Path, must_exist: bool = False) -> Path:
        """
        Validate and convert path parameter.

        Args:
            path: Path to validate
            must_exist: If True, path must exist

        Returns:
            Validated Path object

        Raises:
            ValueError: If validation fails
        """
        if isinstance(path, str):
            path = Path(path)

        if must_exist and not path.exists():
            raise ValueError(f"Path does not exist: {path}")

        return path
