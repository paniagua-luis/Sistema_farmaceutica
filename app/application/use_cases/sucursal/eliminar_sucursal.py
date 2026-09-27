from fastapi import HTTPException
from app.domain.repositories.sucursal_repository import ISucursalRepository
from app.domain.entities.sucursal import Sucursal


class SucursalService:
    def __init__(self, repository: ISucursalRepository):
        self.repository = repository

    def eliminar(self, sucursal_id: int):
        if not self.repository.get_by_id(sucursal_id):
            raise HTTPException(status_code=404, detail="Sucursal no encontrada")
        self.repository.delete(sucursal_id)
        return {"mensaje": "Sucursal eliminada correctamente"}
