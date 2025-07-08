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

# 3) Lee las variables (con valor por defecto vacío)
driver = os.getenv("AZ_Driver", "")
host   = os.getenv("AZ_HOST", "")
db     = os.getenv("AZ_DB", "")
user   = os.getenv("AZ_USER", "")
pass_  = os.getenv("AZ_PASS", "")
 

# raw_pwd es un str garantizado, ahora sí:
pwd = quote_plus(pass_)

# 5) Construye la cadena de conexión
conn_str = (
    f"mssql+pyodbc://{user}:{pwd}@{host}:1433/{db}"
    f"?driver={driver.replace(' ', '+')}"
)

# 6) Crea el engine y prueba la conexión
engine = create_engine(
    conn_str,
    echo=False,
    fast_executemany=True,
    pool_pre_ping=True      # <-- reconexión automática 
    #pool_recycle=1800 #Se reconecta cada 30 min la base de datos
)

try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    logger.info(f"✅ Conexión exitosa a la base de datos: {db}.")
except Exception as e:
    logger.error(f"❌ Error al conectar: {e}")
