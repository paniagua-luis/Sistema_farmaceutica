from fastapi import HTTPException
from uuid import uuid4
from app.domain.repositories.despacho_repository import IDespachoRepository
from app.domain.entities.despacho import Despacho
from app.application.use_cases.lote.obtener_lote import LoteService as ObtenerLote
from app.application.use_cases.lote.descontar_stock import LoteService as DescontarStock
from app.application.use_cases.trazabilidad.registrar_evento import TrazabilidadService


class DespachoService:
    def __init__(self, repository: IDespachoRepository, obtener_lote: ObtenerLote, descontar_stock: DescontarStock, trazabilidad_service: TrazabilidadService):
        self.repository = repository
        self.obtener_lote = obtener_lote
        self.descontar_stock = descontar_stock
        self.trazabilidad_service = trazabilidad_service

    def registrar_despacho(self, datos: dict, usuario_id: int):
        """Eventos 3, 4 y 14: solicitud de abastecimiento y despacho a sucursal."""
        lote = self.obtener_lote.obtener(datos["lote_id"])
        if lote.estado_lote != "aprobado":
            raise HTTPException(status_code=400, detail="Solo se pueden despachar lotes aprobados")

        self.descontar_stock.descontar_stock(lote.id, datos["cantidad_despachada"], usuario_id)
        despacho = self.repository.create(
            Despacho(
                codigo_despacho=f"DESP-{uuid4().hex.upper()}",
                lote_id=datos["lote_id"],
                sucursal_id=datos["sucursal_id"],
                cantidad_despachada=datos["cantidad_despachada"],
            )
        )
        self.trazabilidad_service.registrar_evento(
            lote.id, "despacho", f"Despacho {despacho.codigo_despacho} enviado a la sucursal", usuario_id,
        )
        return despacho
