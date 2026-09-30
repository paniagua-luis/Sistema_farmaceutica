from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.usuario import Usuario


class IUsuarioRepository(ABC):
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[Usuario]: ...

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[Usuario]: ...

    @abstractmethod
    def get_all(self) -> list[Usuario]: ...

    @abstractmethod
    def count(self) -> int: ...

    @abstractmethod
    def count_by_role(self, role: str) -> int: ...

    @abstractmethod
    def create(self, usuario: Usuario) -> Usuario: ...

    @abstractmethod
    def update_role(self, user_id: int, role: str) -> Optional[Usuario]: ...
