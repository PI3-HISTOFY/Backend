from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 🔹 Cambia esta URL según tu base de datos
# Formato PostgreSQL: "postgresql://usuario:contraseña@localhost/nombre_bd"
DATABASE_URL = "sqlite:///./histofy.db"  # Temporal con SQLite para pruebas

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependencia para usar en endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
