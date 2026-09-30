from pydantic import BaseModel


class UsuarioCreate(BaseModel):
    username: str
    password: str


class UsuarioRolUpdate(BaseModel):
    rol: str


class UsuarioResponse(BaseModel):
    id: int
    username: str
    rol: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
