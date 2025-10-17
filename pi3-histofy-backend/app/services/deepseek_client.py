# app/services/deepseek_client.py
import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

PROMPT_BASE = """Eres un asistente experto en documentación clínica. 
Objetivo: A partir del TEXTO OCR, devuelve EXCLUSIVAMENTE un JSON válido con el siguiente esquema y nombres de campo. 
No incluyas ningún comentario ni texto adicional fuera del JSON.

REGLAS DE EXTRACCIÓN Y NORMALIZACIÓN
- Corrige errores típicos de OCR en español (p. ej., “estado dvil/elvi/cilv” → “estado civil”) SOLO cuando sea necesario para que el texto tenga sentido.
- NO inventes datos: si un campo no aparece con claridad, devuelve null.
- No alteres códigos/IDs/fechas/horas salvo para normalizar formato.
- fecha: normaliza en ISO 8601 con zona (p. ej., 2025-01-22T07:27:00-05:00); si no hay, null.
- paciente.cc: si el documento trae “CC/TI/CE + número”, devuelve SOLO el número (solo dígitos); si no hay, null.
- paciente.nombre_completo: un único string con el nombre completo del paciente; si no hay, null.
- sexo: “M”, “F”, “Otro” o null.
- edad: número (años) o null.
- tipo_atencion: “Consulta”, “Urgencias”, “Hospitalización” u otro término razonable si se deduce; si no, null.
- especialidad: inferir si es posible (cardiología, oftalmología, neurología, neumología, endocrinología, medicina general, etc.). Si no hay evidencia, null.
- nivel_atencion: “I”, “II” o “III” si se deduce; si no, null.
- nlp.categorias: lista de etiquetas clínicas (p. ej., “diabetes”, “oftalmología”, “cardiología”). 
- nlp.keywords: lista breve de palabras clave clínicas relevantes.

REGLAS ADICIONALES (prioridad alta):
- Fecha clínica: si hay “Fecha ingreso” o “Fecha de consulta”, úsala para "fecha". Ignora fechas del formulario (ej. “Fecha” junto a “Versión”). Formato ISO 8601 con zona.
- Reconstrucción de espacios: corrige uniones por OCR en frases comunes en español (ej., “VENGOPORCONTROL” → “Vengo por control”) sin modificar números ni códigos.}
- Diagnóstico: si hay sección explícita o términos diagnósticos, rellena "diagnostico" con una frase corta (p. ej., "Endotropía derecha, glaucoma ojo izquierdo"). Si no hay, infiere a partir de antecedentes/examen y marca como diagnóstico probable (sin inventar patologías no respaldadas).
- Formato de texto: usa “Sentence case” (primera letra en mayúscula, resto normal), separa hallazgos con punto y coma, y evita términos concatenados (ej., "vengoporcontrol" → "Vengo por control").
- Tratamiento: incluye solo manejo ACTUAL (medicamentos/indicaciones vigentes). Cirugías previas van en antecedentes. Si no hay manejo actual, devuelve null.



SALIDA OBLIGATORIA (SOLO JSON):
{
  "fecha": string|null,
  "paciente": {
    "cc": string|null,
    "nombre_completo": string|null,
    "sexo": "M"|"F"|"Otro"|null,
    "edad": number|null
  },
  "motivo_consulta": string|null,
  "antecedentes": string|null,
  "examen": string|null,
  "diagnostico": string|null,
  "tratamiento": string|null,
  "tipo_atencion": string|null,
  "especialidad": string|null,
  "nivel_atencion": "I"|"II"|"III"|null,
  "nlp": {
    "categorias": string[]|null,
    "keywords": string[]|null
  }
}

TEXTO OCR:
<<<OCR_INICIO>>>
{{OCR_TEXT}}
<<<OCR_FIN>>>
"""


_client = None
def _client_instance():
    global _client
    if _client is None:
        # Asegúrate de cargar .env por si alguien importa este módulo directamente
        load_dotenv()  # buscará .env en cwd y padres
        api_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com").strip()
        api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("Falta DEEPSEEK_API_KEY en .env")
        _client = OpenAI(api_key=api_key, base_url=api_url)
    return _client

def _extract_json_block(text: str) -> dict:
    """
    Limpia fences ```json ... ``` y, si hace falta, intenta extraer el 1er objeto JSON válido.
    """
    cleaned = text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except Exception:
        # fallback: tomar el primer bloque { ... } por regex básico (no perfecto, pero útil)
        m = re.search(r'\{[\s\S]*\}', cleaned)
        if not m:
            raise ValueError("La respuesta del modelo no contiene JSON")
        return json.loads(m.group(0))

def extract_json_from_ocr(ocr_text: str) -> dict:
    prompt = PROMPT_BASE.replace("{{OCR_TEXT}}", ocr_text)
    client = _client_instance()
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role":"system","content":"Eres un asistente experto en análisis de texto."},
            {"role":"user","content": prompt}
        ],
        stream=False,
        temperature=0.2
    )
    content = resp.choices[0].message.content
    return _extract_json_block(content)
