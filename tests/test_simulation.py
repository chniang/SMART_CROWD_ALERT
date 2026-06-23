import pytest
from core.simulation import get_heure_factor, get_zone_base


# ── get_heure_factor ──────────────────────────────────────────────────────────

class TestGetHeureFactor:
    def test_heure_7(self):
        assert get_heure_factor(7) == 0.3

    def test_heure_9(self):
        assert get_heure_factor(9) == 0.7

    def test_heure_14(self):
        assert get_heure_factor(14) == 0.8

    def test_heure_18(self):
        assert get_heure_factor(18) == 0.9

    def test_heure_20(self):
        assert get_heure_factor(20) == 0.85

    def test_heure_12(self):
        assert get_heure_factor(12) == 0.55

    def test_default_early_morning(self):
        assert get_heure_factor(3) == 0.4

    def test_default_midnight(self):
        assert get_heure_factor(0) == 0.4

    def test_default_late_night(self):
        assert get_heure_factor(23) == 0.4

    def test_default_unregistered_hour(self):
        assert get_heure_factor(6) == 0.4


# ── get_zone_base ─────────────────────────────────────────────────────────────

class TestGetZoneBase:
    F = 0.8  # fixed factor for all tests

    # Category 1 — VIP / Medias / Billetterie / Accreditation / Paddock → ×45
    def test_vip(self):
        assert get_zone_base("Zone VIP", self.F) == pytest.approx(self.F * 45)

    def test_medias(self):
        assert get_zone_base("Zone Medias", self.F) == pytest.approx(self.F * 45)

    def test_billetterie(self):
        assert get_zone_base("Zone Billetterie", self.F) == pytest.approx(self.F * 45)

    def test_accreditation(self):
        assert get_zone_base("Zone Accreditation", self.F) == pytest.approx(self.F * 45)

    def test_paddock(self):
        assert get_zone_base("Zone Paddock", self.F) == pytest.approx(self.F * 45)

    # Category 2 — Parking / Echauffement / Aire  → ×50
    def test_parking(self):
        assert get_zone_base("Parking Relais", self.F) == pytest.approx(self.F * 50)

    def test_echauffement(self):
        assert get_zone_base("Piscine d'Echauffement", self.F) == pytest.approx(self.F * 50)

    def test_aire_with_trailing_space(self):
        # 'Aire ' (with space) is the keyword — must appear in zone name
        assert get_zone_base("Aire Breaking / Skate", self.F) == pytest.approx(self.F * 50)

    # Category 3 — Piste / Salle / Hall → ×55
    def test_piste(self):
        assert get_zone_base("Piste d'Athletisme", self.F) == pytest.approx(self.F * 55)

    def test_salle(self):
        assert get_zone_base("Salle de Boxe", self.F) == pytest.approx(self.F * 55)

    def test_hall(self):
        assert get_zone_base("Hall Principal", self.F) == pytest.approx(self.F * 55)

    # Category 4 — Entree / Porte / Quai / Sortie / Arrivee / Depart → ×80
    def test_entree(self):
        assert get_zone_base("Entree Principale", self.F) == pytest.approx(self.F * 80)

    def test_porte(self):
        assert get_zone_base("Porte A — Nord", self.F) == pytest.approx(self.F * 80)

    def test_quai(self):
        assert get_zone_base("Quai Depart", self.F) == pytest.approx(self.F * 80)

    def test_sortie(self):
        assert get_zone_base("Sortie Principale", self.F) == pytest.approx(self.F * 80)

    def test_arrivee(self):
        assert get_zone_base("Zone Arrivee Cyclisme", self.F) == pytest.approx(self.F * 80)

    def test_depart(self):
        assert get_zone_base("Zone Depart Cyclisme", self.F) == pytest.approx(self.F * 80)

    # Category 5 — Tribune / Secteur / Plage / Piscine / Spectateurs / Restauration → ×70
    def test_tribune(self):
        assert get_zone_base("Tribune Nord", self.F) == pytest.approx(self.F * 70)

    def test_secteur(self):
        assert get_zone_base("Secteur A - Nord", self.F) == pytest.approx(self.F * 70)

    def test_plage(self):
        assert get_zone_base("Plage Nord - Engagement", self.F) == pytest.approx(self.F * 70)

    def test_piscine_olympique(self):
        # 'Piscine' without 'Echauffement' falls to category 5
        assert get_zone_base("Piscine Olympique", self.F) == pytest.approx(self.F * 70)

    def test_restauration(self):
        assert get_zone_base("Zone Restauration", self.F) == pytest.approx(self.F * 70)

    def test_spectateurs(self):
        assert get_zone_base("Zone Spectateurs Plage", self.F) == pytest.approx(self.F * 70)

    # Category 6 — default → ×60
    def test_default_unknown(self):
        assert get_zone_base("Zone Inconnue", self.F) == pytest.approx(self.F * 60)

    def test_default_empty(self):
        assert get_zone_base("", self.F) == pytest.approx(self.F * 60)

    # factor = 0 → base always 0
    def test_factor_zero(self):
        assert get_zone_base("Tribune Nord", 0.0) == pytest.approx(0.0)
