# db/models.py
from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    Column, String, Integer, Text, Float, Numeric,
    DateTime, MetaData, UniqueConstraint, Boolean
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# ───────── Convención global de nombres ─────────
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata_obj = MetaData(naming_convention=naming_convention)

# ------------------------------------------------------------------
#  Declarative Base
# ------------------------------------------------------------------
class Base(DeclarativeBase):
    metadata = metadata_obj
    type_annotation_map = {
        int:     Integer,
        str:     String,
        float:   Float,
        Decimal: Numeric(10, 2),
    }

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

# ------------------------------------------------------------------
# 1. Clientes
# ------------------------------------------------------------------
class Cliente(Base):
    __tablename__ = "clientes_oliva"
    __table_args__ = (
        UniqueConstraint("telefono", name="uq_clientes_telefono"),
        UniqueConstraint("email",    name="uq_clientes_email"),
    )

    id:       Mapped[int]  = mapped_column(primary_key=True, autoincrement=True)
    nombre:   Mapped[str]  = mapped_column(String(120), nullable=False)
    telefono: Mapped[str]  = mapped_column(String(15),  index=True)
    email:    Mapped[str]  = mapped_column(String(120), index=True)

    ventas       = relationship("Venta",       back_populates="cliente", cascade="all, delete-orphan")
    citas        = relationship("Cita",        back_populates="cliente", cascade="all, delete-orphan")
    valoraciones = relationship("Valoracion",  back_populates="cliente", cascade="all, delete-orphan")
    quejas       = relationship("QuejaSugerencia", back_populates="cliente", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Cliente {self.id} {self.nombre}>"

# ------------------------------------------------------------------
# 2. Personal
# ------------------------------------------------------------------

class Empleado(Base):
    __tablename__ = "personal_oliva"

    id:       Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre:   Mapped[str] = mapped_column(String(120), nullable=False)
    puesto:   Mapped[str] = mapped_column(String(60))        # “estilista”, “recepción”…
    telefono: Mapped[str] = mapped_column(String(20))
    email:    Mapped[str] = mapped_column(String(120))

    servicios = relationship("EmpleadoServicioHorario", back_populates="empleado")
    citas     = relationship("Cita", back_populates="empleado")
    asist     = relationship("AsistenciaEmpleado", back_populates="empleado")

# ------------------------------------------------------------------
# 3-4. Catálogos de servicios y productos
# ------------------------------------------------------------------

class Servicio(Base):
    __tablename__ = "servicios_oliva"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    categoria   = Column(String(80),  nullable=False)       # “Cortes”
    nombre      = Column(String(120), nullable=False)       # “Corte Dama”
    
    # --- datos mostrados al usuario ------------------------
    duracion_txt = Column(String(40))      # “1-1.5 horas”
    precio_txt   = Column(String(40))      # “$400–$500 MXP”
    deposito_txt = Column(String(30))      # “No” | “$300 MXP”
    detalles     = Column(Text)

    # --- datos normalizados para filtros / BI -------------
    duracion_min = Column(Integer)         # mínimo en minutos
    duracion_max = Column(Integer)         # máximo en minutos
    precio_min   = Column(Numeric(10, 2))  # 400.00
    precio_max   = Column(Numeric(10, 2))  # 500.00
    deposito     = Column(Numeric(10, 2))  # NULL si no aplica

    activo       = Column(Boolean, default=True)

class Producto(Base):
    __tablename__ = "productos_oliva"

    id:             Mapped[int]         = mapped_column(primary_key=True, autoincrement=True)
    nombre:         Mapped[str]         = mapped_column(String(120), unique=True, nullable=False)
    categoria:      Mapped[str]         = mapped_column(String(60), index=True)
    detalles:       Mapped[str]         = mapped_column(String(800))
    precio:         Mapped[Decimal]     = mapped_column(Numeric(10,2))
    