from fastapi import HTTPException
from app.domain.repositories.lote_repository import ILoteRepository


class LoteService:
    def __init__(self, repository: ILoteRepository):
        self.repository = repository

    def listar_stock_bajo(self, umbral: int):
        if umbral <= 0:
            raise HTTPException(status_code=400, detail="El umbral debe ser mayor que cero")
        return self.repository.get_stock_bajo(umbral)