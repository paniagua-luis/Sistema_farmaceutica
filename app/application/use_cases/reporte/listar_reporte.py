from app.domain.repositories.reporte_repository import IReporteRepository
from app.domain.entities.reporte import Reporte


class ReporteService:
    def __init__(self, repository: IReporteRepository):
        self.repository = repository

    def listar(self):
        return self.repository.get_all()
