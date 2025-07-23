# tests/test_booking.py
import datetime as dt
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Base, Servicio, Empleado, Cliente

# ── motor SQLite in‑memory ──────────────────────────────────────────
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine, autoflush=False)

# ── monkey‑patch a TODAS las fábricas que usa la capa core ─────────
import db.session as db_session
db_session.SessionLocal = Session          # patch global

import core.booking_handler as bh          # importa después del patch
bh.SessionLocal = Session                  # patch local del módulo

# ── fixtures ────────────────────────────────────────────────────────
@pytest.fixture()
def db():
    s = Session(); yield s; s.close()

@pytest.fixture()
def entorno(db):
    svc = Servicio(nombre="Balayage", categoria="Color", duracion_min=60, activo=True)
    emp = Empleado(nombre="Lupita", puesto="Estilista",
                   telefono="5550001111", email="lupita@test.com")
    cli = Cliente(nombre="Ana", telefono="5551234567", email="ana@test.com")
    db.add_all([svc, emp, cli]); db.commit()
    return svc, emp, cli

# ── test ────────────────────────────────────────────────────────────
def test_booking_fluye_ok(db, entorno):
    svc, emp, cli = entorno
    data = {
        "cliente_id":  cli.id,
        "servicio_id": svc.id,
        "empleado_id": emp.id,
        "fecha": dt.date.today().isoformat(),
        "hora":  "10:00",
    }

    assert bh.check_availability(data)["ok"] is True
    res = bh.process_booking_request(data)
    assert res["ok"] and "cita_id" in res
