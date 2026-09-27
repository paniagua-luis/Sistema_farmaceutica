from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.infrastructure.database import Base


class LoteModel(Base):
    __tablename__ = "lotes"

    id = Column(Integer, primary_key=True, index=True)
    codigo_lote = Column(String(50), unique=True, nullable=False)
    medicamento_id = Column(Integer, ForeignKey("medicamentos.id"), nullable=False)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=False)
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=False)
    cantidad_recibida = Column(Integer, nullable=False)
    cantidad_disponible = Column(Integer, nullable=False, default=0)
    fecha_recepcion = Column(Date, nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)
    estado_lote = Column(String(30), nullable=False, default="pendiente_verificacion")

    medicamento = relationship("MedicamentoModel")
    proveedor = relationship("ProveedorModel")
    sucursal = relationship("SucursalModel")
