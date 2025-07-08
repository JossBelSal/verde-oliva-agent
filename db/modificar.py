from sqlalchemy import text
from db.engine import engine                      # tu create_engine()

with engine.begin() as conn:
    # usa el esquema donde vive la tabla (dbo por defecto)
    conn.execute(text("IF OBJECT_ID('dbo.servicios_oliva','U') IS NOT NULL "
                      "DROP TABLE dbo.servicios_oliva"))
