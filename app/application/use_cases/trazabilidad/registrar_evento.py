from app.domain.repositories.trazabilidad_repository import ITrazabilidadRepository
from app.domain.entities.trazabilidad import Trazabilidad


class TrazabilidadService:
    """Servicio central: cada evento importante del sistema registra aqui su huella."""

    def __init__(self, repository: ITrazabilidadRepository):
        self.repository = repository

    def registrar_evento(self, lote_id: int, tipo_evento: str, descripcion: str, usuario_id: int | None = None):
        evento = Trazabilidad(lote_id=lote_id, tipo_evento=tipo_evento, descripcion=descripcion, usuario_id=usuario_id)
        return self.repository.create(evento)

    def registrar_eventos(self, eventos: list[Trazabilidad]):
        return self.repository.create_many(eventos)
