from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.repositories.sqlalchemy_proveedor_repository import SQLAlchemyProveedorRepository
from app.application.use_cases.proveedor.listar_proveedor import ProveedorService as ListarProveedores
from app.application.use_cases.proveedor.obtener_proveedor import ProveedorService as ObtenerProveedor
from app.application.use_cases.proveedor.crear_proveedor import ProveedorService as CrearProveedor
from app.application.use_cases.proveedor.eliminar_proveedor import ProveedorService as EliminarProveedor
from app.presentation.schemas.proveedor_schema import ProveedorCreate, ProveedorResponse
from app.presentation.dependencies import requiere_permiso

router = APIRouter(prefix="/proveedores", tags=["Proveedores"], dependencies=[Depends(requiere_permiso("proveedores.gestionar"))])


@router.get("/", response_model=list[ProveedorResponse])
def listar(db: Session = Depends(get_db)):
    return ListarProveedores(SQLAlchemyProveedorRepository(db)).listar()


@router.get("/{proveedor_id}", response_model=ProveedorResponse)
def obtener(proveedor_id: int, db: Session = Depends(get_db)):
    return ObtenerProveedor(SQLAlchemyProveedorRepository(db)).obtener(proveedor_id)


@router.post("/", response_model=ProveedorResponse, status_code=201)
def crear(datos: ProveedorCreate, db: Session = Depends(get_db)):
    return CrearProveedor(SQLAlchemyProveedorRepository(db)).crear(datos.model_dump())


@router.delete("/{proveedor_id}")
def eliminar(proveedor_id: int, db: Session = Depends(get_db)):
    return EliminarProveedor(SQLAlchemyProveedorRepository(db)).eliminar(proveedor_id)
