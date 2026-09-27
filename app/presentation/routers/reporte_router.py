from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.repositories.sqlalchemy_reporte_repository import SQLAlchemyReporteRepository
from app.application.use_cases.reporte.listar_reporte import ReporteService as ListarReportes
from app.application.use_cases.reporte.generar_reporte import ReporteService as GenerarReporte
from app.presentation.schemas.reporte_schema import ReporteCreate, ReporteResponse
from app.presentation.dependencies import requiere_permiso

router = APIRouter(prefix="/reportes", tags=["Trazabilidad y Reportes"], dependencies=[Depends(requiere_permiso("reportes.consultar"))])


@router.get("/", response_model=list[ReporteResponse])
def listar(db: Session = Depends(get_db)):
    return ListarReportes(SQLAlchemyReporteRepository(db)).listar()


@router.post("/", response_model=ReporteResponse, status_code=201)
def generar(datos: ReporteCreate, db: Session = Depends(get_db)):
    """Eventos 8, 9 y 20: reporte consolidado e informes regulatorios."""
    return GenerarReporte(SQLAlchemyReporteRepository(db)).generar(datos.model_dump())
