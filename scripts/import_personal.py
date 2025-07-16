# Carga archivo CSV Personal
import re
import pandas as pd
from sqlalchemy.orm import Session

from db.session import SessionLocal  # scoped_session factory
from db.models import Empleado  # ORM

CSV_FILE = "data/personal.csv"

# ───────── helpers de limpieza ──────────────────────────────────
_re_digits = re.compile(r"\d+") # Extrae uno o más dígitos

def clean_phone(raw:str) -> str | None:
    """ Deja solo digitos y toma los 10 primeros. Formato MX"""
    if not raw:
        return None
    digits = "".join(_re_digits.findall(raw))
    return digits[:10] if len(digits) >= 10 else None

# ───────── importación ─────────────────────────────────────────

def import_csv(path: str = CSV_FILE) -> None:
    df: pd.DataFrame = pd.read_csv(path, dtype=str).fillna("")
    session: Session = SessionLocal()


    for r in df.itertuples(index=False):

        empl =  Empleado(
            nombre = r.nombre.strip(),
            puesto = r.puesto.strip(),
            telefono = clean_phone(r.telefono),
            email = r.email.strip() if r.email else None,
        )
        # UPSERT por e-mail o por nombre (ajusta según tu convención)
        session.merge(empl)
    session.commit()
    session.close()
    print(f"✅ {len(df)} registros cargados en personal_oliva")

if __name__ == "__main__":
    import_csv()
    print("Importacion completada. ✅")
