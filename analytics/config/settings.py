"""
Configuration settings for the analytics pipeline.
"""
from pathlib import Path
import os

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
ANALYTICS_ROOT = PROJECT_ROOT / "analytics"
CONFIG_DIR = ANALYTICS_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Cache settings
CACHE_ENABLED = True
CACHE_DIR = DATA_DIR / ".cache"
CACHE_TTL_SECONDS = 3600  # 1 hour

# Data source settings
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", None)
GITHUB_API_TIMEOUT = 30  # seconds

# Metric computation settings
METRIC_BATCH_SIZE = 50
COMPUTE_MISSING_METRICS = True

# Normalization settings
DEFAULT_NORMALIZATION_METHOD = "log_minmax"
AVAILABLE_NORMALIZATION_METHODS = ["log_minmax", "z_score", "rank_based"]

# Scoring settings
SCORING_SCALE = 100
MIN_SCORE = 0.0
MAX_SCORE = 100.0

# Chart rendering settings
CHART_DPI = 300
CHART_FORMATS = ["png", "svg"]
DEFAULT_CHART_FORMAT = "png"
CHART_FIGSIZE = (12, 8)

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = OUTPUT_DIR / "analytics.log"

# Validation settings
MIN_REPOS_FOR_ANALYSIS = 1
MAX_REPOS_PER_BATCH = 1000

# Language filtering settings
LANGUAGE_FILTER_CONFIG = CONFIG_DIR / "language_filters.yml"
LANGUAGE_FILTER_ENABLED = True
DEFAULT_EXCLUDED_LANGUAGES = ["HTML", "CSS", "Jupyter Notebook"]

# Time-series tracking settings
HISTORY_DIR = "history"  # Relative to user data dir
MAX_RUNS_PER_USER = 100
INDEX_FILENAME = "index.json"
RUN_FILE_PATTERN = "{run_id}.json"
PRUNE_RUNS_ON_SAVE = True

# Feature flags
ENABLE_CACHING = True
ENABLE_PARALLEL_PROCESSING = True
ENABLE_DETAILED_METRICS = True

# API rate limiting
RATE_LIMIT_REQUESTS = 60
RATE_LIMIT_WINDOW = 60  # seconds

__all__ = [
    "PROJECT_ROOT",
    "ANALYTICS_ROOT",
    "CONFIG_DIR",
    "DATA_DIR",
    "OUTPUT_DIR",
    "CACHE_ENABLED",
    "GITHUB_TOKEN",
    "DEFAULT_NORMALIZATION_METHOD",
    "SCORING_SCALE",
    "LOG_LEVEL",
    "LANGUAGE_FILTER_CONFIG",
    "LANGUAGE_FILTER_ENABLED",
    "HISTORY_DIR",
    "MAX_RUNS_PER_USER",
    "INDEX_FILENAME",
    "RUN_FILE_PATTERN",
    "PRUNE_RUNS_ON_SAVE",
]
