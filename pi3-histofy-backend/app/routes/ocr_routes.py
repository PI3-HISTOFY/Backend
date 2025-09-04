
from fastapi import APIRouter, UploadFile, File

from app.controllers.ocr_controller import procesar_ocr_controller

router = APIRouter(prefix="/ocr", tags=["OCR"])

@router.post("/procesar_ocr")
async def procesar_ocr(file: UploadFile = File(...)):
    """
    Sube una imagen y procesa OCR → DeepSeek → devuelve JSON clínico.
    """
    return await procesar_ocr_controller(file)
