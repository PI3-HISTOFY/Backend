FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Dependencias del sistema para OCR y OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-spa \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Requisitos Python
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Descargar recursos NLTK en build (sin heredoc)
RUN python -c "import nltk; nltk.download('punkt')"

# Copiar código de la app
COPY . /app

# Puerto expuesto
EXPOSE 8000

# Descargar recursos NLTK en build (punkt + punkt_tab)
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"


# Arranque FastAPI
CMD ["uvicorn", "application:app", "--host", "0.0.0.0", "--port", "8000"]
