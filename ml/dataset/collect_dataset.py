# ml/dataset/collect_dataset.py

import json
import logging
from pathlib import Path
from datetime import datetime

from ml.dataset.keywords import KEYWORDS_DATA, KEYWORDS_NON_DATA
from ml.dataset.export_dataset import export_csv_dataset
from pipeline import etape

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s — %(levelname)s — %(message)s")

RACINE      = Path(__file__).parent.parent.parent
DATASET_DIR = RACINE / "data" / "ml" / "dataset"
DATASET_DIR.mkdir(parents=True, exist_ok=True)
TIMESTAMP   = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_PATH = DATASET_DIR / f"dataset_ml_{TIMESTAMP}.jsonl"


def enrichir(offre: dict, keyword: str, categorie: str) -> dict:
    """
    Ajoute les métadonnées ML à une offre normalisée.
    Ne modifie pas le schéma normalisé existant —
    on ajoute uniquement des champs préfixés ml_.
    """
    offre["ml_keyword"]        = keyword
    offre["ml_label_binaire"]  = 1 if categorie == "data" else 0
    offre["ml_label_categorie"]= categorie
    return offre

def sauvegarder_jsonl(offres: list, path: Path):
    """Sauvegarde en JSONL — une offre par ligne."""
    with open(path, "a", encoding="utf-8") as f:
        for offre in offres:
            f.write(json.dumps(offre, ensure_ascii=False) + "\n")
    logging.info(f"{len(offres)} offres sauvegardées → {path}")


def reset_first(reset):
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

if __name__ == "__main__":
    # Premier reset des bdd
    reset_first(False)

    # Tous les mots-clés avec leur catégorie
    keywords = (
        [(kw, "data")     for kw in KEYWORDS_DATA] +
        [(kw, "non_data") for kw in KEYWORDS_NON_DATA]
    )

    for keyword, categorie in keywords:
        logging.info(f"=== '{keyword}' ({categorie}) ===")

        # Ton pipeline existant — une seule ligne
        from pipeline import pipeline_complet
        pipeline_complet(skip_extract=False, keyword=keyword)

        # Charger les offres normalisées produites
        fichiers = sorted(
            (RACINE / "data" / "processed" / "normalise").glob("*.json")
        )
        if not fichiers:
            continue

        with open(fichiers[-1], encoding="utf-8") as f:
            offres = json.load(f)

        # Enrichir chaque offre avec le keyword et le label
        offres_enrichies = [enrichir(o, keyword, categorie) for o in offres]
        sauvegarder_jsonl(offres_enrichies, OUTPUT_PATH)

    logging.info(f"\nDataset complet → {OUTPUT_PATH}")
    export_csv_dataset()

"""
Pour lancer la collecte d'offres :
python -m ml.dataset.collect_dataset
"""
