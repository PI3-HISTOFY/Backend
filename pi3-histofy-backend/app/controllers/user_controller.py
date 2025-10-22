from sqlalchemy.orm import Session
from app.models.user_model import User
from app.schemas.user_schemas import UserCreate, UserUpdate
from app.services import security, auditoria

def create_user(db: Session, current_user: User, user: UserCreate):
    if current_user.rol != "admin":
        raise PermissionError("Solo el administrador puede registrar usuarios")
    
    existente = db.query(User).filter(User.email == user.email).first()
    if existente:
        raise ValueError("El email ya está registrado")
    
    hashed_password = security.hash_password(user.password)
    nuevo_usuario = User(
        nombre=user.nombre,
        apellido=user.apellido,
        email=user.email,
        contrasenaHash=hashed_password,
        rol=user.rol,
        estado=user.estado
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    auditoria.registrar_auditoria(db, current_user.idUsuario, "CREAR_USUARIO", f"Se creó usuario {nuevo_usuario.email}")
    return nuevo_usuario



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
    """Inhabilitar un usuario (solo admin)"""
    if current_user.rol != "admin":
        raise PermissionError("Solo el administrador puede inhabilitar usuarios")

    usuario = db.query(User).filter(User.idUsuario == user_id).first()
    if not usuario:
        raise LookupError("Usuario no encontrado")

    usuario.estado = "inactivo"
    db.commit()
    db.refresh(usuario)

    auditoria.registrar_auditoria(db, current_user.idUsuario, "INHABILITAR_USUARIO", f"Se inhabilitó usuario {usuario.email}")
    return usuario

def get_current_user(db: Session, current_user: User):
    """Obtener nombre del doctor"""
    usuario = db.query(User).filter(User.idUsuario == current_user.idUsuario).first()
    
    if not usuario:
        raise LookupError("Usuario no encontrado")
    
    return {
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
    }

def get_cantidad_medicos(db: Session, current_user: User):
    """Cantidad total de medicos"""
    if current_user.rol != "admin":
        raise PermissionError("Solo el administrador puede consultar esta información")

    cantidad = db.query(User).filter(User.rol == "medico").count()

    return cantidad
