from pydantic import BaseModel, EmailStr
from typing import Literal, Optional
from enum import Enum

#usuarios
class RolEnum(str, Enum):
    admin = "admin"
    medico = "medico"

class EstadoEnum(str, Enum):
    activo = "activo"
    inactivo = "inactivo"

class UserCreate(BaseModel):
    cedula: int
    nombre: str
    apellido: str
    email: EmailStr
    rol: Optional[RolEnum] = RolEnum.medico
    estado: Optional[EstadoEnum] = EstadoEnum.activo

class UserUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    estado: Optional[bool] = None
    rol: Optional[str] = None

class UserResponse(BaseModel):
    idUsuario: int
    cedula: int
    nombre: str
    apellido: str
    email: EmailStr
    estado: bool
    rol: Literal["medico", "admin"]
    estado: Literal["activo", "inactivo"]

    class Config:
        from_attributes = True

class UserResponseCreate(BaseModel):
    usuario: UserResponse
    password_temporal: str

class UserLogin(BaseModel):
    nombre: str
    password: str

