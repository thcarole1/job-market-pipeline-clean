
from pathlib import Path
import json

# ─────────────────────────────────────────────────────────────────────
# ÉTAPE 4 — SAUVEGARDE PROCESSED
# ─────────────────────────────────────────────────────────────────────

def sauvegarder_processed(offres: list, timestamp: str) -> str:
    """
    Sauvegarde les offres parsées dans data/processed/francetravail/.
    Le timestamp est partagé avec la sauvegarde brute pour retrouver
    facilement les deux fichiers correspondant à la même extraction.

    Retourne le chemin du fichier créé.
    """
    Path("data/processed/francetravail").mkdir(parents=True, exist_ok=True)

    chemin = f"data/processed/francetravail/offres_{timestamp}.json"

    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(offres, f, ensure_ascii=False, indent=2)

    print(f"Processed sauvegardé : {chemin} ({len(offres)} offres)")
    return chemin
