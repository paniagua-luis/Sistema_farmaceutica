from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.application.use_cases.auth.gestionar_usuarios import GestionUsuariosService
from app.infrastructure.database import get_db
from app.infrastructure.repositories.sqlalchemy_usuario_repository import SQLAlchemyUsuarioRepository
from app.presentation.dependencies import requiere_permiso
from app.presentation.schemas.usuario_schema import UsuarioResponse, UsuarioRolUpdate

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get(
    "/",
    response_model=list[UsuarioResponse],
    dependencies=[Depends(requiere_permiso("usuarios.gestionar"))],
)
def listar(db: Session = Depends(get_db)):
    return GestionUsuariosService(SQLAlchemyUsuarioRepository(db)).listar()


@router.patch(
    "/{user_id}/rol",
    response_model=UsuarioResponse,
    dependencies=[Depends(requiere_permiso("usuarios.gestionar"))],
)
def asignar_rol(user_id: int, datos: UsuarioRolUpdate, db: Session = Depends(get_db)):
    return GestionUsuariosService(SQLAlchemyUsuarioRepository(db)).asignar_rol(user_id, datos.rol)