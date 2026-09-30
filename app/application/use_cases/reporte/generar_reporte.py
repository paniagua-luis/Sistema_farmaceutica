from uuid import uuid4
from app.domain.repositories.reporte_repository import IReporteRepository
from app.domain.entities.reporte import Reporte


class ReporteService:
    def __init__(self, repository: IReporteRepository):
        self.repository = repository

    def generar(self, datos: dict):
        """Eventos 8, 9 y 20: reportes consolidados e informes regulatorios."""
        datos_reporte = {**datos, "codigo_reporte": f"REP-{uuid4().hex.upper()}"}
        return self.repository.create(Reporte(**datos_reporte))
