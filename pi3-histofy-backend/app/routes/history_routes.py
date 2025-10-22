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

    return history_controller.get_my_histories(db, current_user)

@router.get("/counthistory")
def get_cantidad_historias_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return history_controller.get_cant_histories(db, current_user)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


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

    return history_controller.get_all_histories(db, current_user)



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

    return history_controller.get_histories_by_patient(db, current_user, cc)


# historias de un paciente por nombre
@router.get("/patient/{name}")
def get_histories_by_patient(
    nombre: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debe iniciar sesión para acceder a este recurso"
        )

    return history_controller.get_histories_by_patient_Name(db, current_user, nombre)



