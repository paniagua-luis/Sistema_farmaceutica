from datetime import date
from pydantic import BaseModel


class LoteCreate(BaseModel):
    codigo_lote: str
    medicamento_id: int
    proveedor_id: int
    sucursal_id: int
    cantidad_recibida: int
    fecha_recepcion: date
    fecha_vencimiento: date


class LoteEstadoUpdate(BaseModel):
    nuevo_estado: str


class LoteResponse(BaseModel):
    id: int
    codigo_lote: str
    medicamento_id: int
    proveedor_id: int
    sucursal_id: int
    cantidad_recibida: int
    cantidad_disponible: int
    fecha_recepcion: date
    fecha_vencimiento: date
    estado_lote: str

    class Config:
        from_attributes = True
