from fastapi import FastAPI
from app.routes import router as api_router

app = FastAPI(
    title="Histofy Backend",
    version="1.0.0"
)

# Incluir todas las rutas desde app/routes/__init__.py
app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "API Histofy OK 🚀"}
