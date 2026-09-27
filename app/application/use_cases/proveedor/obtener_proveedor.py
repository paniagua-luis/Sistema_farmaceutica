from fastapi import HTTPException
from app.domain.repositories.proveedor_repository import IProveedorRepository
from app.domain.entities.proveedor import Proveedor


class ProveedorService:
    def __init__(self, repository: IProveedorRepository):
        self.repository = repository

    def obtener(self, proveedor_id: int):
        proveedor = self.repository.get_by_id(proveedor_id)
        if not proveedor:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")
        return proveedor
