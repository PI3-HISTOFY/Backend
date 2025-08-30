# app/user.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, database, security, schemas
from app.auth import get_current_user
from app.auditoria import registrar_auditoria


router = APIRouter(prefix="/user", tags=["Users"])


@router.post("/register", response_model=schemas.UserResponse)
def register(
    user: schemas.UserCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debe iniciar sesión para acceder a este recurso"
        )
    
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo el administrador puede registrar usuarios")

    existente = db.query(models.User).filter(models.User.email == user.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    hashed_password = security.hash_password(user.password)

    nuevo_usuario = models.User(
        nombre=user.nombre,
        apellido=user.apellido,
        email=user.email,
        contrasenaHash=hashed_password,
        rol=user.rol or schemas.RolEnum.medico,
        estado=user.estado or schemas.EstadoEnum.activo
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    registrar_auditoria(db, current_user.idUsuario, "CREAR_USUARIO", f"Se creo usuario {nuevo_usuario.email}")

    return nuevo_usuario


@router.put("/update/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: int, user: schemas.UserUpdate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debe iniciar sesión para acceder a este recurso"
        )
    
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo el administrador puede ver u editar usuarios")

    usuario = db.query(models.User).filter(models.User.idUsuario == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")


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

    registrar_auditoria(db, current_user.idUsuario, "ACTUALIZAR_USUARIO", f"Se actualizo usuario {usuario.email}")
    
    return usuario


@router.get("/getAll", response_model=list[schemas.UserResponse])
def get_all_users(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debe iniciar sesion para acceder a este recurso"
        )

    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo el administrador puede ver todos los usuarios")

    usuarios = db.query(models.User).all()

    registrar_auditoria(db, current_user.idUsuario, "CONSULTAR_USUARIOS", "Se consultaron a los usuarios existentes")

    return usuarios


@router.get("/getId/{user_id}", response_model=schemas.UserResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debe iniciar sesión para acceder a este recurso"
        )

    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo el administrador puede ver un usuario específico")

    usuario = db.query(models.User).filter(models.User.idUsuario == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    registrar_auditoria(db, current_user.idUsuario, F"CONSULTAR_USUARIO {usuario.id}", f"Se consulto al usuario {usuario.id}")

    return usuario


@router.put("/updateState/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: int, user: schemas.UserUpdate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debe iniciar sesión para acceder a este recurso"
        )
    
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo el administrador puede ver u editar usuarios")

    usuario = db.query(models.User).filter(models.User.idUsuario == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.estado = "inactivo"

    db.commit()
    db.refresh(usuario)

    registrar_auditoria(
        db, current_user.idUsuario,
        "INHABILITAR_USUARIO",
        f"Se inhabilito usuario {usuario.email}"
    )
    
    return usuario