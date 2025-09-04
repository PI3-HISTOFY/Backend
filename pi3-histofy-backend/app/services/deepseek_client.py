# app/services/deepseek_client.py
import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

PROMPT_BASE = """Eres un asistente experto en documentación clínica. Tarea: Lee el texto obtenido por OCR y devuelve EXCLUSIVAMENTE un JSON con los campos solicitados. Corrige errores típicos de OCR en español (p. ej., “estado dvil/elvi/cilv” → “estado civil”), pero NO inventes datos inexistentes. Si un campo no aparece, devuelve null.

REGLAS GENERALES
- Corrige solo palabras comunes del español para que las frases tengan sentido; no alteres números, identificadores, códigos (p. ej. TI/CC/CE + dígitos), CIE-10, teléfonos, horas o fechas. Si una hora aparece como 0727 o 07.27, normaliza a “07:27”.
- Mantén acentos y mayúsculas/minúsculas correctas en español.
- Quita duplicados evidentes (líneas repetidas iguales o casi iguales).
- Si hay múltiples candidatos para el mismo campo, elige el más claro/coherente con el contexto clínico.

SINÓNIMOS/VARIANTES (detecta cualquiera de estos encabezados o expresiones)
- Paciente/Nombre/Usuario/Señor(a)/Sra./Sr. → nombre del paciente
- Diagnóstico/Dx/Impresión diagnóstica/Impresión Dx → diagnóstico
- Motivo/Motivo de consulta/Causa/Razón de consulta → motivo
- Examen físico/EF/Exploración física/Ex. físico → examen
- Antecedentes/Historia/Antecedentes personales/familiares → antecedentes
- Especialidad/Servicio/Área (p. ej., Medicina general) → especialidad
- Tipo de atención/Modalidad (p. ej., Consulta presencial, Teleconsulta, Urgencias) → tipo_atencion
- Nivel de atención/Nivel (I, II, III, IV o Primario/Secundario/Terciario) → nivel_atencion
- ID/Documento/Identificación/Documento: TI/CC/CE + número → id

SALIDA (OBLIGATORIA, SOLO EL OBJETO JSON RESULTANTE, SIN ENCABEZADO, SIN TEXTO ADICIONAL NI COMENTARIOS)
{
  "id": string|null,
  "paciente_nombre": string|null,
  "paciente_apellido": string|null,
  "edad": number|null,
  "sexo": "F"|"M"|"Otro"|null,
  "motivo": string|null,
  "antecedentes": string|null,
  "examen": string|null,
  "diagnostico": string|null,
  "plan": string|null,
  "especialidad": string|null,
  "nivel_atencion": string|null,
  "tipo_atencion": string|null
}

TEXTO OCR:
<<<OCR_INICIO>>>
{{OCR_TEXT}}
<<<OCR_FIN>>>"""


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
