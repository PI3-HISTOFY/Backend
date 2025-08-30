from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from app.databaseNSQL import historias_collection
from app import schemas, models, database
from app.auth import get_current_user
from app.auditoria import registrar_auditoria
from sqlalchemy.orm import Session

router = APIRouter(prefix="/history", tags=["History"])

# Crear historia clinica
@router.post("/registerH", response_model=schemas.HistoriaMongoResponse)
def create_history(
    history: schemas.HistoriaMongoCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debe iniciar sesión para acceder a este recurso"
        )
    
    nueva_historia = {
        "idUsuario": current_user.idUsuario,
        "fecha": datetime.utcnow(),
        "paciente": {
            "cc": history.paciente.cc,
            "nombre": history.paciente.nombre,
            "apellido": history.paciente.apellido,
            "edad": history.paciente.edad,
            "sexo": history.paciente.sexo
        },
        "texto": history.texto,
        "diagnostico": history.diagnostico,
        "tratamiento": history.tratamiento,
        "notas": history.notas,
        "nlp": history.nlp.dict() if history.nlp else {}
    }
    result = historias_collection.insert_one(nueva_historia)
    nueva_historia["_id"] = str(result.inserted_id)

    registrar_auditoria(db, current_user.idUsuario, "CREAR_HISTORIA", f"Historia creada para paciente CC {history.paciente.cc}")

    return nueva_historia

@router.get("/getAllId")
def get_my_histories(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debe iniciar sesión para acceder a este recurso"
        )
    
    historias = list(historias_collection.find({"idUsuario": current_user.idUsuario}))
    for h in historias:
        h["_id"] = str(h["_id"])

    registrar_auditoria(db, current_user.idUsuario, "CONSULTAR_HISTORIAS", f"Consultar historias registradas por el usuario {current_user.idUsuario}")

    return historias

# solo admin
@router.get("/getAll")
def get_all_histories(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debe iniciar sesión para acceder a este recurso"
        )
    
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo el administrador puede ver todas las historias")

    historias = list(historias_collection.find())
    for h in historias:
        h["_id"] = str(h["_id"])

    registrar_auditoria(db, current_user.idUsuario, "CONSULTAR_HISTORIAS", "Consulto todas las historias registradas")

    return historias


# por CC paaciente
@router.get("/getAllCc/{cc}")
def get_histories_by_patient(
    cc: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debe iniciar sesión para acceder a este recurso"
        )
    
    historias = list(historias_collection.find({"paciente.cc": cc}))
    for h in historias:
        h["_id"] = str(h["_id"])

    registrar_auditoria(db, current_user.idUsuario, f"CONSULTAR_HISTORIAS DE {historias.paciente.cc}", f"Consulto historias del paciente con CC {cc}")

    return historias

