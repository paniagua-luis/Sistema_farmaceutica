from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.lote import Lote


class ILoteRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[Lote]: ...

    @abstractmethod
    def get_by_id(self, lote_id: int) -> Optional[Lote]: ...

    @abstractmethod
    def get_by_codigo(self, codigo_lote: str) -> Optional[Lote]: ...

    @abstractmethod
    def create(self, lote: Lote) -> Lote: ...

    @abstractmethod
    def update(self, lote: Lote) -> Lote: ...
