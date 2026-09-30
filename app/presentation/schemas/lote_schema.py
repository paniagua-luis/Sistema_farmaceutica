from datetime import date
from pydantic import BaseModel, Field, model_validator


class LoteProductoCreate(BaseModel):
    medicamento_id: int = Field(gt=0)
    cantidad_recibida: int = Field(gt=0)


class LoteProductoResponse(LoteProductoCreate):
    cantidad_disponible: int
    medicamento: str
    model_config = {"from_attributes": True}


class LoteCreate(BaseModel):
    codigo_lote: str | None = None
    proveedor_id: int
    sucursal_id: int
    fecha_recepcion: date
    fecha_vencimiento: date
    productos: list[LoteProductoCreate] | None = Field(default=None, min_length=1)
    medicamento_id: int | None = Field(default=None, gt=0)
    cantidad_recibida: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validar_productos(self):
        if self.productos:
            if self.medicamento_id is not None or self.cantidad_recibida is not None:
                raise ValueError("Usa productos o los campos de medicamento único, no ambos")
            ids = [producto.medicamento_id for producto in self.productos]
            if len(ids) != len(set(ids)):
                raise ValueError("No se puede repetir un medicamento dentro del mismo lote")
        elif self.medicamento_id is None or self.cantidad_recibida is None:
            raise ValueError("Debes indicar productos o medicamento_id y cantidad_recibida")
        return self


class RecepcionLotesCreate(BaseModel):
    lotes: list[LoteCreate] = Field(min_length=1)


class LoteEstadoUpdate(BaseModel):
    nuevo_estado: str


class LoteResponse(BaseModel):
    id: int
    codigo_lote: str
    medicamento_id: int
    proveedor_id: int
    sucursal_id: int
    cantidad_recibida: int
    cantidad_disponible: int
    fecha_recepcion: date
    fecha_vencimiento: date
    estado_lote: str
    productos: list[LoteProductoResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class AlertaStockBajoResponse(BaseModel):
    medicamento_id: int
    medicamento: str
    sucursal_id: int
    sucursal: str
    stock_disponible: int
    umbral: int
