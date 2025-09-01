# app/auth.py 
from fastapi import APIRouter, Depends, HTTPException
import app.services.security as security
from fastapi.security import OAuth2PasswordBearer 
from sqlalchemy.orm import Session 
from app import models, database
from datetime import datetime
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
        

