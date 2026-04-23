# scripts/reset_databases.py
"""
Reset général des bases de données du projet Job Market.

Usage :
    python -m reset_databases              # reset toutes les bases
    python -m reset_databases --mongodb    # reset MongoDB uniquement
    python -m reset_databases --postgresql # reset PostgreSQL uniquement
    python -m reset_databases --elastic    # reset Elasticsearch uniquement

ATTENTION : toutes les données sont supprimées définitivement.
Ce script est réservé au développement — jamais en production.
"""

import argparse
import logging
import sys
from pathlib import Path

from config import (
    MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PASSWORD,
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD,
    ELASTIC_HOST, ELASTIC_PORT,RACINE
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)


# ─────────────────────────────────────────────────────────────
# RESET MONGODB
# ─────────────────────────────────────────────────────────────

def reset_mongodb():
    """
    Supprime toutes les collections de la base job_market dans MongoDB.
    La base elle-même est conservée — seules les données sont effacées.
    """
    from pymongo import MongoClient

    print("\n=== Reset MongoDB ===")

    try:
        client = MongoClient(
            host     = MONGO_HOST,
            port     = MONGO_PORT,
            username = MONGO_USERNAME,
            password = MONGO_PASSWORD,
        )
        db = client["job_market"]

        # Lister les collections existantes
        collections = db.list_collection_names()

        if not collections:
            print("Aucune collection à supprimer.")
            return

        # Supprimer chaque collection
        for collection in collections:
            db[collection].drop()
            print(f"  Collection supprimée : {collection}")

        print(f"MongoDB reset — {len(collections)} collections supprimées.")

    except Exception as e:
        logging.error(f"Erreur reset MongoDB : {e}")
        raise

    finally:
        client.close()


# ─────────────────────────────────────────────────────────────
# RESET POSTGRESQL
# ─────────────────────────────────────────────────────────────

def reset_postgresql():
    """
    Supprime et recrée toutes les tables PostgreSQL.
    Utilise CASCADE pour gérer les dépendances entre tables.
    """
    import psycopg2

    print("\n=== Reset PostgreSQL ===")

    # Tables dans l'ordre de suppression
    # Les tables avec clés étrangères doivent être supprimées avant
    # les tables qu'elles référencent
    TABLES = [
        "ml_labels",
        "avantages",     # référence offres
        "missions",      # référence offres
        "competences",   # référence offres
        "offres",        # table principale
    ]

    conn   = None
    cursor = None

    try:
        conn   = psycopg2.connect(
            host     = POSTGRES_HOST,
            port     = POSTGRES_PORT,
            dbname   = POSTGRES_DB,
            user     = POSTGRES_USER,
            password = POSTGRES_PASSWORD,
        )
        cursor = conn.cursor()

        # Supprimer les tables dans le bon ordre
        for table in TABLES:
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
            print(f"  Table supprimée : {table}")

        conn.commit()
        print("Tables supprimées.")

        # Recréer les tables depuis le schema.sql
        schema_path = RACINE / "storage" / "sql" / "schema.sql"
        if not schema_path.exists():
            raise FileNotFoundError(f"schema.sql introuvable : {schema_path}")

        sql = schema_path.read_text(encoding="utf-8")
        cursor.execute(sql)
        conn.commit()
        print("Tables recréées depuis schema.sql.")
        print("PostgreSQL reset terminé.")

    except Exception as e:
        logging.error(f"Erreur reset PostgreSQL : {e}")
        if conn:
            conn.rollback()
        raise

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ─────────────────────────────────────────────────────────────
# RESET ELASTICSEARCH
# ─────────────────────────────────────────────────────────────

def reset_elasticsearch():
    """
    Supprime et recrée l'index Elasticsearch.
    Le mapping est réappliqué à la recréation.
    """
    from elasticsearch import Elasticsearch
    from storage.elasticsearch.creer_index_elasticsearch import MAPPING
    from config import NOM_INDEX

    print("\n=== Reset Elasticsearch ===")

    try:
        client = Elasticsearch(
            f"http://{ELASTIC_HOST}:{ELASTIC_PORT}",
            request_timeout=30,
        )

        if not client.ping():
            raise ConnectionError(
                f"Elasticsearch inaccessible sur {ELASTIC_HOST}:{ELASTIC_PORT}"
            )

        # Supprimer l'index s'il existe
        if client.indices.exists(index=NOM_INDEX):
            client.indices.delete(index=NOM_INDEX)
            print(f"  Index supprimé : {NOM_INDEX}")
        else:
            print(f"  Index '{NOM_INDEX}' n'existait pas.")

        # Recréer l'index avec le mapping
        client.indices.create(index=NOM_INDEX, body=MAPPING)
        print(f"  Index recréé   : {NOM_INDEX}")
        print("Elasticsearch reset terminé.")

    except Exception as e:
        logging.error(f"Erreur reset Elasticsearch : {e}")
        raise


# ─────────────────────────────────────────────────────────────
# RESET GÉNÉRAL
# ─────────────────────────────────────────────────────────────

def reset_all():
    """Reset toutes les bases dans l'ordre."""
    reset_mongodb()
    reset_postgresql()
    reset_elasticsearch()
    print("\n=== Reset général terminé ===")


# ─────────────────────────────────────────────────────────────
# CONFIRMATION DE SÉCURITÉ
# ─────────────────────────────────────────────────────────────

def confirmer(message: str) -> bool:
    """
    Demande une confirmation explicite avant toute opération destructive.
    Standard de sécurité en Data Engineering — jamais de reset silencieux.
    """
    print(f"\n⚠️  ATTENTION : {message}")
    print("Cette opération est IRRÉVERSIBLE.")
    reponse = input("Tapez 'CONFIRMER' pour continuer : ")
    return reponse.strip() == "CONFIRMER"


# ─────────────────────────────────────────────────────────────
# POINT D'ENTRÉE
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Reset des bases de données Job Market"
    )
    parser.add_argument("--mongodb",    action="store_true", help="Reset MongoDB")
    parser.add_argument("--postgresql", action="store_true", help="Reset PostgreSQL")
    parser.add_argument("--elastic",    action="store_true", help="Reset Elasticsearch")

    args = parser.parse_args()

    # Sans argument → reset toutes les bases
    reset_toutes = not any([args.mongodb, args.postgresql, args.elastic])

    if reset_toutes:
        if not confirmer("Toutes les bases vont être réinitialisées."):
            print("Reset annulé.")
            sys.exit(0)
        reset_all()

    else:
        if args.mongodb:
            if not confirmer("La base MongoDB va être réinitialisée."):
                print("Reset MongoDB annulé.")
            else:
                reset_mongodb()

        if args.postgresql:
            if not confirmer("La base PostgreSQL va être réinitialisée."):
                print("Reset PostgreSQL annulé.")
            else:
                reset_postgresql()

        if args.elastic:
            if not confirmer("L'index Elasticsearch va être réinitialisé."):
                print("Reset Elasticsearch annulé.")
            else:
                reset_elasticsearch()
