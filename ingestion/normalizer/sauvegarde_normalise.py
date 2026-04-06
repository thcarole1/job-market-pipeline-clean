from datetime import datetime
from pathlib import Path
import json

# ─────────────────────────────────────────────────────────────────────
# SAUVEGARDE
# ─────────────────────────────────────────────────────────────────────

def sauvegarder_normalise(offres: list, timestamp: str = None) -> str:
    """
    Sauvegarde les offres normalisées dans data/processed/normalise/.

    On crée un dossier dédié pour les données normalisées, distinct
    des dossiers par source (francetravail/, welcometothejungle/).
    Cela permet de retrouver facilement les données prêtes à insérer
    en base, quelle que soit leur source d'origine.

    Retourne le chemin du fichier créé.
    """
    Path("data/processed/normalise").mkdir(parents=True, exist_ok=True)

    if not timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    chemin = f"data/processed/normalise/offres_{timestamp}.json"

    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(offres, f, ensure_ascii=False, indent=2)

    print(f"Normalisé sauvegardé : {chemin} ({len(offres)} offres)")
    return chemin
