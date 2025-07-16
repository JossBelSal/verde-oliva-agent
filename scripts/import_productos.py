"""
Importa / actualiza productos desde data/productos.csv
en la tabla dbo.productos_oliva  (SQL Azure).

Estrategia ▸ UPSERT por `nombre`
--------------------------------
• Si el nombre YA existe → UPDATE de los campos cambiados
• Si el nombre NO existe → INSERT de un nuevo producto
"""

import re
from decimal import Decimal
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from db.session import SessionLocal          # factory de scoped_session
from db.models  import Producto              # ORM → tabla productos_oliva

# ───── Ruta del CSV ──────────────────────────────────────────────────
CSV_FILE = Path("data/productos.csv")        # ajusta la carpeta si cambias

# ───── Helpers de limpieza ───────────────────────────────────────────
_rx_num = re.compile(r"\d+(?:[\.,]\d+)?")

def _precio_num(raw: str) -> Decimal | None:
    """
    '$2,000 MXP' → 2000    ·    '900' → 900
    Devuelve None si no hay números.
    """
    m = _rx_num.search(raw or "")
    return Decimal(m.group().replace(",", "")) if m else None


# ───── Importación principal ─────────────────────────────────────────
def import_csv(path: Path = CSV_FILE) -> None:
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")

    # 1) Lee CSV y normaliza cabeceras
    df = (
        pd.read_csv(path, dtype=str)
          .fillna("")
          .rename(columns=lambda c: c.strip())
          # Aceptamos ‘Especificaciones’ como alias legado de ‘Detalles’
          .rename(columns={"Especificaciones": "Detalles"})
    )

    session: Session = SessionLocal()
    nuevos, actualizados = 0, 0          # métricas finales

    for r in df.itertuples(index=False):
        # ---------------- valores crudos -------------------
        nombre     = r.Nombre.strip()
        categoria  = r.Categoría.strip()
        detalles   = (str(r.Detalles).strip() or "—")[:800]   # máx 800 chars
        precio_txt = r.Precio.strip()

        # ---------------- valores normalizados -------------
        precio_num = _precio_num(precio_txt)

        # ---------------- instancia ORM --------------------
        prod = Producto(
            nombre     = nombre,
            categoria  = categoria,
            detalles   = detalles,
            precio     = precio_num,
        )

        # ---------------- UPSERT por nombre ----------------
        existing_id = (
            session.query(Producto.id)
                   .filter_by(nombre=nombre)
                   .scalar()              # None si no existe
        )
        if existing_id is not None:
            prod.id = existing_id         # MERGE ⇒ UPDATE
            actualizados += 1
        else:
            nuevos += 1                   # MERGE ⇒ INSERT

        session.merge(prod)

    session.commit()
    session.close()

    print(
        f"✅ Productos cargados / actualizados sin errores.\n"
        f"   Nuevos: {nuevos} · Actualizados: {actualizados}"
    )


# ───── Ejecución desde la terminal ───────────────────────────────────
if __name__ == "__main__":
    import_csv()
