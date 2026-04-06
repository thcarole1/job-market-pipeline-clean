
from pathlib import Path
from datetime import datetime
import json

def sauvegarder_brut(offres: list, timestamp: str = None) -> str:
    """
    Sauvegarde les offres brutes dans data/raw/welcometothejungle/
    avec un timestamp dans le nom de fichier.
    Retourne le chemin du fichier créé.
    """
    Path("data/raw/welcometothejungle").mkdir(parents=True, exist_ok=True)

    if not timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    chemin    = f"data/raw/welcometothejungle/offres_{timestamp}.json"

    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(offres, f, ensure_ascii=False, indent=2)

    print(f"Sauvegardé : {chemin} ({len(offres)} offres)")
    return chemin
