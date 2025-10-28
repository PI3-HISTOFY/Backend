import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv
load_dotenv()

class EncryptionService:
    def __init__(self):
        # Cargar la clave de encriptación desde las variables de entorno
        key = os.getenv("ENCRYPTION_KEY")
        if not key:
            raise ValueError("ENCRYPTION_KEY no está configurada en las variables de entorno (.env).")
        try:
            # Fernet espera bytes; si key viene como str, se decodifica automáticamente
            if isinstance(key, str):
                key_bytes = key.encode()
            else:
                key_bytes = key
            # Validar key creando el objeto Fernet
            self.cipher = Fernet(key_bytes)
        except Exception as e:
            raise ValueError(f"Clave ENCRYPTION_KEY inválida: {e}")

    def encrypt(self, data: str) -> str:
        if data is None:
            return None
        if not isinstance(data, (str, bytes)):
            data = str(data)
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        if encrypted_data is None:
            return None
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception:
            # Si falla el desencriptado, devolvemos el valor original para no romper flujos
            return encrypted_data
