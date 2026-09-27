from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.sucursal import Sucursal


class ISucursalRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[Sucursal]: ...

    @abstractmethod
    def get_by_id(self, sucursal_id: int) -> Optional[Sucursal]: ...

    @abstractmethod
    def create(self, sucursal: Sucursal) -> Sucursal: ...

    @abstractmethod
    def update(self, sucursal: Sucursal) -> Sucursal: ...

    @abstractmethod
    def delete(self, sucursal_id: int) -> None: ...
