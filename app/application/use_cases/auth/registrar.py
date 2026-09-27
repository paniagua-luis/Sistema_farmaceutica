from fastapi import HTTPException
from app.domain.repositories.usuario_repository import IUsuarioRepository
from app.domain.entities.usuario import Usuario
from app.infrastructure.security.security import hash_password, verificar_password, crear_token
from app.infrastructure.security.authorization import ROLE_PERMISSIONS


class AuthService:
    def __init__(self, repository: IUsuarioRepository):
        self.repository = repository

    
    def registrar(self, username: str, password: str, rol: str):
        if rol not in ROLE_PERMISSIONS:
            raise HTTPException(status_code=400, detail="Rol invalido")
        if self.repository.get_by_username(username):
            raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
        usuario = Usuario(username=username, password_hash=hash_password(password), rol=rol)
        return self.repository.create(usuario)
