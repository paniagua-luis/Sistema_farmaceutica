from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.repositories.sqlalchemy_trazabilidad_repository import SQLAlchemyTrazabilidadRepository
from app.application.use_cases.trazabilidad.listar import TrazabilidadService as ListarTrazabilidad
from app.application.use_cases.trazabilidad.historial_lote import TrazabilidadService as HistorialTrazabilidad
from app.presentation.schemas.trazabilidad_schema import TrazabilidadResponse
from app.presentation.dependencies import requiere_permiso

router = APIRouter(prefix="/trazabilidad", tags=["Trazabilidad y Reportes"], dependencies=[Depends(requiere_permiso("trazabilidad.consultar"))])


@router.get("/", response_model=list[TrazabilidadResponse])
def listar(db: Session = Depends(get_db)):
    """Eventos 6 y 7: consulta de trazabilidad de un lote (calidad y administracion)."""
    return ListarTrazabilidad(SQLAlchemyTrazabilidadRepository(db)).listar()


@router.get("/lote/{lote_id}", response_model=list[TrazabilidadResponse])
def historial_de_lote(lote_id: int, db: Session = Depends(get_db)):
    return HistorialTrazabilidad(SQLAlchemyTrazabilidadRepository(db)).historial_de_lote(lote_id)
