import pytest
from analytics.scoring.engineering_score import EngineeringScore


def test_engineering_score_basic():
    """Test basic engineering score calculation."""
    scorer = EngineeringScore()

    components = {
        "metric1": 0.8,
        "metric2": 0.6,
        "weights": {"metric1": 0.6, "metric2": 0.4}
    }

    score = scorer.score(components)
    # (0.8 * 0.6 + 0.6 * 0.4) * 100 = (0.48 + 0.24) * 100 = 72.0
    assert score == pytest.approx(72.0, abs=0.1)


def test_engineering_score_single_component():
    """Test engineering score with single component."""
    scorer = EngineeringScore()

    components = {
        "metric1": 0.9,
        "weights": {"metric1": 1.0}
    }

    score = scorer.score(components)
    assert score == pytest.approx(90.0, abs=0.1)


def test_engineering_score_equal_weights():
    """Test engineering score with equal weights."""
    scorer = EngineeringScore()

    components = {
        "metric1": 1.0,
        "metric2": 0.5,
        "weights": {"metric1": 0.5, "metric2": 0.5}
    }

    score = scorer.score(components)
    # (1.0 * 0.5 + 0.5 * 0.5) * 100 = (0.5 + 0.25) * 100 = 75.0
    assert score == pytest.approx(75.0, abs=0.1)


def test_engineering_score_zero_score():
    """Test engineering score with all zero components."""
    scorer = EngineeringScore()

    components = {
        "metric1": 0.0,
        "metric2": 0.0,
        "weights": {"metric1": 0.5, "metric2": 0.5}
    }

    score = scorer.score(components)
    assert score == pytest.approx(0.0, abs=0.1)


def test_engineering_score_perfect_score():
    """Test engineering score with perfect components."""
    scorer = EngineeringScore()

    components = {
        "metric1": 1.0,
        "metric2": 1.0,
        "metric3": 1.0,
        "weights": {"metric1": 0.33, "metric2": 0.33, "metric3": 0.34}
    }

    score = scorer.score(components)
    assert score == pytest.approx(100.0, abs=1.0)


def test_engineering_score_three_components():
    """Test engineering score with three components."""
    scorer = EngineeringScore()

    components = {
        "quality": 0.8,
        "performance": 0.6,
        "maintenance": 0.7,
        "weights": {"quality": 0.4, "performance": 0.3, "maintenance": 0.3}
    }

    score = scorer.score(components)
    # (0.8 * 0.4 + 0.6 * 0.3 + 0.7 * 0.3) * 100
    # = (0.32 + 0.18 + 0.21) * 100 = 71.0
    assert score == pytest.approx(71.0, abs=0.1)


def test_engineering_score_fractional_components():
    """Test engineering score with fractional components."""
    scorer = EngineeringScore()

    components = {
        "metric1": 0.123,
        "metric2": 0.456,
        "weights": {"metric1": 0.3, "metric2": 0.7}
    }

    score = scorer.score(components)
    # (0.123 * 0.3 + 0.456 * 0.7) * 100
    # = (0.0369 + 0.3192) * 100 = 35.61
    assert score == pytest.approx(35.61, abs=0.1)


def test_engineering_score_asymmetric_weights():
    """Test engineering score with heavily weighted components."""
    scorer = EngineeringScore()

    components = {
        "critical": 0.9,
        "minor": 0.1,
        "weights": {"critical": 0.9, "minor": 0.1}
    }

    score = scorer.score(components)
    # (0.9 * 0.9 + 0.1 * 0.1) * 100 = (0.81 + 0.01) * 100 = 82.0
    assert score == pytest.approx(82.0, abs=0.1)


def test_engineering_score_precision():
    """Test that engineering score returns proper precision."""
    scorer = EngineeringScore()

    components = {
        "metric1": 0.5,
        "metric2": 0.5,
        "weights": {"metric1": 0.5, "metric2": 0.5}
    }

    score = scorer.score(components)
    # Should be rounded to 2 decimal places: 50.0
    assert isinstance(score, float)
    assert score == 50.0
