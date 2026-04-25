import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

ZONES = [
    {"nom": "Stade LSS",        "capacite": 15000},
    {"nom": "Salle de Lutte",   "capacite": 5000},
    {"nom": "Fan Zone Plateau", "capacite": 8000},
    {"nom": "Gare Dakar",       "capacite": 6000},
    {"nom": "Stade Iba Mar",    "capacite": 10000},
    {"nom": "Arena Saly",       "capacite": 4000},
    {"nom": "Zone Transit",     "capacite": 3000},
    {"nom": "Village Athletes", "capacite": 2700},
]

JOURS = [
    datetime(2026, 10, 22),
    datetime(2026, 10, 23),
    datetime(2026, 10, 24),
]

HEURES_COMPETITION = [9, 10, 11, 14, 15, 16, 18, 19, 20]

def generer_affluence(capacite, heure, jour_idx):
    if heure in [9, 10, 14, 15, 18, 19]:
        base = 0.75
    elif heure in [11, 16, 20]:
        base = 0.60
    else:
        base = 0.30
    if jour_idx == 1:
        base *= 1.15
    bruit = np.random.normal(0, 0.08)
    taux = min(max(base + bruit, 0.05), 1.10)
    return int(capacite * taux)

def get_statut(taux):
    if taux < 0.60:
        return "normal"
    elif taux < 0.85:
        return "eleve"
    else:
        return "critique"

def get_score_menace(taux):
    if taux < 0.60:
        return int(taux * 50)
    elif taux < 0.85:
        return int(50 + (taux - 0.60) / 0.25 * 30)
    else:
        return int(80 + min((taux - 0.85) / 0.25 * 20, 20))

rows = []
for jour_idx, jour in enumerate(JOURS):
    for heure in HEURES_COMPETITION:
        for zone in ZONES:
            affluence = generer_affluence(zone["capacite"], heure, jour_idx)
            taux = affluence / zone["capacite"]
            rows.append({
                "datetime": jour + timedelta(hours=heure),
                "jour": jour.strftime("%Y-%m-%d"),
                "heure": heure,
                "zone": zone["nom"],
                "capacite": zone["capacite"],
                "affluence": affluence,
                "taux_occupation": round(taux, 3),
                "statut": get_statut(taux),
                "score_menace": get_score_menace(taux),
            })

df = pd.DataFrame(rows)
df.to_csv("data/joj_crowd_data.csv", index=False)
print(f"Dataset généré : {len(df)} lignes")
print(df["statut"].value_counts())

if __name__ == "__main__":
    pass
