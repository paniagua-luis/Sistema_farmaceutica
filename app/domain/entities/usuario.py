from dataclasses import dataclass
from typing import Optional


@dataclass
class Usuario:
    username: str
    password_hash: str
    rol: str
    id: Optional[int] = None
