from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.repositories.sqlalchemy_sucursal_repository import SQLAlchemySucursalRepository
from app.application.use_cases.sucursal.listar_sucursal import SucursalService as ListarSucursales
from app.application.use_cases.sucursal.obtener_sucursal import SucursalService as ObtenerSucursal
from app.application.use_cases.sucursal.crear_sucursal import SucursalService as CrearSucursal
from app.application.use_cases.sucursal.eliminar_sucursal import SucursalService as EliminarSucursal
from app.presentation.schemas.sucursal_schema import SucursalCreate, SucursalResponse
from app.presentation.dependencies import requiere_permiso

router = APIRouter(prefix="/sucursales", tags=["Sucursales"])


@router.get("/", response_model=list[SucursalResponse], dependencies=[Depends(requiere_permiso("sucursales.consultar"))])
def listar(db: Session = Depends(get_db)):
    return ListarSucursales(SQLAlchemySucursalRepository(db)).listar()


@router.get("/{sucursal_id}", response_model=SucursalResponse, dependencies=[Depends(requiere_permiso("sucursales.consultar"))])
def obtener(sucursal_id: int, db: Session = Depends(get_db)):
    return ObtenerSucursal(SQLAlchemySucursalRepository(db)).obtener(sucursal_id)


@router.post("/", response_model=SucursalResponse, status_code=201, dependencies=[Depends(requiere_permiso("sucursales.gestionar"))])
def crear(datos: SucursalCreate, db: Session = Depends(get_db)):
    return CrearSucursal(SQLAlchemySucursalRepository(db)).crear(datos.model_dump())


@router.delete("/{sucursal_id}", dependencies=[Depends(requiere_permiso("sucursales.gestionar"))])
def eliminar(sucursal_id: int, db: Session = Depends(get_db)):
    return EliminarSucursal(SQLAlchemySucursalRepository(db)).eliminar(sucursal_id)
