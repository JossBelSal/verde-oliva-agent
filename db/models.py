# db/models.py
from datetime import datetime, date, time                # ← tipos Python
from decimal import Decimal
from sqlalchemy import (
    Column, String, Integer, Date, Time, Text, Numeric,
    DateTime, MetaData, UniqueConstraint, Boolean, ForeignKey
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# ──────────── convención global de nombres ────────────
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata_obj = MetaData(naming_convention=naming_convention)


class Base(DeclarativeBase):
    metadata = metadata_obj
    type_annotation_map = {          # default-mapping opcional
        int:     Integer,
        str:     String,
        float:   Numeric(10, 2),
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

# ─────────────────────── 1. Cliente ───────────────────────
class Cliente(Base):
    __tablename__ = "clientes_oliva"
    __table_args__ = (
        UniqueConstraint("telefono"),
        UniqueConstraint("email"),
    )

    id:       Mapped[int]  = mapped_column(primary_key=True, autoincrement=True)
    nombre:   Mapped[str]  = mapped_column(String(120), nullable=False)
    telefono: Mapped[str]  = mapped_column(String(15),  index=True)
    email:    Mapped[str]  = mapped_column(String(120), index=True)

    citas = relationship("Cita", back_populates="cliente")   # Venta vendrá luego

# ─────────────────────── 2. Personal ───────────────────────
class Empleado(Base):
    __tablename__ = "personal_oliva"

    id:       Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre:   Mapped[str] = mapped_column(String(120), nullable=False)
    puesto:   Mapped[str] = mapped_column(String(60))
    telefono: Mapped[str] = mapped_column(String(20))
    email:    Mapped[str] = mapped_column(String(120))

    citas = relationship("Cita", back_populates="empleado")

# ───────────────── 3. Catálogo de servicios ─────────────────
class Servicio(Base):
    __tablename__ = "servicios_oliva"

    id:          Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    categoria:   Mapped[str] = mapped_column(String(80),  nullable=False)
    nombre:      Mapped[str] = mapped_column(String(120), nullable=False, unique=True)

    # texto que muestra Oliva
    duracion_txt = mapped_column(String(40))
    precio_txt   = mapped_column(String(40))
    deposito_txt = mapped_column(String(30))
    detalles     = mapped_column(Text)

    # valores normalizados
    duracion_min = mapped_column(Integer)
    duracion_max = mapped_column(Integer)
    precio_min   = mapped_column(Numeric(10, 2))
    precio_max   = mapped_column(Numeric(10, 2))
    deposito     = mapped_column(Numeric(10, 2))
    activo       = mapped_column(Boolean, default=True)

# ─────────────────────── 5. Cita ───────────────────────
class Cita(Base):
    __tablename__ = "citas"
    __table_args__ = (
        UniqueConstraint("fecha", "hora", "empleado_id", name="uq_empleado_slot"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    fecha: Mapped[date] = mapped_column(Date,  nullable=False)   # ← date/time Python
    hora:  Mapped[time] = mapped_column(Time,  nullable=False)

    cliente_id:  Mapped[int] = mapped_column(ForeignKey("clientes_oliva.id"),    nullable=False)
    servicio_id: Mapped[int] = mapped_column(ForeignKey("servicios_oliva.id"),   nullable=False)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("personal_oliva.id"),    nullable=True)

    cliente  = relationship("Cliente",  back_populates="citas")
    servicio = relationship("Servicio")
    empleado = relationship("Empleado", back_populates="citas")

# ─────────────────────── (más tablas…) ───────────────────────
#  Cuando crees Venta, DetalleTicket, etc. - agrégalas DESPUÉS
#  y actualiza las relationships que habían quedado comentadas.
