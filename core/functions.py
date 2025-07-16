# core/functions.py
from db.session import SessionLocal
from db.models import Servicio

def cargar_servicios():
    """Consulta servicios desde la base de datos"""
    with SessionLocal() as session:
        servicios = session.query(Servicio).filter(Servicio.activo == True).all()
        return [
            {
                "Categoria": s.categoria,
                "Nombre": s.nombre,
                "Duracion": s.duracion_txt,
                "Precio": s.precio_txt,
                "Deposito": s.deposito_txt,
                "Detalles": s.detalles
            }
            for s in servicios
        ]
