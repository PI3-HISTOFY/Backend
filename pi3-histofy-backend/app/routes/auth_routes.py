from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.services.auth import get_current_user
from app.database.database import get_db
from app.models.user_model import User, UserUpdatePassword
from app.controllers import auth_controller

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/login")
def login_route(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    request: Request = None
):
    return auth_controller.login(db, form_data, request)

@router.post("/changepass")
def login_route(
    nueva_contrasena: UserUpdatePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return auth_controller.change_password(db, current_user, current_user.idUsuario, nueva_contrasena.nueva_contrasena)



@router.get("/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    return {
        "message": f"Hola {current_user.nombre} {current_user.apellido}, bienvenido",
        "email": current_user.email,
        "rol": current_user.rol,
        "estado": current_user.estado
    }


@router.post("/logout")
def logout_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return auth_controller.logout(db, current_user)

