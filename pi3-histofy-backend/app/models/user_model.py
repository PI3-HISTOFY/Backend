from sqlalchemy import Column, Integer, String, Boolean, Enum, TIMESTAMP,ForeignKey,DateTime
from sqlalchemy.sql import func
import enum
from app.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime


class RolEnum(str, enum.Enum):
    admin = "admin"
    medico = "medico"
    paciente = "paciente"

class EstadoEnum(str, enum.Enum):
    activo = "activo"
    inactivo = "inactivo"
    suspendido = "suspendido"

class User(Base):
    __tablename__ = "usuarios"

    idUsuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cedula = Column(Integer, unique=True, nullable=False)
    nombre = Column(String(100))
    apellido = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True)
    contrasenaHash = Column(String(255))
    estado = Column(Boolean, default=True)
    rol = Column(Enum(RolEnum), default=RolEnum.medico)
    rol = Column(Enum(RolEnum), nullable=False, server_default="medico")
    estado = Column(Enum(EstadoEnum), nullable=False, server_default="activo")
    fechaRegistro = Column(TIMESTAMP, server_default=func.now())
    password_temporal = Column(Boolean, default=True)

    logs = relationship("Auditoria", back_populates="usuario")


class Sesion(Base):
    __tablename__ = "sesiones"

    idSesion = Column(Integer, primary_key=True, index=True)
    idUsuario = Column(Integer, ForeignKey("usuarios.idUsuario"))
    token = Column(String(500), unique=True, index=True)
    expiracion = Column(DateTime)
    ip = Column(String(50))

    user = relationship("User", backref="sesiones")


class Auditoria(Base):
    __tablename__ = "auditorias"

    idLog = Column(Integer, primary_key=True, index=True, autoincrement=True)
    idUsuario = Column(Integer, ForeignKey("usuarios.idUsuario"))
    accion = Column(String(50), nullable=False)
    recurso = Column(String(500))
    fechaHora = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("User", back_populates="logs")