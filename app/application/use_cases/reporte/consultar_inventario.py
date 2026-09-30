from datetime import date
from fastapi import HTTPException
from app.domain.repositories.lote_repository import ILoteRepository


class ReporteInventarioService:
    def __init__(self, repository: ILoteRepository):
        self.repository = repository

    def consultar(
        self,
        proveedor_id: int | None = None,
        medicamento_id: int | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ):
        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            raise HTTPException(status_code=400, detail="La fecha inicial no puede superar la fecha final")
        return self.repository.consultar_inventario(
            proveedor_id=proveedor_id,
            medicamento_id=medicamento_id,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )

    def listar_alertas_vencimiento(self):
        return self.repository.listar_alertas_vencimiento()