from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.repositories.sqlalchemy_lote_repository import SQLAlchemyLoteRepository
from app.infrastructure.repositories.sqlalchemy_trazabilidad_repository import SQLAlchemyTrazabilidadRepository
from app.application.use_cases.lote.listar import LoteService as ListarLotes
from app.application.use_cases.lote.obtener_lote import LoteService as ObtenerLote
from app.application.use_cases.lote.registrar_recepcion import LoteService as RegistrarRecepcion
from app.application.use_cases.lote.actualizar_estado import LoteService as ActualizarEstado
from app.application.use_cases.lote.listar_stock_bajo import LoteService as ListarStockBajo
from app.application.use_cases.trazabilidad.registrar_evento import TrazabilidadService
from app.presentation.schemas.lote_schema import (
    LoteCreate, LoteResponse, LoteEstadoUpdate, AlertaStockBajoResponse,
    RecepcionLotesCreate,
)
from app.presentation.dependencies import obtener_usuario_actual, requiere_permiso
from fastapi import Query

router = APIRouter(prefix="/lotes", tags=["Lotes"])


@router.get("/", response_model=list[LoteResponse], dependencies=[Depends(requiere_permiso("lotes.consultar"))])
def listar(db: Session = Depends(get_db)):
    return ListarLotes(SQLAlchemyLoteRepository(db)).listar()


@router.get("/alertas/bajo-stock", response_model=list[AlertaStockBajoResponse], dependencies=[Depends(requiere_permiso("lotes.consultar"))])
def listar_stock_bajo(umbral: int = Query(default=10, gt=0), db: Session = Depends(get_db)):
    return ListarStockBajo(SQLAlchemyLoteRepository(db)).listar_stock_bajo(umbral)


@router.post("/recepciones", response_model=list[LoteResponse], status_code=201, dependencies=[Depends(requiere_permiso("lotes.gestionar"))])
def registrar_recepcion_multiple(datos: RecepcionLotesCreate, db: Session = Depends(get_db), usuario=Depends(obtener_usuario_actual)):
    """Registra varios lotes independientes dentro de una misma recepcion."""
    trazabilidad = TrazabilidadService(SQLAlchemyTrazabilidadRepository(db))
    return RegistrarRecepcion(SQLAlchemyLoteRepository(db), trazabilidad).registrar_recepciones(
        [lote.model_dump() for lote in datos.lotes], usuario.id,
    )


@router.get("/{lote_id}", response_model=LoteResponse, dependencies=[Depends(requiere_permiso("lotes.consultar"))])
def obtener(lote_id: int, db: Session = Depends(get_db)):
    return ObtenerLote(SQLAlchemyLoteRepository(db)).obtener(lote_id)


@router.post("/", response_model=LoteResponse, status_code=201, dependencies=[Depends(requiere_permiso("lotes.gestionar"))])
def registrar_recepcion(datos: LoteCreate, db: Session = Depends(get_db), usuario=Depends(obtener_usuario_actual)):
    """Evento 1: recepcion de un nuevo lote de medicamentos."""
    trazabilidad = TrazabilidadService(SQLAlchemyTrazabilidadRepository(db))
    return RegistrarRecepcion(SQLAlchemyLoteRepository(db), trazabilidad).registrar_recepcion(datos.model_dump(), usuario.id)


@router.patch("/{lote_id}/estado", response_model=LoteResponse, dependencies=[Depends(requiere_permiso("lotes.gestionar"))])
def actualizar_estado(lote_id: int, datos: LoteEstadoUpdate, db: Session = Depends(get_db), usuario=Depends(obtener_usuario_actual)):
    trazabilidad = TrazabilidadService(SQLAlchemyTrazabilidadRepository(db))
    return ActualizarEstado(SQLAlchemyLoteRepository(db), trazabilidad).actualizar_estado(lote_id, datos.nuevo_estado, usuario.id)
