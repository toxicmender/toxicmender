from analytics.exceptions import ValidationError

def require_non_empty(value, name: str):
    if not value:
        raise ValidationError(f"{name} must not be empty")


def require_positive(value, name: str):
    if value <= 0:
        raise ValidationError(f"{name} must be positive")


def require_keys(d: dict, keys: list, context: str = ""):
    missing = [k for k in keys if k not in d]
    if missing:
        raise ValidationError(
            f"Missing keys {missing} in {context or 'data'}"
        )

def require_type(value, expected_type: type, name: str):
    if not isinstance(value, expected_type):
        raise ValidationError(
            f"{name} must be of type {expected_type.__name__}, "
            f"got {type(value).__name__}"
        )

def require_in_range(value, min_value, max_value, name: str):
    if not (min_value <= value <= max_value):
        raise ValidationError(
            f"{name} must be between {min_value} and {max_value}, got {value}"
        )

def require_non_null(value, name: str):
    if value is None:
        raise ValidationError(f"{name} must not be null")

def require_non_empty_string(value: str, name: str):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{name} must be a non-empty string")

def require_list_of_type(value: list, expected_type: type, name: str):
    if not isinstance(value, list):
        raise ValidationError(f"{name} must be a list")
    for i, item in enumerate(value):
        if not isinstance(item, expected_type):
            raise ValidationError(
                f"Item at index {i} in {name} must be of type {expected_type.__name__}, "
                f"got {type(item).__name__}"
            )
