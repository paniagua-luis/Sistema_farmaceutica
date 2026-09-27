from sqlalchemy.orm import Session
from app.domain.entities.monitoreo_temperatura import MonitoreoTemperatura
from app.domain.repositories.monitoreo_temperatura_repository import IMonitoreoTemperaturaRepository
from app.infrastructure.models.monitoreo_temperatura_model import MonitoreoTemperaturaModel


class SQLAlchemyMonitoreoTemperaturaRepository(IMonitoreoTemperaturaRepository):
    def __init__(self, db: Session):
        self.db = db

    def _a_entidad(self, m: MonitoreoTemperaturaModel) -> MonitoreoTemperatura:
        return MonitoreoTemperatura(
            id=m.id, codigo_lectura=m.codigo_lectura, lote_id=m.lote_id,
            ubicacion_almacen=m.ubicacion_almacen, temperatura_registrada=m.temperatura_registrada,
            estado_lectura=m.estado_lectura, fecha_hora=m.fecha_hora,
        )

    def get_all(self):
        return [self._a_entidad(m) for m in self.db.query(MonitoreoTemperaturaModel).all()]

    def get_by_id(self, monitoreo_temperatura_id: int):
        m = self.db.query(MonitoreoTemperaturaModel).filter(MonitoreoTemperaturaModel.id == monitoreo_temperatura_id).first()
        return self._a_entidad(m) if m else None

    def get_by_lote(self, lote_id: int):
        return [self._a_entidad(m) for m in self.db.query(MonitoreoTemperaturaModel).filter(MonitoreoTemperaturaModel.lote_id == lote_id).all()]

    def create(self, monitoreo_temperatura: MonitoreoTemperatura):
        m = MonitoreoTemperaturaModel(
            codigo_lectura=monitoreo_temperatura.codigo_lectura, lote_id=monitoreo_temperatura.lote_id,
            ubicacion_almacen=monitoreo_temperatura.ubicacion_almacen,
            temperatura_registrada=monitoreo_temperatura.temperatura_registrada,
            estado_lectura=monitoreo_temperatura.estado_lectura,
        )
        self.db.add(m)
        self.db.commit()
        self.db.refresh(m)
        return self._a_entidad(m)
