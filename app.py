
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import sys, os, json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.alerts import analyser_toutes_zones, generer_notifications
from core.kpis import calculer_kpis

st.set_page_config(page_title="Smart Crowd AI", page_icon="🚨", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #060D12; }
[data-testid="stHeader"] { background: rgba(6,13,18,.95); border-bottom: 1px solid #182832; }
[data-testid="stToolbar"] { display: none; }
.block-container { padding: 1rem 2rem 0.5rem 2rem !important; max-width: 100% !important; }
h1,h2,h3,p,div,span,label { color: #ECF4F8; }
[data-testid="stSelectbox"] > div > div {
    background: #0D1A21 !important; border: 1px solid #182832 !important;
    border-radius: 8px !important; color: #ECF4F8 !important;
}
[data-testid="stSelectbox"] label { color: #4A7080 !important; font-size: 0.75rem !important; }
[data-testid="stToggle"] label { color: #ECF4F8 !important; }
iframe { border: none !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load():
    return pd.read_csv("data/joj_crowd_data.csv")

df = load()

# ── CONTRÔLES STREAMLIT ───────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns([2, 2, 1.5, 5])
with c1:
    jour = st.selectbox("📅 Jour", sorted(df["jour"].unique()))
with c2:
    heure = st.selectbox("🕐 Heure", sorted(df["heure"].unique()), index=3)
with c3:
    st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
    live = st.toggle("🔴 Live", value=False)
with c4:
    pass

# ── DONNÉES ───────────────────────────────────────────────────────────────────
snap = df[(df["jour"] == jour) & (df["heure"] == heure)].copy()
if live:
    b = np.random.uniform(-0.06, 0.10, size=len(snap))
    snap["taux_occupation"] = (snap["taux_occupation"] + b).clip(0.05, 1.10)
    snap["affluence"] = (snap["taux_occupation"] * snap["capacite"]).astype(int)

da = analyser_toutes_zones(snap)
kpis = calculer_kpis(da)
notifs = generer_notifications(da)

# ── CALCUL TOTAL AFFLUENCE ────────────────────────────────────────────────────
if "affluence" in snap.columns:
    total_aff = int(snap["affluence"].sum())
elif "capacite" in snap.columns:
    total_aff = int((snap["taux_occupation"] * snap["capacite"]).sum())
else:
    total_aff = 0
total_aff_fmt = f"{total_aff:,}".replace(",", " ")

# ── COULEURS ──────────────────────────────────────────────────────────────────
color_crit = "#FF3D3D" if kpis["zones_critiques"] > 0 else "#00F0A0"
color_score = (
    "#FF3D3D" if kpis["score_global"] >= 80
    else "#FFBA00" if kpis["score_global"] >= 50
    else "#00F0A0"
)

# ── TICKER ────────────────────────────────────────────────────────────────────
ticker_items = ""
for _, row in da.iterrows():
    if row["statut"] == "critique":
        emoji, label, color = "🔴", "ALERTE DENSITÉ", "var(--r)"
    elif row["statut"] == "eleve":
        emoji, label, color = "🟡", "AFFLUENCE", "var(--y)"
    else:
        emoji, label, color = "🟢", "FLUIDE", "var(--g)"
    ticker_items += (
        f'<div class="tick-item">{emoji} {row["zone"]} — '
        f'<span style="color:{color}">{label}</span></div>'
    )
ticker_items = ticker_items * 2  # duplication pour boucle infinie

# ── ALERTES HTML ──────────────────────────────────────────────────────────────
if notifs:
    alert_html = ""
    for n in notifs:
        cls = "d" if n["niveau"] == "CRITIQUE" else "w"
        badge = "⚠ CRITIQUE" if n["niveau"] == "CRITIQUE" else "◈ ATTENTION"
        alert_html += f"""
        <div class="al {cls}">
          <div class="al-top">
            <span class="al-type">{badge}</span>
            <span class="al-time live-clock">--:--:--</span>
          </div>
          <div class="al-msg">{n["zone"]} — {n["message"]}</div>
          <div class="al-score">🎯 Score : {n["score"]} · {n["action"]}</div>
        </div>"""
else:
    alert_html = """
    <div class="al ok">
      <div class="al-top">
        <span class="al-type">✓ NORMAL</span>
        <span class="al-time live-clock">--:--:--</span>
      </div>
      <div class="al-msg">Toutes les zones sont normales.</div>
    </div>"""

# ── BARRES MÉTRIQUES HTML ─────────────────────────────────────────────────────
metrics_html = ""
for _, row in da.sort_values("taux_occupation", ascending=False).iterrows():
    pct = round(row["taux_occupation"], 1)
    if pct >= 85:
        color = "var(--r)"
    elif pct >= 60:
        color = "var(--y)"
    else:
        color = "var(--g)"
    bar_width = min(pct, 100)
    metrics_html += f"""
    <div class="mt">
      <div class="mt-top">
        <span class="mt-name">{row["zone"]}</span>
        <span class="mt-val" style="color:{color}">{pct}%</span>
      </div>
      <div class="bar">
        <div class="fill" style="width:{bar_width}%;background:{color}"></div>
      </div>
    </div>"""

# ── DONNÉES GRILLE CARTE ──────────────────────────────────────────────────────
zone_data_json = json.dumps([
    {
        "name": row["zone"],
        "cls": "zd" if row["statut"] == "critique"
               else "zw" if row["statut"] == "eleve"
               else "zs",
        "pct": row["taux_occupation"],
    }
    for _, row in da.iterrows()
])

# ── INJECTION DANS LE TEMPLATE HTML ──────────────────────────────────────────
template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "dashboard.html")
with open(template_path, "r", encoding="utf-8") as f:
    html = f.read()

html = (
    html
    .replace("{{JOUR}}", str(jour))
    .replace("{{HEURE}}", str(heure))
    .replace("{{TOTAL_AFFLUENCE}}", total_aff_fmt)
    .replace("{{ZONES_CRITIQUES}}", str(kpis["zones_critiques"]))
    .replace("{{COLOR_CRITIQUES}}", color_crit)
    .replace("{{TAUX_MOYEN}}", str(kpis["taux_occupation_moyen"]))
    .replace("{{SCORE_GLOBAL}}", str(kpis["score_global"]))
    .replace("{{COLOR_SCORE}}", color_score)
    .replace("{{NIVEAU_GLOBAL}}", kpis["niveau_global"].upper())
    .replace("{{TICKER_ITEMS}}", ticker_items)
    .replace("{{ALERT_CARDS}}", alert_html)
    .replace("{{METRIC_BARS}}", metrics_html)
    .replace("{{ZONE_DATA_JSON}}", zone_data_json)
)

# ── AFFICHAGE ─────────────────────────────────────────────────────────────────
components.html(html, height=5200, scrolling=True)

if live:
    import time
    time.sleep(4)
    st.cache_data.clear()
    st.rerun()
