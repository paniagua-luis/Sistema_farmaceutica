from datetime import datetime
from pydantic import BaseModel


class MedicamentoCreate(BaseModel):
    codigo_medicamento: str
    nombre: str
    principio_activo: str
    temperatura_minima: float
    temperatura_maxima: float
    dias_alerta_vencimiento: int = 30


class MedicamentoResponse(MedicamentoCreate):
    id: int
    fecha_actualizacion: datetime | None = None

    class Config:
        from_attributes = True
