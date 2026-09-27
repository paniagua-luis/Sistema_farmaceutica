from fastapi import HTTPException
from app.domain.repositories.lote_repository import ILoteRepository
from app.application.use_cases.trazabilidad.registrar_evento import TrazabilidadService


class LoteService:
    def __init__(self, repository: ILoteRepository, trazabilidad_service: TrazabilidadService):
        self.repository = repository
        self.trazabilidad_service = trazabilidad_service

    def descontar_stock(self, lote_id: int, cantidad: int, usuario_id: int):
        if cantidad <= 0:
            raise HTTPException(status_code=400, detail="La cantidad debe ser mayor que cero")
        lote = self.repository.get_by_id(lote_id)
        if not lote:
            raise HTTPException(status_code=404, detail="Lote no encontrado")
        if lote.cantidad_disponible < cantidad:
            raise HTTPException(status_code=400, detail="Stock insuficiente en el lote")
        lote.cantidad_disponible -= cantidad
        lote = self.repository.update(lote)
        self.trazabilidad_service.registrar_evento(
            lote.id, "descuento_stock", f"Se descontaron {cantidad} unidades del lote {lote.codigo_lote}", usuario_id,
        )
        return lote
