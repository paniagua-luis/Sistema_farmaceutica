from fastapi import HTTPException
from app.domain.repositories.lote_repository import ILoteRepository
from app.domain.entities.lote import Lote
from app.application.use_cases.trazabilidad.registrar_evento import TrazabilidadService


class LoteService:
    def __init__(self, repository: ILoteRepository, trazabilidad_service: TrazabilidadService):
        self.repository = repository
        self.trazabilidad_service = trazabilidad_service

    def registrar_recepcion(self, datos: dict, usuario_id: int):
        """Evento 1: el proveedor entrega un nuevo lote de medicamentos en almacen."""
        if self.repository.get_by_codigo(datos["codigo_lote"]):
            raise HTTPException(status_code=400, detail="Ya existe un lote con ese codigo")
        lote = self.repository.create(Lote(**datos))
        self.trazabilidad_service.registrar_evento(
            lote.id, "recepcion_mercancia", f"Lote {lote.codigo_lote} recibido en almacen", usuario_id,
        )
        return lote

   
