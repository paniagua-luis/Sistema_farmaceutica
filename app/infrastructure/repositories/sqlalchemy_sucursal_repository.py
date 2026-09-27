from sqlalchemy.orm import Session
from app.domain.entities.sucursal import Sucursal
from app.domain.repositories.sucursal_repository import ISucursalRepository
from app.infrastructure.models.sucursal_model import SucursalModel


class SQLAlchemySucursalRepository(ISucursalRepository):
    def __init__(self, db: Session):
        self.db = db

    def _a_entidad(self, s: SucursalModel) -> Sucursal:
        return Sucursal(id=s.id, codigo_sucursal=s.codigo_sucursal, nombre=s.nombre)

    def get_all(self):
        return [self._a_entidad(s) for s in self.db.query(SucursalModel).all()]

    def get_by_id(self, sucursal_id: int):
        s = self.db.query(SucursalModel).filter(SucursalModel.id == sucursal_id).first()
        return self._a_entidad(s) if s else None

    def create(self, sucursal: Sucursal):
        s = SucursalModel(codigo_sucursal=sucursal.codigo_sucursal, nombre=sucursal.nombre)
        self.db.add(s)
        self.db.commit()
        self.db.refresh(s)
        return self._a_entidad(s)

    def update(self, sucursal: Sucursal):
        s = self.db.query(SucursalModel).filter(SucursalModel.id == sucursal.id).first()
        s.codigo_sucursal = sucursal.codigo_sucursal
        s.nombre = sucursal.nombre
        self.db.commit()
        self.db.refresh(s)
        return self._a_entidad(s)

    def delete(self, sucursal_id: int):
        s = self.db.query(SucursalModel).filter(SucursalModel.id == sucursal_id).first()
        if s:
            self.db.delete(s)
            self.db.commit()
