"""
scripts/import_servicios.py
──────────────────────────
Carga (o actualiza) los servicios que vienen en data/servicios.csv
dejándolos normalizados en la tabla dbo.servicios_oliva.

• Si el nombre ya existe           → UPDATE  
• Si el nombre no existe           → INSERT  
"""

import re
import unicodedata as ud
from decimal import Decimal
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from db.session import SessionLocal          # scoped_session factory
from db.models  import Servicio              # ORM

CSV_FILE = Path("data/servicios.csv")        # <- ajusta ruta si es necesario
# ──────────────────────────────────────────────────────────────────────────────
# 1. Helpers de limpieza
# ──────────────────────────────────────────────────────────────────────────────
_rx_num = re.compile(r"\d+(?:[\.,]\d+)?")

def _mins(raw: str) -> tuple[int | None, int | None]:
    """'1‑1.5 horas'  → (60, 90)   |   '1 hora' → (60, None)"""
    nums = [float(n.replace(",", ".")) for n in _rx_num.findall(raw)]
    if not nums:
        return None, None
    mins = [int(x * 60) for x in nums]
    return mins[0], mins[1] if len(mins) > 1 else None

def _monto(raw: str) -> tuple[Decimal | None, Decimal | None]:
    """'$400–$500 MXP' → (400, 500)   |   '$700 MXP' → (700, None)"""
    nums = [n.replace("$", "").replace(",", "") for n in _rx_num.findall(raw)]
    if not nums:
        return None, None
    decs = [Decimal(n) for n in nums]
    return decs[0], decs[1] if len(decs) > 1 else None

def _deposito(raw: str) -> Decimal | None:
    """'$300 MXP' → 300   |   'No' → None"""
    if not raw or raw.strip().lower() == "no":
        return None
    monto, _ = _monto(raw)
    return monto

def _ascii(s: str) -> str:
    """Normaliza a ASCII (sin acentos) y pone guiones bajos."""
    return (
        ud.normalize("NFKD", s)
        .encode("ascii", "ignore")
        .decode()
        .replace(" ", "_")
    )

# ──────────────────────────────────────────────────────────────────────────────
# 2. Importación
# ──────────────────────────────────────────────────────────────────────────────
def import_csv(csv_path: Path = CSV_FILE) -> None:
    if not csv_path.exists():
        raise FileNotFoundError(csv_path)

    # a) Lee el archivo y renombra las columnas a ASCII “limpio”
    df = (
        pd.read_csv(csv_path, dtype=str)
        .fillna("")
        .rename(columns=lambda c: _ascii(c))
    )
    # Espera columnas: Categoria, Nombre, Duracion, Precio, Deposito, Detalles
    required = {"Categoria", "Nombre", "Duracion", "Precio", "Deposito", "Detalles"}
    missing  = required - set(df.columns)
    if missing:
        raise ValueError(f"❌  Faltan columnas: {', '.join(missing)}")

    session: Session = SessionLocal()
    insertados = actualizados = 0            # métricas simples

    for r in df.itertuples(index=False):
        nombre    = r.Nombre.strip()
        categoria = r.Categoria.strip()

        dur_lo, dur_hi = _mins(r.Duracion)
        pre_lo, pre_hi = _monto(r.Precio)
        deposito_num   = _deposito(r.Deposito)

        # 1) ¿Existe un registro con ese nombre?
        existing: Servicio | None = (
            session.query(Servicio).filter_by(nombre=nombre).one_or_none()
        )

        if existing:                         # ---- UPDATE -------------------
            existing.categoria     = categoria
            existing.duracion_txt  = r.Duracion
            existing.precio_txt    = r.Precio
            existing.deposito_txt  = r.Deposito
            existing.detalles      = r.Detalles.strip()[:800]

            existing.duracion_min  = dur_lo
            existing.duracion_max  = dur_hi
            existing.precio_min    = pre_lo
            existing.precio_max    = pre_hi
            existing.deposito      = deposito_num
            existing.activo        = True

            actualizados += 1

        else:                                # ---- INSERT -------------------
            nuevo = Servicio(
                nombre        = nombre,
                categoria     = categoria,
                duracion_txt  = r.Duracion,
                precio_txt    = r.Precio,
                deposito_txt  = r.Deposito,
                detalles      = r.Detalles.strip()[:800],
                duracion_min  = dur_lo,
                duracion_max  = dur_hi,
                precio_min    = pre_lo,
                precio_max    = pre_hi,
                deposito      = deposito_num,
                activo        = True,
            )
            session.add(nuevo)
            insertados += 1

    session.commit()
    session.close()

    print(
        f"✅  Servicios procesados sin errores.\n"
        f"   • Nuevos: {insertados}\n"
        f"   • Actualizados: {actualizados}"
    )


# Ejecutar desde CLI -----------------------------------------------------------
if __name__ == "__main__":
    import_csv()
