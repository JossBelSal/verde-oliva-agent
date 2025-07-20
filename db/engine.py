# db/engine.py
# ==============================================================================
import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# 1) Carga el .env
load_dotenv()

# 2) Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 3) Lista esperada de variables de entorno
REQUIRED_ENV_VARS = ["AZ_Driver", "AZ_HOST", "AZ_DB", "AZ_USER", "AZ_PASS"]

# 4) Detecta cuáles faltan
missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing:
    logger.error(f"❌ Faltan las siguientes variables de entorno: {', '.join(missing)}")
    raise EnvironmentError(f"Faltan variables de entorno: {', '.join(missing)}")

# 5) Lee las variables y asigna con seguridad
driver = os.getenv("AZ_Driver", "")
host   = os.getenv("AZ_HOST", "")
db     = os.getenv("AZ_DB", "")
user   = os.getenv("AZ_USER", "")
pass_  = quote_plus(os.getenv("AZ_PASS", ""))  # Escapa caracteres especiales
 
# 6) Construye la cadena de conexión
def buid_connection_string() -> str:
    """
    Construye la cadena de conexión para SQLAlchemy.
    """
    return (
        f"mssql+pyodbc://{user}:{pass_}@{host}:1433/{db}"
        f"?driver={driver.replace(' ', '+')}"
    )
conn_str = buid_connection_string()

# 7) Crea el engine y prueba la conexión
engine = create_engine(
    conn_str,
    echo=False,
    fast_executemany=True,
    pool_pre_ping=True      # <-- reconexión automática 
    #pool_recycle=1800 #Se reconecta cada 30 min la base de datos
)
# 8) Verifica la conexión
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.info(f"✅ Conexión exitosa a la base de datos: {db}.")
except Exception as e:
    logger.error(f"❌ Error al conectar: {e}")
