from abc import ABC, abstractmethod
from typing import Optional
from app.domain.entities.monitoreo_temperatura import MonitoreoTemperatura


class IMonitoreoTemperaturaRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[MonitoreoTemperatura]: ...

    @abstractmethod
    def get_by_id(self, monitoreo_temperatura_id: int) -> Optional[MonitoreoTemperatura]: ...

    @abstractmethod
    def get_by_lote(self, lote_id: int) -> list[MonitoreoTemperatura]: ...

    @abstractmethod
    def create(self, monitoreo_temperatura: MonitoreoTemperatura) -> MonitoreoTemperatura: ...
