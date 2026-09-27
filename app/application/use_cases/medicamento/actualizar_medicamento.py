from fastapi import HTTPException
from app.domain.repositories.medicamento_repository import IMedicamentoRepository
from app.domain.entities.medicamento import Medicamento


class MedicamentoService:
    def __init__(self, repository: IMedicamentoRepository):
        self.repository = repository

    def actualizar(self, medicamento_id: int, datos: dict):
        medicamento = self.repository.get_by_id(medicamento_id)
        if not medicamento:
            raise HTTPException(status_code=404, detail="Medicamento no encontrado")
        codigo_medicamento = datos.get("codigo_medicamento", medicamento.codigo_medicamento)
        existente = self.repository.get_by_codigo(codigo_medicamento)
        if existente and existente.id != medicamento_id:
            raise HTTPException(status_code=409, detail="Ya existe un medicamento con ese codigo")
        if datos.get("temperatura_minima", medicamento.temperatura_minima) > datos.get("temperatura_maxima", medicamento.temperatura_maxima):
            raise HTTPException(status_code=400, detail="La temperatura minima no puede superar la maxima")
        if datos.get("dias_alerta_vencimiento", medicamento.dias_alerta_vencimiento) < 0:
            raise HTTPException(status_code=400, detail="Los dias de alerta no pueden ser negativos")
        medicamento.codigo_medicamento = codigo_medicamento
        medicamento.nombre = datos.get("nombre", medicamento.nombre)
        medicamento.principio_activo = datos.get("principio_activo", medicamento.principio_activo)
        medicamento.temperatura_minima = datos.get("temperatura_minima", medicamento.temperatura_minima)
        medicamento.temperatura_maxima = datos.get("temperatura_maxima", medicamento.temperatura_maxima)
        medicamento.dias_alerta_vencimiento = datos.get("dias_alerta_vencimiento", medicamento.dias_alerta_vencimiento)
        return self.repository.update(medicamento)

  