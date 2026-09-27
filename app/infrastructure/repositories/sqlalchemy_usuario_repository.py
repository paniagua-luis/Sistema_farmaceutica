from sqlalchemy.orm import Session
from app.domain.entities.usuario import Usuario
from app.domain.repositories.usuario_repository import IUsuarioRepository
from app.infrastructure.models.usuario_model import UsuarioModel


class SQLAlchemyUsuarioRepository(IUsuarioRepository):
    def __init__(self, db: Session):
        self.db = db

    def _a_entidad(self, u: UsuarioModel) -> Usuario:
        return Usuario(id=u.id, username=u.username, password_hash=u.password_hash, rol=u.rol)

    def get_by_username(self, username: str):
        u = self.db.query(UsuarioModel).filter(UsuarioModel.username == username).first()
        return self._a_entidad(u) if u else None

    def create(self, usuario: Usuario):
        u = UsuarioModel(username=usuario.username, password_hash=usuario.password_hash, rol=usuario.rol)
        self.db.add(u)
        self.db.commit()
        self.db.refresh(u)
        return self._a_entidad(u)
