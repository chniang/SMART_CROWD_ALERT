import re

with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Ajouter import get_densite
content = content.replace(
    'from core.kpis import calculer_kpis',
    'from core.kpis import calculer_kpis\nfrom core.data_provider import get_densite'
)

# 2. Supprimer get_heure_factor (maintenant dans core/simulation.py)
content = re.sub(
    r'def get_heure_factor\(heure\):.*?return factors\.get\(heure, 0\.4\)\n\n',
    '',
    content,
    flags=re.DOTALL
)

# 3. Supprimer get_zone_base (maintenant dans core/simulation.py)
content = re.sub(
    r'def get_zone_base\(zone_name, heure_factor\):.*?return heure_factor \* 60\n\n',
    '',
    content,
    flags=re.DOTALL
)

# 4. Remplacer le bloc calcul densite par un seul appel get_densite
old_block = "            if SCENARIO == 'montee':\n                base = min(95, get_zone_base(z[\"zone\"], get_heure_factor(heure)) + 18)\n                densite = int(min(100, max(10, base + random.uniform(-5, 5))))\n            elif SCENARIO == 'critique' and any(x in z[\"zone\"] for x in ['Entree', 'Porte', 'Quai', 'Sortie', 'Arrivee', 'Depart']):\n                densite = random.randint(88, 98)\n            else:\n                base = get_zone_base(z[\"zone\"], get_heure_factor(heure))\n                densite = int(min(100, max(5, base + random.uniform(-10, 10))))"

new_block = "            densite = get_densite(z, SCENARIO, heure, prev_map.get(z[\"zone\"], 50))"

if old_block in content:
    content = content.replace(old_block, new_block)
    print("Bloc densite remplace avec succes")
else:
    print("ATTENTION : bloc densite non trouve - verifier manuellement")

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("server.py mis a jour")
