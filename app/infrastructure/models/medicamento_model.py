from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.infrastructure.database import Base


class MedicamentoModel(Base):
    __tablename__ = "medicamentos"

    id = Column(Integer, primary_key=True, index=True)
    codigo_medicamento = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(150), nullable=False)
    principio_activo = Column(String(150), nullable=False)
    temperatura_minima = Column(Float, nullable=False)
    temperatura_maxima = Column(Float, nullable=False)
    dias_alerta_vencimiento = Column(Integer, nullable=False, default=30)
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())