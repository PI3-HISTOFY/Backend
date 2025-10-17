# app/services/chatbot_service.py
import json, pickle, numpy as np, re, threading
import nltk
from nltk.stem import PorterStemmer
from tensorflow.keras.models import load_model
from typing import Any, Dict, List, Optional, Tuple

from app.database.databaseNSQL import historias_collection  # usa tu conexión existente

# ─────────── CARGA PEREZOSA/SINGLETON DEL MODELO ───────────
_MODEL_LOCK = threading.Lock()
_LOADED = False
_words = None
_classes = None
_model = None
_intents = None

def _ensure_loaded():
    global _LOADED, _words, _classes, _model, _intents
    if _LOADED:
        return
    with _MODEL_LOCK:
        if _LOADED:
            return
        nltk.download('punkt', quiet=True)
        # Rutas dentro de app/chatbot_data
        base = "app/chatbot_data"
        with open(f"{base}/intents_spanish.json", "r", encoding="utf-8") as f:
            _intents = json.load(f)
        _words = pickle.load(open(f"{base}/words.pkl", "rb"))
        _classes = pickle.load(open(f"{base}/classes.pkl", "rb"))
        _model = load_model(f"{base}/chatbot_model.h5")
        _LOADED = True

# ─────────── NLP utilidades ───────────
stemmer = PorterStemmer()

def clean_text(sentence: str) -> List[str]:
    tokens = nltk.word_tokenize(sentence.lower())
    tokens = [stemmer.stem(w) for w in tokens]
    return tokens

def bag_of_words(sentence: str, words: List[str]) -> np.ndarray:
    sentence_words = clean_text(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence: str, threshold: float = 0.2) -> List[Dict[str, str]]:
    _ensure_loaded()
    bow = bag_of_words(sentence, _words)
    res = _model.predict(np.array([bow]), verbose=0)[0]
    results = [(i, r) for i, r in enumerate(res) if r > threshold]
    results.sort(key=lambda x: x[1], reverse=True)
    return [{"intent": _classes[i], "probability": str(r)} for i, r in results] or [{"intent": "fallback", "probability": "0"}]

# ─────────── Diccionarios de sinónimos ───────────
CATEGORY_SYNONYMS = {
    "diabetes": {"diabetes", "diabético", "diabéticos", "dm", "dm2", "e11"},
    "hipertension": {"hipertensión", "hipertension", "hta", "i10"},
    "asma": {"asma"},
    "glaucoma": {"glaucoma"},
    "retina": {"retina", "retinopatía", "retinopatia"},
    "endocrinologia": {"endocrinología", "endocrinologia"},
    "cardiologia": {"cardiología", "cardiologia"}
}
ID_FIELDS = ["paciente.cc"]

# ─────────── Extracción de entidades ───────────
def extract_entities(message: str) -> Dict[str, Any]:
    q = message.strip()
    low = q.lower()

    # Documento → solo dígitos
    m_id = re.search(r"(?:c[eé]dula|documento|id|cc)?\D*([0-9][0-9\.\s-]{5,}[0-9])", q, flags=re.I)
    cedula = re.sub(r"\D", "", m_id.group(1)) if m_id else None

    # Nombre → después de “paciente …” o “historia … de …”
    m_name = re.search(
        r"(?:paciente|historia(?:s)?(?:\s+cl[ií]nica[s]?)?\s+de)\s+([a-záéíóúñ ]{3,})[^\w]*$",
        q, flags=re.I
    )
    nombre = m_name.group(1).strip() if m_name and not any(ch.isdigit() for ch in m_name.group(1)) else None

    # Categoría
    cat, matched = None, None
    for canonical, syns in CATEGORY_SYNONYMS.items():
        for term in syns | {canonical}:
            if re.search(rf"\b{re.escape(term)}\b", low):
                cat, matched = canonical, term
                break
        if cat: break
    if not cat:
        m_gen = re.search(r"pacientes?\s+con\s+([a-záéíóúñ0-9 %\.-]{3,})", low, flags=re.I)
        if m_gen:
            cat = m_gen.group(1).strip()
            matched = cat

    # Especialidad
    m_spec = re.search(r"(?:especialidad|por especialidad)\s+([a-záéíóúñ ]{3,})", low, flags=re.I)
    specialty = m_spec.group(1).strip() if m_spec else None
    if not specialty:
        m_spec2 = re.search(r"(?:historias|casos)\s+de\s+([a-záéíóúñ ]{3,})", low, flags=re.I)
        if m_spec2:
            specialty = m_spec2.group(1).strip()

    # Nivel (I/II/III o 1/2/3)
    level = None
    m_level = re.search(r"(?:nivel(?:\s+de\s+atenci[oó]n)?)[^\w]?(i{1,3}|[1-3])\b", low, flags=re.I)
    if m_level:
        g = m_level.group(1).upper()
        level = {"1": "I", "2": "II", "3": "III"}.get(g, g)

    # Límite
    limit = None
    m_lim = (re.search(r"(?:primeros|top|hasta)\s*(\d{1,4})", low, flags=re.I)
             or re.search(r"(?:l[ií]mite|limit)\s*[:=]?\s*(\d{1,4})", low, flags=re.I))
    if m_lim:
        try: limit = int(m_lim.group(1))
        except: limit = None

    return {
        "cedula": cedula,
        "nombre": nombre,
        "categoria": cat,
        "specialty": specialty,
        "level": level,
        "matched": matched,
        "limit": limit
    }

# ─────────── Query builder (Mongo) ───────────
def build_query(intent: str, ents: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if intent == "get_all":
        return {}

    if intent == "get_by_id" and ents.get("cedula"):
        ced = ents["cedula"]
        ors = [{f: ced} for f in ID_FIELDS]  # ["paciente.cc"]
        return {"$and": [{"$or": ors}]}

    if intent == "get_by_name" and ents.get("nombre"):
        name = ents["nombre"]
        # NUEVO: nombre_completo (esquema v2)
        return {"$and": [{"$or": [
            {"paciente.nombre_completo": {"$regex": name, "$options": "i"}}
        ]}]}

    if intent == "get_by_category" and ents.get("categoria"):
        cat = ents["categoria"].lower().strip()
        if cat in CATEGORY_SYNONYMS:
            values = list(CATEGORY_SYNONYMS[cat] | {cat})
            return {"$and": [{"$or": [
                {"nlp.categorias": {"$in": values}},
                {"analisis_nlu.categorias": {"$in": values}}  # compat legado
            ]}]}
        return {"$and": [{"$or": [
            {"nlp.categorias": {"$regex": cat, "$options": "i"}},
            {"analisis_nlu.categorias": {"$regex": cat, "$options": "i"}}
        ]}]}

    if intent == "get_by_specialty" and ents.get("specialty"):
        spec = ents["specialty"]
        return {"especialidad": {"$regex": spec, "$options": "i"}}

    if intent == "get_by_level" and ents.get("level"):
        lvl = ents["level"]  # "I"/"II"/"III"
        return {"nivel_atencion": {"$regex": f"^{re.escape(lvl)}$", "$options": "i"}}

    return None

# ─────────── Respuesta natural ───────────
def generate_answer(intent: str, ents: Dict[str, Any]) -> str:
    if intent == "get_all":
        return "Listaré todos los historiales disponibles (limitado)."
    if intent == "get_by_category" and ents.get("categoria"):
        return f"Buscaré historias con categoría '{ents['categoria']}'."
    if intent == "get_by_specialty" and ents.get("specialty"):
        return f"Buscaré historias por especialidad '{ents['specialty']}'."
    if intent == "get_by_level" and ents.get("level"):
        return f"Buscaré historias de nivel '{ents['level']}'."
    if intent == "get_by_id" and ents.get("cedula"):
        return f"Buscaré historias por cédula/documento {ents['cedula']}."
    if intent == "get_by_name" and ents.get("nombre"):
        return f"Buscaré historias del/la paciente '{ents['nombre']}'."
    return "Puedo buscar por: todas, por cédula/documento, por nombre, por categoría clínica, por especialidad o por nivel."

# ─────────── Orquestación ───────────
def respond(message: str) -> Dict[str, Any]:
    intents_rank = predict_class(message)
    top = intents_rank[0]["intent"]
    ents = extract_entities(message)
    query = build_query(top, ents)
    answer = generate_answer(top, ents)
    return {"top_intent": top, "intents_rank": intents_rank, "entities": ents, "query": query, "answer": answer}

def run_db_query(mongo_filter: dict | None, limit: int = 50) -> List[Dict[str, Any]]:
    query = mongo_filter if isinstance(mongo_filter, dict) else {}
    cur = historias_collection.find(query).limit(limit)
    out = []
    for d in cur:
        d = dict(d)
        d["_id"] = str(d["_id"])
        out.append(d)
    return out

def respond_and_query(message: str, limit: int = 50) -> Dict[str, Any]:
    out = respond(message)
    top, q = out["top_intent"], out["query"]
    lim = out["entities"].get("limit") or limit if isinstance(out.get("entities"), dict) else limit

    items: List[Dict[str, Any]] = []
    if top == "get_all":
        items = run_db_query({}, limit=lim)
    elif isinstance(q, dict) and q:
        items = run_db_query(q, limit=lim)
    else:
        out["answer"] += " (No identifiqué filtros, no consulté la base de datos.)"

    out["count"] = len(items)
    out["items"] = items
    if items:
        out["answer"] += f" Encontré {len(items)} resultado(s)."
    return out
