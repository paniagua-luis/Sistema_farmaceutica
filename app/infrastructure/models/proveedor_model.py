from sqlalchemy import Column, Integer, String
from app.infrastructure.database import Base


class ProveedorModel(Base):
    __tablename__ = "proveedores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    contacto = Column(String(150), nullable=True)
    codigo_proveedor = Column(String(50), unique=True, nullable=False)
