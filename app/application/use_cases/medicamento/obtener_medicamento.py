from fastapi import HTTPException
from app.domain.repositories.medicamento_repository import IMedicamentoRepository
from app.domain.entities.medicamento import Medicamento


class MedicamentoService:
    def __init__(self, repository: IMedicamentoRepository):
        self.repository = repository

    def obtener(self, medicamento_id: int):
        medicamento = self.repository.get_by_id(medicamento_id)
        if not medicamento:
            raise HTTPException(status_code=404, detail="Medicamento no encontrado")
        return medicamento
