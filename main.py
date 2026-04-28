# main.py
"""
Point d'entrée unique du projet Job Market.

Usage :
    # Pipeline standard
    python main.py                        # extraction + normalisation + insertion
    python main.py --reset                # reset puis pipeline
    python main.py --skip-extract         # sans extraction
    python main.py --reset-only           # reset uniquement

    # Collecte dataset ML
    python main.py --collect              # collecte tous les métiers
    python main.py --collect --data-only      # métiers data uniquement
    python main.py --collect --non-data-only  # métiers non-data uniquement
    python main.py --collect --reset          # reset puis collecte
"""

import argparse
import logging
import sys
import time
import asyncio
from pathlib import Path

from config import RACINE, NB_PAGES

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
# PIPELINE STANDARD
# ─────────────────────────────────────────────────────────────

def pipeline_complet(
    reset:        bool = False,
    skip_extract: bool = False,
    keyword:      str  = "data engineer",
) -> dict:
    """Pipeline complet : extraction → normalisation → insertion."""

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
            from ingestion.francetravail.pipeline_complet_ft import pipeline_complet_ft
            pipeline_complet_ft(keyword, NB_PAGES)
            rapport_final["etapes"]["extraction_ft"] = "OK"
        except Exception as e:
            logging.error(f"Extraction FT échouée : {e}")
            rapport_final["etapes"]["extraction_ft"] = f"ERREUR : {e}"
            rapport_final["succes"] = False

        etape(2, "Extraction WTTJ")
        try:
            from ingestion.welcometothejungle.pipeline_complet_wttj import pipeline_complet_wttj
            asyncio.run(pipeline_complet_wttj(keyword, NB_PAGES))
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
        return rapport_final

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
    rapport_final["keyword"] = keyword

    return rapport_final


# ─────────────────────────────────────────────────────────────
# COLLECTE DATASET ML
# ─────────────────────────────────────────────────────────────

def collecter_dataset(
    reset:         bool = False,
    data_only:     bool = False,
    non_data_only: bool = False,
):
    """Collecte les offres par métiers prédéfinis pour le dataset ML."""
    from ml.dataset.collect_dataset import collecter_par_keywords
    from ml.dataset.keywords import KEYWORDS_DATA, KEYWORDS_NON_DATA
    from ml.dataset.export_dataset import export_csv_dataset

    if data_only:
        keywords = [(kw, "data") for kw in KEYWORDS_DATA]
    elif non_data_only:
        keywords = [(kw, "non_data") for kw in KEYWORDS_NON_DATA]
    else:
        keywords = (
            [(kw, "data")     for kw in KEYWORDS_DATA] +
            [(kw, "non_data") for kw in KEYWORDS_NON_DATA]
        )

    collecter_par_keywords(keywords=keywords, reset=reset)
    export_csv_dataset()


# ─────────────────────────────────────────────────────────────
# POINT D'ENTRÉE
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Job Market — point d'entrée unique"
    )

    # ── Mode pipeline standard ────────────────────────────────
    parser.add_argument("--reset",        action="store_true",
                        help="Réinitialiser les bases")
    parser.add_argument("--reset-only",   action="store_true",
                        help="Réinitialiser uniquement")
    parser.add_argument("--skip-extract", action="store_true",
                        help="Sauter l'extraction")

    # ── Mode collecte ML ──────────────────────────────────────
    parser.add_argument("--collect",       action="store_true",
                        help="Collecter le dataset ML")
    parser.add_argument("--data-only",     action="store_true",
                        help="Métiers data uniquement")
    parser.add_argument("--non-data-only", action="store_true",
                        help="Métiers non-data uniquement")

    args = parser.parse_args()

    # ── Reset uniquement ──────────────────────────────────────
    if args.reset_only:
        from reset_databases import reset_all
        reset_all()

    # ── Collecte dataset ML ───────────────────────────────────
    elif args.collect:
        collecter_dataset(
            reset         = args.reset,
            data_only     = args.data_only,
            non_data_only = args.non_data_only,
        )

    # ── Pipeline standard ─────────────────────────────────────
    else:
        rapport = pipeline_complet(
            reset        = args.reset,
            skip_extract = args.skip_extract,
        )
        sys.exit(0 if rapport["succes"] else 1)
