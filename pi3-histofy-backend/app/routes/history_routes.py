from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.user_model import User
from app.models.history_model import HistoriaMongoCreate, HistoriaMongoResponse
from app.database.databaseNSQL import historias_collection
from app.controllers import history_controller
from app.services.auth import get_current_user
from app.services.auditoria import registrar_auditoria
from app.models.history_model import (
    HistoriaMongoCreateV2,
    HistoriaMongoResponseV2
)


router = APIRouter(prefix="/history", tags=["History"])

@router.post("/registerH", response_model=HistoriaMongoResponseV2)
def register_history_v2(
    history: HistoriaMongoCreateV2,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debe iniciar sesión"
        )

    return history_controller.create_history_v2(db, history, current_user)



# historias del usuario actual
@router.get("/mine")
def get_my_histories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debe iniciar sesión para acceder a este recurso"
        )

    historias = list(historias_collection.find({"idUsuario": current_user.idUsuario}))
    for h in historias:
        h["_id"] = str(h["_id"])

    return historias


# todas las historias (solo admin)??
@router.get("/all")
def get_all_histories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debe iniciar sesión para acceder a este recurso"
        )

    historias = list(historias_collection.find())
    for h in historias:
        h["_id"] = str(h["_id"])

    return historias


# historias de un paciente por CC
@router.get("/patient/{cc}")
def get_histories_by_patient(
    cc: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debe iniciar sesión para acceder a este recurso"
        )

    historias = list(historias_collection.find({"paciente.cc": cc}))
    for h in historias:
        h["_id"] = str(h["_id"])

    return historias