from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.repositories.sqlalchemy_despacho_repository import SQLAlchemyDespachoRepository
from app.infrastructure.repositories.sqlalchemy_lote_repository import SQLAlchemyLoteRepository
from app.infrastructure.repositories.sqlalchemy_trazabilidad_repository import SQLAlchemyTrazabilidadRepository
from app.application.use_cases.despacho.listar_despaacho import DespachoService as ListarDespachos
from app.application.use_cases.despacho.registrar_despacho import DespachoService as RegistrarDespacho
from app.application.use_cases.despacho.confirmar_recepcion import DespachoService as ConfirmarRecepcion
from app.application.use_cases.lote.obtener_lote import LoteService as ObtenerLote
from app.application.use_cases.lote.descontar_stock import LoteService as DescontarStock
from app.application.use_cases.trazabilidad.registrar_evento import TrazabilidadService
from app.presentation.schemas.despacho_schema import DespachoCreate, DespachoResponse
from app.presentation.dependencies import obtener_usuario_actual, requiere_permiso

router = APIRouter(prefix="/despachos", tags=["Distribucion y Despacho"], dependencies=[Depends(requiere_permiso("despachos.gestionar"))])


@router.get("/", response_model=list[DespachoResponse])
def listar(db: Session = Depends(get_db)):
    return ListarDespachos(SQLAlchemyDespachoRepository(db)).listar()


@router.post("/", response_model=DespachoResponse, status_code=201)
def registrar_despacho(datos: DespachoCreate, db: Session = Depends(get_db), usuario=Depends(obtener_usuario_actual)):
    """Eventos 3, 4 y 14: solicitud de abastecimiento y despacho a la sucursal."""
    trazabilidad = TrazabilidadService(SQLAlchemyTrazabilidadRepository(db))
    return RegistrarDespacho(SQLAlchemyDespachoRepository(db), ObtenerLote(SQLAlchemyLoteRepository(db)), DescontarStock(SQLAlchemyLoteRepository(db), trazabilidad), trazabilidad).registrar_despacho(datos.model_dump(), usuario.id)


@router.patch("/{despacho_id}/confirmar", response_model=DespachoResponse)
def confirmar_recepcion(despacho_id: int, db: Session = Depends(get_db), usuario=Depends(obtener_usuario_actual)):
    """Evento 5: la sucursal confirma la recepcion fisica de la mercancia."""
    trazabilidad = TrazabilidadService(SQLAlchemyTrazabilidadRepository(db))
    return ConfirmarRecepcion(SQLAlchemyDespachoRepository(db), trazabilidad).confirmar_recepcion(despacho_id, usuario.id)
