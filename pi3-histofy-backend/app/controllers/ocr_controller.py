from fastapi import UploadFile, HTTPException
from app.services.ocr_local import procesar_imagen_bytes
from app.services.ocr_postprocess import clean_text_generic
from app.services.deepseek_client import extract_json_from_ocr

async def procesar_ocr_controller(file: UploadFile) -> dict:
    try:
        file_bytes = await file.read()
        texto = procesar_imagen_bytes(file_bytes)
        texto_limpio = clean_text_generic(texto)
        json_final = extract_json_from_ocr(texto_limpio)
        return {
            "mensaje": "✅ OCR procesado correctamente",
            "json_final": json_final
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando OCR: {str(e)}")
