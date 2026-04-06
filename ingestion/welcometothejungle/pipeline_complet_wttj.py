import asyncio
from datetime import datetime

from ingestion.welcometothejungle.scraper import scraper_wttj
from ingestion.welcometothejungle.sauvegarde_offres_brutes_wttj import sauvegarder_brut
from ingestion.welcometothejungle.parser_offres_brutes_wttj import parser_brutes
from ingestion.welcometothejungle.sauvegarde_offres_processed_wttj import sauvegarder_processed


async def pipeline_complet_wttj(mots_cles: str = "data engineer", nb_pages: int = 3):
    """
    Pipeline complet : scraping → parsing → sauvegarde.

    1. Scrape les offres brutes
    2. Sauvegarde les données brutes dans data/raw/
    3. Parse chaque offre
    4. Sauvegarde les données parsées dans data/processed/
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ── Scraping  : Welcome To The Jungle ────────────────
    print("=== Scraping  : Welcome To The Jungle ===")

    # ── Étape 1 : Scraping ────────────────────────────────
    print("=== ÉTAPE 1 : Scraping ===")
    offres_brutes = await scraper_wttj(nb_pages=nb_pages)

    if not offres_brutes:
        print("Aucune offre récupérée. Arrêt.")
        return

    # ── Étape 2 : Sauvegarde brute ────────────────────────
    print("\n=== ÉTAPE 2 : Sauvegarde brute ===")
    sauvegarder_brut(offres_brutes, timestamp)

    # ── Étape 3 : Parsing ─────────────────────────────────
    print("\n=== ÉTAPE 3 : Parsing ===")
    offres_parsees = parser_brutes(offres_brutes)

    # ── Étape 4 : Sauvegarde processed ───────────────────
    print("\n=== ÉTAPE 4 : Sauvegarde processed ===")
    sauvegarder_processed(offres_parsees, timestamp)

    # ── Résumé ────────────────────────────────────────────
    print(f"""
╔══════════════════════════════════════╗
  Pipeline WTTJ terminé
  Offres brutes   : {len(offres_brutes)}
  Offres parsées  : {len(offres_parsees)}
  Timestamp       : {timestamp}
╚══════════════════════════════════════╝
    """)

    return offres_parsees

if __name__ == "__main__":
    asyncio.run(pipeline_complet_wttj(
        mots_cles="data engineer",
        nb_pages=10,
    ))
