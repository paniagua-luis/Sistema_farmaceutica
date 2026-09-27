from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Despacho:
    codigo_despacho: str
    lote_id: int
    sucursal_id: int
    cantidad_despachada: int
    estado_despacho: str = "en_transito"
    id: Optional[int] = None
    fecha_despacho: Optional[datetime] = None
    fecha_recepcion: Optional[datetime] = None
