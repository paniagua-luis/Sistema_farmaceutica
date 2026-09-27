from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class InspeccionCalidad:
    lote_id: int
    usuario_id: int
    resultado: str  # "aprobado" | "rechazado"
    observaciones: Optional[str] = None
    id: Optional[int] = None
    fecha_inspeccion: Optional[datetime] = None
