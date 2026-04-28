# utils/csv_to_json.py
"""
Convertit un fichier CSV en fichier JSON horodaté.

Usage :
    python -m utils.csv_to_json --fichier data/ml/dataset/dataset_ml.csv
    python -m utils.csv_to_json --fichier data/ml/dataset/dataset_ml.csv --dossier_sortie data/processed/normalise
    python -m utils.csv_to_json --fichier data/ml/dataset/dataset_ml_csv_20260423_074301.csv
"""

import json
import logging
import argparse
import pandas as pd
from pathlib import Path
from datetime import datetime
from config import RACINE

logging.basicConfig(
    level  = logging.INFO,
    format = "%(asctime)s — %(levelname)s — %(message)s"
)

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


def csv_to_json(
    fichier:        str | Path,
    dossier_sortie: str | Path = None,
) -> Path | None:
    """
    Convertit un fichier CSV en fichier JSON horodaté.

    - Lit le fichier CSV avec pandas
    - Convertit en liste de dictionnaires (orient="records")
    - Déduplique par champ "id" si présent
    - Sauvegarde dans le dossier de sortie avec un timestamp

    Paramètres :
        fichier        : chemin vers le fichier CSV à convertir
        dossier_sortie : dossier de destination (défaut : même dossier que le CSV)

    Retourne :
        Path vers le fichier JSON produit, ou None si erreur
    """
    fichier = Path(fichier)

    # ── Vérifications ─────────────────────────────────────────
    if not fichier.exists():
        logging.error(f"Fichier introuvable : {fichier}")
        return None

    if fichier.suffix.lower() != ".csv":
        logging.error(f"Le fichier n'est pas un CSV : {fichier}")
        return None

    # Dossier de sortie — même dossier que le CSV par défaut
    dossier_sortie = Path(dossier_sortie) if dossier_sortie else fichier.parent
    dossier_sortie.mkdir(parents=True, exist_ok=True)

    # ── Lecture du CSV ────────────────────────────────────────
    try:
        df = pd.read_csv(fichier, encoding="utf-8")
        logging.info(f"CSV chargé : {fichier.name}")
        logging.info(f"  Lignes   : {len(df)}")
        logging.info(f"  Colonnes : {list(df.columns)}")

    except Exception as e:
        logging.error(f"Erreur lecture CSV : {e}")
        return None

    # ── Conversion en liste de dicts ──────────────────────────
    offres = df.to_dict(orient="records")

    # ── Déduplication par id si le champ existe ───────────────
    if "id" in df.columns:
        ids_vus       = set()
        offres_unique = []

        for offre in offres:
            offre_id = offre.get("id")

            if offre_id and offre_id in ids_vus:
                continue

            if offre_id:
                ids_vus.add(offre_id)

            offres_unique.append(offre)

        nb_doublons = len(offres) - len(offres_unique)
        offres      = offres_unique

        if nb_doublons > 0:
            logging.info(f"  Doublons supprimés : {nb_doublons}")

    # ── Sauvegarde ────────────────────────────────────────────
    nom_fichier   = f"{fichier.stem}_{TIMESTAMP}.json"
    chemin_sortie = dossier_sortie / nom_fichier

    try:
        with open(chemin_sortie, "w", encoding="utf-8") as f:
            json.dump(offres, f, ensure_ascii=False, indent=2)

    except Exception as e:
        logging.error(f"Erreur sauvegarde JSON : {e}")
        return None

    # ── Rapport ───────────────────────────────────────────────
    logging.info(f"{'─' * 50}")
    logging.info(f"Fichier source  : {fichier}")
    logging.info(f"Offres converties : {len(offres)}")
    logging.info(f"Fichier produit : {chemin_sortie}")

    return chemin_sortie


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Convertit un fichier CSV en fichier JSON horodaté"
    )
    parser.add_argument(
        "--fichier",
        type     = str,
        required = True,
        help     = "Chemin vers le fichier CSV à convertir"
    )
    parser.add_argument(
        "--dossier_sortie",
        type    = str,
        default = None,
        help    = "Dossier de destination (défaut : même dossier que le CSV)"
    )

    args = parser.parse_args()

    csv_to_json(
        fichier        = args.fichier,
        dossier_sortie = args.dossier_sortie,
    )
