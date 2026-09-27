from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.repositories.sqlalchemy_lote_repository import SQLAlchemyLoteRepository
from app.infrastructure.repositories.sqlalchemy_trazabilidad_repository import SQLAlchemyTrazabilidadRepository
from app.application.use_cases.lote.listar import LoteService as ListarLotes
from app.application.use_cases.lote.obtener_lote import LoteService as ObtenerLote
from app.application.use_cases.lote.registrar_recepcion import LoteService as RegistrarRecepcion
from app.application.use_cases.lote.actualizar_estado import LoteService as ActualizarEstado
from app.application.use_cases.trazabilidad.registrar_evento import TrazabilidadService
from app.presentation.schemas.lote_schema import LoteCreate, LoteResponse, LoteEstadoUpdate
from app.presentation.dependencies import obtener_usuario_actual, requiere_permiso

router = APIRouter(prefix="/lotes", tags=["Lotes"], dependencies=[Depends(requiere_permiso("lotes.gestionar"))])


@router.get("/", response_model=list[LoteResponse])
def listar(db: Session = Depends(get_db)):
    return ListarLotes(SQLAlchemyLoteRepository(db)).listar()


@router.get("/{lote_id}", response_model=LoteResponse)
def obtener(lote_id: int, db: Session = Depends(get_db)):
    return ObtenerLote(SQLAlchemyLoteRepository(db)).obtener(lote_id)


@router.post("/", response_model=LoteResponse, status_code=201)
def registrar_recepcion(datos: LoteCreate, db: Session = Depends(get_db), usuario=Depends(obtener_usuario_actual)):
    """Evento 1: recepcion de un nuevo lote de medicamentos."""
    trazabilidad = TrazabilidadService(SQLAlchemyTrazabilidadRepository(db))
    return RegistrarRecepcion(SQLAlchemyLoteRepository(db), trazabilidad).registrar_recepcion(datos.model_dump(), usuario.id)


@router.patch("/{lote_id}/estado", response_model=LoteResponse)
def actualizar_estado(lote_id: int, datos: LoteEstadoUpdate, db: Session = Depends(get_db), usuario=Depends(obtener_usuario_actual)):
    trazabilidad = TrazabilidadService(SQLAlchemyTrazabilidadRepository(db))
    return ActualizarEstado(SQLAlchemyLoteRepository(db), trazabilidad).actualizar_estado(lote_id, datos.nuevo_estado, usuario.id)
