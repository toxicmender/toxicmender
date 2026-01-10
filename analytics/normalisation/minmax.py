import math

def log_minmax(values: dict) -> dict:
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