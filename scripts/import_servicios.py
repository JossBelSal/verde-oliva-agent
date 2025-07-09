"""
Carga / actualiza los servicios desde data/servicios.csv
y los deja normalizados en la tabla dbo.servicios_oliva
"""
import re
from decimal import Decimal

import pandas as pd
from sqlalchemy.orm import Session

from db.session import SessionLocal           # scoped_session factory
from db.models  import Servicio               # ORM

CSV_FILE = "data/servicios.csv"

# ───────── helpers de limpieza ──────────────────────────────────
_rx_num = re.compile(r"\d+(?:[\.,]\d+)?")

def _mins(raw: str) -> tuple[int | None, int | None]:
    """‘1-1.5 horas’ → (60, 90) ; ‘1 hora’ → (60,None)"""
    nums = [float(n.replace(",", "."))
            for n in _rx_num.findall(raw)]
    if not nums:
        return None, None
    mins = [int(x * 60) for x in nums]
    return mins[0], mins[1] if len(mins) > 1 else None

def _monto(raw: str) -> tuple[Decimal | None, Decimal | None]:
    """‘$400–$500 MXP’ → (400,500) ; ‘$700 MXP’ → (700,None)"""
    nums = [n.replace("$", "").replace(",", "")
            for n in _rx_num.findall(raw)]
    if not nums:
        return None, None
    decs = [Decimal(n) for n in nums]
    return decs[0], decs[1] if len(decs) > 1 else None

def _deposito(raw: str) -> Decimal | None:
    """‘$300 MXP’ → 300 ; ‘No’ → None"""
    if not raw or raw.strip().lower() == "no":
        return None
    monto, _ = _monto(raw)
    return monto

# ───────── importación ─────────────────────────────────────────
def import_csv(path: str = CSV_FILE) -> None:
    df = pd.read_csv(path, dtype=str).fillna("")
    session: Session = SessionLocal()

    for r in df.itertuples(index=False):
        # 1. valores crudos (texto que verá la clienta)
        dur_txt, pre_txt, dep_txt = r.Duración, r.Precio, r.Depósito

        # 2. valores numéricos normalizados
        dur_lo, dur_hi = _mins(dur_txt)
        pre_lo, pre_hi = _monto(pre_txt)
        deposito_num   = _deposito(dep_txt)

        srv = Servicio(
            categoria    = r.Categoría.strip(),
            nombre       = r.Nombre.strip(),
            duracion_txt = dur_txt,
            precio_txt   = pre_txt,
            deposito_txt = dep_txt,
            detalles     = r.Detalles.strip()[:800],

            duracion_min = dur_lo,
            duracion_max = dur_hi,
            precio_min   = pre_lo,
            precio_max   = pre_hi,
            deposito     = deposito_num,
            activo       = True
        )

        # UPSERT por nombre (unique=True)
        session.merge(srv)

    session.commit()
    session.close()
    print("✅  Servicios cargados / actualizados sin errores.")

if __name__ == "__main__":
    import_csv()
