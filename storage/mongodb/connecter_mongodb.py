from pymongo import MongoClient
import os

# from dotenv import load_dotenv
# load_dotenv()

def connecter_mongodb():
    client = MongoClient(
        host     = os.getenv("MONGO_HOST", "127.0.0.1"),
        port     = int(os.getenv("MONGO_PORT", 27017)),
        username = os.getenv("MONGO_USERNAME"),
        password = os.getenv("MONGO_PASSWORD"),
    )
    return client
