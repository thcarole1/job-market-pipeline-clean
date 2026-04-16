# config.py
"""
Configuration centrale du projet.
Chargé une seule fois — importé par tous les modules qui ont besoin
de variables d'environnement.
"""

from pathlib import Path
from dotenv import load_dotenv
import os

# Chemin absolu vers la racine du projet
# RACINE = Path(__file__).parent
RACINE = Path(__file__).parent.resolve()

# Chemin absolu vers le .env
ENV_PATH = RACINE / ".env"

# Vérification explicite
if not ENV_PATH.exists():
    raise FileNotFoundError(
        f"Fichier .env introuvable : {ENV_PATH}\n"
        f"Vérifiez qu'il est bien à la racine du projet."
    )

# Chargement explicite avec chemin absolu
load_dotenv(dotenv_path=ENV_PATH, override=True)

# MongoDB
MONGO_HOST     = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT     = int(os.getenv("MONGO_PORT", 27017))
MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")

# PostgreSQL
POSTGRES_HOST     = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT     = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_DB       = os.getenv("POSTGRES_DB", "job_market")
POSTGRES_USER     = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")


# Elasticsearch
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "localhost")
ELASTIC_PORT = int(os.getenv("ELASTIC_PORT", 9200))
NOM_INDEX = "offres"
SCHEMA_PATH = RACINE / "storage/sql/schema.sql"
