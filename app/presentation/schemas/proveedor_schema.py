from pydantic import BaseModel


class ProveedorCreate(BaseModel):
    nombre: str
    contacto: str | None = None
    codigo_proveedor: str


class ProveedorResponse(ProveedorCreate):
    id: int

    class Config:
        from_attributes = True
