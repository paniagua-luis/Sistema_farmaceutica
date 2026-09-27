from datetime import datetime
from fastapi import HTTPException
from app.domain.repositories.despacho_repository import IDespachoRepository
from app.domain.entities.despacho import Despacho
from app.application.use_cases.trazabilidad.registrar_evento import TrazabilidadService


class DespachoService:
    def __init__(self, repository: IDespachoRepository, trazabilidad_service: TrazabilidadService):
        self.repository = repository
        self.trazabilidad_service = trazabilidad_service

    def confirmar_recepcion(self, despacho_id: int, usuario_id: int):
        """Evento 5: la sucursal confirma la recepcion fisica de la mercancia."""
        despacho = next((d for d in self.repository.get_all() if d.id == despacho_id), None)
        if not despacho:
            raise HTTPException(status_code=404, detail="Despacho no encontrado")
        despacho.estado_despacho = "recibido"
        despacho.fecha_recepcion = datetime.utcnow()
        despacho = self.repository.update(despacho)
        self.trazabilidad_service.registrar_evento(
            despacho.lote_id, "confirmacion_recepcion", f"Despacho {despacho.codigo_despacho} confirmado por la sucursal", usuario_id,
        )
        return despacho
