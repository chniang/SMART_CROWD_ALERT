# core/prediction.py
"""
Inférence LSTM en pur numpy — zéro dépendance TensorFlow en production.

Les poids sont exportés depuis notebook/prediction_densite.ipynb et chargés
une seule fois au démarrage depuis core/models/.

Architecture : LSTM(32) → Dense(1)
Normalisation : d_min=5.0, d_max=100.0 (espace [0, 1])
"""

import os
import json
import numpy as np

_MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')

# ── Chargement des poids (une seule fois au démarrage) ───────────────────────

def _load():
    scaler_path = os.path.join(_MODEL_DIR, 'scaler.json')
    if not os.path.exists(scaler_path):
        return None
    try:
        with open(scaler_path) as f:
            scaler = json.load(f)
        return {
            'W':     np.load(os.path.join(_MODEL_DIR, 'lstm_kernel.npy')),
            'U':     np.load(os.path.join(_MODEL_DIR, 'lstm_recurrent_kernel.npy')),
            'b':     np.load(os.path.join(_MODEL_DIR, 'lstm_bias.npy')),
            'Wd':    np.load(os.path.join(_MODEL_DIR, 'dense_kernel.npy')),
            'bd':    np.load(os.path.join(_MODEL_DIR, 'dense_bias.npy')),
            'units': scaler['units'],
            'dmin':  scaler['d_min'],
            'dmax':  scaler['d_max'],
            'slen':  scaler['seq_len'],
        }
    except Exception:
        return None

_M = _load()

# ── Activation helpers ───────────────────────────────────────────────────────

def _sig(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -50.0, 50.0)))

# ── Passe avant LSTM numpy ────────────────────────────────────────────────────

def _forward(seq_norm):
    """
    Passe avant LSTM sur une séquence normalisée (1D array, longueur slen).
    Retourne la sortie dénormalisée (densité en %).
    Porte Keras : [i, f, g, o] × units dans chaque quart du kernel.
    """
    units = _M['units']
    W, U, b   = _M['W'], _M['U'], _M['b']
    Wd, bd    = _M['Wd'], _M['bd']
    dmin, dmax = _M['dmin'], _M['dmax']

    h = np.zeros((1, units), dtype=np.float32)
    c = np.zeros((1, units), dtype=np.float32)

    for x_t in seq_norm:
        x = np.array([[x_t]], dtype=np.float32)
        z = x @ W + h @ U + b                      # (1, 4·units)
        i = _sig(z[:, 0*units:1*units])
        f = _sig(z[:, 1*units:2*units])
        g = np.tanh(z[:, 2*units:3*units])
        o = _sig(z[:, 3*units:4*units])
        c = f * c + i * g
        h = o * np.tanh(c)

    out_norm = (h @ Wd + bd).item()
    return out_norm * (dmax - dmin) + dmin

# ── Interface publique ────────────────────────────────────────────────────────

def model_available() -> bool:
    """Retourne True si les poids numpy sont chargés et prêts."""
    return _M is not None

def predict_densite(historique: list) -> float | None:
    """
    Prédit la densité au prochain pas de temps (30 min).

    Args:
        historique : dernières densités connues en % (liste de floats).
                     Doit contenir au moins seq_len=10 valeurs.

    Returns:
        Densité prédite en % (float clampée [5, 100]), ou None si indisponible.
    """
    if _M is None or len(historique) < _M['slen']:
        return None

    dmin, dmax = _M['dmin'], _M['dmax']
    seq_norm = (np.array(historique[-_M['slen']:], dtype=np.float32) - dmin) / (dmax - dmin)
    predicted = _forward(seq_norm)
    return round(float(np.clip(predicted, dmin, dmax)), 1)
