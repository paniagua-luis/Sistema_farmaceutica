from app.domain.repositories.inspeccion_calidad_repository import IInspeccionCalidadRepository


class InspeccionCalidadService:
    def __init__(self, repository: IInspeccionCalidadRepository):
        self.repository = repository

    def historial_de_lote(self, lote_id: int):
        return self.repository.get_by_lote(lote_id)
