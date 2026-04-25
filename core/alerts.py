import pandas as pd
from datetime import datetime

SEUILS = {
    "normal":   {"min": 0.00, "max": 0.60, "couleur": "🟢", "couleur_hex": "#00C9A7"},
    "eleve":    {"min": 0.60, "max": 0.85, "couleur": "🟡", "couleur_hex": "#FF6B35"},
    "critique": {"min": 0.85, "max": 9.99, "couleur": "🔴", "couleur_hex": "#E63946"},
}

MESSAGES_ALERTE = {
    "normal":   "Situation normale — aucune action requise.",
    "eleve":    "⚠️ Affluence élevée — surveillance renforcée recommandée.",
    "critique": "🚨 ZONE CRITIQUE — Intervention immédiate requise !",
}

ACTIONS_ALERTE = {
    "normal":   "Monitoring standard",
    "eleve":    "Renforcer les équipes sur place",
    "critique": "Déclencher protocole d'urgence + notifier agents",
}

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

def analyser_zone(zone, affluence, capacite):
    taux = affluence / capacite
    statut = get_statut(taux)
    score = get_score_menace(taux)
    return {
        "zone": zone,
        "affluence": affluence,
        "capacite": capacite,
        "taux_occupation": round(taux * 100, 1),
        "statut": statut,
        "score_menace": score,
        "couleur": SEUILS[statut]["couleur"],
        "couleur_hex": SEUILS[statut]["couleur_hex"],
        "message": MESSAGES_ALERTE[statut],
        "action": ACTIONS_ALERTE[statut],
        "alerte_active": statut in ["eleve", "critique"],
        "timestamp": datetime.now().strftime("%H:%M:%S"),
    }

def analyser_toutes_zones(df_snapshot):
    resultats = []
    for _, row in df_snapshot.iterrows():
        r = analyser_zone(row["zone"], row["affluence"], row["capacite"])
        resultats.append(r)
    return pd.DataFrame(resultats)

def generer_notifications(df_analyse):
    alertes = df_analyse[df_analyse["alerte_active"] == True].copy()
    notifications = []
    for _, row in alertes.iterrows():
        notif = {
            "timestamp": row["timestamp"],
            "zone": row["zone"],
            "niveau": row["statut"].upper(),
            "message": row["message"],
            "action": row["action"],
            "score": row["score_menace"],
        }
        notifications.append(notif)
    notifications.sort(key=lambda x: x["score"], reverse=True)
    return notifications
