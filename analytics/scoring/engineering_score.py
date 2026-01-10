class EngineeringScore:
    def score(self, components):
        return round(sum(
            components[k] * w
            for k, w in components["weights"].items()
        ) * 100, 2)
