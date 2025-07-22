# alembic/env.py
from logging.config import fileConfig
from alembic import context

# --- Configuración de logging ---
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Importa tu engine y metadata ---
from db.engine import engine            # usa el engine ya configurado
from db.models import Base

target_metadata = Base.metadata         # ← autogenerate escaneará esto

# --- Inserta la URL del engine en la config (útil para offline) ---
config.set_main_option("sqlalchemy.url", str(engine.url))

# ---------------- Modo OFFLINE ----------------
def run_migrations_offline() -> None:
    """Genera el SQL sin conectarse a la BD."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,              # detecta cambios de tipo
    )
    with context.begin_transaction():
        context.run_migrations()

# ---------------- Modo ONLINE -----------------
def run_migrations_online() -> None:
    """Aplica las migraciones conectándose a la BD."""
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,          # detecta cambios de tipo
        )
        with context.begin_transaction():
            context.run_migrations()

# -------- Dispatcher --------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

