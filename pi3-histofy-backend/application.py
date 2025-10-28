import os
from pathlib import Path
from dotenv import load_dotenv

# Carga las variables antes de que nada más se importe
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)


#load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")
print("ENCRYPTION_KEY =", os.getenv("ENCRYPTION_KEY"))

from fastapi import FastAPI
from app.routes import router as api_router
from app.controllers.history_controller import test_encryption

app = FastAPI(
    title="Histofy Backend",
    version="1.0.0"
)

# Test encriptación al iniciar
try:
    test_encryption()
except Exception as e:
    print(f"Advertencia: Test de encriptación falló: {e}")

app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "API Histofy OK 🚀"}
