import certifi
from pymongo import MongoClient
from app.services.encryption_service import EncryptionService

encryption_service = EncryptionService()

def save_clinical_data(collection, data: dict):
    # Encriptar solo los campos sensibles
    sensitive_fields = [
        "motivo_consulta",
        "antecedentes",
        "examen",
        "diagnostico",
        "tratamiento",
        "notas"
    ]

    for field in sensitive_fields:
        if field in data and data[field]:
            data[field] = encryption_service.encrypt(data[field])

    result = collection.insert_one(data)
    return str(result.inserted_id)

def get_clinical_data(collection, query: dict):
    result = collection.find_one(query)
    if result:
        sensitive_fields = [
            "motivo_consulta",
            "antecedentes",
            "diagnostico",
            "tratamiento"
        ]
        for field in sensitive_fields:
            if field in result and result[field]:
                result[field] = encryption_service.decrypt(result[field])
    return result


MONGO_USER = "Histofy"   
MONGO_PASSWORD = "HistofyPass"
MONGO_CLUSTER = "cluster0.xxxxx.mongodb.net"
MONGO_DB = "Histofybd"

# URI de conexión
MONGO_URI = f"mongodb+srv://Histofy:HistofyPass@histofy.vspggto.mongodb.net/Histofy?retryWrites=true&w=majority&appName=Histofy/Histofybd"


from pymongo import MongoClient

client = MongoClient(MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where())
try:
    client.admin.command("ping")
    print("Conexion exitosa a MongoDB")
except Exception as e:
    print("Error de conexion:", e)

client = MongoClient(MONGO_URI)



mongo_db = client[MONGO_DB]

historias_collection = mongo_db["historias_clinicas"]
