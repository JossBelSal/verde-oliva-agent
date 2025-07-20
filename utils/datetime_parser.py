#=================================================================
# utils/datetime_parser.py
#=================================================================

import re
from datetime import datetime
from typing import List, Optional
import os
import json
#=================================================================
from openai import OpenAI
from dotenv import load_dotenv

#cargar variable de env
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#=================================================================

# Creamos los patrones de formato de fecha y hora
DATE_PATTERNS = [
    r"\b(\d{2}[-/]\d{2}[-/]\d{4})\b",                    # dd/mm/yyyy o dd-mm-yyyy
    r"\b(\d{4}[-/]\d{2}[-/]\d{2})\b",                    # yyyy/mm/dd o yyyy-mm-dd
    r"\b(\d{1,2}:\d{2}(?::\d{2})? ?(?:am|pm)?)\b",        # hora am/pm
    r"\b(\d{1,2}(?:st|nd|rd|th)?\s+(?:de\s+)?\w+\s+(?:de\s+)?\d{4})\b",  # 17 de julio de 2025
    r"\b(mañana|ayer|hoy)\b.*?(a las)?\s*(\d{1,2}:\d{2}(?:am|pm)?)"     # mañana a las 3 pm
]


def detect_datetime_patterns(text: str) -> List[str]:
    """Extrae fechas y horas con expresiones regulares."""
    matches = []
    for pattern in DATE_PATTERNS:
        found = re.findall(pattern, text.lower())
        matches.extend(found)
    return matches

def validar_fecha(fecha_str: str) -> datetime | None:
    """
    Valida que una fecha ISO sea real usando datetime.fromisoformat().
    """
    try:
        return datetime.fromisoformat(fecha_str)
    except ValueError:
        return None
    

def parse_datetime_with_ai(text: str, patterns: List[str]) -> List[str]:
    """
    Llama a la API openAI, interpreta el texto y extrae las fechas y horas ambiguas o en formato libre.
    Devuelve la fecha y hora en formato ISO 8601.
    """
    #======  Fecha actual ===========
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not patterns:
        prompt =(
            f"Hoy es {now}. Interpreta si hay una fecha y hora en este texto: '{text}'. "
            "Si no hay, pide al usuario que ingrese una fecha y hora válida.\n"
            "Devuelve un JSON así: { \"datetimes\": [\"2025-07-18T10:30:00\"] } (formato ISO 8601)"

        )
    else:
        prompt = (
            f"Hoy es {now}. Dada la lista de patrones detectados: {patterns}, "
            f"y el texto original: '{text}', convierte las fechas y horas a formato ISO 8601.\n"
            "Devuelve un JSON así: { \"datetimes\": [\"2025-07-18T10:30:00\"] } (formato ISO 8601)"


        )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
    )

    try:
        result = response.choices[0].message.content.strip()
        data = json.loads(result)
        return data.get("datetimes", [])
    except Exception as e:
        print("❌ Error al interpretar respuesta IA:", e)
        return []

def datetime_parser(text: str) -> List[str]:
    """Pipeline principal para detección de fechas y horas."""
    patterns = detect_datetime_patterns(text)
    iso_datetimes = parse_datetime_with_ai(text, patterns)
    return [
        dt for dt in iso_datetimes
        if validar_fecha(dt) is not None
    ]

# Prueba manual (CLI)
if __name__ == "__main__":
    test_inputs = [
        "Quiero agendar para mañana a las 3 pm",
        "17/07/2025 a las 20:14",
        "lunes 22 a las 2:30pm",
        "para el jueves a medio día"
    ]
    for input_text in test_inputs:
        print(f"Texto: {input_text}")
        print("Detectado:", datetime_parser(input_text))
        print("-")




