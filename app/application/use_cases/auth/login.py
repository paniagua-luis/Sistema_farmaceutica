from fastapi import HTTPException
from app.domain.repositories.usuario_repository import IUsuarioRepository
from app.domain.entities.usuario import Usuario
from app.infrastructure.security.security import hash_password, verificar_password, crear_token


class AuthService:
    def __init__(self, repository: IUsuarioRepository):
        self.repository = repository

    def registrar(self, username: str, password: str, rol: str):
        if self.repository.get_by_username(username):
            raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
        usuario = Usuario(username=username, password_hash=hash_password(password), rol=rol)
        return self.repository.create(usuario)

    def login(self, username: str, password: str):
        usuario = self.repository.get_by_username(username)
        if not usuario or not verificar_password(password, usuario.password_hash):
            raise HTTPException(status_code=401, detail="Usuario o contraseña invalidos")
        return {"access_token": crear_token({"sub": usuario.username, "rol": usuario.rol}), "token_type": "bearer"}
