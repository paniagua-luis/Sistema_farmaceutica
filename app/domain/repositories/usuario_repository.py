from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.usuario import Usuario


class IUsuarioRepository(ABC):
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[Usuario]: ...

    @abstractmethod
    def create(self, usuario: Usuario) -> Usuario: ...
