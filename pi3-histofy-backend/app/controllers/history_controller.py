from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user_model import User
from app.models.history_model import HistoriaMongoCreate, HistoriaMongoResponse
from app.services.auditoria import registrar_auditoria
from app.database.databaseNSQL import save_clinical_data, get_clinical_data, historias_collection
from app.services.encryption_service import EncryptionService

encryption_service = EncryptionService()

def test_encryption():
    """Prueba el servicio de encriptación"""
    test_data = "Dato de prueba para encriptación"
    encrypted = encryption_service.encrypt(test_data)
    decrypted = encryption_service.decrypt(encrypted)
    assert test_data == decrypted, "Error en encriptación/desencriptación"
    print("Test de encriptación exitoso")
    return True

def create_history(db: Session, history: HistoriaMongoCreate, current_user: User):
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

    # Encriptar datos sensibles antes de guardar
    history.encrypt_sensitive_data()
    inserted_id = save_clinical_data(historias_collection, nueva_historia)
    nueva_historia["_id"] = inserted_id

    registrar_auditoria(
        db, 
        current_user.idUsuario, 
        "CREAR_HISTORIA", 
        f"Historia creada para paciente CC {history.paciente.cc}"
    )

    return nueva_historia


def get_my_histories(db: Session, current_user: User):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado"
        )
    
    historias = get_clinical_data(historias_collection, {"idUsuario": current_user.idUsuario})
    
    registrar_auditoria(
        db,
        current_user.idUsuario,
        "CONSULTAR_HISTORIAS",
        "Usuario consultó sus historias clínicas"
    )

    return historias if isinstance(historias, list) else [historias] if historias else []


def get_all_histories(db: Session, current_user: User):
    historias = get_clinical_data(historias_collection, {})
    
    registrar_auditoria(
        db,
        current_user.idUsuario,
        "CONSULTAR_TODAS",
        "Usuario consultó todas las historias"
    )
    
    return historias if isinstance(historias, list) else [historias] if historias else []

def get_cant_histories(db: Session, current_user: User):
    historias = get_clinical_data(historias_collection, {"idUsuario": current_user.idUsuario})
    count = len(historias) if isinstance(historias, list) else 1 if historias else 0
    return {"count": count}

def get_histories_by_patient(db: Session, current_user: User, cc: str):
    historias = get_clinical_data(historias_collection, {"paciente.cc": cc})
    
    registrar_auditoria(
        db,
        current_user.idUsuario,
        "CONSULTAR_HISTORIAS_PACIENTE",
        f"Consulta historias del paciente CC {cc}"
    )
    
    return historias if isinstance(historias, list) else [historias] if historias else []

def get_histories_by_patient_Name(db: Session, current_user: User, nombre: str):
    historias = get_clinical_data(historias_collection, {
        "paciente.nombre": {"$regex": nombre, "$options": "i"}
    })
    
    registrar_auditoria(
        db,
        current_user.idUsuario,
        "CONSULTAR_HISTORIAS_NOMBRE",
        f"Consulta historias por nombre {nombre}"
    )
    
    return historias if isinstance(historias, list) else [historias] if historias else []

def _solo_digitos(cc: str | None) -> str | None:
    if not cc:
        return None
    return ''.join(c for c in cc if c.isdigit())