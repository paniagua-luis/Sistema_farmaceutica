from sqlalchemy.orm import Session
from app.domain.entities.despacho import Despacho
from app.domain.repositories.despacho_repository import IDespachoRepository
from app.infrastructure.models.despacho_model import DespachoModel


class SQLAlchemyDespachoRepository(IDespachoRepository):
    def __init__(self, db: Session):
        self.db = db

    def _a_entidad(self, d: DespachoModel) -> Despacho:
        return Despacho(
            id=d.id, codigo_despacho=d.codigo_despacho, lote_id=d.lote_id, sucursal_id=d.sucursal_id,
            medicamento_id=d.medicamento_id, cantidad_despachada=d.cantidad_despachada,
            estado_despacho=d.estado_despacho,
            fecha_despacho=d.fecha_despacho, fecha_recepcion=d.fecha_recepcion,
        )

    def get_all(self):
        return [self._a_entidad(d) for d in self.db.query(DespachoModel).all()]

    def get_by_id(self, despacho_id: int):
        d = self.db.query(DespachoModel).filter(DespachoModel.id == despacho_id).first()
        return self._a_entidad(d) if d else None

    def get_by_lote(self, lote_id: int):
        return [self._a_entidad(d) for d in self.db.query(DespachoModel).filter(DespachoModel.lote_id == lote_id).all()]

    def create(self, despacho: Despacho):
        d = DespachoModel(
            codigo_despacho=despacho.codigo_despacho, lote_id=despacho.lote_id,
            medicamento_id=despacho.medicamento_id, sucursal_id=despacho.sucursal_id,
            cantidad_despachada=despacho.cantidad_despachada, estado_despacho=despacho.estado_despacho,
        )
        self.db.add(d)
        self.db.commit()
        self.db.refresh(d)
        return self._a_entidad(d)

    def create_many_pending(self, despachos: list[Despacho]) -> list[Despacho]:
        modelos = [
            DespachoModel(
                codigo_despacho=despacho.codigo_despacho,
                lote_id=despacho.lote_id,
                medicamento_id=despacho.medicamento_id,
                sucursal_id=despacho.sucursal_id,
                cantidad_despachada=despacho.cantidad_despachada,
                estado_despacho=despacho.estado_despacho,
            )
            for despacho in despachos
        ]
        self.db.add_all(modelos)
        self.db.flush()
        return [self._a_entidad(modelo) for modelo in modelos]

    def update(self, despacho: Despacho):
        d = self.db.query(DespachoModel).filter(DespachoModel.id == despacho.id).first()
        d.estado_despacho = despacho.estado_despacho
        d.fecha_recepcion = despacho.fecha_recepcion
        self.db.commit()
        self.db.refresh(d)
        return self._a_entidad(d)
