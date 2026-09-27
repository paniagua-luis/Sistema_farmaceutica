from app.domain.repositories.despacho_repository import IDespachoRepository


class DespachoService:
    def __init__(self, repository: IDespachoRepository):
        self.repository = repository

    def listar(self):
        return self.repository.get_all()
