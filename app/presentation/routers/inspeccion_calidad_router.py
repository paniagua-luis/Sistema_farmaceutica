from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.repositories.sqlalchemy_inspeccion_calidad_repository import SQLAlchemyInspeccionCalidadRepository
from app.infrastructure.repositories.sqlalchemy_lote_repository import SQLAlchemyLoteRepository
from app.infrastructure.repositories.sqlalchemy_trazabilidad_repository import SQLAlchemyTrazabilidadRepository
from app.application.use_cases.inspeccion_calidad.listar import InspeccionCalidadService as ListarInspecciones
from app.application.use_cases.inspeccion_calidad.historial_lote import InspeccionCalidadService as HistorialInspecciones
from app.application.use_cases.inspeccion_calidad.registrar import InspeccionCalidadService as RegistrarInspeccion
from app.application.use_cases.lote.obtener_lote import LoteService as ObtenerLote
from app.application.use_cases.lote.actualizar_estado import LoteService as ActualizarEstado
from app.application.use_cases.trazabilidad.registrar_evento import TrazabilidadService
from app.presentation.schemas.inspeccion_calidad_schema import InspeccionCalidadCreate, InspeccionCalidadResponse
from app.presentation.dependencies import obtener_usuario_actual, requiere_permiso

router = APIRouter(prefix="/inspecciones", tags=["Verificacion de Calidad"], dependencies=[Depends(requiere_permiso("calidad.gestionar"))])


@router.get("/", response_model=list[InspeccionCalidadResponse])
def listar(db: Session = Depends(get_db)):
    return ListarInspecciones(SQLAlchemyInspeccionCalidadRepository(db)).listar()


@router.get("/lote/{lote_id}", response_model=list[InspeccionCalidadResponse])
def historial_de_lote(lote_id: int, db: Session = Depends(get_db)):
    return HistorialInspecciones(SQLAlchemyInspeccionCalidadRepository(db)).historial_de_lote(lote_id)


@router.post("/", response_model=InspeccionCalidadResponse, status_code=201)
def registrar(datos: InspeccionCalidadCreate, db: Session = Depends(get_db), usuario=Depends(obtener_usuario_actual)):
    """Eventos 2 y 13: inspeccion de un lote (aprueba o rechaza)."""
    trazabilidad = TrazabilidadService(SQLAlchemyTrazabilidadRepository(db))
    obtener_lote = ObtenerLote(SQLAlchemyLoteRepository(db))
    actualizar_estado = ActualizarEstado(SQLAlchemyLoteRepository(db), trazabilidad)
    return RegistrarInspeccion(SQLAlchemyInspeccionCalidadRepository(db), obtener_lote, actualizar_estado, trazabilidad).registrar(datos.model_dump(), usuario.id)
