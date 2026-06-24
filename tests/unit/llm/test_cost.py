"""Unit tests for the token/cost estimator."""

from mars777_cop_thief.llm.cost import estimate_cost, estimate_tokens


def test_empty_text_is_zero_tokens():
    assert estimate_tokens("") == 0


def test_non_empty_text_has_positive_tokens():
    assert estimate_tokens("abcd") >= 1
    assert estimate_tokens("a" * 40) >= 10


def test_cost_is_zero_for_zero_rate():
    assert estimate_cost(100, 50, 0.0) == 0.0


def test_cost_is_non_negative_and_scales():
    assert estimate_cost(1000, 0, 1.0) == 1.0
    assert estimate_cost(-5, -5, -1.0) == 0.0  # clamped, never negative
