from app import models

def registrar_auditoria(db, idUsuario: int, accion: str, descripcion: str = None):
    log = models.Auditoria(
        idUsuario=idUsuario,
        accion=accion,
        recurso=descripcion
    )
    db.add(log)
    db.commit()