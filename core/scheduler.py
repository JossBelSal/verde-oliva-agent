# core/scheduler.py
"""Lógica de agenda y disponibilidad de citas para Oliva.

👀 Responsabilidades:
    - Validar que un empleado tenga un *slot* libre antes de confirmar cita.
    - Detectar solapamientos según duración del servicio.
    - Crear la cita (persistencia) aislando la lógica de *core* de la capa HTTP.

Nota:
    - Se usa la sesión de SQLAlchemy como dependencia explícita para que las
      capas superiores (Flask, tests, scripts) gestionen el ciclo de vida
      (commit/rollback/context‑manager).
"""
from __future__ import annotations
from datetime import datetime,date, time, timedelta
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from db.models import Cita, Servicio

class SlotOccupiedError(Exception):
    """Excepción personalizada para indicar que el slot ya está ocupado."""
    pass
class InvalidInputError(Exception):
    """Parametros invalidos como fecha pasada. duracion negativa, etc."""
    pass
# ────────────────────────────────────────────────────────────────────────────────
# Helpers internos
# ────────────────────────────────────────────────────────────────────────────────

def _compute_end(hora: time, duracion_min: int) -> time:
    """Suma *duracion_min* a *hora* y devuelve la nueva ``time``.
    No valida overflow a día siguiente (las citas de Oliva son mismo día).
    """
    dt_start = datetime.combine(date.today(), hora)
    dt_end = dt_start + timedelta(minutes=duracion_min)
    return dt_end.time()

def _slot_overlaps(start_a: time, end_a: time, start_b: time, end_b: time) -> bool:
    """Comprueba si dos intervalos de tiempo se solapan."""
    return start_a < end_b and start_b < end_a

# ────────────────────────────────────────────────────────────────────────────────
# API público
# ────────────────────────────────────────────────────────────────────────────────

def is_slot_available(
    db: Session,
    fecha: date,
    hora: time,
    empleado_id: int,
    servicio: Servicio | int,
) -> bool:
    """Devuelve **True** si *empleado_id* está libre en *fecha* a *hora*.

    Args:
        db: Sesión SQLAlchemy viva.
        fecha: Día elegido.
        hora: Hora de inicio (time).
        empleado_id: ID del estilista / barbero.
        servicio: Instancia ``Servicio`` **o** ``servicio_id``.
    """
    # Asegura instancia Servicio
    if isinstance(servicio, int):
        servicio = db.get(Servicio, servicio)
    if not servicio:
        raise ValueError(f"Servicio no encontrado: {servicio} 👀")
    
    # Rango de la nueva cita
    new_start = hora
    new_end = _compute_end(hora, servicio.duracion_max or servicio.duracion_min)

    # Consulta citas existentes ese día con posible solapamiento
    existing: list[Cita] = (
        db.query(Cita)
        .filter(
            Cita.empleado_id == empleado_id,
            Cita.fecha == fecha,
        )
        .all()
    )

    # Revisa si hay solapamientos
    for cita in existing:
        cita_end = _compute_end(cita.hora, servicio.duracion_max or servicio.duracion_min)
        if _slot_overlaps(new_start, new_end, cita.hora, cita_end):
            return False
    return True

def book_slot(
    db: Session,
    cliente_id: int,
    servicio_id: int,
    empleado_id: int,
    fecha: date,
    hora: time,
) -> Cita:
    """Crea la cita *si y solo si* el slot está libre; de lo contrario lanza ``ValueError``."""
    servicio = db.get(Servicio, servicio_id)
    if servicio is None:
        raise ValueError("Servicio inexistente")

    if not is_slot_available(db, fecha, hora, empleado_id, servicio):
        raise SlotOccupiedError("Slot no disponible ⛔")
    
    cita = Cita(
        fecha=fecha,
        hora=hora,
        cliente_id=cliente_id,
        servicio_id=servicio_id,
        empleado_id=empleado_id,
    )
    db.add(cita)
    db.flush()  # obtiene ID sin commit para que capa superior decida
    return cita

# ────────────────────────────────────────────────────────────────────────────────
# Ejemplo CLI
# ────────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from datetime import date, time
    from db.session import get_session

    with get_session() as session:
        disponible = is_slot_available(session, date.today(), time(10), 1, 1)
        print("Disponible?", disponible)

