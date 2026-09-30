from abc import ABC, abstractmethod
from datetime import date
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
    def create_many(self, lotes: list[Lote]) -> list[Lote]: ...

    @abstractmethod
    def update(self, lote: Lote) -> Lote: ...

    @abstractmethod
    def update_many_pending(self, lotes: list[Lote]) -> None: ...

    @abstractmethod
    def get_stock_bajo(self, umbral: int) -> list[dict]: ...

    @abstractmethod
    def consultar_inventario(
        self,
        proveedor_id: int | None = None,
        medicamento_id: int | None = None,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
    ) -> list[dict]: ...

    @abstractmethod
    def listar_alertas_vencimiento(self) -> list[dict]: ...
