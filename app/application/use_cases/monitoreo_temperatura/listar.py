from app.domain.repositories.monitoreo_temperatura_repository import IMonitoreoTemperaturaRepository
class MonitoreoTemperaturaService:
    def __init__(self, repository: IMonitoreoTemperaturaRepository):
        self.repository = repository

    def listar(self):
        return self.repository.get_all()
