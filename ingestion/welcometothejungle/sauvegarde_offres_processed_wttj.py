from datetime import datetime
from pathlib import Path
import json

def sauvegarder_processed(offres: list, timestamp: str = None) -> str:
    """
    Sauvegarde les offres parsées dans data/processed/welcometothejungle/.
    Retourne le chemin du fichier créé.
    """
    Path("data/processed/welcometothejungle").mkdir(parents=True, exist_ok=True)

    if not timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    chemin = f"data/processed/welcometothejungle/offres_{timestamp}.json"

    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(offres, f, ensure_ascii=False, indent=2)

    print(f"Processed sauvegardé : {chemin} ({len(offres)} offres)")
    return chemin
