from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import json
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.alerts import analyser_toutes_zones, generer_notifications
from core.kpis import calculer_kpis

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

df_base = pd.read_csv("data/joj_crowd_data.csv")

LIEUX = {
    "Stade Abdoulaye Wade": [
        {"zone": "Tribune Nord",      "capacite": 10000},
        {"zone": "Tribune Sud",       "capacite": 10000},
        {"zone": "Tribune Est",       "capacite": 4000},
        {"zone": "Tribune Ouest",     "capacite": 4000},
        {"zone": "Entrée Principale", "capacite": 5000},
        {"zone": "Entrée Secondaire", "capacite": 2500},
        {"zone": "Zone VIP",          "capacite": 1000},
        {"zone": "Parking",           "capacite": 3000},
    ],
    "Dakar Arena": [
        {"zone": "Secteur A",         "capacite": 4000},
        {"zone": "Secteur B",         "capacite": 4000},
        {"zone": "Secteur C",         "capacite": 4000},
        {"zone": "Secteur D",         "capacite": 4000},
        {"zone": "Entrée Principale", "capacite": 3000},
        {"zone": "Entrée Secondaire", "capacite": 2000},
        {"zone": "Zone Médias",       "capacite": 500},
        {"zone": "Parking",           "capacite": 2000},
    ],
    "Stade Iba Mar Diop": [
        {"zone": "Tribune Nord",      "capacite": 6000},
        {"zone": "Tribune Sud",       "capacite": 6000},
        {"zone": "Tribune Est",       "capacite": 2500},
        {"zone": "Tribune Ouest",     "capacite": 2500},
        {"zone": "Entrée Principale", "capacite": 3000},
        {"zone": "Entrée Secondaire", "capacite": 1500},
        {"zone": "Fan Zone",          "capacite": 2000},
        {"zone": "Parking",           "capacite": 1500},
    ],
    "Corniche Ouest": [
        {"zone": "Zone Plage Nord",   "capacite": 5000},
        {"zone": "Zone Plage Sud",    "capacite": 5000},
        {"zone": "Zone VIP",          "capacite": 1000},
        {"zone": "Entrée Principale", "capacite": 3000},
        {"zone": "Zone Restauration", "capacite": 2000},
        {"zone": "Parking",           "capacite": 1500},
        {"zone": "Zone Médias",       "capacite": 300},
    ],
    "Complexe Tour de l'Oeuf": [
        {"zone": "Piscine Principale","capacite": 3000},
        {"zone": "Piscine Secondaire","capacite": 2000},
        {"zone": "Tribune Piscine",   "capacite": 2500},
        {"zone": "Entrée Principale", "capacite": 2000},
        {"zone": "Zone Échauffement", "capacite": 800},
        {"zone": "Zone Médias",       "capacite": 300},
        {"zone": "Parking",           "capacite": 1000},
    ],
    "Saly Beach West": [
        {"zone": "Plage Principale",  "capacite": 8000},
        {"zone": "Zone Compétition",  "capacite": 3000},
        {"zone": "Zone Spectateurs",  "capacite": 5000},
        {"zone": "Entrée Nord",       "capacite": 2000},
        {"zone": "Entrée Sud",        "capacite": 2000},
        {"zone": "Zone VIP",          "capacite": 500},
        {"zone": "Zone Médias",       "capacite": 300},
        {"zone": "Parking",           "capacite": 1000},
    ],
    "Gare Obélisque (BRT)": [
        {"zone": "Porte A — Nord",    "capacite": 1200},
        {"zone": "Porte B — Centre",  "capacite": 1200},
        {"zone": "Porte C — Sud",     "capacite": 1200},
        {"zone": "Quai Départ",       "capacite": 2000},
        {"zone": "Quai Arrivée",      "capacite": 2000},
        {"zone": "Hall Principal",    "capacite": 3000},
        {"zone": "Zone Billetterie",  "capacite": 800},
        {"zone": "Parking Relais",    "capacite": 800},
    ],
    "Gare Colobane (TER)": [
        {"zone": "Quai 1 — Dakar",      "capacite": 1500},
        {"zone": "Quai 2 — Diamniadio", "capacite": 1500},
        {"zone": "Hall Accueil",        "capacite": 2500},
        {"zone": "Zone Contrôle",       "capacite": 1000},
        {"zone": "Sortie Principale",   "capacite": 800},
        {"zone": "Sortie Secondaire",   "capacite": 500},
        {"zone": "Zone Attente",        "capacite": 700},
        {"zone": "Parking TER",         "capacite": 600},
    ],
}

SCENARIO = "normal"

def get_heure_factor(heure):
    factors = {7: 0.3, 8: 0.3, 9: 0.7, 10: 0.7, 11: 0.65,
               12: 0.55, 13: 0.55, 14: 0.8, 15: 0.8, 16: 0.75,
               17: 0.7, 18: 0.9, 19: 0.9, 20: 0.85}
    return factors.get(heure, 0.4)

def compute_risk_score(densite, trend, heure, zone_name):
    score = densite
    if trend == 'hausse_rapide': score += 15
    elif trend == 'hausse': score += 8
    if heure in [9,10,14,15,18,19,20]: score += 10
    elif heure in [11,16]: score += 5
    if 'Entrée' in zone_name or 'Porte' in zone_name: score += 10
    elif 'Quai' in zone_name: score += 8
    elif 'Parking' in zone_name: score += 3
    return min(100, score)

@app.route('/')
def index():
    return send_from_directory('.', 'dashboard.html')

@app.route('/api/jours')
def get_jours():
    return jsonify(sorted(df_base['jour'].unique().tolist()))

@app.route('/api/heures')
def get_heures():
    return jsonify(sorted(df_base['heure'].unique().tolist()))

@app.route('/api/data')
def get_data():
    jour = request.args.get('jour', df_base['jour'].max())
    heure = int(request.args.get('heure', 14))
    live = request.args.get('live', 'false') == 'true'

    snap = df_base[(df_base['jour']==jour) & (df_base['heure']==heure)].copy()

    if live:
        bruit = np.random.uniform(-0.06, 0.10, size=len(snap))
        snap['taux_occupation'] = (snap['taux_occupation'] + bruit).clip(0.05, 1.10)
        snap['affluence'] = (snap['taux_occupation'] * snap['capacite']).astype(int)

    da = analyser_toutes_zones(snap)
    kpis = calculer_kpis(da)
    notifs = generer_notifications(da)

    return jsonify({
        'kpis': {
            'zones_critiques': int(kpis['zones_critiques']),
            'zones_elevees':   int(kpis['zones_elevees']),
            'taux_occupation_moyen': float(kpis['taux_occupation_moyen']),
            'score_global':    float(kpis['score_global']),
            'zone_plus_chargee': kpis['zone_plus_chargee'],
            'taux_zone_max':   float(kpis['taux_zone_max']),
            'niveau_global':   kpis['niveau_global'],
        },
        'alertes': notifs,
        'zones': da[['zone','taux_occupation','statut','score_menace',
                     'affluence','capacite','couleur_hex','message','action']].to_dict('records'),
    })

@app.route('/api/evolution')
def get_evolution():
    jour = request.args.get('jour', df_base['jour'].max())
    zone = request.args.get('zone', '')
    dz = df_base[(df_base['jour']==jour) & (df_base['zone']==zone)].sort_values('heure')
    taux = (dz['taux_occupation'] * 100).round(1).tolist()
    statuts = ['critique' if t >= 85 else 'eleve' if t >= 60 else 'normal' for t in taux]
    return jsonify({
        'heures':  dz['heure'].tolist(),
        'taux':    taux,
        'statuts': statuts,
    })

@app.route('/api/scenario')
def set_scenario():
    global SCENARIO
    mode = request.args.get('mode', 'normal')
    if mode in ['normal', 'montee', 'critique']:
        SCENARIO = mode
    return jsonify({'scenario': SCENARIO, 'status': 'ok'})

@app.route('/data.json')
def get_data_json():
    return send_from_directory('.', 'data.json')

@app.route('/api/refresh')
def refresh_data():
    import random
    from datetime import datetime
    _now = datetime.now()
    now  = _now.strftime("%H:%M:%S")
    heure = _now.hour

    try:
        with open("data.json", "r", encoding="utf-8") as f:
            prev_raw = json.load(f)
        prev_map = {}
        if isinstance(prev_raw, dict):
            for zones in prev_raw.values():
                for z in zones:
                    prev_map[z["zone"]] = z["densite"]
        else:
            for z in prev_raw:
                prev_map[z.get("zone", "")] = z.get("densite", 50)
    except Exception:
        prev_map = {}

    all_results = {}
    for lieu, zones in LIEUX.items():
        result = []
        _critique_idx = (random.sample(range(len(zones)), min(2, len(zones)))
                         if SCENARIO == 'critique' else [])
        for i, z in enumerate(zones):
            if SCENARIO == 'montee':
                base = min(95, get_heure_factor(heure) * 100 + 15)
                densite = int(min(100, max(5, base + random.uniform(-5, 5))))
            elif SCENARIO == 'critique' and i in _critique_idx:
                densite = random.randint(88, 98)
            else:
                base = get_heure_factor(heure) * 100
                densite = int(min(100, max(5, base + random.uniform(-8, 8))))
            previous = prev_map.get(z["zone"], densite)
            delta = densite - previous

            if delta > 10:
                trend = "hausse_rapide"; trend_icon = "⬆⬆"; trend_label = "hausse rapide"
            elif delta > 3:
                trend = "hausse";        trend_icon = "⬆";  trend_label = "en hausse"
            elif delta < -10:
                trend = "baisse_rapide"; trend_icon = "⬇⬇"; trend_label = "baisse rapide"
            elif delta < -3:
                trend = "baisse";        trend_icon = "⬇";  trend_label = "en baisse"
            else:
                trend = "stable";        trend_icon = "→";  trend_label = "stable"

            if densite >= 85:
                status = "danger"
                if trend in ["hausse", "hausse_rapide"]:
                    risk_reason = f"Densité {densite}% + {trend_label} — risque critique"
                else:
                    risk_reason = f"Densité critique à {densite}% — intervention requise"
            elif densite >= 60:
                status = "modere"
                if trend == "hausse_rapide":
                    risk_reason = f"Densité {densite}% avec hausse rapide — surveiller"
                else:
                    risk_reason = f"Affluence élevée à {densite}% — surveillance renforcée"
            else:
                status = "fluide"
                risk_reason = f"Situation normale à {densite}% — flux fluide"

            risk_score = compute_risk_score(densite, trend, heure, z["zone"])

            result.append({
                "zone":        z["zone"],
                "capacite":    z["capacite"],
                "personnes":   int(z["capacite"] * densite / 100),
                "densite":     densite,
                "previous":    previous,
                "delta":       delta,
                "trend":       trend,
                "trend_icon":  trend_icon,
                "trend_label": trend_label,
                "status":      status,
                "risk_score":  min(100, risk_score),
                "risk_reason": risk_reason,
                "time":        now
            })
        capacite_totale  = sum(zn["capacite"] for zn in zones)
        total_affluence  = sum(r["personnes"] for r in result)
        taux_remplissage = round(total_affluence / capacite_totale * 100, 1) if capacite_totale > 0 else 0.0
        for r in result:
            r["capacite_totale_site"]  = capacite_totale
            r["taux_remplissage_site"] = taux_remplissage
        all_results[lieu] = result

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    return jsonify(all_results)

@app.route('/api/lieu')
def get_lieu():
    lieu = request.args.get('lieu', 'Stade LSS')
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        zones = data.get(lieu, [])
        return jsonify(zones)
    except Exception:
        return jsonify([])

import os as _os
if not _os.path.exists("data.json"):
    with app.test_client() as c:
        c.get('/api/refresh')

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
