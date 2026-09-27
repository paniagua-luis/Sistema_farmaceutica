from app.domain.repositories.monitoreo_temperatura_repository import IMonitoreoTemperaturaRepository
from app.domain.entities.monitoreo_temperatura import MonitoreoTemperatura
from app.application.use_cases.trazabilidad.registrar_evento import TrazabilidadService


class MonitoreoTemperaturaService:
    def __init__(self, repository: IMonitoreoTemperaturaRepository, trazabilidad_service: TrazabilidadService):
        self.repository = repository
        self.trazabilidad_service = trazabilidad_service

    def registrar_lectura(self, datos: dict, temp_minima: float, temp_maxima: float, usuario_id: int | None = None):
        """Eventos 16 y 19: monitoreo periodico y deteccion de desviacion de temperatura."""
        fuera_de_rango = not (temp_minima <= datos["temperatura_registrada"] <= temp_maxima)
        datos["estado_lectura"] = "desviacion" if fuera_de_rango else "normal"
        lectura = self.repository.create(MonitoreoTemperatura(**datos))

        if fuera_de_rango and datos.get("lote_id"):
            self.trazabilidad_service.registrar_evento(
                datos["lote_id"], "desviacion_temperatura",
                f"Temperatura {datos['temperatura_registrada']} fuera de rango en {datos['ubicacion_almacen']}",
                usuario_id,
            )
        return lectura
