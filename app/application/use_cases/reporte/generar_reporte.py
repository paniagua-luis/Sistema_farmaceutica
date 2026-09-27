from app.domain.repositories.reporte_repository import IReporteRepository
from app.domain.entities.reporte import Reporte


class ReporteService:
    def __init__(self, repository: IReporteRepository):
        self.repository = repository

    def generar(self, datos: dict):
        """Eventos 8, 9 y 20: reportes consolidados e informes regulatorios."""
        return self.repository.create(Reporte(**datos))
