from fastapi import HTTPException
from app.domain.repositories.sucursal_repository import ISucursalRepository
from app.domain.entities.sucursal import Sucursal


class SucursalService:
    def __init__(self, repository: ISucursalRepository):
        self.repository = repository

    def listar(self):
        return self.repository.get_all()

