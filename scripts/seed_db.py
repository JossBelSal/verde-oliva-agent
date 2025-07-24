#============================================================
#=========== importacion de los csv a la base de datos ======
#============================================================

# scripts/seed_db.py
from db.session import SessionLocal

from scripts.import_servicios import load as load_servicios
from scripts.import_productos  import load as load_productos
from scripts.import_personal   import load as load_personal

def main() -> None:
    print("🌱  Sembrando base de datos…")
    with SessionLocal() as session:
        rep = {}

        rep["servicios"] = load_servicios(session)
        rep["productos"] = load_productos(session)
        rep["personal"]  = load_personal(session)

        session.commit()

    # 🎯 reporte bonito
    print("\n────────── RESUMEN ──────────")
    for k,(n,u) in rep.items():
        print(f"• {k.capitalize():10s} ▸ Nuevos: {n:<3}  Actualizados: {u}")
    print("✅ Importación completada sin errores.\n")

if __name__ == "__main__":
    main()
