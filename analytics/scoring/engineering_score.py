from typing import Dict, Any

class EngineeringScore:
    def score(self, components: Dict[str, Any]) -> float:
        weights: Dict[str, float] = components["weights"]
        return round(sum(
            components[k] * w
            for k, w in weights.items()
        ) * 100, 2)
