import pytest
from analytics.normalization.minmax import log_minmax
from analytics.exceptions import ValidationError

def test_normalization_basic():
    data = {"a": 10, "b": 100}
    norm = log_minmax(data)
    assert 0 <= norm["a"] <= 1
    assert 0 <= norm["b"] <= 1


def test_normalization_empty():
    with pytest.raises(ValidationError):
        log_minmax({})

def test_normalization_single_value():
    data = {"a": 50}
    norm = log_minmax(data)
    assert norm["a"] == 0.0  # Single value should map to 0.0

def test_normalization_identical_values():
    data = {"a": 20, "b": 20, "c": 20}
    norm = log_minmax(data)
    for value in norm.values():
        assert value == 0.0  # All identical values should map to 0.0

def test_normalization_negative_values():
    data = {"a": -10, "b": -1, "c": 0}
    norm = log_minmax(data)
    assert 0 <= norm["a"] <= 1
    assert 0 <= norm["b"] <= 1
    assert 0 <= norm["c"] <= 1

def test_normalization_mixed_values():
    data = {"a": -50, "b": 0, "c": 50, "d": 100}
    norm = log_minmax(data)
    for value in norm.values():
        assert 0 <= value <= 1

def test_normalization_large_range():
    data = {"a": 1, "b": 1000, "c": 1000000}
    norm = log_minmax(data)
    for value in norm.values():
        assert 0 <= value <= 1

def test_normalization_small_range():
    data = {"a": 0.1, "b": 0.2, "c": 0.3}
    norm = log_minmax(data)
    for value in norm.values():
        assert 0 <= value <= 1

def test_normalization_floats():
    data = {"a": 1.5, "b": 2.5, "c": 3.5}
    norm = log_minmax(data)
    for value in norm.values():
        assert 0 <= value <= 1
