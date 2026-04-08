
import asyncio
from pathlib import Path
from ingestion.francetravail.pipeline_complet import pipeline_complet
from ingestion.welcometothejungle.pipeline_complet_wttj import pipeline_complet_wttj
from ingestion.normalizer.pipeline_normalizer import pipeline_normalisation



if __name__ == "__main__":

    # ── Mots Clés  ────────────────────────
    mots_cles    = "data engineer"

    # ── Appel API France Travail  ────────────────────────
    print("\n=== Appel API France Travail ===")

    pipeline_complet(
        mots_cles    = mots_cles,
        nb_pages_max = 1,
        avec_details = False,  # passer à True pour les descriptions complètes
    )

    # ── Scraping Welcome to the Jungle  ────────────────────────
    print("\n=== Scraping Welcome to the Jungle ===")

    asyncio.run(pipeline_complet_wttj(
        mots_cles= mots_cles,
        nb_pages=1,
    ))

    # ── Normalisation Sources de données  ────────────────────────
    print("\n=== Normalisation Sources de données ===")

    # Adapter les chemins selon les fichiers disponibles sur ta machine.
    # Le glob("*.json") prend automatiquement le fichier le plus récent
    # de chaque source grâce au tri alphabétique des timestamps.

    fichiers = []

    dossier_ft = Path("data/processed/francetravail")
    if dossier_ft.exists():
        fichiers_ft = sorted(dossier_ft.glob("*.json"))
        if fichiers_ft:
            fichiers.append(str(fichiers_ft[-1]))  # le plus récent

    dossier_wttj = Path("data/processed/welcometothejungle")
    if dossier_wttj.exists():
        fichiers_wttj = sorted(dossier_wttj.glob("*.json"))
        if fichiers_wttj:
            fichiers.append(str(fichiers_wttj[-1]))  # le plus récent

    if not fichiers:
        print("Aucun fichier processed trouvé.")
        print("Lance d'abord extractor.py pour FranceTravail et WTTJ.")
    else:
        pipeline_normalisation(fichiers, valider=True)

# Insertion en base mongodb
# insertion en base SQL
