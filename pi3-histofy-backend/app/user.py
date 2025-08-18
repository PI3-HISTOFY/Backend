# app/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import models, database, security, schemas

router = APIRouter(prefix="/user", tags=["Users"])


@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    
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

    return nuevo_usuario


@router.put("/update/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(database.get_db)):
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
    return usuario
