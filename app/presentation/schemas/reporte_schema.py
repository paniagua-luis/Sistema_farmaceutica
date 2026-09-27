from datetime import datetime
from pydantic import BaseModel


class ReporteCreate(BaseModel):
    codigo_reporte: str
    tipo_reporte: str
    destinatario: str
    contenido: str
    lote_id: int | None = None


class ReporteResponse(ReporteCreate):
    id: int
    fecha: datetime | None = None

    class Config:
        from_attributes = True
