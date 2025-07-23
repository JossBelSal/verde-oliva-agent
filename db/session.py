# db/session.py
"""Gestión de sesiones SQLAlchemy para OLIVA_MODEL_AI

Incluye:
- Creación y verificación de tablas (init_db).
- Factoría de sesiones thread‑safe (SessionLocal).
- Context manager "get_session" (con `yield`) para usar en scripts o tests.
- Dependency "get_db" para frameworks web (Flask, FastAPI).
- Manejo de errores con rollback automático.
"""
from contextlib import contextmanager
import logging
from typing import Generator, Iterator, ContextManager

from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.exc import SQLAlchemyError

from db.engine import engine
from db.models import Base

# Configuración del logger
logger = logging.getLogger(__name__)

#============================================================================
# 1) Inicializar esquema 

def init_db() -> None:
    """ Crea todas la tablas declaradas en models.py """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tablas creadas exitosamente/ verificadas en la BD.")
    except SQLAlchemyError as exc:
        logger.error(f"❌ Error al crear las tablas: {exc}")
        raise
#============================================================================
# 2) Factoría de sesiones thread-safe

SessionLocal: scoped_session[Session] = scoped_session(
    sessionmaker(bind=engine, autocommit=False, autoflush=False)
)
#============================================================================
# 3) Helpers / utilidades

@contextmanager
def get_session() -> Iterator[Session]:
    """Context manager seguro para scripts CLI o pruebas.

    Uso:
        with get_session() as db:
            db.add(obj)
            ...
    Al salir hace **commit**; si ocurre una excepción, hace **rollback**.
    """
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error en la sesión: {e}")
        raise
    finally:
        db.close()

def get_db() -> Generator[Session, None, None]:
    """Dependency compatible con FastAPI (yield) o generador genérico.

    Ejemplo FastAPI:
        @app.get("/users/{id}")
        def read_user(id: int, db: Session = Depends(get_db)):
            return db.get(User, id)
    """
    db: Session = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error en la sesión: {e}")
        raise
    finally:
        db.close()
#============================================================================
# 4) Ejecutar como script "python -m db.session"
if __name__ == "__main__":
    init_db()
    print("✅ Esquema creado/actualizado en la base de datos")
