from pymongo import MongoClient
import os


MONGO_USER = "Histofy"   
MONGO_PASSWORD = "HistofyPass"
MONGO_CLUSTER = "cluster0.xxxxx.mongodb.net"
MONGO_DB = "Histofybd"

# URI de conexión
MONGO_URI = f"mongodb+srv://Histofy:HistofyPass@histofy.vspggto.mongodb.net/Histofy?retryWrites=true&w=majority&appName=Histofy/Histofybd"

client = MongoClient(MONGO_URI)
try:
    client.admin.command("ping")
    print("Conexion exitosa a MongoDB")
except Exception as e:
    print("Error de conexion:", e)

client = MongoClient(MONGO_URI)



mongo_db = client[MONGO_DB]

historias_collection = mongo_db["historias_clinicas"]
