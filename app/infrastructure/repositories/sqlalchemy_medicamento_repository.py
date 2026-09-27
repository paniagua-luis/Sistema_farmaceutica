from sqlalchemy.orm import Session
from app.domain.entities.medicamento import Medicamento
from app.domain.repositories.medicamento_repository import IMedicamentoRepository
from app.infrastructure.models.medicamento_model import MedicamentoModel


class SQLAlchemyMedicamentoRepository(IMedicamentoRepository):
    def __init__(self, db: Session):
        self.db = db

    def _a_entidad(self, m: MedicamentoModel) -> Medicamento:
        return Medicamento(
            id=m.id, codigo_medicamento=m.codigo_medicamento, nombre=m.nombre, principio_activo=m.principio_activo,
            temperatura_minima=m.temperatura_minima, temperatura_maxima=m.temperatura_maxima,
            dias_alerta_vencimiento=m.dias_alerta_vencimiento, fecha_actualizacion=m.fecha_actualizacion,
        )

    def get_all(self):
        return [self._a_entidad(m) for m in self.db.query(MedicamentoModel).all()]

    def get_by_id(self, medicamento_id: int):
        m = self.db.query(MedicamentoModel).filter(MedicamentoModel.id == medicamento_id).first()
        return self._a_entidad(m) if m else None

    def get_by_codigo(self, codigo_medicamento: str):
        m = self.db.query(MedicamentoModel).filter(
            MedicamentoModel.codigo_medicamento == codigo_medicamento,
        ).first()
        return self._a_entidad(m) if m else None

    def create(self, medicamento: Medicamento):
        m = MedicamentoModel(
            codigo_medicamento=medicamento.codigo_medicamento, nombre=medicamento.nombre, principio_activo=medicamento.principio_activo,
            temperatura_minima=medicamento.temperatura_minima, temperatura_maxima=medicamento.temperatura_maxima,
            dias_alerta_vencimiento=medicamento.dias_alerta_vencimiento,
        )
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return self._a_entidad(m)

    def update(self, medicamento: Medicamento):
        m = self.db.query(MedicamentoModel).filter(MedicamentoModel.id == medicamento.id).first()
        m.nombre = medicamento.nombre
        m.codigo_medicamento = medicamento.codigo_medicamento
        m.principio_activo = medicamento.principio_activo
        m.temperatura_minima = medicamento.temperatura_minima
        m.temperatura_maxima = medicamento.temperatura_maxima
        m.dias_alerta_vencimiento = medicamento.dias_alerta_vencimiento
        self.db.commit()
        self.db.refresh(m)
        return self._a_entidad(m)

    def delete(self, medicamento_id: int):
        m = self.db.query(MedicamentoModel).filter(MedicamentoModel.id == medicamento_id).first()
        if m:
            self.db.delete(m)
            self.db.commit()
