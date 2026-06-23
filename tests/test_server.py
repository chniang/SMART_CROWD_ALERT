import pytest
from server import compute_risk_score


# ── Base: score = density when no bonuses apply ───────────────────────────────

def test_base_score_equals_density():
    # stable trend, off-peak hour (8), neutral zone → no bonus
    assert compute_risk_score(50, "stable", 8, "Tribune Nord") == 50

def test_base_score_zero_density():
    assert compute_risk_score(0, "stable", 8, "Tribune") == 0

def test_base_score_high_density():
    assert compute_risk_score(84, "stable", 8, "Tribune") == 84


# ── Trend bonuses ─────────────────────────────────────────────────────────────

def test_hausse_rapide_adds_15():
    assert compute_risk_score(50, "hausse_rapide", 8, "Tribune") == 65

def test_hausse_adds_8():
    assert compute_risk_score(50, "hausse", 8, "Tribune") == 58

def test_baisse_no_bonus():
    assert compute_risk_score(50, "baisse", 8, "Tribune") == 50

def test_baisse_rapide_no_bonus():
    assert compute_risk_score(50, "baisse_rapide", 8, "Tribune") == 50

def test_stable_no_bonus():
    assert compute_risk_score(50, "stable", 8, "Tribune") == 50


# ── Hour bonuses ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize("heure", [9, 10, 14, 15, 18, 19, 20])
def test_peak_hours_add_10(heure):
    score = compute_risk_score(50, "stable", heure, "Tribune")
    assert score == 60, f"Expected 60 for heure={heure}, got {score}"

@pytest.mark.parametrize("heure", [11, 16])
def test_medium_hours_add_5(heure):
    score = compute_risk_score(50, "stable", heure, "Tribune")
    assert score == 55, f"Expected 55 for heure={heure}, got {score}"

@pytest.mark.parametrize("heure", [0, 3, 7, 8, 12, 13, 17, 21, 23])
def test_off_peak_hours_no_bonus(heure):
    score = compute_risk_score(50, "stable", heure, "Tribune")
    assert score == 50, f"Expected 50 for heure={heure}, got {score}"


# ── Zone bonuses ──────────────────────────────────────────────────────────────

def test_entree_adds_10():
    assert compute_risk_score(50, "stable", 8, "Entree Principale") == 60

def test_porte_adds_10():
    assert compute_risk_score(50, "stable", 8, "Porte A — Nord") == 60

def test_arrivee_adds_10():
    assert compute_risk_score(50, "stable", 8, "Zone Arrivee Cyclisme") == 60

def test_depart_adds_10():
    assert compute_risk_score(50, "stable", 8, "Zone Depart Cyclisme") == 60

def test_quai_adds_8():
    # "Quai 1 — Dakar" contains "Quai" but none of Entree/Porte/Arrivee/Depart
    assert compute_risk_score(50, "stable", 8, "Quai 1 — Dakar") == 58

def test_parking_adds_3():
    assert compute_risk_score(50, "stable", 8, "Parking Relais") == 53

def test_neutral_zone_no_bonus():
    assert compute_risk_score(50, "stable", 8, "Secteur A - Nord") == 50


# ── Cap at 100 ────────────────────────────────────────────────────────────────

def test_score_capped_at_100_simple():
    # 90 + hausse_rapide(15) = 105 → 100
    assert compute_risk_score(90, "hausse_rapide", 8, "Tribune") == 100

def test_score_capped_at_100_all_bonuses():
    # 80 + hausse_rapide(15) + peak(10) + Entree(10) = 115 → 100
    assert compute_risk_score(80, "hausse_rapide", 14, "Entree Principale") == 100

def test_score_already_100():
    assert compute_risk_score(100, "stable", 8, "Tribune") == 100

def test_score_not_exceeded():
    result = compute_risk_score(95, "hausse_rapide", 20, "Entree Principale")
    assert result == 100
