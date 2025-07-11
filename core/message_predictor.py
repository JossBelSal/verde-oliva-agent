import joblib
import re

#cargar modelos
modelo_intencion = joblib.load("models/modelo_intencion.pkl")
modelo_servicio = joblib.load("models/modelo_servicio.pkl")
modelo_sentimiento = joblib.load("models/modelo_sentimiento.pkl")

#extraer hora con expresiones regulares
def extraer_hora(texto: str) -> str:
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

#lista de estilistas para detección
ESTILISTAS = ["Eleonora", "Sol", "Sofía", "Isabel", "Anahí", "Ale", "Nidia", "Jessica"]

def detectar_estilista(texto: str) -> str:
    for nombre in ESTILISTAS:
        if re.search(nombre, texto, re.IGNORECASE):
            return nombre
    return ""

#predicción
def predecir_todo(texto: str) -> dict:
    intencion = modelo_intencion.predict([texto])[0]
    servicio = modelo_servicio.predict([texto])[0] if intencion in ["agendar", "consultar"] else None
    sentimiento = modelo_sentimiento.predict([texto])[0] if intencion == "opinar" else None
    hora = extraer_hora(texto)

    corte_precision = "corte corto" in texto.lower() or "alta precisión" in texto.lower()
    deslave_necesario = "más claro" in texto.lower() or "deslave" in texto.lower()
    estilista_solicitada = detectar_estilista(texto)

    #reglas de asignación
    asignada_a = ""
    razon_asignacion = ""
    if corte_precision:
        asignada_a = "Eleonora"
        razon_asignacion = "Corte corto de alta precisión"
    elif deslave_necesario:
        asignada_a = "Jessica"
        razon_asignacion = "Requiere deslave"
    elif estilista_solicitada:
        asignada_a = estilista_solicitada
        razon_asignacion = "Solicitada por el cliente"

    return {
        "texto": texto,
        "intencion": intencion,
        "servicio": servicio,
        "sentimiento": sentimiento,
        "hora_preferida": hora,
        "corte_precision": corte_precision,
        "deslave_necesario": deslave_necesario,
        "estilista_solicitada": estilista_solicitada,
        "asignada_a": asignada_a,
        "razon_asignacion": razon_asignacion
    }
