import pytest
from analytics.normalisation.minmax import log_minmax, z_score, rank_based
from analytics.exceptions import ValidationError

# ============ log_minmax tests ============

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
    assert norm["a"] == 1.0  # Single value should map to 1.0

def test_normalization_identical_values():
    data = {"a": 20, "b": 20, "c": 20}
    norm = log_minmax(data)
    for value in norm.values():
        assert value == 1.0  # All identical values should map to 1.0

def test_normalization_negative_values():
    data = {"a": -10, "b": -1, "c": 0}
    with pytest.raises(ValidationError):
        log_minmax(data)

def test_normalization_mixed_values():
    data = {"a": 0, "b": 50, "c": 100, "d": 1000}
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

# ============ z_score tests ============

def test_z_score_empty():
    with pytest.raises(ValidationError):
        z_score({})

def test_z_score_single_value():
    data = {"a": 100}
    norm = z_score(data)
    assert norm["a"] == 0.5  # Single value maps to 0.5 (center)

def test_z_score_two_values():
    data = {"a": 10, "b": 20}
    norm = z_score(data)
    assert 0 <= norm["a"] <= 1
    assert 0 <= norm["b"] <= 1
    # Lower value should be < higher value
    assert norm["a"] < norm["b"]

def test_z_score_identical_values():
    data = {"a": 50, "b": 50, "c": 50}
    norm = z_score(data)
    # All identical values should map to 0.5 (center)
    for value in norm.values():
        assert value == 0.5

def test_z_score_three_values():
    data = {"a": 1, "b": 2, "c": 3}
    norm = z_score(data)
    for value in norm.values():
        assert 0 <= value <= 1
    # Middle value should be close to 0.5
    assert 0.4 < norm["b"] < 0.6

def test_z_score_large_spread():
    data = {"a": 0, "b": 50, "c": 100}
    norm = z_score(data)
    for value in norm.values():
        assert 0 <= value <= 1

def test_z_score_negative_values():
    data = {"a": -100, "b": 0, "c": 100}
    norm = z_score(data)
    for value in norm.values():
        assert 0 <= value <= 1
    # Mean is 0, so center should be near 0.5
    assert norm["b"] == pytest.approx(0.5, abs=0.1)

def test_z_score_preserves_order():
    data = {"a": 10, "b": 20, "c": 30}
    norm = z_score(data)
    assert norm["a"] < norm["b"] < norm["c"]

def test_z_score_multiple_values():
    data = {"a": 1, "b": 5, "c": 10, "d": 15, "e": 20}
    norm = z_score(data)
    for value in norm.values():
        assert 0 <= value <= 1
    # Values should maintain order
    sorted_keys = sorted(data.keys(), key=lambda k: data[k])
    sorted_norms = [norm[k] for k in sorted_keys]
    assert sorted_norms == sorted(sorted_norms)

# ============ rank_based tests ============

def test_rank_based_empty():
    with pytest.raises(ValidationError):
        rank_based({})

def test_rank_based_single_value():
    data = {"a": 100}
    norm = rank_based(data)
    assert norm["a"] == 1.0

def test_rank_based_two_values():
    data = {"a": 10, "b": 20}
    norm = rank_based(data)
    assert norm["a"] == 0.0  # Lower rank
    assert norm["b"] == 1.0  # Higher rank

def test_rank_based_three_values():
    data = {"a": 1, "b": 3, "c": 2}
    norm = rank_based(data)
    assert norm["a"] == 0.0    # Lowest
    assert norm["c"] == 0.5    # Middle
    assert norm["b"] == 1.0    # Highest

def test_rank_based_identical_values():
    data = {"a": 50, "b": 50, "c": 50}
    norm = rank_based(data)
    # All identical values get same rank
    assert norm["a"] == norm["b"] == norm["c"]

def test_rank_based_many_values():
    data = {f"item_{i}": i for i in range(10)}
    norm = rank_based(data)
    assert norm["item_0"] == 0.0
    assert norm["item_9"] == 1.0
    for i in range(10):
        assert 0 <= norm[f"item_{i}"] <= 1

def test_rank_based_preserves_order():
    data = {"a": 100, "b": 50, "c": 75}
    norm = rank_based(data)
    assert norm["b"] < norm["c"] < norm["a"]

def test_rank_based_duplicate_values():
    data = {"a": 1, "b": 2, "c": 2, "d": 3}
    norm = rank_based(data)
    # Items with same value should be ranked sequentially
    assert norm["a"] == 0.0
    assert norm["b"] < norm["c"]  # Both are 2, ordered by insertion
    assert norm["d"] == 1.0

def test_rank_based_negative_values():
    data = {"a": -100, "b": 0, "c": 100}
    norm = rank_based(data)
    assert norm["a"] == 0.0
    assert norm["b"] == 0.5
    assert norm["c"] == 1.0

def test_rank_based_floats():
    data = {"a": 1.1, "b": 2.2, "c": 3.3}
    norm = rank_based(data)
    assert norm["a"] == 0.0
    assert norm["b"] == 0.5
    assert norm["c"] == 1.0
