# core/booking_handler.py
"""Disponibilidad y reservas para Oliva (function‑calling).

Puntos de entrada *sync*:

* check_availability(data)   → solo consulta el hueco
* process_booking_request(data) → valida y crea la cita
"""

from __future__ import annotations

import datetime as dt
from datetime import date, time
from typing import Any, Dict

from sqlalchemy.orm import Session

from db.session import SessionLocal
from db.models import Servicio, Cita
from core.scheduler import is_slot_available, book_slot, next_free_slots
from utils.datetime_parser import datetime_parser  # regex + IA

# ───────────────────────── helpers internos ──────────────────────────


class _ValidationError(ValueError):
    """Entrada incompleta o mal formada."""


def _ensure_int(data: Dict[str, Any], key: str) -> int:
    try:
        return int(data[key])
    except (KeyError, TypeError, ValueError):
        raise _ValidationError(f"Parámetro faltante o inválido: {key}") from None


def _parse_date(data: Dict[str, Any]) -> date:
    """ISO date o se extrae de fecha_texto."""
    if d := data.get("fecha"):
        return date.fromisoformat(str(d))
    if txt := data.get("fecha_texto"):
        iso = datetime_parser(txt)
        if iso:
            return dt.datetime.fromisoformat(iso[0]).date()
    raise _ValidationError("Falta fecha")


def _parse_time(data: Dict[str, Any]) -> time:
    """ISO time o se extrae de fecha_texto."""
    if t := data.get("hora"):
        return time.fromisoformat(str(t))
    if txt := data.get("fecha_texto"):
        iso = datetime_parser(txt)
        if iso:
            return dt.datetime.fromisoformat(iso[0]).time()
    raise _ValidationError("Falta hora")


def _compute_end(start: time, minutes: int) -> time:
    dt_start = dt.datetime.combine(date.today(), start)
    return (dt_start + dt.timedelta(minutes=minutes)).time()


# ───────────────────────────── API pública ───────────────────────────


def check_availability(data: Dict[str, Any]) -> Dict[str, Any]:
    """True si libre; False con sugerencias si ocupado."""
    db: Session = SessionLocal()
    try:
        servicio_id = _ensure_int(data, "servicio_id")
        empleado_id = _ensure_int(data, "empleado_id")
        fecha = _parse_date(data)
        hora = _parse_time(data)

        if is_slot_available(db, fecha, hora, empleado_id, servicio_id):
            return {"ok": True}

        sugerencias = next_free_slots(
            db, fecha, hora, empleado_id, servicio_id, n=3, step_min=30
        )
        return {
            "ok": False,
            "reason": "slot_occupied",
            "suggestions": sugerencias,
        }
    finally:
        db.close()


def process_booking_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Crea la cita o devuelve alternativas si el hueco no está disponible."""
    db: Session = SessionLocal()
    try:
        cliente_id = _ensure_int(data, "cliente_id")
        servicio_id = _ensure_int(data, "servicio_id")
        empleado_id = _ensure_int(data, "empleado_id")
        fecha = _parse_date(data)
        hora = _parse_time(data)

        # 1. disponibilidad
        if not is_slot_available(db, fecha, hora, empleado_id, servicio_id):
            sugerencias = next_free_slots(
                db, fecha, hora, empleado_id, servicio_id, n=3, step_min=30
            )
            return {
                "ok": False,
                "reason": "slot_occupied",
                "suggestions": sugerencias,
            }

        # 2. crear cita
        cita: Cita = book_slot(
            db,
            cliente_id=cliente_id,
            servicio_id=servicio_id,
            empleado_id=empleado_id,
            fecha=fecha,
            hora=hora,
        )
        db.commit()

        servicio: Servicio = db.get(Servicio, servicio_id)
        duracion = servicio.duracion_max or servicio.duracion_min or 60
        hora_fin = _compute_end(hora, duracion)

        return {
            "ok": True,
            "cita_id": cita.id,
            "inicio": f"{fecha}T{hora}",
            "fin": f"{fecha}T{hora_fin}",
        }
    except _ValidationError as ve:
        return {"ok": False, "reason": "validation_error", "detail": str(ve)}
    finally:
        db.close()
