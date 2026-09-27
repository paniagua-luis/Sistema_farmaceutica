from dataclasses import dataclass
from typing import Optional


@dataclass
class Proveedor:
    nombre: str
    contacto: str
    codigo_proveedor: str
    id: Optional[int] = None
