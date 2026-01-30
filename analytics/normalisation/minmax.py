from typing import Dict
import math
import statistics
from analytics.exceptions import ValidationError

def log_minmax(values: Dict[str, float]) -> Dict[str, float]:
    if not values:
        raise ValidationError("Cannot normalize empty dataset")

    if any(v < 0 for v in values.values()):
        raise ValidationError("Values must be >= 0")

    mn, mx = min(values.values()), max(values.values())
    if mn == mx:
        return {k: 1.0 for k in values}

    return {
        k: (math.log(v + 1) - math.log(mn + 1)) /
           (math.log(mx + 1) - math.log(mn + 1))
        for k, v in values.items()
    }

def z_score(values: Dict[str, float]) -> Dict[str, float]:
    """
    Normalize values using Z-score standardization.
    Transforms data to have mean=0 and std=1.
    Returns values centered around 0.5 (shifted for [0,1] range).
    """
    if not values:
        raise ValidationError("Cannot normalize empty dataset")

    value_list = list(values.values())

    if len(value_list) < 2:
        return {k: 0.5 for k in values}

    mean = statistics.mean(value_list)
    stdev = statistics.stdev(value_list)

    if stdev == 0:
        return {k: 0.5 for k in values}

    # Calculate z-scores and shift to [0, 1] range
    # z-score is typically in [-3, 3], we map it to approximately [0, 1]
    z_scores = {
        k: max(0.0, min(1.0, (v - mean) / (3 * stdev) + 0.5))
        for k, v in values.items()
    }

    return z_scores

def rank_based(values: Dict[str, float]) -> Dict[str, float]:
    """
    Normalize values using rank-based normalization.
    Assigns normalized ranks from 0 to 1 based on sorted values.
    """
    if not values:
        raise ValidationError("Cannot normalize empty dataset")

    if len(values) == 1:
        return {k: 1.0 for k in values}

    # Sort by value
    sorted_items = sorted(values.items(), key=lambda x: x[1])
    n = len(sorted_items)

    # Assign average ranks for ties
    result = {}
    i = 0
    while i < n:
        j = i
        while j + 1 < n and sorted_items[j + 1][1] == sorted_items[i][1]:
            j += 1

        # Average rank for ties
        avg_rank = (i + j) / 2
        normalized = avg_rank / (n - 1) if n > 1 else 1.0

        for k in range(i, j + 1):
            result[sorted_items[k][0]] = normalized

        i = j + 1

    return result