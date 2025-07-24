"""core/message_predictor.py
=================================
Clasifica un mensaje entrante mediante una **cascada de tres niveles**:

1. Reglas rápidas (regex) – µs, sin costo.
2. Modelo ligero (scikit‑learn pkl) – ms, 100 % local.
3. LLM (GPT‑3.5‑turbo o similar) – sólo si la confianza del paso 2 < umbral.

Estrategia → velocidad y coste mínimo sin perder precisión.
"""
from __future__ import annotations

import os
import re
import json
from functools import lru_cache
from pathlib import Path
from typing import Literal, Tuple, Dict, cast, get_args

import joblib
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

# ───────────────────────── Configuración ──────────────────────────
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY no definido en el entorno")

LLM_MODEL       = os.getenv("LLM_INTENT_MODEL", "gpt-3.5-turbo")
LLM_CONFIDENCE  = 0.90   # confianza fija asignada al LLM
ML_THRESHOLD    = 0.25   # pkl debe superar esto para saltar el LLM

openai = OpenAI(api_key=OPENAI_API_KEY)

# ───────────────────────── Tipos y etiquetas ─────────────────────
Intent = Literal[
    "saludo",
    "ubicacion",
    "pago",
    "listar_servicios",
    "listar_productos",
    "agendar_cita",
    "soporte_tecnico",
    "otro",
]
ALLOWED_INTENTS: Tuple[str, ...] = get_args(Intent)

__all__ = ["Intent", "predict_intent"]

# ───────────────────────── 1) Reglas rápidas ─────────────────────
_QUICK_RULES: Dict[Intent, list[re.Pattern[str]]] = {
    "saludo":            [re.compile(r"\b(hola|buenas|hey|qué onda)\b", re.I)],
    "ubicacion":         [re.compile(r"\b(ubicaci[oó]n|d[oó]nde est[aá]n?)\b", re.I)],
    "pago":              [re.compile(r"\b(pago|tarjeta|factura|transferencia)\b", re.I)],
    "listar_servicios":  [re.compile(r"\b(servicio[s]?|corte|tinte|tratamiento)\b", re.I)],
    "listar_productos":  [re.compile(r"\b(producto[s]?|shampoo|crema|aceite)\b", re.I)],
    "agendar_cita":      [re.compile(r"\b(cita|agendar|reservar|apartad[oa])\b", re.I)],
    "soporte_tecnico":   [re.compile(r"\b(ayuda|soporte|no funciona)\b", re.I)],
}

# ───────────────────────── 2) Modelo local pkl ───────────────────
_MODEL_FILE = Path("models/modelo_intencion.pkl")
_VEC_FILE   = Path("models/vectorizador.pkl")

@lru_cache(maxsize=1)
def _load_local_model():
    """Carga perezosa del clasificador & vectorizador."""
    if _MODEL_FILE.exists() and _VEC_FILE.exists():
        clf  = joblib.load(_MODEL_FILE)
        vect = joblib.load(_VEC_FILE)
        return clf, vect
    return None, None  # type: ignore[return-value]

# ───────────────────────── 3) LLM fallback ───────────────────────
@lru_cache(maxsize=512)
def _ask_llm(text: str) -> Intent:
    """Pregunta al modelo en la nube (few‑shot) y devuelve la etiqueta."""
    messages = [
        {
            "role": "system",
            "content": (
                "Eres un clasificador de intenciones para un salón de belleza."\
                "Devuelve **solo** una de estas palabras: "
                + ", ".join(ALLOWED_INTENTS)
            ),
        },
        {"role": "user", "content": text},
    ]
    resp = openai.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0,
        max_tokens=15,
    )
    label = resp.choices[0].message.content.strip().split()[0]
    return cast(Intent, label if label in ALLOWED_INTENTS else "otro")

# ───────────────────────── API público ───────────────────────────

def predict_intent(text: str) -> Tuple[Intent, float]:
    """Devuelve `(intención, confianza)` usando la cascada regex → pkl → LLM."""
    text = text.lower().strip()

    # 1) regex ultra‑rápido
    for intent, patterns in _QUICK_RULES.items():
        if any(p.search(text) for p in patterns):
            return intent, 1.0

    # 2) modelo local
    clf, vect = _load_local_model()
    if clf is not None:
        proba = clf.predict_proba(vect.transform([text]))[0]
        idx   = int(np.argmax(proba))
        conf  = float(proba[idx])
        label: Intent = cast(Intent, clf.classes_[idx])  # type: ignore[assignment]
        if conf >= ML_THRESHOLD:
            return label, conf

    # 3) LLM (ambigüedad)
    label_llm = _ask_llm(text)
    return label_llm, LLM_CONFIDENCE
