from pydantic import BaseModel, EmailStr
from typing import Literal, Optional, List
from enum import Enum
from datetime import datetime

#usuarios
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


#historias clinicas
class Paciente(BaseModel):
    cc: str
    nombre: str
    apellido: str
    edad: Optional[int] = None
    sexo: Optional[str] = None

class NLPData(BaseModel):
    categorias: List[str] = []
    keywords: List[str] = []
    sentimiento: Optional[str] = None
    riesgo: Optional[str] = None

class HistoriaMongoBase(BaseModel):
    paciente: Paciente
    texto: str
    diagnostico: Optional[str] = None
    tratamiento: Optional[str] = None
    notas: Optional[str] = None
    nlp: Optional[NLPData] = None

class HistoriaMongoCreate(HistoriaMongoBase):
    pass

class HistoriaMongoResponse(HistoriaMongoBase):
    idUsuario: int
    fecha: datetime

    class Config:
        orm_mode = True
