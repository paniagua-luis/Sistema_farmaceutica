from sqlalchemy.orm import Session
from app.domain.entities.lote import Lote
from app.domain.repositories.lote_repository import ILoteRepository
from app.infrastructure.models.lote_model import LoteModel


class SQLAlchemyLoteRepository(ILoteRepository):
    def __init__(self, db: Session):
        self.db = db

    def _a_entidad(self, l: LoteModel) -> Lote:
        return Lote(
            id=l.id, codigo_lote=l.codigo_lote, medicamento_id=l.medicamento_id,
            proveedor_id=l.proveedor_id, sucursal_id=l.sucursal_id,
            cantidad_recibida=l.cantidad_recibida, cantidad_disponible=l.cantidad_disponible,
            fecha_recepcion=l.fecha_recepcion, fecha_vencimiento=l.fecha_vencimiento,
            estado_lote=l.estado_lote,
        )

    def get_all(self):
        return [self._a_entidad(l) for l in self.db.query(LoteModel).all()]

    def get_by_id(self, lote_id: int):
        l = self.db.query(LoteModel).filter(LoteModel.id == lote_id).first()
        return self._a_entidad(l) if l else None

    def get_by_codigo(self, codigo_lote: str):
        l = self.db.query(LoteModel).filter(LoteModel.codigo_lote == codigo_lote).first()
        return self._a_entidad(l) if l else None

    def create(self, lote: Lote):
        l = LoteModel(
            codigo_lote=lote.codigo_lote, medicamento_id=lote.medicamento_id,
            proveedor_id=lote.proveedor_id, sucursal_id=lote.sucursal_id,
            cantidad_recibida=lote.cantidad_recibida, cantidad_disponible=lote.cantidad_recibida,
            fecha_recepcion=lote.fecha_recepcion, fecha_vencimiento=lote.fecha_vencimiento,
            estado_lote=lote.estado_lote,
        )
        self.db.add(l)
        self.db.commit()
        self.db.refresh(l)
        return self._a_entidad(l)

    def update(self, lote: Lote):
        l = self.db.query(LoteModel).filter(LoteModel.id == lote.id).first()
        l.estado_lote = lote.estado_lote
        l.cantidad_disponible = lote.cantidad_disponible
        self.db.commit()
        self.db.refresh(l)
        return self._a_entidad(l)
