from pydantic import BaseModel


class UsuarioCreate(BaseModel):
    username: str
    password: str
    rol: str = "operador"


class UsuarioResponse(BaseModel):
    id: int
    username: str
    rol: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
