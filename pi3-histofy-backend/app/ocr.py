from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image, ImageEnhance
import pytesseract
from pdf2image import convert_from_bytes

router = APIRouter()

POPPLER_PATH = r'C:\Poppler\poppler-24.08.0\Library\bin'

def preprocess_image(img):
    img = img.convert('L')
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    img = img.point(lambda x: 0 if x < 140 else 255, '1')
    return img

@router.post("/ocr")
async def ocr(file: UploadFile = File(...)):
    filename = file.filename.lower()
    extracted_text = ""
    try:
        if filename.endswith('.pdf'):
            file_bytes = await file.read()
            images = convert_from_bytes(file_bytes, poppler_path=POPPLER_PATH)
            for page_num, img in enumerate(images):
                processed_img = preprocess_image(img)
                text = pytesseract.image_to_string(processed_img, lang='spa')
                extracted_text += f"\n--- Página {page_num + 1} ---\n{text}"
        else:
            img = Image.open(file.file)
            processed_img = preprocess_image(img)
            extracted_text = pytesseract.image_to_string(processed_img, lang='spa')
        return {"text": extracted_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))