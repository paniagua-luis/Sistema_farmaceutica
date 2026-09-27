from sqlalchemy.orm import Session
from app.domain.entities.inspeccion_calidad import InspeccionCalidad
from app.domain.repositories.inspeccion_calidad_repository import IInspeccionCalidadRepository
from app.infrastructure.models.inspeccion_calidad_model import InspeccionCalidadModel


class SQLAlchemyInspeccionCalidadRepository(IInspeccionCalidadRepository):
    def __init__(self, db: Session):
        self.db = db

    def _a_entidad(self, i: InspeccionCalidadModel) -> InspeccionCalidad:
        return InspeccionCalidad(
            id=i.id, lote_id=i.lote_id, usuario_id=i.usuario_id,
            resultado=i.resultado, observaciones=i.observaciones, fecha_inspeccion=i.fecha_inspeccion,
        )

    def get_all(self):
        return [self._a_entidad(i) for i in self.db.query(InspeccionCalidadModel).all()]

    def get_by_id(self, inspeccion_calidad_id: int):
        i = self.db.query(InspeccionCalidadModel).filter(InspeccionCalidadModel.id == inspeccion_calidad_id).first()
        return self._a_entidad(i) if i else None

    def get_by_lote(self, lote_id: int):
        return [self._a_entidad(i) for i in self.db.query(InspeccionCalidadModel).filter(InspeccionCalidadModel.lote_id == lote_id).all()]

    def create(self, inspeccion_calidad: InspeccionCalidad):
        i = InspeccionCalidadModel(
            lote_id=inspeccion_calidad.lote_id, usuario_id=inspeccion_calidad.usuario_id,
            resultado=inspeccion_calidad.resultado, observaciones=inspeccion_calidad.observaciones,
        )
        self.db.add(i)
        self.db.commit()
        self.db.refresh(i)
        return self._a_entidad(i)
