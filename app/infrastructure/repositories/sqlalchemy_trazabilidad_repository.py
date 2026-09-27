from sqlalchemy.orm import Session
from app.domain.entities.trazabilidad import Trazabilidad
from app.domain.repositories.trazabilidad_repository import ITrazabilidadRepository
from app.infrastructure.models.trazabilidad_model import TrazabilidadModel


class SQLAlchemyTrazabilidadRepository(ITrazabilidadRepository):
    def __init__(self, db: Session):
        self.db = db

    def _a_entidad(self, t: TrazabilidadModel) -> Trazabilidad:
        return Trazabilidad(
            id=t.id, lote_id=t.lote_id, usuario_id=t.usuario_id,
            tipo_evento=t.tipo_evento, descripcion=t.descripcion, fecha=t.fecha,
        )

    def get_all(self):
        return [self._a_entidad(t) for t in self.db.query(TrazabilidadModel).order_by(TrazabilidadModel.fecha.desc()).all()]

    def get_by_lote(self, lote_id: int):
        return [self._a_entidad(t) for t in self.db.query(TrazabilidadModel).filter(TrazabilidadModel.lote_id == lote_id).order_by(TrazabilidadModel.fecha.desc()).all()]

    def create(self, evento: Trazabilidad):
        t = TrazabilidadModel(
            lote_id=evento.lote_id, usuario_id=evento.usuario_id,
            tipo_evento=evento.tipo_evento, descripcion=evento.descripcion,
        )
        self.db.add(t)
        self.db.commit()
        self.db.refresh(t)
        return self._a_entidad(t)
