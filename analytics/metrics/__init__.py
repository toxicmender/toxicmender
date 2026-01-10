"""
Metrics module for computing repository quality metrics.
Provides various metric implementations for analysis.
"""

from analytics.metrics.base import Metric
from analytics.metrics.loc import LOCMetric
from analytics.metrics.efficiency import EfficiencyMetric
from analytics.metrics.breadth import BreadthMetric
from analytics.metrics.consistency import ConsistencyMetric
from analytics.metrics.impact import ImpactMetric
from analytics.metrics.scale import ScaleMetric

__all__ = [
    "Metric",
    "LOCMetric",
    "EfficiencyMetric",
    "BreadthMetric",
    "ConsistencyMetric",
    "ImpactMetric",
    "ScaleMetric",
]
