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
        {"zone": "Tribune Nord",      "capacite": 10000, "lat": 14.7250, "lng": -17.4671},
        {"zone": "Tribune Sud",       "capacite": 10000, "lat": 14.7238, "lng": -17.4671},
        {"zone": "Tribune Est",       "capacite":  4000, "lat": 14.7244, "lng": -17.4660},
        {"zone": "Tribune Ouest",     "capacite":  4000, "lat": 14.7244, "lng": -17.4682},
        {"zone": "Entrée Principale", "capacite":  5000, "lat": 14.7232, "lng": -17.4671},
        {"zone": "Entrée Secondaire", "capacite":  2500, "lat": 14.7258, "lng": -17.4665},
        {"zone": "Zone VIP",          "capacite":  1000, "lat": 14.7244, "lng": -17.4667},
        {"zone": "Parking",           "capacite":  3000, "lat": 14.7222, "lng": -17.4678},
    ],
    "Dakar Arena": [
        {"zone": "Secteur A",         "capacite": 4000, "lat": 14.7291, "lng": -17.2461},
        {"zone": "Secteur B",         "capacite": 4000, "lat": 14.7291, "lng": -17.2477},
        {"zone": "Secteur C",         "capacite": 4000, "lat": 14.7277, "lng": -17.2461},
        {"zone": "Secteur D",         "capacite": 4000, "lat": 14.7277, "lng": -17.2477},
        {"zone": "Entrée Principale", "capacite": 3000, "lat": 14.7269, "lng": -17.2469},
        {"zone": "Entrée Secondaire", "capacite": 2000, "lat": 14.7299, "lng": -17.2469},
        {"zone": "Zone Médias",       "capacite":  500, "lat": 14.7284, "lng": -17.2454},
        {"zone": "Parking",           "capacite": 2000, "lat": 14.7260, "lng": -17.2482},
    ],
    "Stade Iba Mar Diop": [
        {"zone": "Tribune Nord",      "capacite": 6000, "lat": 14.6885, "lng": -17.4452},
        {"zone": "Tribune Sud",       "capacite": 6000, "lat": 14.6869, "lng": -17.4452},
        {"zone": "Tribune Est",       "capacite": 2500, "lat": 14.6877, "lng": -17.4443},
        {"zone": "Tribune Ouest",     "capacite": 2500, "lat": 14.6877, "lng": -17.4461},
        {"zone": "Entrée Principale", "capacite": 3000, "lat": 14.6863, "lng": -17.4452},
        {"zone": "Entrée Secondaire", "capacite": 1500, "lat": 14.6891, "lng": -17.4452},
        {"zone": "Fan Zone",          "capacite": 2000, "lat": 14.6877, "lng": -17.4437},
        {"zone": "Parking",           "capacite": 1500, "lat": 14.6855, "lng": -17.4460},
    ],
    "Corniche Ouest": [
        {"zone": "Zone Plage Nord",   "capacite": 5000, "lat": 14.7082, "lng": -17.4958},
        {"zone": "Zone Plage Sud",    "capacite": 5000, "lat": 14.7038, "lng": -17.4962},
        {"zone": "Zone VIP",          "capacite": 1000, "lat": 14.7065, "lng": -17.4948},
        {"zone": "Entrée Principale", "capacite": 3000, "lat": 14.7060, "lng": -17.4972},
        {"zone": "Zone Restauration", "capacite": 2000, "lat": 14.7055, "lng": -17.4952},
        {"zone": "Parking",           "capacite": 1500, "lat": 14.7048, "lng": -17.4978},
        {"zone": "Zone Médias",       "capacite":  300, "lat": 14.7072, "lng": -17.4944},
    ],
    "Complexe Tour de l'Oeuf": [
        {"zone": "Piscine Principale","capacite": 3000, "lat": 14.6943, "lng": -17.4848},
        {"zone": "Piscine Secondaire","capacite": 2000, "lat": 14.6937, "lng": -17.4852},
        {"zone": "Tribune Piscine",   "capacite": 2500, "lat": 14.6946, "lng": -17.4844},
        {"zone": "Entrée Principale", "capacite": 2000, "lat": 14.6931, "lng": -17.4856},
        {"zone": "Zone Échauffement", "capacite":  800, "lat": 14.6935, "lng": -17.4842},
        {"zone": "Zone Médias",       "capacite":  300, "lat": 14.6949, "lng": -17.4841},
        {"zone": "Parking",           "capacite": 1000, "lat": 14.6927, "lng": -17.4862},
    ],
    "Saly Beach West": [
        {"zone": "Plage Principale",  "capacite": 8000, "lat": 14.4558, "lng": -17.0184},
        {"zone": "Zone Compétition",  "capacite": 3000, "lat": 14.4544, "lng": -17.0193},
        {"zone": "Zone Spectateurs",  "capacite": 5000, "lat": 14.4563, "lng": -17.0199},
        {"zone": "Entrée Nord",       "capacite": 2000, "lat": 14.4574, "lng": -17.0190},
        {"zone": "Entrée Sud",        "capacite": 2000, "lat": 14.4528, "lng": -17.0190},
        {"zone": "Zone VIP",          "capacite":  500, "lat": 14.4550, "lng": -17.0176},
        {"zone": "Zone Médias",       "capacite":  300, "lat": 14.4556, "lng": -17.0203},
        {"zone": "Parking",           "capacite": 1000, "lat": 14.4538, "lng": -17.0212},
    ],
    "Gare Obélisque (BRT)": [
        {"zone": "Porte A — Nord",    "capacite": 1200, "lat": 14.7053, "lng": -17.4640},
        {"zone": "Porte B — Centre",  "capacite": 1200, "lat": 14.7045, "lng": -17.4640},
        {"zone": "Porte C — Sud",     "capacite": 1200, "lat": 14.7037, "lng": -17.4640},
        {"zone": "Quai Départ",       "capacite": 2000, "lat": 14.7045, "lng": -17.4630},
        {"zone": "Quai Arrivée",      "capacite": 2000, "lat": 14.7045, "lng": -17.4650},
        {"zone": "Hall Principal",    "capacite": 3000, "lat": 14.7049, "lng": -17.4637},
        {"zone": "Zone Billetterie",  "capacite":  800, "lat": 14.7041, "lng": -17.4645},
        {"zone": "Parking Relais",    "capacite":  800, "lat": 14.7031, "lng": -17.4650},
    ],
    "Gare Colobane (TER)": [
        {"zone": "Quai 1 — Dakar",      "capacite": 1500, "lat": 14.7016, "lng": -17.4475},
        {"zone": "Quai 2 — Diamniadio", "capacite": 1500, "lat": 14.7008, "lng": -17.4475},
        {"zone": "Hall Accueil",        "capacite": 2500, "lat": 14.7012, "lng": -17.4485},
        {"zone": "Zone Contrôle",       "capacite": 1000, "lat": 14.7017, "lng": -17.4489},
        {"zone": "Sortie Principale",   "capacite":  800, "lat": 14.7007, "lng": -17.4491},
        {"zone": "Sortie Secondaire",   "capacite":  500, "lat": 14.7019, "lng": -17.4469},
        {"zone": "Zone Attente",        "capacite":  700, "lat": 14.7012, "lng": -17.4480},
        {"zone": "Parking TER",         "capacite":  600, "lat": 14.7003, "lng": -17.4493},
    ],
}

SCENARIO = "normal"
ZONE_HISTORY = {}

def get_heure_factor(heure):
    factors = {7: 0.3, 8: 0.3, 9: 0.7, 10: 0.7, 11: 0.65,
               12: 0.55, 13: 0.55, 14: 0.8, 15: 0.8, 16: 0.75,
               17: 0.7, 18: 0.9, 19: 0.9, 20: 0.85}
    return factors.get(heure, 0.4)

def get_zone_base(zone_name, heure_factor):
    if any(x in zone_name for x in ['VIP', 'Médias', 'Billetterie']):
        return heure_factor * 45
    elif any(x in zone_name for x in ['Parking', 'Parking Relais', 'Parking TER']):
        return heure_factor * 55
    elif any(x in zone_name for x in ['Entrée', 'Porte', 'Quai', 'Sortie']):
        return heure_factor * 80
    elif any(x in zone_name for x in ['Tribune', 'Secteur', 'Plage', 'Piscine']):
        return heure_factor * 70
    else:
        return heure_factor * 60

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
        for i, z in enumerate(zones):
            if SCENARIO == 'montee':
                base = min(95, get_zone_base(z["zone"], get_heure_factor(heure)) + 18)
                densite = int(min(100, max(10, base + random.uniform(-5, 5))))
            elif SCENARIO == 'critique' and any(x in z["zone"] for x in ['Entrée', 'Porte', 'Quai', 'Sortie']):
                densite = random.randint(88, 98)
            else:
                base = get_zone_base(z["zone"], get_heure_factor(heure))
                densite = int(min(100, max(5, base + random.uniform(-10, 10))))

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

            key = f"{lieu}::{z['zone']}"
            if key not in ZONE_HISTORY:
                ZONE_HISTORY[key] = []
            ZONE_HISTORY[key].append(densite)
            if len(ZONE_HISTORY[key]) > 5:
                ZONE_HISTORY[key].pop(0)

            hist = ZONE_HISTORY[key]
            if len(hist) >= 3:
                n = len(hist)
                x_mean = (n - 1) / 2
                y_mean = sum(hist) / n
                num = sum((j - x_mean) * (hist[j] - y_mean) for j in range(n))
                den = sum((j - x_mean) ** 2 for j in range(n)) or 1
                slope = num / den
                predicted = round(hist[-1] + slope, 1)
                predicted = max(0.0, min(100.0, predicted))
            else:
                predicted = float(densite)

            confirmed   = (len(hist) >= 3 and all(h >= 85 for h in hist[-3:])) if status == "danger"  else False
            observation = (len(hist) >= 2 and all(h >= 60 for h in hist[-2:])) if status == "modere" else False
            alert_status = "confirmée" if confirmed else ("observation" if observation else "normale")

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
                "time":        now,
                "predicted_densite": predicted,
                "alert_status":      alert_status,
                "zone_id":     f"{lieu[:3].upper()}-{z['zone'][:3].upper()}-{str(i+1).zfill(2)}",
                "source":      ("orange_antenna" if any(x in z["zone"] for x in ["Tribune", "Secteur", "Plage"])
                                else "wifi_hotspot" if any(x in z["zone"] for x in ["Hall", "Billetterie", "VIP"])
                                else "iot_counter"),
                "lat": z.get("lat", 14.693),
                "lng": z.get("lng", -17.447),
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
