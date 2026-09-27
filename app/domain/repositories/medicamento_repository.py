from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.medicamento import Medicamento


class IMedicamentoRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[Medicamento]: ...

    @abstractmethod
    def get_by_id(self, medicamento_id: int) -> Optional[Medicamento]: ...

    @abstractmethod
    def create(self, medicamento: Medicamento) -> Medicamento: ...

    @abstractmethod
    def update(self, medicamento: Medicamento) -> Medicamento: ...

    @abstractmethod
    def delete(self, medicamento_id: int) -> None: ...

    @abstractmethod
    def get_by_codigo(self, codigo_medicamento: str) -> Optional[Medicamento]: ...