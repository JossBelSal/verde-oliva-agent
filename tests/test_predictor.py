# tests/test_predictor.py
"""pytest: pruebas unitarias para
1. core/message_predictor.py (cascada regex → pkl → LLM)
2. core/scheduler.py (slot disponible / ocupado)

❗ Para aislar dependencias externas:
   • Se usa monkeypatch para fingir la API de OpenAI (sin tokens).
   • Se crea una DB SQLite in‑memory con modelos cargados.
"""
from datetime import date, time, timedelta
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Base, Servicio, Cita, Empleado
from core import scheduler
from core.message_predictor import predict_intent, Intent

# ───────────────────────────── fixtures DB ───────────────────────────────────
@pytest.fixture(scope="session")
def engine():
    eng = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(eng)
    return eng

@pytest.fixture()
def db(engine):
    """Sesión SQLAlchemy renovable por prueba."""
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    sess = Session()
    yield sess
    sess.rollback()
    sess.close()

@pytest.fixture(autouse=True)
def seed_minimal(db):
    """Carga datos mínimos: 1 servicio (30 min) y 1 empleado."""
    svc = Servicio(id=1, nombre="Corte básico", categoria="Corte", duracion_min=30)
    emp = Empleado(id=1, nombre="Ana", puesto="Estilista")
    db.add_all([svc, emp])
    db.commit()

# ─────────────────────── fixture: mock OpenAI ────────────────────────────────
@pytest.fixture(autouse=True)
def mock_openai(monkeypatch):
    """Evita llamadas reales a OpenAI; siempre responde ‘otro’."""
    def _fake_completion(*_, **__):
        msg = SimpleNamespace(content="otro")
        choice = SimpleNamespace(message=msg)
        return SimpleNamespace(choices=[choice])

    import core.message_predictor as mp
    monkeypatch.setattr(mp.openai.chat.completions, "create", _fake_completion)
    yield

# ──────────────────────────── Tests predictor ────────────────────────────────
@pytest.mark.parametrize(
    "texto, esperado",
    [
        ("Hola, buenos días", "saludo"),
        ("¿Dónde están ubicados?", "ubicacion"),
        ("Quiero pagar con tarjeta", "pago"),
        ("Me enseñas los servicios", "listar_servicios"),
        ("Necesito agendar cita mañana", "agendar_cita"),
    ],
)
def test_predictor_regex(texto: str, esperado: Intent):
    label, conf = predict_intent(texto)
    assert label == esperado
    assert conf == 1.0

# ─────────────────────────── Tests scheduler ────────────────────────────────

def test_scheduler_slot_libre(db):
    disponible = scheduler.is_slot_available(db, date.today(), time(10, 0), 1, 1)
    assert disponible is True


def test_scheduler_slot_ocupado(db):
    # 1) crea cita que ocupa 10:00‑10:30
    cita = Cita(fecha=date.today(), hora=time(10, 0), cliente_id=1,
                servicio_id=1, empleado_id=1)
    db.add(cita); db.commit()

    # 2) intenta reservar mismo horario
    disponible = scheduler.is_slot_available(db, date.today(), time(10, 0), 1, 1)
    assert disponible is False


@pytest.mark.parametrize("offset", [0, 15])
def test_scheduler_solapamiento(db, offset):
    # cita existente 10:00‑10:30
    cita = Cita(fecha=date.today(), hora=time(10, 0), cliente_id=1,
                servicio_id=1, empleado_id=1)
    db.add(cita); db.commit()

    # nuevo intento 10:00 o 10:15  (se solapan)
    hora_nueva = (datetime := time(10, 0)).replace(minute=offset)
    disponible = scheduler.is_slot_available(db, date.today(), hora_nueva, 1, 1)
    assert disponible is False
