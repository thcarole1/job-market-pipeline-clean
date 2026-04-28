# api/dependencies.py
"""
Injection de dépendances FastAPI.
Chaque fonction est appelée automatiquement par FastAPI
à chaque requête — la connexion est ouverte et fermée proprement.
"""

from pymongo import MongoClient
from elasticsearch import Elasticsearch
import psycopg2
from config import (
    MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PASSWORD,
    ELASTIC_HOST, ELASTIC_PORT,
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB,
    POSTGRES_USER, POSTGRES_PASSWORD,
)


def get_mongo():
    """Retourne la base MongoDB job_market."""
    client = MongoClient(
        host     = MONGO_HOST,
        port     = MONGO_PORT,
        username = MONGO_USERNAME,
        password = MONGO_PASSWORD,
    )
    try:
        yield client["job_market"]
    finally:
        client.close()


def get_elasticsearch():
    """Retourne le client Elasticsearch."""
    client = Elasticsearch(
        f"http://{ELASTIC_HOST}:{ELASTIC_PORT}",
        request_timeout=30,
    )
    try:
        yield client
    finally:
        client.close()


def get_postgresql():
    """Retourne une connexion PostgreSQL."""
    conn = psycopg2.connect(
        host     = POSTGRES_HOST,
        port     = POSTGRES_PORT,
        dbname   = POSTGRES_DB,
        user     = POSTGRES_USER,
        password = POSTGRES_PASSWORD,
    )
    try:
        yield conn
    finally:
        conn.close()
