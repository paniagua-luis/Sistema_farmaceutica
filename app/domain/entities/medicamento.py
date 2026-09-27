from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Medicamento:
    codigo_medicamento: str
    nombre: str
    principio_activo: str
    temperatura_minima: float
    temperatura_maxima: float
    dias_alerta_vencimiento: int
    id: Optional[int] = None
    fecha_actualizacion: Optional[datetime] = None