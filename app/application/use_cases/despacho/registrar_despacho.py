from fastapi import HTTPException
from uuid import uuid4
from app.domain.repositories.despacho_repository import IDespachoRepository
from app.domain.entities.despacho import Despacho
from app.domain.entities.trazabilidad import Trazabilidad
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

        medicamento_id = datos.get("medicamento_id")
        if medicamento_id is None:
            if len(lote.productos or []) != 1:
                raise HTTPException(
                    status_code=400,
                    detail="Indica medicamento_id para despachar desde un lote con varios medicamentos",
                )
            medicamento_id = lote.productos[0].medicamento_id

        self.descontar_stock.descontar_stock(
            datos["lote_id"], datos["cantidad_despachada"], usuario_id, medicamento_id,
        )
        despacho = self.repository.create(
            Despacho(
                codigo_despacho=f"DESP-{uuid4().hex.upper()}",
                lote_id=datos["lote_id"],
                sucursal_id=datos["sucursal_id"],
                cantidad_despachada=datos["cantidad_despachada"],
                medicamento_id=medicamento_id,
            )
        )
        self.trazabilidad_service.registrar_evento(
            lote.id, "despacho", f"Despacho {despacho.codigo_despacho} enviado a la sucursal", usuario_id,
        )
        return despacho

    def registrar_despachos(self, datos: dict, usuario_id: int) -> list[Despacho]:
        """Registra despachos de varios lotes hacia la misma sucursal."""
        lote_repository = self.obtener_lote.repository
        lotes_por_id = {}
        lineas = []

        for producto_despacho in datos["productos"]:
            lote_id = producto_despacho["lote_id"]
            lote = lotes_por_id.get(lote_id)
            if lote is None:
                lote = self.obtener_lote.obtener(lote_id)
                if lote.estado_lote != "aprobado":
                    raise HTTPException(
                        status_code=400,
                        detail=f"El lote {lote.codigo_lote} no está aprobado",
                    )
                lotes_por_id[lote_id] = lote

            producto = next(
                (
                    producto
                    for producto in lote.productos or []
                    if producto.medicamento_id == producto_despacho["medicamento_id"]
                ),
                None,
            )
            if producto is None:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"El medicamento {producto_despacho['medicamento_id']} "
                        f"no pertenece al lote {lote.codigo_lote}"
                    ),
                )
            cantidad = producto_despacho["cantidad_despachada"]
            if producto.cantidad_disponible < cantidad:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para el medicamento del lote {lote.codigo_lote}",
                )

            producto.cantidad_disponible -= cantidad
            lote.cantidad_disponible = sum(
                item.cantidad_disponible for item in lote.productos or []
            )
            lineas.append((lote, producto_despacho))

        lote_repository.update_many_pending(list(lotes_por_id.values()))
        nuevos_despachos = [
            Despacho(
                codigo_despacho=f"DESP-{uuid4().hex.upper()}",
                lote_id=lote.id,
                medicamento_id=producto_despacho["medicamento_id"],
                sucursal_id=datos["sucursal_id"],
                cantidad_despachada=producto_despacho["cantidad_despachada"],
            )
            for lote, producto_despacho in lineas
        ]
        despachos = self.repository.create_many_pending(nuevos_despachos)

        eventos = [
            Trazabilidad(
                lote_id=despacho.lote_id,
                tipo_evento="despacho",
                descripcion=(
                    f"Despacho {despacho.codigo_despacho} del medicamento "
                    f"{despacho.medicamento_id} enviado a la sucursal"
                ),
                usuario_id=usuario_id,
            )
            for despacho in despachos
        ]
        self.trazabilidad_service.registrar_eventos(eventos)
        return despachos
