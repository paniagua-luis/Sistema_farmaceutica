from datetime import datetime
from pydantic import BaseModel


class TrazabilidadResponse(BaseModel):
    id: int
    lote_id: int
    usuario_id: int | None = None
    tipo_evento: str
    descripcion: str
    fecha: datetime | None = None

    class Config:
        from_attributes = True
