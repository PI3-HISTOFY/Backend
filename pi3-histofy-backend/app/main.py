from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import shutil
import os
import ocr2
from pipeline_postocr import clean_text_generic

app = FastAPI(title="Histofy Backend", version="1.0.0")

@app.get("/")
def root():
    return {"message": "API Histofy funcionando 🚀"}

@app.post("/procesar_ocr")
async def procesar_ocr(file: UploadFile = File(...)):
    """
    Recibe una imagen del frontend, la guarda temporalmente,
    llama a la función del módulo OCR y devuelve el texto.
    """
    try:
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Llamar a la función de tu script OCR y obtener el resultado
        texto, archivo_word = ocr2.procesar_imagen(temp_path)

        texto_limpio = clean_text_generic(texto)

        # Eliminar el archivo temporal
        os.remove(temp_path)

        return JSONResponse(content={
            "mensaje": "✅ OCR procesado correctamente",
            "textobase": texto,
            "textolimpio": texto_limpio,
            "archivo_word": archivo_word
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando imagen: {str(e)}")

