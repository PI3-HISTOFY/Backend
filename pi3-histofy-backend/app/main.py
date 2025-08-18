from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from datetime import datetime
from app import auth, security, ocr, database, models, user


app = FastAPI(title="Histofy Backend", version="1.0.0")

# Rutas de autenticación
app.include_router(auth.router)
app.include_router(ocr.router)
app.include_router(user.router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

#validar sesion activa
def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(database.get_db)
        ):
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token invalido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    sesion = db.query(models.Sesion).filter(models.Sesion.token == token).first()
    if not sesion:
        raise HTTPException(status_code=401, detail="Sesión no encontrada o cerrada")

    # Verificar expiracion
    if sesion.expiracion < datetime.utcnow():
        db.delete(sesion)
        db.commit()
        raise HTTPException(status_code=401, detail="Sesión expirada")
    
    return email

@app.get("/")
def root():
    return {"message": "API Histofy ok"}

@app.get("/protected")
def protected_route(current_user: models.User = Depends(get_current_user)):
    return {
        "message": f"Hola {current_user.nombre} {current_user.apellido}, bienvenido",
        "email": current_user.email,
        "rol": current_user.rol,
        "estado": current_user.estado
    }

