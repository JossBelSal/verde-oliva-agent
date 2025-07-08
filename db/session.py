# db/session.py
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError

from db.engine import engine          # tu engine.py ya probado
from db.models import Base            # todas las tablas

# 1) Crea las tablas si no existen
def init_db() -> None:
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas / verificadas en la BD.")
    except SQLAlchemyError as e:
        print(f"❌ Error al crear tablas: {e}")

# 2) Fábrica de sesión thread-safe
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))

if __name__ == "__main__":
    # python -m db.session  ➜  crea las tablas
    init_db()
    print("✅ Esquema creado/actualizado en la base de datos")
