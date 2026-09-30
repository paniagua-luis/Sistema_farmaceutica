from fastapi import HTTPException

from app.domain.repositories.usuario_repository import IUsuarioRepository
from app.infrastructure.security.authorization import ROLE_PERMISSIONS


class GestionUsuariosService:
    def __init__(self, repository: IUsuarioRepository):
        self.repository = repository

    def listar(self):
        return self.repository.get_all()

    def asignar_rol(self, user_id: int, role: str):
        if role not in ROLE_PERMISSIONS:
            raise HTTPException(status_code=400, detail="Rol invalido")

        usuario = self.repository.get_by_id(user_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if usuario.rol == "administrador" and role != "administrador":
            if self.repository.count_by_role("administrador") <= 1:
                raise HTTPException(
                    status_code=400,
                    detail="No se puede quitar el rol del ultimo administrador",
                )

        return self.repository.update_role(user_id, role)