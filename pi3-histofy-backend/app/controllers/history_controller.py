from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.database.databaseNSQL import historias_collection
from app.models.user_model import User
from app.models.history_model import HistoriaMongoCreate
from app.services.auditoria import registrar_auditoria
from app.models.history_model import HistoriaMongoCreateV2 


def create_history(db: Session, history: HistoriaMongoCreate, current_user: User
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debe iniciar sesión para acceder a este recurso"
        )
    
    nueva_historia = {
        "idUsuario": current_user.idUsuario,
        "fecha": datetime.utcnow(),
        "paciente": {
            "cc": history.paciente.cc,
            "nombre": history.paciente.nombre,
            "apellido": history.paciente.apellido,
            "edad": history.paciente.edad,
            "sexo": history.paciente.sexo
        },
        "motivo_consulta": history.motivo_consulta,
        "antecedentes": history.antecedentes,
        "diagnostico": history.diagnostico,
        "tratamiento": history.tratamiento,
        "notas": history.notas,
        "nlp": history.nlp.dict() if history.nlp else {}
    }
    result = historias_collection.insert_one(nueva_historia)
    nueva_historia["_id"] = str(result.inserted_id)

    registrar_auditoria(db, current_user.idUsuario, "CREAR_HISTORIA", f"Historia creada para paciente CC {history.paciente.cc}")

    return nueva_historia


def get_my_histories(db: Session, current_user: User):
    """Obtiene las historias clínicas del usuario actual"""
    historias = list(historias_collection.find({"idUsuario": current_user.idUsuario}))
    for h in historias:
        h["_id"] = str(h["_id"])

    registrar_auditoria(
        db, current_user.idUsuario,
        "CONSULTAR_HISTORIAS",
        f"Usuario {current_user.idUsuario} consultó sus historias clínicas"
    )

    return historias


def get_all_histories(db: Session, current_user: User):
    """Obtiene todas las historias (solo admin)"""
    if current_user.rol != "admin":
        raise PermissionError("Solo el administrador puede ver todas las historias")

    historias = list(historias_collection.find())
    for h in historias:
        h["_id"] = str(h["_id"])

    registrar_auditoria(
        db, current_user.idUsuario,
        "CONSULTAR_HISTORIAS",
        "El administrador consultó todas las historias clínicas"
    )

    return historias

def get_cant_histories(db: Session, current_user: User):
    """Obtiene todas las historias (solo admin)"""
    if current_user.rol != "admin":
        raise PermissionError("Solo el administrador puede ver todas las historias")

    historias = historias_collection.count_documents({})

    return historias


def get_histories_by_patient(db: Session, current_user: User, cc: str):
    """Obtiene todas las historias clínicas de un paciente por CC"""
    historias = list(historias_collection.find({"paciente.cc": cc}))
    for h in historias:
        h["_id"] = str(h["_id"])

    registrar_auditoria(
        db, current_user.idUsuario,
        "CONSULTAR_HISTORIAS_PACIENTE",
        f"Consultó historias del paciente con CC {cc}"
    )

    return historias

def get_histories_by_patient_Name(db: Session, current_user: User, nombre: str):
    """Obtiene todas las historias clínicas de un paciente por nombre"""
    historias = list(historias_collection.find({"paciente.nombre": nombre}))
    historias += list(historias_collection.find({"paciente.apellido": nombre}))
    for h in historias:
        h["_id"] = str(h["_id"])

    registrar_auditoria(
        db, current_user.idUsuario,
        "CONSULTAR_HISTORIAS_PACIENTE",
        f"Consultó historias del paciente por {nombre}"
    )

    return historias

def _solo_digitos(cc: str | None) -> str | None:
    if not cc:
        return None
    return "".join(ch for ch in cc if ch.isdigit())


def create_history_v2(
    db: Session,
    history: HistoriaMongoCreateV2,
    current_user: User
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debe iniciar sesión para acceder a este recurso"
        )

    # Normalizaciones mínimas
    paciente = history.paciente.dict() if history.paciente else {}
    paciente["cc"] = _solo_digitos(paciente.get("cc"))

    doc = {
        "idUsuario": current_user.idUsuario,
        # si viene fecha, úsala; si no, puedes dejarla en None o setear ahora
        "fecha": history.fecha if history.fecha else None,
        "paciente": paciente,
        "motivo_consulta": history.motivo_consulta,
        "antecedentes": history.antecedentes,
        "examen": history.examen,
        "diagnostico": history.diagnostico,
        "tratamiento": history.tratamiento,
        "tipo_atencion": history.tipo_atencion,
        "especialidad": history.especialidad,
        "nivel_atencion": history.nivel_atencion,
        "nlp": history.nlp.dict() if history.nlp else {}
    }

    res = historias_collection.insert_one(doc)
    doc["_id"] = str(res.inserted_id)

    registrar_auditoria(
        db,
        current_user.idUsuario,
        "CREAR_HISTORIA",
        f"Historia creada (v2) para paciente CC {paciente.get('cc')}"
    )

    return doc