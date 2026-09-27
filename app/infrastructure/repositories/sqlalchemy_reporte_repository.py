from sqlalchemy.orm import Session
from app.domain.entities.reporte import Reporte
from app.domain.repositories.reporte_repository import IReporteRepository
from app.infrastructure.models.reporte_model import ReporteModel


class SQLAlchemyReporteRepository(IReporteRepository):
    def __init__(self, db: Session):
        self.db = db

    def _a_entidad(self, r: ReporteModel) -> Reporte:
        return Reporte(
            id=r.id, codigo_reporte=r.codigo_reporte, lote_id=r.lote_id, tipo_reporte=r.tipo_reporte,
            destinatario=r.destinatario, contenido=r.contenido, fecha=r.fecha,
        )

    def get_all(self):
        return [self._a_entidad(r) for r in self.db.query(ReporteModel).all()]

    def create(self, reporte: Reporte):
        r = ReporteModel(
            codigo_reporte=reporte.codigo_reporte, lote_id=reporte.lote_id, tipo_reporte=reporte.tipo_reporte,
            destinatario=reporte.destinatario, contenido=reporte.contenido,
        )
        self.db.add(r)
        self.db.commit()
        self.db.refresh(r)
        return self._a_entidad(r)
