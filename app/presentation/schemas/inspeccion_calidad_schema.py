from datetime import datetime
from pydantic import BaseModel


class InspeccionCalidadCreate(BaseModel):
    lote_id: int
    resultado: str
    observaciones: str | None = None


class InspeccionCalidadResponse(BaseModel):
    id: int
    lote_id: int
    usuario_id: int
    resultado: str
    observaciones: str | None = None
    fecha_inspeccion: datetime | None = None

    class Config:
        from_attributes = True
