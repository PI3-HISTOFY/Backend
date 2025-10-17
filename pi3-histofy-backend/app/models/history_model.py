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
        
        
# app/models/history_model.py
from typing import Optional, List, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime

# ===== Modelos V2 (formato clínico nuevo) =====

class PacienteV2(BaseModel):
    cc: Optional[str] = None
    nombre_completo: Optional[str] = None
    sexo: Optional[str] = Field(default=None, pattern=r"^(M|F|Otro)?$")
    edad: Optional[int] = None

class NLPV2(BaseModel):
    categorias: Optional[List[str]] = None
    keywords: Optional[List[str]] = None

class HistoriaMongoCreateV2(BaseModel):
    fecha: Optional[str] = None  # ISO 8601 o None
    paciente: PacienteV2
    motivo_consulta: Optional[str] = None
    antecedentes: Optional[str] = None
    examen: Optional[Union[str, dict]] = None  # string o dict si algún día separas por ojo
    diagnostico: Optional[str] = None
    tratamiento: Optional[str] = None
    tipo_atencion: Optional[str] = None
    especialidad: Optional[str] = None
    nivel_atencion: Optional[str] = Field(default=None, pattern=r"^(I|II|III)?$")
    nlp: Optional[NLPV2] = None

    @validator("fecha")
    def _validar_fecha_iso(cls, v):
        if v is None:
            return v
        try:
            # acepta 2025-06-24T00:00:00-05:00 o con Z
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            return v
        except Exception:
            raise ValueError("fecha debe estar en ISO 8601 (ej. 2025-06-24T00:00:00-05:00)")

class HistoriaMongoResponseV2(HistoriaMongoCreateV2):
    _id: Optional[str] = None
    idUsuario: Optional[int] = None

