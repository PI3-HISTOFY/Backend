# app/services/ocr_postprocess.py
import re, unicodedata
try:
    from language_tool_python import LanguageTool
except Exception:
    LanguageTool = None

try:
    from symspellpy import SymSpell, Verbosity
except Exception:
    SymSpell, Verbosity = None, None

# tool = LanguageTool('es') if LanguageTool else None
sym = SymSpell(max_dictionary_edit_distance=2) if SymSpell else None
# if sym: sym.load_dictionary("frecuencias_es.txt", term_index=0, count_index=1)

CIE10 = re.compile(r'\b[A-Z]\d{2}[A-Z0-9]?\b')
DOCID = re.compile(r'\b(TI|CC|CE)\d+\b', re.I)
FECHA = re.compile(r'\b\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2}\b')
HORA  = re.compile(r'\b\d{1,2}:\d{2}(:\d{2})?\b')

def _normalize(s:str)->str:
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("ﬁ","fi").replace("ﬂ","fl").replace("—","-").replace("–","-")
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r' *\n *', '\n', s)
    return s.strip()

def _mask(text:str):
    masks = []
    def do(pat, tag):
        nonlocal text
        def repl(m):
            idx=len(masks); token=f"__{tag}{idx}__"
            masks.append((token, m.group(0)))
            return token
        text = pat.sub(repl, text)
    for pat,tag in [(CIE10,"CIE10"),(DOCID,"DOC"),(FECHA,"DATE"),(HORA,"TIME")]:
        do(pat,tag)
    return text, masks

def _unmask(text:str, masks):
    for token, orig in masks:
        text = text.replace(token, orig)
    return text

def _lt_correct(s: str) -> str:
    # if tool: return tool.correct(s)
    return s

def _symspell_fallback(s:str)->str:
    if not sym: return s
    from symspellpy import Verbosity as V
    toks = re.findall(r'\w+|[^\w\s]', s, re.UNICODE)
    out=[]
    for t in toks:
        if not re.match(r'\w+', t): out.append(t); continue
        sug = sym.lookup(t.lower(), V.TOP, max_edit_distance=2)
        if sug and sug[0].distance <= 2:
            cand = sug[0].term
            if t.istitle(): cand=cand.title()
            if t.isupper(): cand=cand.upper()
            out.append(cand)
        else:
            out.append(t)
    return ''.join(out)

def clean_text_generic(ocr_text:str)->str:
    s = _normalize(ocr_text)
    s, masks = _mask(s)
    s = _lt_correct(s)
    s = _symspell_fallback(s)
    s = _unmask(s, masks)
    return s
