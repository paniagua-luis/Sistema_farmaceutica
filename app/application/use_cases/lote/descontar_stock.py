from fastapi import HTTPException
from app.domain.repositories.lote_repository import ILoteRepository
from app.application.use_cases.trazabilidad.registrar_evento import TrazabilidadService


class LoteService:
    def __init__(self, repository: ILoteRepository, trazabilidad_service: TrazabilidadService):
        self.repository = repository
        self.trazabilidad_service = trazabilidad_service

    def descontar_stock(
        self,
        lote_id: int,
        cantidad: int,
        usuario_id: int,
        medicamento_id: int | None = None,
    ):
        if cantidad <= 0:
            raise HTTPException(status_code=400, detail="La cantidad debe ser mayor que cero")
        lote = self.repository.get_by_id(lote_id)
        if not lote:
            raise HTTPException(status_code=404, detail="Lote no encontrado")
        productos = lote.productos or []
        if medicamento_id is None:
            if len(productos) != 1:
                raise HTTPException(
                    status_code=400,
                    detail="Indica medicamento_id para despachar desde un lote con varios medicamentos",
                )
            producto = productos[0]
        else:
            producto = next(
                (p for p in productos if p.medicamento_id == medicamento_id),
                None,
            )
            if producto is None:
                raise HTTPException(status_code=404, detail="El medicamento no pertenece a este lote")
        if producto.cantidad_disponible < cantidad:
            raise HTTPException(status_code=400, detail="Stock insuficiente en el lote")
        producto.cantidad_disponible -= cantidad
        lote.cantidad_disponible = sum(p.cantidad_disponible for p in productos)
        lote = self.repository.update(lote)
        self.trazabilidad_service.registrar_evento(
            lote.id, "descuento_stock",
            f"Se descontaron {cantidad} unidades del medicamento {producto.medicamento_id} "
            f"del lote {lote.codigo_lote}",
            usuario_id,
        )
        return lote
