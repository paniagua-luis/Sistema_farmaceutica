from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, field_serializer


class ReporteCreate(BaseModel):
    tipo_reporte: str
    destinatario: str
    contenido: str
    lote_id: int | None = None


class ReporteResponse(ReporteCreate):
    codigo_reporte: str
    id: int
    fecha: datetime | None = None

    @field_serializer("fecha", when_used="json", return_type=str | None)
    def serializar_fecha(self, fecha: datetime | None) -> str | None:
        return fecha.strftime("%Y-%m-%dT%H:%M") if fecha is not None else None

    class Config:
        from_attributes = True


class ReporteInventarioResponse(BaseModel):
    lote_id: int
    codigo_lote: str
    medicamento_id: int
    medicamento: str
    proveedor_id: int
    proveedor: str
    sucursal_id: int
    sucursal: str
    cantidad_recibida: int
    cantidad_disponible: int
    fecha_vencimiento: date
    estado_lote: str
    dias_alerta_vencimiento: int


class AlertaVencimientoResponse(ReporteInventarioResponse):
    dias_restantes: int
    estado_alerta: Literal["vencido", "por_vencer"]
