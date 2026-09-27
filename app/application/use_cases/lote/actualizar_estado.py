from fastapi import HTTPException
from app.domain.repositories.lote_repository import ILoteRepository
from app.application.use_cases.trazabilidad.registrar_evento import TrazabilidadService


class LoteService:
    def __init__(self, repository: ILoteRepository, trazabilidad_service: TrazabilidadService):
        self.repository = repository
        self.trazabilidad_service = trazabilidad_service

    def actualizar_estado(self, lote_id: int, nuevo_estado: str, usuario_id: int):
        lote = self.repository.get_by_id(lote_id)
        if not lote:
            raise HTTPException(status_code=404, detail="Lote no encontrado")
        lote.estado_lote = nuevo_estado
        lote = self.repository.update(lote)
        self.trazabilidad_service.registrar_evento(
            lote.id, "cambio_estado", f"Lote {lote.codigo_lote} cambio a estado '{nuevo_estado}'", usuario_id,
        )
        return lote
