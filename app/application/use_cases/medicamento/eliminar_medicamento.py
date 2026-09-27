from fastapi import HTTPException
from app.domain.repositories.medicamento_repository import IMedicamentoRepository
from app.domain.entities.medicamento import Medicamento


class MedicamentoService:
    def __init__(self, repository: IMedicamentoRepository):
        self.repository = repository

    def eliminar(self, medicamento_id: int):
        if not self.repository.get_by_id(medicamento_id):
            raise HTTPException(status_code=404, detail="Medicamento no encontrado")
        self.repository.delete(medicamento_id)
        return {"mensaje": "Medicamento eliminado correctamente"}
