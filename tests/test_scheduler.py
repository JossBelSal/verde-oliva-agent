# tests/test_scheduler.py
"""
Pruebas unitarias del *scheduler* de Oliva (verificación de disponibilidad).
...
"""
import uuid
import datetime as dt
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Base, Servicio, Empleado, Cliente
from core.scheduler import is_slot_available, book_slot, SlotOccupiedError

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def engine_memory():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return engine

@pytest.fixture()
def db(engine_memory):
    connection = engine_memory.connect()
    trans = connection.begin()
    Session = sessionmaker(bind=connection, autoflush=False)
    session = Session()
    yield session
    session.close()
    trans.rollback()
    connection.close()

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def seed_basic(db):
    u = uuid.uuid4().hex[:6]
    servicio = Servicio(
        nombre=f"Balayage_{u}", categoria="Color", duracion_min=60
    )
    empleado = Empleado(
        nombre="Lupita", puesto="Estilista",
        telefono=f"555000{u}", email=f"lupita{u}@example.com"
    )
    cliente = Cliente(
        nombre="Ana", telefono=f"555123{u}", email=f"ana{u}@test.com"
    )
    db.add_all([servicio, empleado, cliente]); db.commit()
    return servicio, empleado, cliente

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_slot_available_when_empty(db):
    servicio, empleado, _ = seed_basic(db)
    fecha = dt.date.today()
    hora = dt.time(10, 0)

    assert is_slot_available(db, fecha, hora, empleado.id, servicio) is True

def test_slot_conflict_after_booking(db):
    servicio, empleado, cliente = seed_basic(db)
    fecha = dt.date.today()
    hora = dt.time(11, 0)

    book_slot(db, cliente.id, servicio.id, empleado.id, fecha, hora)

    with pytest.raises(SlotOccupiedError):
        book_slot(db, cliente.id, servicio.id, empleado.id, fecha, hora)

def test_non_overlapping_slots(db):
    servicio, empleado, cliente = seed_basic(db)
    fecha = dt.date.today()
    hora1 = dt.time(9, 0)
    hora2 = dt.time(10, 0)

    book_slot(db, cliente.id, servicio.id, empleado.id, fecha, hora1)

    assert is_slot_available(db, fecha, hora2, empleado.id, servicio) is True

def test_different_employee_does_not_conflict(db):
    servicio, empleado1, cliente = seed_basic(db)

    u = uuid.uuid4().hex[:4]
    empleado2 = Empleado(
        nombre="Mario", puesto="Barbero",
        telefono=f"555999{u}", email=f"mario{u}@example.com"
    )
    db.add(empleado2); db.commit()

    fecha = dt.date.today()
    hora = dt.time(14, 0)

    book_slot(db, cliente.id, servicio.id, empleado1.id, fecha, hora)

    assert is_slot_available(db, fecha, hora, empleado2.id, servicio) is True
