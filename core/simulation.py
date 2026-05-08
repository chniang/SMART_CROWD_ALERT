# core/simulation.py
"""
Logique de simulation calibree — facteurs horaires et bases par type de zone.
Isole la simulation du reste du systeme pour faciliter le remplacement par vraies donnees.
"""

def get_heure_factor(heure: int) -> float:
    factors = {
        7: 0.3, 8: 0.3, 9: 0.7, 10: 0.7, 11: 0.65,
        12: 0.55, 13: 0.55, 14: 0.8, 15: 0.8, 16: 0.75,
        17: 0.7, 18: 0.9, 19: 0.9, 20: 0.85
    }
    return factors.get(heure, 0.4)


def get_zone_base(zone_name: str, heure_factor: float) -> float:
    if any(x in zone_name for x in ['VIP', 'Medias', 'Billetterie', 'Accreditation', 'Paddock']):
        return heure_factor * 45
    elif any(x in zone_name for x in ['Parking', 'Echauffement', 'Aire ']):
        return heure_factor * 50
    elif any(x in zone_name for x in ['Piste', 'Salle', 'Hall']):
        return heure_factor * 55
    elif any(x in zone_name for x in ['Entree', 'Porte', 'Quai', 'Sortie', 'Arrivee', 'Depart']):
        return heure_factor * 80
    elif any(x in zone_name for x in ['Tribune', 'Secteur', 'Plage', 'Piscine', 'Spectateurs', 'Restauration']):
        return heure_factor * 70
    else:
        return heure_factor * 60
