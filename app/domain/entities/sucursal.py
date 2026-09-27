from dataclasses import dataclass
from typing import Optional


@dataclass
class Sucursal:
    codigo_sucursal: str
    nombre: str
    id: Optional[int] = None
