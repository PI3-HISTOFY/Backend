from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.models.user_model import User, Sesion
from app.services import security


def login(db: Session, form_data: OAuth2PasswordRequestForm, request: Request = None):
    """Inicia sesión y genera token JWT"""
    usuario = db.query(User).filter(User.email == form_data.username).first()
    if not usuario or not security.verify_password(form_data.password, usuario.contrasenaHash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    access_token = security.create_access_token({"sub": usuario.email})
    expiracion = datetime.utcnow() + timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)

    nueva_sesion = Sesion(
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


def logout(db: Session, current_user: User):
    """Elimina todas las sesiones activas del usuario"""
    db.query(Sesion).filter(Sesion.idUsuario == current_user.idUsuario).delete()
    db.commit()
    return {"msg": "Sesiones eliminadas, logout exitoso"}
