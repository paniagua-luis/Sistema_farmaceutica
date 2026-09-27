from app.domain.repositories.inspeccion_calidad_repository import IInspeccionCalidadRepository

class InspeccionCalidadService:
    def __init__(self, repository: IInspeccionCalidadRepository):
        self.repository = repository

    def listar(self):
        return self.repository.get_all()

