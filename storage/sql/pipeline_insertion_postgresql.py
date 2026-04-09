
import json
from pathlib import Path
from dotenv import load_dotenv
from storage.sql.inserer_batch_postgresql import inserer_batch_postgresql

load_dotenv()

RACINE = Path(__file__).parent.parent.parent

# ─────────────────────────────────────────────────────────────
# PIPELINE SOURCE PAR SOURCE
# ─────────────────────────────────────────────────────────────

def pipeline_insertion_postgresql() -> dict:
    """
    Charge les fichiers normalisés et les insère dans PostgreSQL
    source par source.
    """
    # sources = [
    #     ("FranceTravail", RACINE / "data" / "processed" / "francetravail"),
    #     ("WTTJ",          RACINE / "data" / "processed" / "welcometothejungle"),
    # ]

    sources = [("Offres normalisées", RACINE / "data" / "processed" / "normalise"),]

    rapport_final = {}

    for nom_source, dossier in sources:
        print(f"\n=== Insertion PostgreSQL — {nom_source} ===")

        try:
            fichiers = sorted(dossier.glob("*.json"))
            if not fichiers:
                print(f"Aucun fichier trouvé pour {nom_source}")
                continue

            with open(fichiers[-1], "r", encoding="utf-8") as f:
                offres = json.load(f)

            print(f"{len(offres)} offres chargées")

            rapport = inserer_batch_postgresql(offres)
            rapport_final[nom_source] = rapport

            print(f"Offres insérées  : {rapport['offres_inserees']}")
            print(f"Doublons ignorés : {rapport['offres_doublons']}")
            print(f"Compétences      : {rapport['competences_inserees']}")
            print(f"Missions         : {rapport['missions_inserees']}")
            print(f"Avantages        : {rapport['avantages_inseres']}")
            print(f"Erreurs          : {rapport['erreurs']}")

        except Exception as e:
            print(f"Erreur sur {nom_source} : {e}")
            rapport_final[nom_source] = {"erreur": str(e)}
            continue

    return rapport_final


# ─────────────────────────────────────────────────────────────
# POINT D'ENTRÉE
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    rapport = pipeline_insertion_postgresql()
    print("\n=== Rapport final ===")
    print(rapport)


'''
# Créer les tables si pas encore fait
python -m storage.sql.creer_tables_sql

# Insérer les données
python -m storage.sql.pipeline_insertion_postgresql

'''
