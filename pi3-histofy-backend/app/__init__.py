# Este archivo se utiliza para inicializar el paquete `app`. Puede contener configuraciones iniciales o importaciones de otros módulos.

from .main import app
from .models import Base
from .database import engine

# Aquí puedes incluir configuraciones iniciales si es necesario
# Por ejemplo, crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)