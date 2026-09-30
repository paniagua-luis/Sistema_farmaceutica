from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.repositories.sqlalchemy_usuario_repository import SQLAlchemyUsuarioRepository
from app.application.use_cases.auth.registrar import AuthService as RegistrarUsuario
from app.application.use_cases.auth.login import AuthService as IniciarSesion
from app.presentation.schemas.usuario_schema import UsuarioCreate, UsuarioResponse, Token

router = APIRouter(prefix="/auth", tags=["Autenticacion"])


@router.post("/registro", response_model=UsuarioResponse, status_code=201)
def registrar(datos: UsuarioCreate, db: Session = Depends(get_db)):
    repository = SQLAlchemyUsuarioRepository(db)
    rol = "administrador" if repository.count() == 0 else "personal_sucursal"
    usuario = RegistrarUsuario(repository).registrar(datos.username, datos.password, rol)
    return usuario


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return IniciarSesion(SQLAlchemyUsuarioRepository(db)).login(form.username, form.password)
