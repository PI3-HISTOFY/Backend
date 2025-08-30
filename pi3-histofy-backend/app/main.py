from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from datetime import datetime
from app import auth, ocr, history, user

app = FastAPI(title="Histofy Backend", version="1.0.0")

# Rutas de autenticación
app.include_router(auth.router)
app.include_router(ocr.router)
app.include_router(user.router)
app.include_router(history.router)


@app.get("/")
def root():
    return {"message": "API Histofy ok"}

