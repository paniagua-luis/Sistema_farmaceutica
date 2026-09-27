from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.security.security import decodificar_token
from app.infrastructure.repositories.sqlalchemy_usuario_repository import SQLAlchemyUsuarioRepository
from app.infrastructure.models.role_model import RoleModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def obtener_usuario_actual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decodificar_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalido o expirado")

    username = payload.get("sub")
    usuario = SQLAlchemyUsuarioRepository(db).get_by_username(username)
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return usuario


def requiere_permiso(permission_name: str):
    def dependency(usuario=Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
        role = db.query(RoleModel).filter(RoleModel.nombre == usuario.rol).first()
        if not role or not any(permission.nombre == permission_name for permission in role.permisos):
            raise HTTPException(status_code=403, detail="El usuario no tiene permisos para esta operacion")
        return usuario

    return dependency
