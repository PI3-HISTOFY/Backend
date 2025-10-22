from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from app.services import security, auditoria
from sqlalchemy.orm import Session

from app.models.user_model import User, Sesion
from app.services import security

def login(db: Session, form_data: OAuth2PasswordRequestForm, request: Request = None):
    """Inicia sesión y genera token JWT"""
    ip_cliente = request.client.host if request else "desconocido"
    email = form_data.username

    usuario = db.query(User).filter(User.email == email).first()

    if not usuario or not security.verify_password(form_data.password, usuario.contrasenaHash):
        auditoria.registrar_auditoria(
            db, usuario.idUsuario if usuario else None,
            "login", f"Intento fallido desde {ip_cliente}"
        )
        raise HTTPException(status_code=401, detail="Credenciales inválidas")


    access_token = security.create_access_token({"sub": usuario.email})
    expiracion = datetime.utcnow() + timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)

    nueva_sesion = Sesion(
        idUsuario=usuario.idUsuario,
        token=access_token,
        expiracion=expiracion,
        ip=ip_cliente
    )
    db.add(nueva_sesion)
    db.commit()


    auditoria.registrar_auditoria(
        db, usuario.idUsuario,
        "login", f"Inicio de sesión exitoso desde {ip_cliente}"
    )

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
