import pytest
from core.data_provider import get_densite

# Representative zone config (Tribune: non-entry zone, bounded output)
_TRIBUNE = {"zone": "Tribune Nord", "cap": 6000, "lat": 14.7005, "lng": -17.4580}
_ENTREE  = {"zone": "Entree Principale", "cap": 2000, "lat": 14.6890, "lng": -17.4553}


# ── Dispatch: all sources return int ─────────────────────────────────────────

@pytest.mark.parametrize("source", [
    "orange_antenna",
    "iot_counter",
    "wifi_hotspot",
    "simulation",
    "unknown_source",   # falls through to _simulate
])
def test_dispatch_returns_int(source):
    zone = {**_TRIBUNE, "source": source}
    result = get_densite(zone, "normal", 14, 50)
    assert isinstance(result, int), f"Expected int, got {type(result)} for source={source}"


# ── All sources stay within [0, 100] ─────────────────────────────────────────

@pytest.mark.parametrize("source", ["orange_antenna", "iot_counter", "wifi_hotspot", "simulation"])
def test_dispatch_in_bounds(source):
    zone = {**_TRIBUNE, "source": source}
    result = get_densite(zone, "normal", 14, 50)
    assert 0 <= result <= 100, f"Out of bounds ({result}) for source={source}"


# ── All scenarios stay within [0, 100] — repeat for randomness ───────────────

@pytest.mark.parametrize("scenario", ["normal", "montee", "critique"])
def test_scenarios_in_bounds(scenario):
    zone = {**_TRIBUNE, "source": "simulation"}
    for _ in range(30):
        result = get_densite(zone, scenario, 14, 50)
        assert 0 <= result <= 100, f"Out of bounds ({result}) for scenario={scenario}"


# ── critique on entry zone → high density (88–98) ────────────────────────────

def test_critique_entree_returns_high_density():
    zone = {**_ENTREE, "source": "simulation"}
    for _ in range(20):
        result = get_densite(zone, "critique", 14, 50)
        assert 88 <= result <= 98, f"Expected 88–98, got {result}"


# ── previous parameter is accepted (signature check) ─────────────────────────

def test_previous_parameter_accepted():
    zone = {**_TRIBUNE, "source": "simulation"}
    result = get_densite(zone, "normal", 14, previous=75)
    assert isinstance(result, int)
