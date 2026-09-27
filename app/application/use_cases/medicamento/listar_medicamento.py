from fastapi import HTTPException
from app.domain.repositories.medicamento_repository import IMedicamentoRepository
from app.domain.entities.medicamento import Medicamento


class MedicamentoService:
    def __init__(self, repository: IMedicamentoRepository):
        self.repository = repository

    def listar(self):
        return self.repository.get_all()
