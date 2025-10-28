from email.mime.text import MIMEText
import random
import smtplib
import string
from sqlalchemy.orm import Session
from app.models.user_model import Auditoria, User
from app.schemas.user_schemas import UserCreate, UserUpdate
from app.services import security, auditoria


def generar_contrasena(longitud: int = 8) -> str:
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(longitud))

def create_user(db: Session, current_user: User, user: UserCreate):
    if current_user.rol != "admin":
        raise PermissionError("Solo el administrador puede registrar usuarios")
    
    existente = db.query(User).filter(User.email == user.email).first()
    if existente:
        raise ValueError("El email ya está registrado")
    existentew = db.query(User).filter(User.cedula == user.cedula).first()
    if existentew:
        raise ValueError("La cedula ya está registrada")
    
    pass_dado = generar_contrasena()
    print(pass_dado)
    hashed_password = security.hash_password(pass_dado)
    nuevo_usuario = User(
        cedula=user.cedula,
        nombre=user.nombre,
        apellido=user.apellido,
        email=user.email,
        contrasenaHash=hashed_password,
        rol=user.rol,
        estado=user.estado,
        password_temporal=True
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    

    auditoria.registrar_auditoria(db, current_user.idUsuario, "CREAR_USUARIO", f"Se creó usuario {nuevo_usuario.email}")
    return {
        "usuario": nuevo_usuario,
        "password_temporal": pass_dado
    }



def update_user(db: Session, current_user: User, user_id: int, user: UserUpdate):
    """Actualizar datos de un usuario"""
    if current_user.rol != "admin":
        raise PermissionError("Solo el administrador puede editar usuarios")

    usuario = db.query(User).filter(User.idUsuario == user_id).first()
    if not usuario:
        raise LookupError("Usuario no encontrado")

    if user.nombre is not None:
        usuario.nombre = user.nombre
    if user.apellido is not None:
        usuario.apellido = user.apellido
    if user.email is not None:
        usuario.email = user.email
    if user.password is not None:
        usuario.contrasenaHash = security.hash_password(user.password)
    if user.rol is not None:
        usuario.rol = user.rol
    if user.estado is not None:
        usuario.estado = user.estado

    db.commit()
    db.refresh(usuario)

    auditoria.registrar_auditoria(db, current_user.idUsuario, "ACTUALIZAR_USUARIO", f"Se actualizó usuario {usuario.email}")
    return usuario


def get_all_users(db: Session, current_user: User):
    """Obtener todos los usuarios (solo admin)"""
    if current_user.rol != "admin":
        raise PermissionError("Solo el administrador puede ver todos los usuarios")

    usuarios = db.query(User).all()

    auditoria.registrar_auditoria(db, current_user.idUsuario, "CONSULTAR_USUARIOS", "Se consultaron a los usuarios existentes")
    return usuarios


def get_user_by_id(db: Session, current_user: User, user_id: int):
    """Obtener un usuario por ID (solo admin)"""
    if current_user.rol != "admin":
        raise PermissionError("Solo el administrador puede ver un usuario específico")

    usuario = db.query(User).filter(User.idUsuario == user_id).first()
    if not usuario:
        raise LookupError("Usuario no encontrado")

    auditoria.registrar_auditoria(db, current_user.idUsuario, "CONSULTAR_USUARIO", f"Se consultó al usuario {usuario.idUsuario}")
    return usuario


def disable_user(db: Session, current_user: User, user_id: int):
    
    if current_user.rol != "admin":
        raise PermissionError("Solo el administrador puede cambiar el estado de usuarios")

    usuario = db.query(User).filter(User.idUsuario == user_id).first()
    if not usuario:
        raise LookupError("Usuario no encontrado")

    nuevo_estado = "activo" if usuario.estado == "inactivo" else "inactivo"
    usuario.estado = nuevo_estado

    db.commit()
    db.refresh(usuario)

    accion = "HABILITAR_USUARIO" if nuevo_estado == "activo" else "INHABILITAR_USUARIO"
    auditoria.registrar_auditoria(db, current_user.idUsuario, accion, f"Se cambió estado de usuario {usuario.email} a {nuevo_estado}")

    return usuario


def get_current_user(db: Session, current_user: User):
    """Obtener nombre del doctor"""
    usuario = db.query(User).filter(User.idUsuario == current_user.idUsuario).first()
    
    if not usuario:
        raise LookupError("Usuario no encontrado")
    
    return usuario

def get_cantidad_medicos(db: Session, current_user: User):
    """Cantidad total de medicos"""
    if current_user.rol != "admin":
        raise PermissionError("Solo el administrador puede consultar esta información")

    cantidad = db.query(User).filter(User.rol == "medico").count()

    return cantidad

def get_cantidad_medicosactivos(db: Session, current_user: User):
    """Cantidad total de medicos activos"""
    if current_user.rol != "admin":
        raise PermissionError("Solo el administrador puede consultar esta información")

    cantidad = db.query(User).filter(
        User.rol == "medico",
        User.estado == "activo"
    ).count()

    return cantidad

def get_all_logs(db: Session):
    """Devuelve todos los logs del sistema"""
    return db.query(Auditoria).order_by(Auditoria.fechaHora.desc()).all()

def get_user_access_logs(db: Session, user_id: int):
    """Devuelve los logs de un usuario específico"""
    return (
        db.query(Auditoria)
        .filter(Auditoria.idUsuario == user_id)
        .order_by(Auditoria.fechaHora.desc())
        .all()
    )

def get_all_login_logs(db: Session):
    """Devuelve todos los logs relacionados con inicio de sesión"""
    return (
        db.query(Auditoria)
        .filter(Auditoria.accion == "login")
        .order_by(Auditoria.fechaHora.desc())
        .all()
    )