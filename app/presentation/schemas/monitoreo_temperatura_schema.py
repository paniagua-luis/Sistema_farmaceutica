from datetime import datetime
from pydantic import BaseModel


class MonitoreoTemperaturaCreate(BaseModel):
    codigo_lectura: str
    ubicacion_almacen: str
    temperatura_registrada: float
    lote_id: int | None = None


class MonitoreoTemperaturaResponse(MonitoreoTemperaturaCreate):
    id: int
    estado_lectura: str
    fecha_hora: datetime | None = None

    class Config:
        from_attributes = True
