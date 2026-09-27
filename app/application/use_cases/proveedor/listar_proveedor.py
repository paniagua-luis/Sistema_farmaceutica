from fastapi import HTTPException
from app.domain.repositories.proveedor_repository import IProveedorRepository
from app.domain.entities.proveedor import Proveedor


class ProveedorService:
    def __init__(self, repository: IProveedorRepository):
        self.repository = repository

    def listar(self):
        return self.repository.get_all()
