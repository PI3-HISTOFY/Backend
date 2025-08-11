from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app import auth, security, ocr


app = FastAPI(title="Histofy Backend", version="1.0.0")

# Rutas de autenticación
app.include_router(auth.router)
app.include_router(ocr.router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

@app.get("/")
def root():
    return {"message": "API Histofy funcionando 🚀"}

@app.get("/protected")
def protected_route(current_user: str = Depends(get_current_user)):
    return {"message": f"Hola {current_user}, esta es una ruta protegida"}
