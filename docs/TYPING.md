# Type Hints Guide

This project uses Python type hints throughout the codebase to improve code quality, catch bugs early, and enhance IDE support.

## Overview

- **Python Version**: 3.12+
- **Type Checker**: [mypy](https://mypy-lang.org/)
- **Type Stubs**: `types-PyYAML` for YAML parsing

## Running Type Checks

```bash
# Check all files in the analytics package
uv run mypy analytics

# Check specific file
uv run mypy analytics/data_sources/github.py

# Check with verbose output
uv run mypy analytics --verbose
```

## Configuration

Type checking is configured in `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
no_implicit_optional = true  # Enforce explicit Optional[]
check_untyped_defs = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

# Gradually enable strict checking per module
[[tool.mypy.overrides]]
module = [
    "analytics.models.repo",
    "analytics.models.time_series",
    "analytics.exceptions",
    "analytics.charts.base",
    "analytics.normalisation.minmax",
    "analytics.scoring.impact_score",
    "analytics.utils.validation",
    "analytics.config.auth",
]
disallow_untyped_defs = true
```

### Gradual Typing Approach

We enable strict typing (`disallow_untyped_defs = true`) module by module:

1. **Start with core models** - Pydantic models (`analytics.models.*`)
2. **Simple utility modules** - Pure functions with clear signatures (`analytics.utils.validation`, `analytics.normalisation.minmax`)
3. **Well-isolated components** - Base classes, exceptions, config
4. **Complex modules last** - Data sources, metrics, charts with external dependencies

## Typing Patterns

### Basic Function Annotations

```python
from typing import List, Dict, Optional, Any
from pathlib import Path

def process_repos(repos: List[str], output: Path) -> Dict[str, Any]:
    """Process repositories and return metrics."""
    results: Dict[str, Any] = {}
    for repo in repos:
        results[repo] = analyze(repo)
    return results
```

### Pydantic Models

Pydantic models provide automatic type validation. No need for explicit type hints on fields:

```python
from pydantic import BaseModel, Field
from typing import Optional

class RepoStats(BaseModel):
    name: str = Field(min_length=1)
    loc: int
    commits: int
    stars: int = 0
    original_loc: Optional[int] = None
```

### Abstract Base Classes

```python
from abc import ABC, abstractmethod
from typing import Any

class DataSource(ABC):
    @abstractmethod
    def fetch(self) -> Any:
        """Fetch data from source."""
        pass
```

### Pipeline Steps

```python
from analytics.pipeline.base import PipelineStep
from analytics.models.repo import RepoStats
from typing import List, Dict, Any

class Analyser(PipelineStep):
    def __init__(self, metrics: List[Metric]) -> None:
        super().__init__("Analyser")
        self.metrics: List[Metric] = metrics

    def execute(self, repos: List[RepoStats], **kwargs: Any) -> Dict[str, Any]:
        """Run analysis pipeline."""
        return {"results": self._compute_metrics(repos)}
```

### Chart Classes

```python
from analytics.charts.base import Chart
from pathlib import Path
from typing import Dict

class EfficiencyChart(Chart):
    def __init__(self, data: Dict[str, float]) -> None:
        self.data: Dict[str, float] = data

    def render(self, output: Path) -> None:
        """Render chart to file."""
        self._validate_path(output)
        # rendering logic...
```

### Optional Parameters

**Always use `Optional[T]` when a parameter defaults to `None`:**

```python
from typing import Optional
from pathlib import Path

# ❌ WRONG - mypy error with no_implicit_optional=True
def load_data(path: Path, cache_dir: Path = None) -> dict:
    ...

# ✅ CORRECT - Explicit Optional
def load_data(path: Path, cache_dir: Optional[Path] = None) -> dict:
    if cache_dir is not None:
        # Type checker knows cache_dir is Path here
        cache_dir.mkdir(parents=True, exist_ok=True)
    ...

# Also works for multiple optional parameters
def fetch_repos(
    username: str,
    token: Optional[str] = None,
    cache_dir: Optional[Path] = None
) -> list:
    ...
```

The `no_implicit_optional = true` mypy setting enforces this, preventing subtle bugs from None being passed unexpectedly.

### Optional Parameters

Use `Optional[T]` for parameters that can be `None`:

```python
from typing import Optional

def get_github_token() -> Optional[str]:
    """Get token or None if not found."""
    token = os.environ.get('GITHUB_TOKEN')
    return token if token else None
```

### Dict with Mixed Value Types

For dictionaries with heterogeneous values, use `Dict[str, Any]`:

```python
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """Load configuration with mixed types."""
    return {
        "enabled": True,
        "timeout": 30,
        "paths": ["/data", "/cache"]
    }
```

### Type Variance (Mapping vs Dict)

When passing dicts as arguments, prefer `Mapping` for covariance:

```python
from typing import Dict, Mapping

# Use Mapping for parameters (covariant in value type)
def normalize(values: Mapping[str, float]) -> Dict[str, float]:
    """Normalize values to [0, 1] range."""
    max_val = max(values.values())
    return {k: v / max_val for k, v in values.items()}

# Dict is invariant, so this works:
data: Dict[str, float] = {"a": 1.0, "b": 2.0}
result = normalize(data)  # OK

# And this also works (Mapping accepts Dict[str, int]):
int_data: Dict[str, int] = {"a": 1, "b": 2}
result = normalize(int_data)  # OK with Mapping, would fail with Dict
```

## Common Patterns

### Union Types

```python
from typing import Union

def parse_value(value: Union[str, int, float]) -> float:
    """Parse numeric value from various types."""
    return float(value)
```

### Generic Collections

```python
from typing import List, Tuple

def create_chart_configs() -> List[Tuple[Chart, str]]:
    """Create list of (chart, output_path) tuples."""
    return [
        (EfficiencyChart(data), "charts/efficiency.png"),
        (LanguageChart(langs), "charts/languages.png")
    ]
```

## Testing with Type Hints

### Pytest Fixtures

**Add return types to fixtures for better type checking:**

```python
import pytest
from typing import List
from analytics.models.repo import RepoStats

@pytest.fixture
def sample_repo() -> RepoStats:
    """Single repository fixture."""
    return RepoStats(
        name="test-repo",
        loc=1500,
        commits=10,
        stars=5,
        forks=2,
        languages={"Python": 1000, "JavaScript": 500}
    )

@pytest.fixture
def sample_repos() -> List[RepoStats]:
    """Multiple repositories fixture."""
    return [
        RepoStats(name="repo1", loc=5000, commits=50, stars=100, languages={"Python": 5000}),
        RepoStats(name="repo2", loc=10000, commits=100, stars=250, languages={"Go": 10000}),
    ]
```

### Test Functions

**Add return type `None` to test functions:**

```python
from typing import List
from analytics.models.repo import RepoStats

def test_metric_computation(sample_repos: List[RepoStats]) -> None:
    """Test LOC metric calculation."""
    metric = LOCMetric()
    result = metric.compute(sample_repos)

    assert result.name == "loc"
    assert len(result.repo_names) == 2

def test_normalisation_consistency() -> None:
    """Test normalization methods produce consistent ordering."""
    data = {"repo_a": 100, "repo_b": 200, "repo_c": 300}

    log_norm = log_minmax(data)
    rank_norm = rank_based(data)

    assert sorted(log_norm.keys()) == sorted(rank_norm.keys())
```

### Ignoring Types in Tests

Use `# type: ignore` when mocking makes types incompatible:

```python
from unittest.mock import MagicMock

def test_with_mock() -> None:
    mock_source = MagicMock()  # type: ignore[no-untyped-def]
    mock_source.fetch.return_value = {"data": "value"}

    # Or be more specific:
    collector = DataCollector([mock_source])  # type: ignore[arg-type]
```

## PyGithub Type Hints

PyGithub library has type stubs. Import types explicitly:

```python
from github import Github, Auth
from github.Repository import Repository

def fetch_repo(name: str, token: str) -> Repository:
    """Fetch repository using GitHub API."""
    auth = Auth.Token(token) if token else None
    client = Github(auth=auth)
    return client.get_repo(name)
```

## Ignoring Type Errors (Last Resort)

If a specific line has unavoidable type issues, use inline ignore comments:

```python
result = some_untyped_library_function()  # type: ignore[no-untyped-call]
```

Common ignore codes:
- `[no-untyped-call]` - Calling untyped function
- `[no-untyped-def]` - Function without type hints
- `[arg-type]` - Argument type mismatch
- `[return-value]` - Return type mismatch
- `[attr-defined]` - Attribute not defined

## Testing Type Hints

Test files should also have type hints where practical:

```python
from analytics.metrics.loc import LOCMetric
from analytics.models.repo import RepoStats

def test_loc_metric() -> None:
    """Test LOC metric computation."""
    repos: List[RepoStats] = [
        RepoStats(name="repo1", loc=1000, commits=50, languages={"Python": 1000}),
        RepoStats(name="repo2", loc=2000, commits=100, languages={"Python": 2000}),
    ]

    metric = LOCMetric()
    result = metric.compute(repos)

    assert result.name == "loc"
    assert "total_loc" in result.values
```

## Gradual Typing Strategy

1. **Start with models** - Pydantic models are already strictly typed
2. **Add return types** - Start with function return types (most valuable)
3. **Add parameter types** - Type function parameters
4. **Internal variables** - Type local variables when helpful
5. **Enable strict mode gradually** - Module by module

## Resources

- [mypy documentation](https://mypy.readthedocs.io/)
- [Python typing module](https://docs.python.org/3/library/typing.html)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)

## Known Issues

Some test files may have type errors due to:
- Mock objects not matching exact types
- Test data with simplified structures
- Dynamic test fixtures

These can be resolved by:
1. Using proper type annotations in test fixtures
2. Creating typed test data factories
3. Using `# type: ignore` comments for mock-specific issues
