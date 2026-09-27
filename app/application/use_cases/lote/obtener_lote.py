from fastapi import HTTPException
from app.domain.repositories.lote_repository import ILoteRepository


class LoteService:
    def __init__(self, repository: ILoteRepository):
        self.repository = repository


    def obtener(self, lote_id: int):
        lote = self.repository.get_by_id(lote_id)
        if not lote:
            raise HTTPException(status_code=404, detail="Lote no encontrado")
        return lote
