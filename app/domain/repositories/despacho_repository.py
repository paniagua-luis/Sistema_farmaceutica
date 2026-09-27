from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.despacho import Despacho


class IDespachoRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[Despacho]: ...

    @abstractmethod
    def get_by_id(self, despacho_id: int) -> Optional[Despacho]: ...

    @abstractmethod
    def get_by_lote(self, lote_id: int) -> list[Despacho]: ...

    @abstractmethod
    def create(self, despacho: Despacho) -> Despacho: ...

    @abstractmethod
    def update(self, despacho: Despacho) -> Despacho: ...
