#============================================================
#=========== importacion de los csv a la base de datos ======
#============================================================

from scripts import import_servicios, import_personal, import_productos

def run():
    for fn in (import_servicios, import_personal, import_productos):
        fn()
    print("✅ Importación de datos completada.")

if __name__ == "__main__":
    run()