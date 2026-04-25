# ⚡ Smart Crowd AI — JOJ Dakar 2026

Système de surveillance de densité de foule en temps réel pour les Jeux Olympiques de la Jeunesse (JOJ) Dakar 2026.

Développé dans le cadre du **Hackathon JOJ Innovation Challenge** organisé par SONATEL · Orange Digital Center.

---

## 🎯 Fonctionnalités

- Surveillance en temps réel de 4 sites JOJ (Stade LSS, Gare Obélisque BRT, Gare Colobane TER, Stade Abdoulaye Wade)
- Carte thermique des zones avec alertes colorées
- Détection de tendances (hausse rapide, baisse, stable)
- Mode LIVE avec rafraîchissement automatique toutes les 5 secondes
- Graphique d'évolution de la densité (8 dernières valeurs)

---

## 🚦 Niveaux d'alerte

| Niveau | Seuil | Action |
|---|---|---|
| 🟢 FLUIDE | < 60% | Surveillance standard |
| 🟡 MODÉRÉ | 60–85% | Surveillance renforcée |
| 🔴 CRITIQUE | > 85% | Intervention immédiate |

Exemple : densité 72% + hausse rapide = "Densité 72% avec hausse rapide — surveiller"

---

## 📊 KPIs temps réel

- Zones en danger + score moyen /100
- Densité moyenne globale du site
- Total personnes présentes
- Zones surveillées actives

---

## 🛠️ Stack technique

- Backend : Python 3.12 · Flask · flask-cors
- Frontend : HTML5 · CSS3 · JavaScript vanilla · Canvas API
- Données : Simulation dynamique avec logique de tendance
- Serveur : Flask (port 5000)

---

## 🚀 Lancer le projet

```bash
pip install flask flask-cors pandas numpy
python server.py
```

Ouvrir : http://localhost:5000

---

## 🔌 API

| Route | Description |
|---|---|
| `GET /` | Dashboard HTML |
| `GET /api/refresh` | Génère nouvelles données |
| `GET /api/lieu?lieu=X` | Données d'un site |

---

## 👥 Équipe

Hackathon JOJ Innovation Challenge · SONATEL · Orange Digital Center · Dakar 2026

---

## 📄 Licence

MIT
