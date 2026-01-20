# Pipeline Architecture

The analytics pipeline follows a standardized four-stage architecture, with each stage implementing the `PipelineStep` base class.

## Pipeline Steps

### 1. Collection (`collect.py`)
**Class**: `DataCollector`
**Purpose**: Fetch repository data from various sources (GitHub API, cache, filesystem)

**Interface**:
```python
def run(username: str, output_dir: Path) -> None
```

**Responsibilities**:
- Configure and initialize data sources
- Fetch repository metadata and statistics
- Aggregate data from multiple sources
- Persist collected data to JSON

### 2. Analysis (`analyse.py`)
**Class**: `Analyser`
**Purpose**: Compute metrics and scores on collected repository data

**Interface**:
```python
def run(input_dir: Path, output_dir: Path) -> None
```

**Responsibilities**:
- Load collected repository data
- Apply configured metrics
- Compute normalized scores
- Save analysis results

### 3. Visualization (`visualize.py`)
**Class**: `Visualizer`
**Purpose**: Generate charts and visual representations

**Interface**:
```python
def run(data_dir: Path, charts_dir: Path) -> None
```

**Responsibilities**:
- Load metrics and analysis results
- Generate configured charts
- Save visualizations to disk

### 4. Rendering (`render.py`)
**Class**: `ResultRenderer`
**Purpose**: Generate formatted output (README, reports)

**Interface**:
```python
def run(template: Path, output: Path, data_dir: Path) -> None
```

**Responsibilities**:
- Load analysis results
- Apply template rendering
- Generate final output files

## Base Abstraction

All pipeline steps inherit from `PipelineStep`:

```python
class PipelineStep(ABC):
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Implement step-specific logic"""
        pass

    def run(self, **kwargs) -> Any:
        """Execute with logging and error handling"""
        pass
```

### Benefits

1. **Standardization**: All steps follow the same interface pattern
2. **Logging**: Automatic logging of step execution
3. **Error Handling**: Consistent error propagation
4. **Testability**: Easy to mock and test individual steps
5. **Extensibility**: Simple to add new pipeline steps

## Usage

### Individual Steps

```python
from analytics.pipeline import collect, analyse, visualize, render

# Run individual steps
collect.run(username="user", output_dir=Path("data"))
analyse.run(input_dir=Path("data"), output_dir=Path("data"))
visualize.run(data_dir=Path("data"), charts_dir=Path("charts"))
render.run(template=Path("README.template.md"), output=Path("README.md"), data_dir=Path("data"))
```

### Full Pipeline

The `main.py` CLI orchestrates all steps:

```bash
# Run complete pipeline
python main.py run --username "your-github-username"

# Run individual steps
python main.py collect-data --username "user"
python main.py analyze-data
python main.py visualize-data
python main.py render-readme
```

## Extending the Pipeline

To add a new pipeline step:

1. Create a new module in `analytics/pipeline/`
2. Define a class inheriting from `PipelineStep`
3. Implement the `execute()` method
4. Add a module-level `run()` function
5. Update `main.py` to include the new command

Example:

```python
# analytics/pipeline/validate.py
from analytics.pipeline.base import PipelineStep
from pathlib import Path

class Validator(PipelineStep):
    def __init__(self, rules):
        super().__init__("Validator")
        self.rules = rules

    def execute(self, data, **kwargs):
        # Validation logic here
        pass

def run(data_dir: Path, rules_file: Path) -> None:
    # Load data and rules
    validator = Validator(rules)
    validator.run(data=data)
```
