from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.repositories.sqlalchemy_monitoreo_temperatura_repository import SQLAlchemyMonitoreoTemperaturaRepository
from app.application.use_cases.monitoreo_temperatura.listar import MonitoreoTemperaturaService as ListarLecturas
from app.application.use_cases.monitoreo_temperatura.registrar_lectura import MonitoreoTemperaturaService as RegistrarLectura
from app.application.use_cases.trazabilidad.registrar_evento import TrazabilidadService as RegistrarEvento
from app.infrastructure.repositories.sqlalchemy_trazabilidad_repository import SQLAlchemyTrazabilidadRepository
from app.presentation.schemas.monitoreo_temperatura_schema import MonitoreoTemperaturaCreate, MonitoreoTemperaturaResponse
from app.presentation.dependencies import obtener_usuario_actual, requiere_permiso

router = APIRouter(prefix="/monitoreo-temperatura", tags=["Monitoreo Cadena de Frio"], dependencies=[Depends(requiere_permiso("temperatura.gestionar"))])


@router.get("/", response_model=list[MonitoreoTemperaturaResponse])
def listar(db: Session = Depends(get_db)):
    return ListarLecturas(SQLAlchemyMonitoreoTemperaturaRepository(db)).listar()


@router.post("/", response_model=MonitoreoTemperaturaResponse, status_code=201)
def registrar_lectura(datos: MonitoreoTemperaturaCreate, db: Session = Depends(get_db), usuario=Depends(obtener_usuario_actual)):
    """Eventos 16 y 19: monitoreo periodico de temperatura y deteccion de desviaciones."""
    temp_min, temp_max = -100.0, 100.0
    trazabilidad = RegistrarEvento(SQLAlchemyTrazabilidadRepository(db))
    return RegistrarLectura(SQLAlchemyMonitoreoTemperaturaRepository(db), trazabilidad).registrar_lectura(datos.model_dump(), temp_min, temp_max, usuario.id)
