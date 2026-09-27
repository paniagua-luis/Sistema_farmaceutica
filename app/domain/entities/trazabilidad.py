from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Trazabilidad:
    lote_id: int
    tipo_evento: str
    descripcion: str
    usuario_id: Optional[int] = None
    id: Optional[int] = None
    fecha: Optional[datetime] = None
