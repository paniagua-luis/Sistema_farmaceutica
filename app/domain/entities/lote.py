from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Lote:
    codigo_lote: str
    medicamento_id: int
    proveedor_id: int
    sucursal_id: int
    cantidad_recibida: int
    fecha_recepcion: date
    fecha_vencimiento: date
    cantidad_disponible: int = 0
    estado_lote: str = "pendiente_verificacion"
    id: Optional[int] = None
