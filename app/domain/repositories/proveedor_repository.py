from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.proveedor import Proveedor


class IProveedorRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[Proveedor]: ...

    @abstractmethod
    def get_by_id(self, proveedor_id: int) -> Optional[Proveedor]: ...

    @abstractmethod
    def create(self, proveedor: Proveedor) -> Proveedor: ...

    @abstractmethod
    def update(self, proveedor: Proveedor) -> Proveedor: ...

    @abstractmethod
    def delete(self, proveedor_id: int) -> None: ...
