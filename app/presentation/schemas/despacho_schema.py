from datetime import datetime
from pydantic import BaseModel


class DespachoCreate(BaseModel):
    codigo_despacho: str
    lote_id: int
    sucursal_id: int
    cantidad_despachada: int


class DespachoResponse(BaseModel):
    id: int
    codigo_despacho: str
    lote_id: int
    sucursal_id: int
    cantidad_despachada: int
    estado_despacho: str
    fecha_despacho: datetime | None = None
    fecha_recepcion: datetime | None = None

    class Config:
        from_attributes = True
