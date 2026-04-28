# ml/dataset/collect_dataset.py
"""
Collecte des offres d'emploi par métiers prédéfinis.
Appelé exclusivement depuis main.py — pas de point d'entrée direct.
"""

import json
import logging
from pathlib import Path
from datetime import datetime

RACINE      = Path(__file__).parent.parent.parent
DATASET_DIR = RACINE / "data" / "ml" / "dataset"
DATASET_DIR.mkdir(parents=True, exist_ok=True)
TIMESTAMP   = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_PATH = DATASET_DIR / f"dataset_ml_{TIMESTAMP}.jsonl"


# ─────────────────────────────────────────────────────────────
# UTILITAIRES
# ─────────────────────────────────────────────────────────────

def enrichir(offre: dict, keyword: str, categorie: str) -> dict:
    """
    Ajoute les métadonnées ML à une offre normalisée.
    Ne modifie pas le schéma normalisé existant —
    on ajoute uniquement des champs préfixés ml_.
    """
    offre["ml_keyword"]         = keyword
    offre["ml_label_binaire"]   = 1 if categorie == "data" else 0
    offre["ml_label_categorie"] = categorie
    return offre


def sauvegarder_jsonl(offres: list, path: Path):
    """
    Sauvegarde en JSONL — une offre par ligne — mode append.
    Le mode append permet de reprendre une collecte interrompue
    sans écraser les offres déjà sauvegardées.
    """
    with open(path, "a", encoding="utf-8") as f:
        for offre in offres:
            f.write(json.dumps(offre, ensure_ascii=False) + "\n")
    logging.info(f"{len(offres)} offres sauvegardées → {path}")


def charger_offres_normalisees() -> list:
    """
    Charge le fichier normalisé le plus récent produit par le pipeline.
    Retourne une liste vide si aucun fichier n'est trouvé.
    """
    dossier  = RACINE / "data" / "processed" / "normalise"
    fichiers = sorted(dossier.glob("*.json"))

    if not fichiers:
        logging.warning("Aucun fichier normalisé trouvé.")
        return []

    with open(fichiers[-1], encoding="utf-8") as f:
        offres = json.load(f)

    logging.info(f"{len(offres)} offres chargées depuis {fichiers[-1].name}")
    return offres


# ─────────────────────────────────────────────────────────────
# COLLECTE PAR KEYWORDS
# ─────────────────────────────────────────────────────────────

def collecter_par_keywords(
    keywords:    list[tuple[str, str]],
    reset:       bool = False,
    output_path: Path = OUTPUT_PATH,
) -> Path:
    """
    Lance le pipeline pour chaque (keyword, categorie) et
    sauvegarde les offres enrichies dans un fichier JSONL.

    Paramètres :
        keywords    : liste de tuples (keyword, categorie)
                      ex: [("data engineer", "data"),
                           ("comptable", "non_data")]
        reset       : réinitialise les bases avant le premier keyword
                      uniquement — pas à chaque itération
        output_path : chemin du fichier JSONL de sortie

    Retourne :
        Path vers le fichier JSONL produit

    Comportement en cas d'erreur :
        Si un keyword échoue, on log l'erreur et on continue
        avec le keyword suivant — la collecte n'est pas interrompue.
    """
    from main import pipeline_complet

    total_offres = 0
    premier_run  = True
    keywords_ok  = []
    keywords_ko  = []

    for keyword, categorie in keywords:
        logging.info(f"\n{'═' * 60}")
        logging.info(f"  Keyword  : '{keyword}'")
        logging.info(f"  Catégorie: {categorie}")
        logging.info(f"  Progression : {len(keywords_ok) + len(keywords_ko) + 1}"
                     f"/{len(keywords)}")
        logging.info(f"{'═' * 60}")

        try:
            # ── Pipeline d'extraction + insertion ────────────
            # Reset uniquement avant le premier keyword
            # pour ne pas perdre les offres déjà collectées
            pipeline_complet(
                reset        = reset and premier_run,
                skip_extract = False,
                keyword      = keyword,
            )
            premier_run = False

            # ── Chargement des offres normalisées ─────────────
            offres = charger_offres_normalisees()
            if not offres:
                logging.warning(f"Aucune offre pour '{keyword}' — on continue.")
                keywords_ko.append(keyword)
                continue

            # ── Enrichissement avec les métadonnées ML ────────
            offres_enrichies = [
                enrichir(offre, keyword, categorie)
                for offre in offres
            ]

            # ── Sauvegarde en JSONL ───────────────────────────
            sauvegarder_jsonl(offres_enrichies, output_path)
            total_offres += len(offres_enrichies)
            keywords_ok.append(keyword)

            logging.info(
                f"  ✓ {len(offres_enrichies)} offres ajoutées "
                f"(total cumulé : {total_offres})"
            )

        except Exception as e:
            logging.error(f"Erreur sur '{keyword}' : {e}")
            keywords_ko.append(keyword)
            continue

    # ── Rapport final ─────────────────────────────────────────
    logging.info(f"\n{'═' * 60}")
    logging.info(f"  Collecte terminée")
    logging.info(f"  Keywords OK  : {len(keywords_ok)} / {len(keywords)}")
    logging.info(f"  Keywords KO  : {len(keywords_ko)}")
    if keywords_ko:
        logging.info(f"  En erreur    : {keywords_ko}")
    logging.info(f"  Total offres : {total_offres}")
    logging.info(f"  Dataset      : {output_path}")
    logging.info(f"{'═' * 60}")

    return output_path
