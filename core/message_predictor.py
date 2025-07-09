import joblib
import re

# Cargar modelos
modelo_intencion = joblib.load("models/modelo_intencion.pkl")
modelo_servicio = joblib.load("models/modelo_servicio.pkl")
modelo_sentimiento = joblib.load("models/modelo_sentimiento.pkl")

# Extraer hora con expresiones regulares
def extraer_hora(texto: str) -> str:
    """
    Busca una hora en formato HH o HH:MM con AM/PM opcional.
    Ej: 'a las 5', '5 pm', '17:00', etc.
    """
    match = re.search(r"\b(?:a\s+las\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", texto, re.IGNORECASE)
    if match:
        horas = int(match.group(1))
        minutos = int(match.group(2)) if match.group(2) else 0
        periodo = match.group(3)

        if periodo:
            periodo = periodo.lower()
            if periodo == "pm" and horas < 12:
                horas += 12
            elif periodo == "am" and horas == 12:
                horas = 0

        return f"{horas:02d}:{minutos:02d}"
    return ""

# Predicción unificada
def predecir_todo(texto: str) -> dict:
    intencion = modelo_intencion.predict([texto])[0]
    servicio = modelo_servicio.predict([texto])[0] if intencion in ["agendar", "consultar"] else None
    sentimiento = modelo_sentimiento.predict([texto])[0] if intencion == "opinar" else None
    hora = extraer_hora(texto)

    return {
        "texto": texto,
        "intencion": intencion,
        "servicio": servicio,
        "sentimiento": sentimiento,
        "hora_preferida": hora
    }
