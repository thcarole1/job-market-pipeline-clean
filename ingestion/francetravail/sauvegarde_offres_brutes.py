
from datetime import datetime
import json
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────
# ÉTAPE 2 — SAUVEGARDE BRUTE
# ─────────────────────────────────────────────────────────────────────

def sauvegarder_brut(offres: list, mots_cles: str = "", timestamp: str = None) -> str:
    """
    Sauvegarde les données brutes dans data/raw/francetravail/
    avec un timestamp dans le nom de fichier.

    On conserve toujours les données brutes avant transformation.
    Si le parsing est à revoir, on peut relancer sans refaire l'extraction.

    Retourne le chemin du fichier créé.
    """
    Path("data/raw/francetravail").mkdir(parents=True, exist_ok=True)

    if not timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    slug      = mots_cles.replace(" ", "_") if mots_cles else "offres"
    chemin    = f"data/raw/francetravail/{slug}_{timestamp}.json"

    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(offres, f, ensure_ascii=False, indent=2)

    print(f"Brut sauvegardé : {chemin} ({len(offres)} offres)")
    return chemin
