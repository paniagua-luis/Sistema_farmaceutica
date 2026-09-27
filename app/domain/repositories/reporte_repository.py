from abc import ABC, abstractmethod
from app.domain.entities.reporte import Reporte


class IReporteRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[Reporte]: ...

    @abstractmethod
    def create(self, reporte: Reporte) -> Reporte: ...
