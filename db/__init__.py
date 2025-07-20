# db/__init__.py
# ==============================================================================
# Inicializa la base de datos: importa modelos y crea las tablas si no existen
# ==============================================================================

from .engine import engine
from .models import Base, Cliente, Empleado, DisponibilidadPersonal, Servicio, Producto, Cita

def bootstrap_db():
    """
    Crea las tablas definidas en models.py si no existen aún en la BD.
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas o verificadas en la base de datos.")

# Modo script: ejecutar directamente con `python -m db`
if __name__ == "__main__":
    bootstrap_db()
