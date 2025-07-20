# tests/test_db.py
"""
Pruebas de integración para verificar la conexión a la base de datos Azure
configurada y la presencia de las tablas definidas en `db.models`.

Ejecución:
    pytest -q

Requisitos:
    - Variables de entorno AZ_* configuradas (ver .env.template)
    - Dependencias instaladas: pytest, SQLAlchemy, pyodbc (driver ODBC 17)
"""
import pytest
from sqlalchemy import text, inspect

from db.engine import engine
from db.models import Base

@pytest.fixture(scope="session")
def connection():
    """ Provee una conexión a la base de datos para las pruebas. """
    with engine.connect() as conn:
        yield conn

def tests_connection_alive(connection):
    """ La base de datos responde correctamente a una consulta simple. """
    result = connection.execute(text("SELECT 1")).scalar()
    assert result == 1, "La conexión a la base de datos falló."

def test_tables_exist(connection):
    """Verifica que todas las tablas declaradas existen realmente en la BD."""
    inspector = inspect(connection)

    expected_tables = [table.name for table in Base.metadata.sorted_tables]
    existing_tables = inspector.get_table_names()

    missing = [tbl for tbl in expected_tables if tbl not in existing_tables]
    assert not missing, f"Faltan las siguientes tablas en la base de datos: {', '.join(missing)}"

