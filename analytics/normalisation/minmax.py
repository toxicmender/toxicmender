from typing import Dict
import math
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

# TODO: implement Z-score based normalisation

# TODO: implement Rank-based normalisation