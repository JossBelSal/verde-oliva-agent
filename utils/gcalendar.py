import os
import pickle
from datetime import datetime, timedelta

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ============================================
# CONFIG
# ============================================

SCOPES = ['https://www.googleapis.com/auth/calendar.events']
CREDENTIALS_FILE = 'utils/google_calendar_oauth.json'
TOKEN_FILE = 'utils/token_gcalendar_user.pickle'  # generado tras login

# ============================================
# AUTENTICACIÓN Y SERVICIO
# ============================================

def get_user_calendar_service():
    """
    Retorna un servicio autenticado para interactuar con el Google Calendar del usuario.
    Si no hay token guardado, lanza el flujo de autenticación en localhost:8080.
    """
    creds = None

    #cargar token si ya existe
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    #si no existe o es inválido, iniciar nuevo flujo OAuth
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=8080)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)

# ============================================
# FUNCIÓN PARA CREAR EVENTO
# ============================================

def crear_evento_usuario(nombre_cliente: str, nombre_servicio: str,
                         fecha: datetime.date, hora: datetime.time,
                         duracion_min: int) -> str:
    """
    Crea un evento en el Google Calendar del usuario autenticado.
    Retorna el ID del evento creado.
    """
    service = get_user_calendar_service()

    start = datetime.combine(fecha, hora)
    end = start + timedelta(minutes=duracion_min)

    evento = {
        'summary': f'{nombre_servicio} con {nombre_cliente}',
        'description': 'Cita agendada desde OLIVA (modo prueba)',
        'start': {'dateTime': start.isoformat(), 'timeZone': 'America/Mexico_City'},
        'end': {'dateTime': end.isoformat(), 'timeZone': 'America/Mexico_City'},
    }

    evento_creado = service.events().insert(calendarId='primary', body=evento).execute()
    return evento_creado.get('id')
