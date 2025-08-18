from pydantic import BaseModel, EmailStr
from typing import Literal, Optional
from enum import Enum

class RolEnum(str, Enum):
    admin = "admin"
    medico = "medico"
    paciente = "paciente"

class EstadoEnum(str, Enum):
    activo = "activo"
    inactivo = "inactivo"
    suspendido = "suspendido"

class UserCreate(BaseModel):
    nombre: str
    apellido: str
    email: EmailStr
    password: str
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
    nombre: str
    apellido: str
    email: EmailStr
    estado: bool
    rol: Literal["medico", "admin"]
    estado: Literal["activo", "inactivo"]

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    nombre: str
    password: str