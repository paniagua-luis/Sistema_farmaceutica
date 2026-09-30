from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.repositories.sqlalchemy_lote_repository import SQLAlchemyLoteRepository
from app.infrastructure.repositories.sqlalchemy_reporte_repository import SQLAlchemyReporteRepository
from app.application.use_cases.reporte.consultar_inventario import ReporteInventarioService
from app.application.use_cases.reporte.listar_reporte import ReporteService as ListarReportes
from app.application.use_cases.reporte.generar_reporte import ReporteService as GenerarReporte
from app.presentation.schemas.reporte_schema import (
    AlertaVencimientoResponse,
    ReporteCreate,
    ReporteInventarioResponse,
    ReporteResponse,
)
from app.presentation.dependencies import requiere_permiso

router = APIRouter(prefix="/reportes", tags=["Trazabilidad y Reportes"], dependencies=[Depends(requiere_permiso("reportes.consultar"))])


@router.get("/", response_model=list[ReporteResponse])
def listar(db: Session = Depends(get_db)):
    return ListarReportes(SQLAlchemyReporteRepository(db)).listar()


@router.get("/inventario", response_model=list[ReporteInventarioResponse])
def consultar_inventario(
    proveedor_id: int | None = Query(default=None, gt=0),
    medicamento_id: int | None = Query(default=None, gt=0),
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    db: Session = Depends(get_db),
):
    return ReporteInventarioService(SQLAlchemyLoteRepository(db)).consultar(
        proveedor_id=proveedor_id,
        medicamento_id=medicamento_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )


@router.get("/alertas/vencimiento", response_model=list[AlertaVencimientoResponse])
def alertas_vencimiento(db: Session = Depends(get_db)):
    return ReporteInventarioService(SQLAlchemyLoteRepository(db)).listar_alertas_vencimiento()


@router.post("/", response_model=ReporteResponse, status_code=201)
def generar(datos: ReporteCreate, db: Session = Depends(get_db)):
    """Eventos 8, 9 y 20: reporte consolidado e informes regulatorios."""
    return GenerarReporte(SQLAlchemyReporteRepository(db)).generar(datos.model_dump())
