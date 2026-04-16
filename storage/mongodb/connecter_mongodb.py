from pymongo import MongoClient
from config import MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PASSWORD

def connecter_mongodb():
    client = MongoClient(
        host     = MONGO_HOST,
        port     = MONGO_PORT,
        username = MONGO_USERNAME,
        password = MONGO_PASSWORD,
    )
    return client
