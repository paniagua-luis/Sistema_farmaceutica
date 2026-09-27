from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class MonitoreoTemperatura:
    ubicacion_almacen: str
    temperatura_registrada: float
    lote_id: Optional[int] = None
    estado_lectura: str = "normal"
    id: Optional[int] = None
    codigo_lectura: Optional[str] = None
    fecha_hora: Optional[datetime] = None
