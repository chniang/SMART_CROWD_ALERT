import pytest
from core.prediction import predict_densite, model_available


# ── Sanity check: model loaded ────────────────────────────────────────────────

def test_model_available():
    assert model_available() is True


# ── Returns None when history is too short (< seq_len = 10) ──────────────────

def test_returns_none_empty():
    assert predict_densite([]) is None

def test_returns_none_short_5():
    assert predict_densite([50.0] * 5) is None

def test_returns_none_at_9():
    assert predict_densite([50.0] * 9) is None


# ── Returns float in [5, 100] when history >= 10 ─────────────────────────────

def test_returns_float_at_exactly_10():
    result = predict_densite([50.0] * 10)
    assert result is not None
    assert isinstance(result, float)

def test_returns_float_with_more_than_10():
    result = predict_densite([50.0] * 20)
    assert result is not None
    assert isinstance(result, float)

def test_output_in_bounds_normal_density():
    hist = [40.0, 42.0, 44.0, 43.0, 45.0, 46.0, 44.0, 45.0, 46.0, 47.0]
    result = predict_densite(hist)
    assert 5.0 <= result <= 100.0

def test_output_in_bounds_high_density():
    hist = [85.0, 87.0, 88.0, 89.0, 90.0, 88.0, 89.0, 90.0, 91.0, 92.0]
    result = predict_densite(hist)
    assert 5.0 <= result <= 100.0

def test_output_in_bounds_low_density():
    hist = [10.0, 11.0, 10.0, 12.0, 11.0, 10.0, 11.0, 12.0, 10.0, 11.0]
    result = predict_densite(hist)
    assert 5.0 <= result <= 100.0


# ── Only last seq_len values are used ────────────────────────────────────────

def test_uses_last_10_values():
    # Pad with extreme values that should be ignored
    hist_long  = [99.0] * 10 + [20.0] * 10
    hist_short = [20.0] * 10
    assert predict_densite(hist_long) == predict_densite(hist_short)


# ── Output is a rounded float (1 decimal) ────────────────────────────────────

def test_output_is_rounded():
    result = predict_densite([50.0] * 10)
    assert result == round(result, 1)
