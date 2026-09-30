from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.infrastructure.database import Base


class LoteProductoModel(Base):
    __tablename__ = "lote_productos"
    __table_args__ = (
        UniqueConstraint("lote_id", "medicamento_id", name="uq_lote_producto"),
    )

    id = Column(Integer, primary_key=True, index=True)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False, index=True)
    medicamento_id = Column(Integer, ForeignKey("medicamentos.id"), nullable=False)
    cantidad_recibida = Column(Integer, nullable=False)
    cantidad_disponible = Column(Integer, nullable=False)

    lote = relationship("LoteModel", back_populates="productos")
    medicamento = relationship("MedicamentoModel")
