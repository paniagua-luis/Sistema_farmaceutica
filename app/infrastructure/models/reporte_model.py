from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.infrastructure.database import Base


class ReporteModel(Base):
    __tablename__ = "reportes"

    id = Column(Integer, primary_key=True, index=True)
    codigo_reporte = Column(String(50), unique=True, nullable=False)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=True)
    tipo_reporte = Column(String(80), nullable=False)
    destinatario = Column(String(150), nullable=False)
    contenido = Column(String(2000), nullable=False)
    fecha = Column(DateTime(timezone=False), server_default=func.now())
