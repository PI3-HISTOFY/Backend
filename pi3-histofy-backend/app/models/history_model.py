from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

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
    motivo_consulta: str
    antecedentes: Optional[str] = None
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
