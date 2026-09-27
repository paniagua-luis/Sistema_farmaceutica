from app.domain.repositories.trazabilidad_repository import ITrazabilidadRepository
class TrazabilidadService:
    """Servicio central: cada evento importante del sistema registra aqui su huella."""

    def __init__(self, repository: ITrazabilidadRepository):
        self.repository = repository


    def listar(self):
        return self.repository.get_all()
