import pandas as pd

def calculer_kpis(df_analyse):
    total_zones = len(df_analyse)
    zones_critiques = len(df_analyse[df_analyse["statut"] == "critique"])
    zones_elevees = len(df_analyse[df_analyse["statut"] == "eleve"])
    zones_normales = len(df_analyse[df_analyse["statut"] == "normal"])
    taux_moyen = df_analyse["taux_occupation"].mean()
    score_global = df_analyse["score_menace"].mean()
    zone_max = df_analyse.loc[df_analyse["taux_occupation"].idxmax()]
    alertes_actives = len(df_analyse[df_analyse["alerte_active"] == True])

    if score_global >= 80:
        niveau_global = "critique"
        couleur_globale = "#E63946"
    elif score_global >= 50:
        niveau_global = "eleve"
        couleur_globale = "#FF6B35"
    else:
        niveau_global = "normal"
        couleur_globale = "#00C9A7"

    return {
        "total_zones": total_zones,
        "zones_critiques": zones_critiques,
        "zones_elevees": zones_elevees,
        "zones_normales": zones_normales,
        "taux_occupation_moyen": round(taux_moyen, 1),
        "score_global": round(score_global, 1),
        "niveau_global": niveau_global,
        "couleur_globale": couleur_globale,
        "zone_plus_chargee": zone_max["zone"],
        "taux_zone_max": round(zone_max["taux_occupation"], 1),
        "alertes_actives": alertes_actives,
    }

def resume_par_zone(df_analyse):
    return df_analyse[[
        "zone", "affluence", "capacite",
        "taux_occupation", "statut",
        "score_menace", "couleur", "message", "action"
    ]].sort_values("score_menace", ascending=False).reset_index(drop=True)

def historique_alertes(df_complet, df_analyse_actuelle):
    alertes = df_analyse_actuelle[df_analyse_actuelle["alerte_active"] == True].copy()
    alertes = alertes[["timestamp", "zone", "statut", "score_menace", "message"]].copy()
    alertes.columns = ["Heure", "Zone", "Niveau", "Score", "Message"]
    alertes["Niveau"] = alertes["Niveau"].str.upper()
    return alertes.sort_values("Score", ascending=False).reset_index(drop=True)
