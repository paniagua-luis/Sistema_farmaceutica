from fastapi import HTTPException
from app.domain.repositories.inspeccion_calidad_repository import IInspeccionCalidadRepository
from app.domain.entities.inspeccion_calidad import InspeccionCalidad
from app.application.use_cases.lote.obtener_lote import LoteService as ObtenerLote
from app.application.use_cases.lote.actualizar_estado import LoteService as ActualizarEstado
from app.application.use_cases.trazabilidad.registrar_evento import TrazabilidadService

class InspeccionCalidadService:
    def __init__(self, repository: IInspeccionCalidadRepository, obtener_lote: ObtenerLote, actualizar_estado: ActualizarEstado, trazabilidad_service: TrazabilidadService):
        self.repository = repository
        self.obtener_lote = obtener_lote
        self.actualizar_estado = actualizar_estado
        self.trazabilidad_service = trazabilidad_service

    def registrar(self, datos: dict, usuario_id: int):
        """Eventos 2 y 13: verificacion e inspeccion del lote; puede rechazarlo."""
        lote = self.obtener_lote.obtener(datos["lote_id"])
        if datos["resultado"] not in ("aprobado", "rechazado"):
            raise HTTPException(status_code=400, detail="Resultado invalido, use 'aprobado' o 'rechazado'")

        inspeccion = self.repository.create(InspeccionCalidad(usuario_id=usuario_id, **datos))

        nuevo_estado = "aprobado" if datos["resultado"] == "aprobado" else "rechazado"
        self.actualizar_estado.actualizar_estado(lote.id, nuevo_estado, usuario_id)
        self.trazabilidad_service.registrar_evento(
            lote.id, "inspeccion_calidad", f"Inspeccion registrada: {datos['resultado']}", usuario_id,
        )
        return inspeccion
