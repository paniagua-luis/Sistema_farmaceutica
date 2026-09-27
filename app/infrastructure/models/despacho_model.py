from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.infrastructure.database import Base


class DespachoModel(Base):
    __tablename__ = "despachos"

    id = Column(Integer, primary_key=True, index=True)
    codigo_despacho = Column(String(50), unique=True, nullable=False)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=False)
    cantidad_despachada = Column(Integer, nullable=False)
    estado_despacho = Column(String(30), nullable=False, default="en_transito")
    fecha_despacho = Column(DateTime(timezone=True), server_default=func.now())
    fecha_recepcion = Column(DateTime(timezone=True), nullable=True)
