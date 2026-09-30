from abc import ABC, abstractmethod
from app.domain.entities.trazabilidad import Trazabilidad


class ITrazabilidadRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[Trazabilidad]: ...

    @abstractmethod
    def get_by_lote(self, lote_id: int) -> list[Trazabilidad]: ...

    @abstractmethod
    def create(self, evento: Trazabilidad) -> Trazabilidad: ...

    @abstractmethod
    def create_many(self, eventos: list[Trazabilidad]) -> list[Trazabilidad]: ...
