
from pathlib import Path
from datetime import datetime
import json
from ingestion.normalizer.normaliser_batch import normaliser_batch
from ingestion.normalizer.sauvegarde_normalise import sauvegarder_normalise
from ingestion.normalizer.valider_batch import valider_batch

# ─────────────────────────────────────────────────────────────────────
# PIPELINE COMPLET
# ─────────────────────────────────────────────────────────────────────

def pipeline_normalisation(
    fichiers_processed: list,
    valider: bool = True
) -> list:
    """
    Pipeline complet de normalisation à partir de fichiers processed.

    Étapes :
        1. Charge les fichiers processed de chaque source
        2. Normalise toutes les offres vers le schéma commun
        3. Valide les données normalisées (optionnel)
        4. Sauvegarde dans data/processed/normalise/

    fichiers_processed : liste de chemins vers les fichiers JSON parsés
    valider            : si True, lance la validation et affiche le rapport

    Exemple d'utilisation :
        pipeline_normalisation([
            "data/processed/francetravail/offres_20260401.json",
            "data/processed/welcometothejungle/offres_20260401.json",
        ])
    """
    timestamp     = datetime.now().strftime("%Y%m%d_%H%M%S")
    toutes_offres = []

    # ── Étape 1 : Chargement ──────────────────────────────
    print("=== ÉTAPE 1 : Chargement des fichiers ===")
    for chemin in fichiers_processed:
        try:
            with open(chemin, "r", encoding="utf-8") as f:
                offres = json.load(f)
            print(f"  {chemin} → {len(offres)} offres")
            toutes_offres.extend(offres)
        except Exception as e:
            print(f"  Erreur chargement {chemin} : {e}")

    print(f"Total chargé : {len(toutes_offres)} offres\n")

    if not toutes_offres:
        print("Aucune offre à normaliser. Arrêt.")
        return []

    # ── Étape 2 : Normalisation ───────────────────────────
    print("=== ÉTAPE 2 : Normalisation ===")
    offres_normalisees = normaliser_batch(toutes_offres)

    # ── Étape 3 : Validation ──────────────────────────────
    if valider:
        print("\n=== ÉTAPE 3 : Validation ===")
        rapport = valider_batch(offres_normalisees)
        print(f"  Valides   : {rapport['valides']}")
        print(f"  Invalides : {rapport['invalides']}")
        if rapport["erreurs"]:
            print("  Détail des erreurs :")
            for err in rapport["erreurs"][:5]:  # affiche les 5 premières
                print(f"    Offre {err['id']} ({err['source']}) : "
                      f"{err['detail']}")

    # ── Étape 4 : Sauvegarde ──────────────────────────────
    print("\n=== ÉTAPE 4 : Sauvegarde ===")
    sauvegarder_normalise(offres_normalisees, timestamp)

    # ── Résumé ────────────────────────────────────────────
    ft_count   = sum(1 for o in offres_normalisees if o["source"] == "francetravail")
    wttj_count = sum(1 for o in offres_normalisees if o["source"] == "welcometothejungle")

    print(f"""
╔══════════════════════════════════════════╗
  Normalisation terminée
  FranceTravail       : {ft_count} offres
  Welcome to the Jungle: {wttj_count} offres
  Total               : {len(offres_normalisees)} offres
  Timestamp           : {timestamp}
╚══════════════════════════════════════════╝
    """)

    return offres_normalisees



# ─────────────────────────────────────────────────────────────────────
# POINT D'ENTRÉE
# ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
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
