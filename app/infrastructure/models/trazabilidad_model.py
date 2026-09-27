from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.infrastructure.database import Base


class TrazabilidadModel(Base):
    __tablename__ = "trazabilidad"

    id = Column(Integer, primary_key=True, index=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    tipo_evento = Column(String(80), nullable=False)
    descripcion = Column(String(500), nullable=False)
    fecha = Column(DateTime(timezone=True), server_default=func.now())
