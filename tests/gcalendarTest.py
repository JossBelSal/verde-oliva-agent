from utils.gcalendar import crear_evento_usuario
from datetime import date, time

if __name__ == "__main__":
    evento_id = crear_evento_usuario(
        nombre_cliente="Valeria",
        nombre_servicio="Depilación + Facial",
        fecha=date(2025, 7, 19),
        hora=time(11, 30),
        duracion_min=75
    )
    print("Evento creado:", evento_id)
