from sqlalchemy import Column, Integer, String
from app.infrastructure.database import Base


class SucursalModel(Base):
    __tablename__ = "sucursales"

    id = Column(Integer, primary_key=True, index=True)
    codigo_sucursal = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(150), nullable=False)
