# pipeline.py
"""
Point d'entrée unique du pipeline Job Market.

Usage :
    python pipeline.py                  # pipeline complet
    python pipeline.py --reset          # reset puis pipeline
    python pipeline.py --reset-only     # reset uniquement
    python pipeline.py --skip-extract   # sans extraction
"""

import argparse
import logging
import sys
import time
from pathlib import Path
import asyncio

from config import RACINE
# RACINE = Path(__file__).parent


# Créer le dossier logs avant la configuration du logging
(RACINE / "logs").mkdir(exist_ok=True)


logging.basicConfig(
    level    = logging.INFO,
    format   = "%(asctime)s — %(levelname)s — %(message)s",
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/pipeline.log"),
    ]
)


# ─────────────────────────────────────────────────────────────
# Critères de recherche
# ─────────────────────────────────────────────────────────────
MOTS_CLES = "électricien"
NB_PAGES = 15

# ─────────────────────────────────────────────────────────────
# UTILITAIRES
# ─────────────────────────────────────────────────────────────

def titre(message: str):
    logging.info("═" * 60)
    logging.info(f"  {message}")
    logging.info("═" * 60)

def etape(numero: int, message: str):
    logging.info(f"\n{'─' * 60}")
    logging.info(f"  ÉTAPE {numero} — {message}")
    logging.info(f"{'─' * 60}")


# ─────────────────────────────────────────────────────────────
# PIPELINE
# ─────────────────────────────────────────────────────────────

def pipeline_complet(reset: bool = False, skip_extract: bool = False) -> dict:

    debut = time.time()
    titre("JOB MARKET PIPELINE — Démarrage")

    rapport_final = {"etapes": {}, "succes": True}

    # ── Étape 0 — Reset (optionnel) ───────────────────────────
    if reset:
        etape(0, "Reset des bases de données")
        try:
            from reset_databases import reset_all
            reset_all()
            rapport_final["etapes"]["reset"] = "OK"
        except Exception as e:
            logging.error(f"Reset échoué : {e}")
            rapport_final["etapes"]["reset"] = f"ERREUR : {e}"
            rapport_final["succes"] = False
            return rapport_final

    # ── Étapes 1 & 2 — Extraction (optionnelle) ───────────────
    if not skip_extract:
        etape(1, "Extraction FranceTravail")
        try:
            from ingestion.francetravail.pipeline_complet import pipeline_complet as pipeline_ft
            pipeline_ft(MOTS_CLES, NB_PAGES)
            rapport_final["etapes"]["extraction_ft"] = "OK"
        except Exception as e:
            logging.error(f"Extraction FT échouée : {e}")
            rapport_final["etapes"]["extraction_ft"] = f"ERREUR : {e}"
            rapport_final["succes"] = False

        etape(2, "Extraction WTTJ")
        try:
            from ingestion.welcometothejungle.pipeline_complet_wttj import pipeline_complet_wttj as pipeline_wttj
            asyncio.run(pipeline_wttj(MOTS_CLES, NB_PAGES))
            rapport_final["etapes"]["extraction_wttj"] = "OK"
        except Exception as e:
            logging.error(f"Extraction WTTJ échouée : {e}")
            rapport_final["etapes"]["extraction_wttj"] = f"ERREUR : {e}"
            rapport_final["succes"] = False

    # ── Étape 3 — Normalisation ───────────────────────────────
    etape(3, "Normalisation")
    try:
        from ingestion.normalizer.pipeline_normalizer import pipeline_normalisation
        fichiers = [
            str(sorted((RACINE / "data/processed/francetravail").glob("*.json"))[-1]),
            str(sorted((RACINE / "data/processed/welcometothejungle").glob("*.json"))[-1]),
        ]
        pipeline_normalisation(fichiers, valider=True)
        rapport_final["etapes"]["normalisation"] = "OK"
    except Exception as e:
        logging.error(f"Normalisation échouée : {e}")
        rapport_final["etapes"]["normalisation"] = f"ERREUR : {e}"
        rapport_final["succes"] = False
        return rapport_final  # inutile de continuer sans données normalisées

    # ── Étape 4 — Insertion MongoDB ───────────────────────────
    etape(4, "Insertion MongoDB")
    try:
        from storage.mongodb.connecter_mongodb import connecter_mongodb
        from storage.mongodb.pipeline_insert_mongodb import pipeline_insertion_mongodb

        client     = connecter_mongodb()
        collection = client["job_market"]["normalisées"]
        pipeline_insertion_mongodb(collection)
        rapport_final["etapes"]["mongodb"] = "OK"
    except Exception as e:
        logging.error(f"Insertion MongoDB échouée : {e}")
        rapport_final["etapes"]["mongodb"] = f"ERREUR : {e}"
        rapport_final["succes"] = False

    # ── Étape 5 — Insertion PostgreSQL ────────────────────────
    etape(5, "Insertion PostgreSQL")
    try:
        from storage.sql.pipeline_insertion_postgresql import pipeline_insertion_postgresql
        pipeline_insertion_postgresql()
        rapport_final["etapes"]["postgresql"] = "OK"
    except Exception as e:
        logging.error(f"Insertion PostgreSQL échouée : {e}")
        rapport_final["etapes"]["postgresql"] = f"ERREUR : {e}"
        rapport_final["succes"] = False

    # ── Étape 6 — Insertion Elasticsearch ────────────────────
    etape(6, "Insertion Elasticsearch")
    try:
        from storage.elasticsearch.pipeline_insert_elasticsearch import pipeline_indexation_elasticsearch
        pipeline_indexation_elasticsearch()
        rapport_final["etapes"]["elasticsearch"] = "OK"
    except Exception as e:
        logging.error(f"Insertion Elasticsearch échouée : {e}")
        rapport_final["etapes"]["elasticsearch"] = f"ERREUR : {e}"
        rapport_final["succes"] = False

    # ── Rapport final ─────────────────────────────────────────
    duree = time.time() - debut
    titre(f"Pipeline terminé en {duree:.1f}s")
    logging.info(f"Rapport : {rapport_final}")

    return rapport_final


# ─────────────────────────────────────────────────────────────
# POINT D'ENTRÉE
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Créer le dossier logs s'il n'existe pas
    (RACINE / "logs").mkdir(exist_ok=True)

    parser = argparse.ArgumentParser(
        description="Pipeline Job Market — orchestration complète"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Réinitialiser les bases avant le pipeline"
    )
    parser.add_argument(
        "--reset-only",
        action="store_true",
        help="Réinitialiser les bases uniquement"
    )
    parser.add_argument(
        "--skip-extract",
        action="store_true",
        help="Sauter l'extraction — repartir des fichiers existants"
    )

    args = parser.parse_args()

    if args.reset_only:
        from reset_databases import reset_all
        reset_all()
    else:
        rapport = pipeline_complet(
            reset        = args.reset,
            skip_extract = args.skip_extract,
        )
        sys.exit(0 if rapport["succes"] else 1)


'''
# Pipeline complet
python pipeline.py

# Sans ré-extraire (rejoue depuis les fichiers existants)
python pipeline.py --skip-extract

# Reset puis pipeline
python pipeline.py --reset

# Reset uniquement
python pipeline.py --reset-only
'''
