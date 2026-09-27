from fastapi import HTTPException
from app.domain.repositories.proveedor_repository import IProveedorRepository
from app.domain.entities.proveedor import Proveedor


class ProveedorService:
    def __init__(self, repository: IProveedorRepository):
        self.repository = repository

    def eliminar(self, proveedor_id: int):
        if not self.repository.get_by_id(proveedor_id):
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")
        self.repository.delete(proveedor_id)
        return {"mensaje": "Proveedor eliminado correctamente"}
