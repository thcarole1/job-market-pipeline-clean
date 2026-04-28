# utils/concat_json.py
"""
Concatène tous les fichiers JSON d'un répertoire en un seul fichier horodaté.
Utile pour fusionner plusieurs extractions avant insertion en base.

Usage :
    python -m utils.concat_json
    python -m utils.concat_json --dossier data/processed/francetravail
    python -m utils.concat_json --dossier data/processed/normalise
"""

import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from config import RACINE

logging.basicConfig(
    level  = logging.INFO,
    format = "%(asctime)s — %(levelname)s — %(message)s"
)

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")


def concatener_json(dossier: str | Path) -> Path | None:
    """
    Concatène tous les fichiers JSON d'un répertoire en un seul fichier.

    - Parcourt tous les fichiers *.json du dossier
    - Fusionne les listes d'offres en une seule liste
    - Déduplique par champ "id" — une offre ne peut apparaître qu'une fois
    - Sauvegarde le résultat dans le même dossier avec un timestamp

    Paramètres :
        dossier : chemin vers le répertoire contenant les fichiers JSON

    Retourne :
        Path vers le fichier concatené, ou None si aucun fichier trouvé
    """
    dossier = Path(dossier)

    if not dossier.exists():
        logging.error(f"Dossier introuvable : {dossier}")
        return None

    # Lister tous les fichiers JSON du dossier
    # On exclut les fichiers déjà concatenés pour éviter les doublons
    fichiers = sorted([
        f for f in dossier.glob("*.json")
        if not f.name.startswith("concat_")
    ])

    if not fichiers:
        logging.warning(f"Aucun fichier JSON trouvé dans : {dossier}")
        return None

    logging.info(f"{len(fichiers)} fichier(s) trouvé(s) dans {dossier}")

    # ── Fusion des fichiers ───────────────────────────────────
    toutes_offres = []
    ids_vus       = set()  # pour la déduplication
    erreurs       = 0

    for fichier in fichiers:
        try:
            with open(fichier, "r", encoding="utf-8") as f:
                offres = json.load(f)

            # Gérer le cas où le fichier contient un dict au lieu d'une liste
            if isinstance(offres, dict):
                offres = [offres]

            nb_avant = len(toutes_offres)

            for offre in offres:
                offre_id = offre.get("id")

                # Déduplication par id
                if offre_id and offre_id in ids_vus:
                    continue

                if offre_id:
                    ids_vus.add(offre_id)

                toutes_offres.append(offre)

            nb_ajoutes = len(toutes_offres) - nb_avant
            logging.info(f"  {fichier.name} → {nb_ajoutes} offres ajoutées")

        except json.JSONDecodeError as e:
            logging.error(f"  {fichier.name} → JSON invalide : {e}")
            erreurs += 1
            continue

        except Exception as e:
            logging.error(f"  {fichier.name} → Erreur : {e}")
            erreurs += 1
            continue

    if not toutes_offres:
        logging.warning("Aucune offre à sauvegarder après fusion.")
        return None

    # ── Sauvegarde ────────────────────────────────────────────
    nom_fichier = f"concat_{TIMESTAMP}.json"
    chemin_sortie = dossier / nom_fichier

    with open(chemin_sortie, "w", encoding="utf-8") as f:
        json.dump(toutes_offres, f, ensure_ascii=False, indent=2)

    # ── Rapport ───────────────────────────────────────────────
    logging.info(f"{'─' * 50}")
    logging.info(f"Fichiers traités  : {len(fichiers)}")
    logging.info(f"Offres fusionnées : {len(toutes_offres)}")
    logging.info(f"Doublons ignorés  : {len(ids_vus) - len(toutes_offres) + len(ids_vus)}")
    logging.info(f"Erreurs           : {erreurs}")
    logging.info(f"Fichier produit   : {chemin_sortie}")

    return chemin_sortie


def concatener_toutes_sources() -> dict:
    """
    Concatène les fichiers JSON de toutes les sources du projet.
    Retourne un dictionnaire avec les chemins des fichiers produits.
    """
    sources = [
        RACINE / "data" / "processed" / "francetravail",
        RACINE / "data" / "processed" / "welcometothejungle",
        RACINE / "data" / "processed" / "normalise",
    ]

    resultats = {}

    for dossier in sources:
        logging.info(f"\n=== Concaténation : {dossier.name} ===")
        chemin = concatener_json(dossier)
        resultats[dossier.name] = chemin

    return resultats


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Concatène les fichiers JSON d'un répertoire"
    )
    parser.add_argument(
        "--dossier",
        type    = str,
        default = None,
        help    = "Chemin du dossier à traiter (défaut : toutes les sources)"
    )
    args = parser.parse_args()

    if args.dossier:
        # Concaténer un dossier spécifique
        concatener_json(args.dossier)
    else:
        # Concaténer toutes les sources
        concatener_toutes_sources()
