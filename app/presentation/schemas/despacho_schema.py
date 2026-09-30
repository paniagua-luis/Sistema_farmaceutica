from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class DespachoProductoCreate(BaseModel):
    lote_id: int = Field(gt=0)
    medicamento_id: int = Field(gt=0)
    cantidad_despachada: int = Field(gt=0)


class DespachoMultipleCreate(BaseModel):
    sucursal_id: int = Field(gt=0)
    productos: list[DespachoProductoCreate] = Field(min_length=1)

    @model_validator(mode="after")
    def validar_productos_unicos(self):
        claves = [(p.lote_id, p.medicamento_id) for p in self.productos]
        if len(claves) != len(set(claves)):
            raise ValueError("No se puede repetir el medicamento del mismo lote en el despacho")
        return self


class DespachoCreate(BaseModel):
    lote_id: int = Field(gt=0)
    medicamento_id: int | None = Field(default=None, gt=0)
    sucursal_id: int = Field(gt=0)
    cantidad_despachada: int = Field(gt=0)


class DespachoResponse(BaseModel):
    id: int
    codigo_despacho: str
    lote_id: int
    medicamento_id: int | None = None
    sucursal_id: int
    cantidad_despachada: int
    estado_despacho: str
    fecha_despacho: datetime | None = None
    fecha_recepcion: datetime | None = None

    class Config:
        from_attributes = True
