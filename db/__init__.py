#==============================================================================
#================ IMPORTACION DE LAS TABLAS DE MODELOS.PY =====================
#==============================================================================

from .engine import engine
from .models import Base, Cliente, Empleado, DisponibilidadPersonal, Servicio, Producto, Cita

def bootstrap_db():
    """
    Crea las tablas en la base de datos si no existen.
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas cargadas y listas en la base de datos.")
bootstrap_db()
