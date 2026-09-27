from sqlalchemy.orm import Session
from app.domain.entities.proveedor import Proveedor
from app.domain.repositories.proveedor_repository import IProveedorRepository
from app.infrastructure.models.proveedor_model import ProveedorModel


class SQLAlchemyProveedorRepository(IProveedorRepository):
    def __init__(self, db: Session):
        self.db = db

    def _a_entidad(self, p: ProveedorModel) -> Proveedor:
        return Proveedor(id=p.id, nombre=p.nombre, contacto=p.contacto, codigo_proveedor=p.codigo_proveedor)

    def get_all(self):
        return [self._a_entidad(p) for p in self.db.query(ProveedorModel).all()]

    def get_by_id(self, proveedor_id: int):
        p = self.db.query(ProveedorModel).filter(ProveedorModel.id == proveedor_id).first()
        return self._a_entidad(p) if p else None

    def create(self, proveedor: Proveedor):
        p = ProveedorModel(nombre=proveedor.nombre, contacto=proveedor.contacto, codigo_proveedor=proveedor.codigo_proveedor)
        self.db.add(p)
        self.db.commit()
        self.db.refresh(p)
        return self._a_entidad(p)

    def update(self, proveedor: Proveedor):
        p = self.db.query(ProveedorModel).filter(ProveedorModel.id == proveedor.id).first()
        p.nombre = proveedor.nombre
        p.contacto = proveedor.contacto
        p.codigo_proveedor = proveedor.codigo_proveedor
        self.db.commit()
        self.db.refresh(p)
        return self._a_entidad(p)

    def delete(self, proveedor_id: int):
        p = self.db.query(ProveedorModel).filter(ProveedorModel.id == proveedor_id).first()
        if p:
            self.db.delete(p)
            self.db.commit()
