from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from app.infrastructure.database import Base


class MonitoreoTemperaturaModel(Base):
    __tablename__ = "monitoreo_temperatura"

    id = Column(Integer, primary_key=True, index=True)
    codigo_lectura = Column(String(50), unique=True, nullable=False)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=True)
    ubicacion_almacen = Column(String(150), nullable=False)
    temperatura_registrada = Column(Float, nullable=False)
    estado_lectura = Column(String(30), nullable=False, default="normal")
    fecha_hora = Column(DateTime(timezone=True), server_default=func.now())
