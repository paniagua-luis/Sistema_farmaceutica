from fastapi import HTTPException
from app.domain.repositories.medicamento_repository import IMedicamentoRepository
from app.domain.entities.medicamento import Medicamento


class MedicamentoService:
    def __init__(self, repository: IMedicamentoRepository):
        self.repository = repository

    def crear(self, datos: dict):
        if self.repository.get_by_codigo(datos["codigo_medicamento"]):
            raise HTTPException(status_code=409, detail="Ya existe un medicamento con ese codigo")
        if datos["temperatura_minima"] > datos["temperatura_maxima"]:
            raise HTTPException(status_code=400, detail="La temperatura minima no puede superar la maxima")
        if datos["dias_alerta_vencimiento"] < 0:
            raise HTTPException(status_code=400, detail="Los dias de alerta no pueden ser negativos")
        return self.repository.create(Medicamento(**datos))
