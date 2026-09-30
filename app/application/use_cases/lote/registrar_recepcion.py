from fastapi import HTTPException
from uuid import uuid4
from app.domain.repositories.lote_repository import ILoteRepository
from app.domain.entities.lote import Lote, LoteProducto
from app.domain.entities.trazabilidad import Trazabilidad
from app.application.use_cases.trazabilidad.registrar_evento import TrazabilidadService


class LoteService:
    def __init__(self, repository: ILoteRepository, trazabilidad_service: TrazabilidadService):
        self.repository = repository
        self.trazabilidad_service = trazabilidad_service

    def registrar_recepcion(self, datos: dict, usuario_id: int):
        """Evento 1: el proveedor entrega un nuevo lote de medicamentos en almacen."""
        datos_lote = self._preparar_lote(datos)
        if self.repository.get_by_codigo(datos_lote["codigo_lote"]):
            raise HTTPException(status_code=400, detail="Ya existe un lote con ese codigo")
        lote = self.repository.create(self._a_entidad(datos_lote))
        self.trazabilidad_service.registrar_evento(
            lote.id, "recepcion_mercancia", f"Lote {lote.codigo_lote} recibido en almacen", usuario_id,
        )
        return lote

    def registrar_recepciones(self, datos_lotes: list[dict], usuario_id: int):
        datos_lotes = [self._preparar_lote(datos) for datos in datos_lotes]
        codigos = [datos["codigo_lote"] for datos in datos_lotes]
        if len(codigos) != len(set(codigos)):
            raise HTTPException(status_code=400, detail="Hay codigos de lote repetidos en la recepcion")

        for codigo in codigos:
            if self.repository.get_by_codigo(codigo):
                raise HTTPException(status_code=400, detail=f"Ya existe un lote con el codigo {codigo}")

        lotes = self.repository.create_many([self._a_entidad(datos) for datos in datos_lotes])
        eventos = [
            Trazabilidad(
                lote_id=lote.id,
                tipo_evento="recepcion_mercancia",
                descripcion=f"Lote {lote.codigo_lote} recibido en almacen",
                usuario_id=usuario_id,
            )
            for lote in lotes
        ]
        self.trazabilidad_service.registrar_eventos(eventos)
        return lotes

    @staticmethod
    def _preparar_lote(datos: dict) -> dict:
        productos = datos.get("productos")
        if productos is None:
            productos = [{
                "medicamento_id": datos["medicamento_id"],
                "cantidad_recibida": datos["cantidad_recibida"],
            }]
        codigo_lote = datos.get("codigo_lote") or f"LOTE-{uuid4().hex[:12].upper()}"
        return datos | {"codigo_lote": codigo_lote, "productos": productos}

    @staticmethod
    def _a_entidad(datos: dict) -> Lote:
        productos = [
            LoteProducto(
                medicamento_id=producto["medicamento_id"],
                cantidad_recibida=producto["cantidad_recibida"],
                cantidad_disponible=producto["cantidad_recibida"],
            )
            for producto in datos["productos"]
        ]
        return Lote(
            codigo_lote=datos["codigo_lote"],
            medicamento_id=productos[0].medicamento_id,
            proveedor_id=datos["proveedor_id"],
            sucursal_id=datos["sucursal_id"],
            cantidad_recibida=sum(producto.cantidad_recibida for producto in productos),
            fecha_recepcion=datos["fecha_recepcion"],
            fecha_vencimiento=datos["fecha_vencimiento"],
            cantidad_disponible=sum(producto.cantidad_disponible for producto in productos),
            estado_lote=datos.get("estado_lote", "pendiente_verificacion"),
            productos=productos,
        )
