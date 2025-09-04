from fastapi import APIRouter
from .user_routes import router as user_router
from .history_routes import router as history_router
from .auth_routes import router as auth_router
from .ocr_routes import router as ocr_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(user_router)
router.include_router(history_router)
router.include_router(ocr_router)



__all__ = ["router"]
