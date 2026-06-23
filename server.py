from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import json
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.data_provider import get_densite
from core.prediction import predict_densite

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

LIEUX = {

    # ── ZONE DAKAR ────────────────────────────────────────────────────────────

    "Complexe Tour de l'Oeuf": [
        # Sports : Natation, Basketball 3x3, Breaking, Baseball5, Skateboard
        {"zone": "Piscine Olympique",        "cap": 3000,  "lat": 14.6892, "lng": -17.4550, "source": "iot_counter"},
        {"zone": "Piscine d'Echauffement",   "cap": 800,   "lat": 14.6891, "lng": -17.4552, "source": "wifi_hotspot"},
        {"zone": "Tribune Piscine",          "cap": 2500,  "lat": 14.6893, "lng": -17.4549, "source": "orange_antenna"},
        {"zone": "Aire Basketball 3x3",      "cap": 1500,  "lat": 14.6895, "lng": -17.4548, "source": "iot_counter"},
        {"zone": "Aire Breaking / Skate",    "cap": 1200,  "lat": 14.6896, "lng": -17.4547, "source": "iot_counter"},
        {"zone": "Entree Principale",        "cap": 2000,  "lat": 14.6890, "lng": -17.4553, "source": "iot_counter"},
        {"zone": "Entree Secondaire",        "cap": 1000,  "lat": 14.6889, "lng": -17.4554, "source": "iot_counter"},
        {"zone": "Parking",                  "cap": 1500,  "lat": 14.6888, "lng": -17.4556, "source": "orange_antenna"},
    ],

    "Stade Iba Mar Diop": [
        # Sports : Athletisme, Boxe, Futsal, Rugby a 7
        {"zone": "Tribune Nord",             "cap": 6000,  "lat": 14.7005, "lng": -17.4580, "source": "orange_antenna"},
        {"zone": "Tribune Sud",              "cap": 6000,  "lat": 14.7003, "lng": -17.4582, "source": "orange_antenna"},
        {"zone": "Tribune Est",              "cap": 3000,  "lat": 14.7004, "lng": -17.4578, "source": "orange_antenna"},
        {"zone": "Tribune Ouest",            "cap": 3000,  "lat": 14.7004, "lng": -17.4584, "source": "orange_antenna"},
        {"zone": "Piste d'Athletisme",       "cap": 500,   "lat": 14.7004, "lng": -17.4581, "source": "wifi_hotspot"},
        {"zone": "Salle de Boxe",            "cap": 800,   "lat": 14.7006, "lng": -17.4579, "source": "iot_counter"},
        {"zone": "Entree Principale",        "cap": 3000,  "lat": 14.7002, "lng": -17.4583, "source": "iot_counter"},
        {"zone": "Parking",                  "cap": 2000,  "lat": 14.7001, "lng": -17.4585, "source": "orange_antenna"},
    ],

    "Corniche Ouest": [
        # Sports : Cyclisme sur route + 10 sports d'engagement (surf, voile cote, etc.)
        {"zone": "Zone Depart Cyclisme",     "cap": 2000,  "lat": 14.7120, "lng": -17.4820, "source": "iot_counter"},
        {"zone": "Zone Arrivee Cyclisme",    "cap": 3000,  "lat": 14.7115, "lng": -17.4818, "source": "iot_counter"},
        {"zone": "Plage Nord - Engagement",  "cap": 4000,  "lat": 14.7125, "lng": -17.4825, "source": "orange_antenna"},
        {"zone": "Plage Sud - Engagement",   "cap": 4000,  "lat": 14.7110, "lng": -17.4815, "source": "orange_antenna"},
        {"zone": "Zone VIP / Medias",        "cap": 600,   "lat": 14.7118, "lng": -17.4821, "source": "wifi_hotspot"},
        {"zone": "Entree Principale",        "cap": 2500,  "lat": 14.7112, "lng": -17.4817, "source": "iot_counter"},
        {"zone": "Zone Restauration",        "cap": 1500,  "lat": 14.7122, "lng": -17.4823, "source": "wifi_hotspot"},
        {"zone": "Parking",                  "cap": 2000,  "lat": 14.7108, "lng": -17.4812, "source": "orange_antenna"},
    ],

    # ── ZONE DIAMNIADIO ───────────────────────────────────────────────────────

    "Dakar Arena": [
        # Sports : Badminton, Futsal
        {"zone": "Secteur A - Nord",         "cap": 4000,  "lat": 14.7280, "lng": -17.1420, "source": "orange_antenna"},
        {"zone": "Secteur B - Sud",          "cap": 4000,  "lat": 14.7278, "lng": -17.1422, "source": "orange_antenna"},
        {"zone": "Secteur C - Est",          "cap": 3500,  "lat": 14.7282, "lng": -17.1418, "source": "orange_antenna"},
        {"zone": "Secteur D - Ouest",        "cap": 3500,  "lat": 14.7276, "lng": -17.1424, "source": "orange_antenna"},
        {"zone": "Aire Badminton",           "cap": 400,   "lat": 14.7280, "lng": -17.1421, "source": "wifi_hotspot"},
        {"zone": "Entree Principale",        "cap": 3000,  "lat": 14.7275, "lng": -17.1425, "source": "iot_counter"},
        {"zone": "Zone Medias",              "cap": 300,   "lat": 14.7283, "lng": -17.1417, "source": "wifi_hotspot"},
        {"zone": "Parking",                  "cap": 2500,  "lat": 14.7272, "lng": -17.1428, "source": "orange_antenna"},
    ],

    "Stade Abdoulaye Wade": [
        # Sports : Tir a l'arc + Ceremonie d'ouverture
        {"zone": "Tribune Nord",             "cap": 10000, "lat": 14.7260, "lng": -17.1380, "source": "orange_antenna"},
        {"zone": "Tribune Sud",              "cap": 10000, "lat": 14.7258, "lng": -17.1382, "source": "orange_antenna"},
        {"zone": "Tribune Est",              "cap": 4000,  "lat": 14.7262, "lng": -17.1378, "source": "orange_antenna"},
        {"zone": "Tribune Ouest",            "cap": 4000,  "lat": 14.7258, "lng": -17.1384, "source": "orange_antenna"},
        {"zone": "Aire de Tir a l'arc",      "cap": 500,   "lat": 14.7260, "lng": -17.1381, "source": "wifi_hotspot"},
        {"zone": "Zone VIP Ceremonie",       "cap": 1500,  "lat": 14.7263, "lng": -17.1377, "source": "wifi_hotspot"},
        {"zone": "Entree Principale",        "cap": 5000,  "lat": 14.7256, "lng": -17.1385, "source": "iot_counter"},
        {"zone": "Entree Secondaire",        "cap": 2500,  "lat": 14.7257, "lng": -17.1386, "source": "iot_counter"},
        {"zone": "Parking",                  "cap": 3000,  "lat": 14.7254, "lng": -17.1388, "source": "orange_antenna"},
    ],

    "Centre des Expositions": [
        # Sports : Escrime, Gym artistique, Judo, Taekwondo, Tennis de table, Wushu
        {"zone": "Hall A - Escrime / Wushu",      "cap": 2000,  "lat": 14.7270, "lng": -17.1400, "source": "wifi_hotspot"},
        {"zone": "Hall B - Judo / Taekwondo",     "cap": 2000,  "lat": 14.7272, "lng": -17.1398, "source": "wifi_hotspot"},
        {"zone": "Hall C - Gym artistique",       "cap": 2500,  "lat": 14.7268, "lng": -17.1402, "source": "wifi_hotspot"},
        {"zone": "Hall D - Tennis de table",      "cap": 1500,  "lat": 14.7274, "lng": -17.1396, "source": "wifi_hotspot"},
        {"zone": "Tribune Centrale",              "cap": 3000,  "lat": 14.7271, "lng": -17.1400, "source": "orange_antenna"},
        {"zone": "Entree Principale",             "cap": 2500,  "lat": 14.7266, "lng": -17.1404, "source": "iot_counter"},
        {"zone": "Zone Accreditation",            "cap": 500,   "lat": 14.7265, "lng": -17.1405, "source": "iot_counter"},
        {"zone": "Parking",                       "cap": 1800,  "lat": 14.7263, "lng": -17.1407, "source": "orange_antenna"},
    ],

    "Centre Equestre Gendarmerie": [
        # Sports : Saut d'obstacles
        {"zone": "Piste Principale",         "cap": 1000,  "lat": 14.7240, "lng": -17.1360, "source": "wifi_hotspot"},
        {"zone": "Tribune Nord",             "cap": 1500,  "lat": 14.7242, "lng": -17.1358, "source": "orange_antenna"},
        {"zone": "Tribune Sud",              "cap": 1500,  "lat": 14.7238, "lng": -17.1362, "source": "orange_antenna"},
        {"zone": "Zone Paddock",             "cap": 400,   "lat": 14.7244, "lng": -17.1356, "source": "wifi_hotspot"},
        {"zone": "Zone VIP",                 "cap": 300,   "lat": 14.7243, "lng": -17.1357, "source": "wifi_hotspot"},
        {"zone": "Entree Principale",        "cap": 800,   "lat": 14.7236, "lng": -17.1364, "source": "iot_counter"},
        {"zone": "Parking",                  "cap": 600,   "lat": 14.7234, "lng": -17.1366, "source": "orange_antenna"},
    ],

    # ── ZONE SALY ─────────────────────────────────────────────────────────────

    "Saly Beach West": [
        # Sports : Beach Handball, Beach Volleyball, Beach Wrestling,
        #          Aviron de mer, Voile, Triathlon
        {"zone": "Plage Volleyball / Handball","cap": 5000, "lat": 14.4520, "lng": -16.9980, "source": "orange_antenna"},
        {"zone": "Plage Triathlon / Aviron",   "cap": 3000, "lat": 14.4518, "lng": -16.9982, "source": "orange_antenna"},
        {"zone": "Zone Voile - Embarcadere",   "cap": 1000, "lat": 14.4522, "lng": -16.9978, "source": "orange_antenna"},
        {"zone": "Zone Spectateurs Plage",     "cap": 6000, "lat": 14.4516, "lng": -16.9984, "source": "orange_antenna"},
        {"zone": "Zone VIP / Medias",          "cap": 500,  "lat": 14.4524, "lng": -16.9976, "source": "wifi_hotspot"},
        {"zone": "Entree Nord",                "cap": 2000, "lat": 14.4526, "lng": -16.9975, "source": "iot_counter"},
        {"zone": "Entree Sud",                 "cap": 2000, "lat": 14.4514, "lng": -16.9986, "source": "iot_counter"},
        {"zone": "Parking",                    "cap": 1500, "lat": 14.4512, "lng": -16.9988, "source": "orange_antenna"},
    ],

    # ── TRANSPORT ─────────────────────────────────────────────────────────────

    "Gare Obélisque (BRT)": [
        {"zone": "Porte A — Nord",      "cap": 1200, "lat": 14.6967, "lng": -17.4441, "source": "iot_counter"},
        {"zone": "Porte B — Centre",    "cap": 1200, "lat": 14.6966, "lng": -17.4442, "source": "iot_counter"},
        {"zone": "Porte C — Sud",       "cap": 1200, "lat": 14.6965, "lng": -17.4443, "source": "iot_counter"},
        {"zone": "Quai Départ",         "cap": 2000, "lat": 14.6968, "lng": -17.4440, "source": "orange_antenna"},
        {"zone": "Quai Arrivée",        "cap": 2000, "lat": 14.6969, "lng": -17.4439, "source": "orange_antenna"},
        {"zone": "Hall Principal",      "cap": 3000, "lat": 14.6970, "lng": -17.4438, "source": "wifi_hotspot"},
        {"zone": "Zone Billetterie",    "cap": 800,  "lat": 14.6964, "lng": -17.4444, "source": "wifi_hotspot"},
        {"zone": "Parking Relais",      "cap": 1000, "lat": 14.6963, "lng": -17.4445, "source": "orange_antenna"},
    ],

    "Gare Colobane (TER)": [
        {"zone": "Quai 1 — Dakar",       "cap": 1500, "lat": 14.7072, "lng": -17.4558, "source": "iot_counter"},
        {"zone": "Quai 2 — Diamniadio",  "cap": 1500, "lat": 14.7073, "lng": -17.4557, "source": "iot_counter"},
        {"zone": "Hall Accueil",         "cap": 2500, "lat": 14.7074, "lng": -17.4556, "source": "wifi_hotspot"},
        {"zone": "Zone Contrôle",        "cap": 1000, "lat": 14.7075, "lng": -17.4555, "source": "wifi_hotspot"},
        {"zone": "Sortie Principale",    "cap": 800,  "lat": 14.7071, "lng": -17.4559, "source": "iot_counter"},
        {"zone": "Sortie Secondaire",    "cap": 500,  "lat": 14.7070, "lng": -17.4560, "source": "iot_counter"},
        {"zone": "Zone Attente",         "cap": 700,  "lat": 14.7076, "lng": -17.4554, "source": "orange_antenna"},
        {"zone": "Parking TER",          "cap": 800,  "lat": 14.7069, "lng": -17.4561, "source": "orange_antenna"},
    ],
}

SCENARIO = "normal"
ZONE_HISTORY = {}

def compute_risk_score(densite, trend, heure, zone_name):
    score = densite
    if trend == 'hausse_rapide': score += 15
    elif trend == 'hausse': score += 8
    if heure in [9,10,14,15,18,19,20]: score += 10
    elif heure in [11,16]: score += 5
    if any(x in zone_name for x in ['Entree', 'Porte', 'Arrivee', 'Depart']): score += 10
    elif 'Quai' in zone_name: score += 8
    elif 'Parking' in zone_name: score += 3
    return min(100, score)

@app.route('/')
def index():
    return send_from_directory('.', 'dashboard.html')


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
            for key, zones in prev_raw.items():
                if key.startswith("_"):
                    continue
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
        for z in zones:
            densite = get_densite(z, SCENARIO, heure, prev_map.get(z["zone"], 50))

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
            if len(ZONE_HISTORY[key]) > 10:
                ZONE_HISTORY[key].pop(0)

            hist = ZONE_HISTORY[key]
            try:
                lstm_pred = predict_densite(hist)
            except Exception as _e:
                import traceback as _tb
                app.logger.error(f"predict_densite error: {_tb.format_exc()}")
                lstm_pred = None
            if lstm_pred is not None:
                predicted = lstm_pred
            elif len(hist) >= 3:
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
                "capacite":    z["cap"],
                "personnes":   int(z["cap"] * densite / 100),
                "densite":     densite,
                "trend":       trend,
                "trend_icon":  trend_icon,
                "trend_label": trend_label,
                "status":      status,
                "risk_score":  min(100, risk_score),
                "risk_reason": risk_reason,
                "time":        now,
                "predicted_densite": predicted,
                "alert_status":      alert_status,
            })
        capacite_totale  = sum(zn["cap"] for zn in zones)
        total_affluence  = sum(r["personnes"] for r in result)
        taux_remplissage = round(total_affluence / capacite_totale * 100, 1) if capacite_totale > 0 else 0.0
        for r in result:
            r["taux_remplissage_site"] = taux_remplissage
        all_results[lieu] = result

    all_results["_history"] = ZONE_HISTORY
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    return jsonify(all_results)

@app.route('/api/lieu')
def get_lieu():
    lieu = request.args.get('lieu', "Complexe Tour de l'Oeuf")
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        zones = data.get(lieu, [])
        return jsonify(zones)
    except Exception:
        return jsonify([])

@app.route('/api/debug/lstm')
def debug_lstm():
    import traceback as _tb
    from core.prediction import model_available, predict_densite, _M
    info = {'model_available': model_available()}
    if _M:
        info['shapes'] = {k: list(v.shape) for k, v in _M.items() if hasattr(v, 'shape')}
        info['scaler'] = {k: v for k, v in _M.items() if not hasattr(v, 'shape')}
    try:
        pred = predict_densite([40.0] * 10)
        info['test_prediction'] = pred
        info['status'] = 'ok'
    except Exception as e:
        info['error'] = str(e)
        info['traceback'] = _tb.format_exc()
        info['status'] = 'error'
    return jsonify(info)

import os as _os
if _os.path.exists("data.json"):
    try:
        with open("data.json", "r", encoding="utf-8") as _f:
            _saved = json.load(_f)
        if isinstance(_saved.get("_history"), dict):
            ZONE_HISTORY.update(_saved["_history"])
    except Exception:
        pass
else:
    with app.test_client() as c:
        c.get('/api/refresh')

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)
