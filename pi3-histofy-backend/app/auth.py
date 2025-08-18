# app/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app import models, database, security, schemas
from datetime import datetime, timedelta
from fastapi import Request
from jose import jwt, JWTError

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# aaaaaaaaaaaaaaaaaaaaaaaa verificar
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db)
):
    try:
        # Decodificar el JWT
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    # Validar sesión en DB
    sesion = db.query(models.Sesion).filter(models.Sesion.token == token).first()
    if not sesion:
        raise HTTPException(status_code=401, detail="Sesión no encontrada o cerrada")

    # Verificar expiración
    if sesion.expiracion < datetime.utcnow():
        db.delete(sesion)
        db.commit()
        raise HTTPException(status_code=401, detail="Sesión expirada")

    # Obtener usuario
    usuario = db.query(models.User).filter(models.User.email == email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return usuario

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
    request: Request = None
):
    # Buscar usuario
    usuario = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not usuario or not security.verify_password(form_data.password, usuario.contrasenaHash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Crear token JWT
    access_token = security.create_access_token({"sub": usuario.email})
    expiracion = datetime.utcnow() + timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Guardar sesión en DB
    nueva_sesion = models.Sesion(
        idUsuario=usuario.idUsuario,
        token=access_token,
        expiracion=expiracion,
        ip=request.client.host if request else None
    )
    db.add(nueva_sesion)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": security.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/logout")
def logout(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)  # ya es User
):
    # Ya tienes el usuario, no necesitas buscarlo otra vez
    db.query(models.Sesion).filter(models.Sesion.idUsuario == current_user.idUsuario).delete()
    db.commit()
    return {"msg": "Sesiones eliminadas, logout exitoso"}

# @router.post("/login")
# def login(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: Session = Depends(database.get_db)
# ):
#     # Buscar usuario por email
#     user = db.query(models.User).filter(models.User.email == form_data.nombre).first()
#     if not user or not security.verify_password(form_data.password, user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Credenciales inválidas"
#         )
    
#     # Crear token
#     access_token = security.create_access_token({"sub": user.email})
#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#         "expires_in": security.ACCESS_TOKEN_EXPIRE_MINUTES * 60
#     }
