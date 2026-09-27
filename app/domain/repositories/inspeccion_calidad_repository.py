from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.inspeccion_calidad import InspeccionCalidad


class IInspeccionCalidadRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[InspeccionCalidad]: ...

    @abstractmethod
    def get_by_id(self, inspeccion_calidad_id: int) -> Optional[InspeccionCalidad]: ...

    @abstractmethod
    def get_by_lote(self, lote_id: int) -> list[InspeccionCalidad]: ...

    @abstractmethod
    def create(self, inspeccion_calidad: InspeccionCalidad) -> InspeccionCalidad: ...
