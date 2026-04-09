# storage/sql/create_tables.py

import psycopg2
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Chemin vers le fichier schema.sql
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def connecter_postgresql():
    """Crée et retourne une connexion PostgreSQL."""
    return psycopg2.connect(
        host     = os.getenv("POSTGRES_HOST", "localhost"),
        port     = int(os.getenv("POSTGRES_PORT", 5432)),
        dbname   = os.getenv("POSTGRES_DB", "job_market"),
        user     = os.getenv("POSTGRES_USER"),
        password = os.getenv("POSTGRES_PASSWORD"),
    )


def creer_tables():
    """
    Lit le fichier schema.sql et exécute toutes les instructions.
    Utilise IF NOT EXISTS — safe à appeler plusieurs fois.
    """
    conn   = None
    cursor = None

    try:
        # Connexion
        conn   = connecter_postgresql()
        cursor = conn.cursor()

        # Lire le fichier SQL
        sql = SCHEMA_PATH.read_text(encoding="utf-8")

        # Exécuter toutes les instructions d'un coup
        cursor.execute(sql)

        # Valider les changements
        conn.commit()

        print("Tables creees avec succes :")
        print("  offres, competences, missions, avantages")
        print("  + tous les index")

    except Exception as e:
        print(f"Erreur lors de la creation des tables : {e}")
        if conn:
            conn.rollback()
        raise

    finally:
        # Toujours fermer proprement
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    creer_tables()
