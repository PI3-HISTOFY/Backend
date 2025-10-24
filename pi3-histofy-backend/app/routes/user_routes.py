from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.user_schemas import UserCreate, UserResponse, UserResponseCreate
from app.controllers import user_controller
from app.services.auth import get_current_user
from app.models.user_model import User

router = APIRouter(prefix="/user", tags=["Users"])

@router.post("/register", response_model=UserResponseCreate)
def register(user: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return user_controller.create_user(db, current_user, user)
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/all", response_model=list[UserResponse])
def get_all_users_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return user_controller.get_all_users(db, current_user)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/me", response_model=UserResponse)
def get_my_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return user_controller.get_current_user(db, current_user)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/countmedicos")
def get_cantidad_medicos_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return user_controller.get_cantidad_medicos(db, current_user)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get("/accesos")
def get_all_login_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener todos los logs de inicio de sesión (solo admin)"""
    if current_user.rol != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el administrador puede consultar los logs")

    return user_controller.get_all_login_logs(db)


@router.get("/allLogs")
def get_all_logs_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if  current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="No autorizado para ver todos los logs")
    
    return user_controller.get_all_logs(db)

@router.get("/buscar", response_model=list[UserResponse])
def search_doctors(
    q: str = Query(..., min_length=2, description="Texto a buscar (nombre, apellido o correo)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo el administrador puede buscar doctores")

    resultados = db.query(User).filter(
        User.rol != "Admin",
        or_(
            User.nombre.ilike(f"%{q}%"),
            User.apellido.ilike(f"%{q}%"),
            User.email.ilike(f"%{q}%")
        )
    ).all()

    if not resultados:
        raise HTTPException(status_code=404, detail="No se encontraron doctores con ese criterio")

    return resultados


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id_route(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return user_controller.get_user_by_id(db, current_user, user_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/state/{user_id}", response_model=UserResponse)
def disable_user_route(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return user_controller.disable_user(db, current_user, user_id)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/logs/{user_id}")
def get_all_login_logs(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.rol != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo el administrador puede consultar los logs")

    return user_controller.get_user_access_logs(db, user_id)


@router.put("/update/{user_id}", response_model=UserResponse)
def update_user_route(
    user_id: int,
    user: user_controller.UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return user_controller.update_user(db, current_user, user_id, user)
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
