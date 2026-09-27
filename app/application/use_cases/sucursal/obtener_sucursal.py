from fastapi import HTTPException
from app.domain.repositories.sucursal_repository import ISucursalRepository
from app.domain.entities.sucursal import Sucursal


class SucursalService:
    def __init__(self, repository: ISucursalRepository):
        self.repository = repository

    def obtener(self, sucursal_id: int):
        sucursal = self.repository.get_by_id(sucursal_id)
        if not sucursal:
            raise HTTPException(status_code=404, detail="Sucursal no encontrada")
        return sucursal
