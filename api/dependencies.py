# api/dependencies.py

import logging
import psycopg2
from pymongo import MongoClient
from elasticsearch import Elasticsearch

from config import (
    MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PASSWORD,
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB,
    POSTGRES_USER, POSTGRES_PASSWORD,
    ELASTIC_HOST, ELASTIC_PORT,
)
from ml.search import SearchEngine

logging.basicConfig(
    level  = logging.INFO,
    format = "%(asctime)s — %(levelname)s — %(message)s"
)

# Singleton — initialisé une seule fois
_search_engine: SearchEngine = None


def get_search_engine() -> SearchEngine:
    """Retourne le SearchEngine TF-IDF — initialisé au premier appel."""
    global _search_engine
    if _search_engine is None:
        logging.info("Initialisation du SearchEngine TF-IDF...")
        _search_engine = SearchEngine()
        _search_engine.initialiser()
        logging.info("SearchEngine prêt.")
    return _search_engine


def get_mongo():
    """Connexion MongoDB."""
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
    """Connexion Elasticsearch."""
    client = Elasticsearch(
        f"http://{ELASTIC_HOST}:{ELASTIC_PORT}",
        request_timeout  = 30,
        retry_on_timeout = True,
        max_retries      = 3,
    )
    try:
        yield client
    finally:
        client.close()


def get_postgresql():
    """Connexion PostgreSQL."""
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
