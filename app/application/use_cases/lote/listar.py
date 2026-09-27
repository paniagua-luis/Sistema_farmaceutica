from app.domain.repositories.lote_repository import ILoteRepository


class LoteService:
    def __init__(self, repository: ILoteRepository):
        self.repository = repository

    def listar(self):
        return self.repository.get_all()
