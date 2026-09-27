from pydantic import BaseModel


class SucursalCreate(BaseModel):
    codigo_sucursal: str
    nombre: str


class SucursalResponse(SucursalCreate):
    id: int

    class Config:
        from_attributes = True
