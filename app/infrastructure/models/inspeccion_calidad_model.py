from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.infrastructure.database import Base


class InspeccionCalidadModel(Base):
    __tablename__ = "inspecciones_calidad"

    id = Column(Integer, primary_key=True, index=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    resultado = Column(String(20), nullable=False)
    observaciones = Column(String(500), nullable=True)
    fecha_inspeccion = Column(DateTime(timezone=True), server_default=func.now())
