# app/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import models, database, security

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db)
):
    # Buscar usuario por email
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    
    # Crear token
    access_token = security.create_access_token({"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": security.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
