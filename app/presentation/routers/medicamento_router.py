from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.repositories.sqlalchemy_medicamento_repository import SQLAlchemyMedicamentoRepository
from app.application.use_cases.medicamento.listar_medicamento import MedicamentoService as ListarMedicamentos
from app.application.use_cases.medicamento.obtener_medicamento import MedicamentoService as ObtenerMedicamento
from app.application.use_cases.medicamento.crear_medicamento import MedicamentoService as CrearMedicamento
from app.application.use_cases.medicamento.actualizar_medicamento import MedicamentoService as ActualizarMedicamento
from app.application.use_cases.medicamento.eliminar_medicamento import MedicamentoService as EliminarMedicamento
from app.presentation.schemas.medicamento_schema import MedicamentoCreate, MedicamentoResponse
from app.presentation.dependencies import requiere_permiso

router = APIRouter(prefix="/medicamentos", tags=["Medicamentos"], dependencies=[Depends(requiere_permiso("medicamentos.gestionar"))])


@router.get("/", response_model=list[MedicamentoResponse])
def listar(db: Session = Depends(get_db)):
    return ListarMedicamentos(SQLAlchemyMedicamentoRepository(db)).listar()


@router.get("/{medicamento_id}", response_model=MedicamentoResponse)
def obtener(medicamento_id: int, db: Session = Depends(get_db)):
    return ObtenerMedicamento(SQLAlchemyMedicamentoRepository(db)).obtener(medicamento_id)


@router.post("/", response_model=MedicamentoResponse, status_code=201)
def crear(datos: MedicamentoCreate, db: Session = Depends(get_db)):
    return CrearMedicamento(SQLAlchemyMedicamentoRepository(db)).crear(datos.model_dump())


@router.put("/{medicamento_id}", response_model=MedicamentoResponse)
def actualizar(medicamento_id: int, datos: MedicamentoCreate, db: Session = Depends(get_db)):
    return ActualizarMedicamento(SQLAlchemyMedicamentoRepository(db)).actualizar(medicamento_id, datos.model_dump())


@router.delete("/{medicamento_id}")
def eliminar(medicamento_id: int, db: Session = Depends(get_db)):
    return EliminarMedicamento(SQLAlchemyMedicamentoRepository(db)).eliminar(medicamento_id)
