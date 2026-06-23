# core/historical_generator.py
"""
Génère un historique simulé de 30 jours (48 points/30min/zone).
Réutilise get_heure_factor() et get_zone_base() de core/simulation.py.

Usage  : python core/historical_generator.py
Output : data/historique_simule.csv
"""

import random
import math
import csv
import os
import sys
from datetime import datetime, timedelta

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

from core.simulation import get_heure_factor, get_zone_base
from server import LIEUX

# ── CONFIG ────────────────────────────────────────────────────────────────────

START_DATE  = datetime(2026, 9, 1)   # 30 jours avant les JOJ (oct 2026)
NB_DAYS     = 30
# Jours de compétition majeure (indices 0–29) : pics d'affluence marqués
EVENT_DAYS  = {7, 14, 22}
RANDOM_SEED = 42
OUT_PATH    = os.path.join(_ROOT, "data", "historique_simule.csv")

# ── FACTEURS JOURNALIERS ──────────────────────────────────────────────────────

def day_factor(day_idx: int, weekday: int) -> float:
    if day_idx in EVENT_DAYS:
        return 1.45    # compétition majeure JOJ : +45 %
    if weekday >= 5:
        return 1.20    # weekend : +20 %
    return 1.0

# ── GÉNÉRATION ────────────────────────────────────────────────────────────────

def generate() -> list:
    random.seed(RANDOM_SEED)
    rows = []

    for lieu, zones in LIEUX.items():
        for zone_cfg in zones:
            zone_name = zone_cfg["zone"]
            # biais persistant par zone : certaines zones naturellement plus chargées
            zone_bias = random.gauss(0, 3)

            for day_idx in range(NB_DAYS):
                current_day = START_DATE + timedelta(days=day_idx)
                weekday     = current_day.weekday()
                d_factor    = day_factor(day_idx, weekday)
                daily_trend = random.gauss(0, 2)   # tendance propre à la journée

                for slot in range(48):             # 48 créneaux de 30 min
                    dt    = current_day + timedelta(minutes=slot * 30)
                    hf    = get_heure_factor(dt.hour)
                    base  = get_zone_base(zone_name, hf)

                    # vague sinusoïdale légère sur la journée (pic de milieu de journée)
                    wave  = 2.5 * math.sin(math.pi * slot / 47)
                    noise = random.gauss(0, 4)

                    densite = base * d_factor + zone_bias + daily_trend + wave + noise
                    densite = round(max(5.0, min(100.0, densite)), 1)

                    rows.append({
                        "lieu":         lieu,
                        "zone":         zone_name,
                        "timestamp":    dt.strftime("%Y-%m-%d %H:%M"),
                        "densite":      densite,
                        "is_event_day": 1 if day_idx in EVENT_DAYS else 0,
                    })
    return rows

# ── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    os.makedirs(os.path.join(_ROOT, "data"), exist_ok=True)
    rows = generate()

    fieldnames = ["lieu", "zone", "timestamp", "densite", "is_event_day"]
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    n_zones = len(set(r["zone"] for r in rows))
    print(f"Fichier : {OUT_PATH}")
    print(f"Lignes  : {len(rows):,}  ({n_zones} zones x {NB_DAYS} jours x 48 pts)")
    print(f"Jours evenement : indices {sorted(EVENT_DAYS)}")
    # apercu densites
    densites = [r["densite"] for r in rows]
    print(f"Densite — min:{min(densites)}  max:{max(densites)}  moy:{sum(densites)/len(densites):.1f}")
