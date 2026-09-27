from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Reporte:
    tipo_reporte: str
    destinatario: str
    contenido: str
    codigo_reporte: Optional[str] = None
    lote_id: Optional[int] = None
    id: Optional[int] = None
    fecha: Optional[datetime] = None
