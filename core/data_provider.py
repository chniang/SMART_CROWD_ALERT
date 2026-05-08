# core/data_provider.py
"""
Couche d abstraction des sources de donnees.
Pour brancher l API Orange Network Analytics :
  -> remplacer _fetch_orange_antenna() uniquement
Tout le reste du systeme ne change pas.
"""

import random

# ── INTERFACE PRINCIPALE ──────────────────────────────────────────────────────

def get_densite(zone_config: dict, scenario: str, heure: int, previous: float) -> int:
    """
    Point d entree unique pour obtenir la densite d une zone.
    Dispatche vers la bonne source selon zone_config["source"].
    """
    source = zone_config.get("source", "simulation")

    if source == "orange_antenna":
        return _fetch_orange_antenna(zone_config, scenario, heure)
    elif source == "iot_counter":
        return _fetch_iot_counter(zone_config, scenario, heure)
    elif source == "wifi_hotspot":
        return _fetch_wifi_hotspot(zone_config, scenario, heure)
    else:
        return _simulate(zone_config, scenario, heure)


# ── SOURCES REELLES (a implementer avec Sonatel) ──────────────────────────────

def _fetch_orange_antenna(zone_config: dict, scenario: str, heure: int) -> int:
    """
    TODO V2 : Appel API Orange Network Analytics
    Endpoint cible : GET /network-analytics/crowd-density
    Params         : lat, lng, radius, timestamp
    Auth           : Bearer token Sonatel

    Exemple futur :
        response = requests.get(
            ORANGE_API_URL,
            params={"lat": zone_config["lat"], "lng": zone_config["lng"]},
            headers={"Authorization": f"Bearer {ORANGE_API_KEY}"}
        )
        return response.json()["density_percent"]
    """
    return _simulate(zone_config, scenario, heure)


def _fetch_iot_counter(zone_config: dict, scenario: str, heure: int) -> int:
    """
    TODO V2 : Lecture capteurs IoT (entrees/sorties)
    Pour l instant : simulation calibree
    """
    return _simulate(zone_config, scenario, heure)


def _fetch_wifi_hotspot(zone_config: dict, scenario: str, heure: int) -> int:
    """
    TODO V2 : Donnees hotspots WiFi Orange
    Pour l instant : simulation calibree
    """
    return _simulate(zone_config, scenario, heure)


# ── SIMULATION (MVP actuel) ────────────────────────────────────────────────────

def _simulate(zone_config: dict, scenario: str, heure: int) -> int:
    from core.simulation import get_zone_base, get_heure_factor
    zone_name = zone_config["zone"]
    heure_factor = get_heure_factor(heure)

    if scenario == 'montee':
        base = min(95, get_zone_base(zone_name, heure_factor) + 18)
        return int(min(100, max(10, base + random.uniform(-5, 5))))
    elif scenario == 'critique' and any(
        x in zone_name for x in ['Entree', 'Porte', 'Quai', 'Sortie', 'Arrivee', 'Depart']
    ):
        return random.randint(88, 98)
    else:
        base = get_zone_base(zone_name, heure_factor)
        return int(min(100, max(5, base + random.uniform(-10, 10))))
