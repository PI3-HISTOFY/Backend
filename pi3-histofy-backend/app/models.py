from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)  # Se agregó longitud
    email = Column(String(255), unique=True, index=True)     # Se agregó longitud
    hashed_password = Column(String(255))                    # Se agregó longitud
