import json
from config import NOM_INDEX, RACINE

from  storage.elasticsearch.connecter_elasticsearch import connecter_elasticsearch
from storage.elasticsearch.creer_index_elasticsearch import creer_index
from storage.elasticsearch.indexer_offres import indexer_offres

# ─────────────────────────────────────────────────────────────
# PIPELINE COMPLET
# ─────────────────────────────────────────────────────────────

def pipeline_indexation_elasticsearch() -> dict:
    """
    Pipeline complet :
        1. Connexion à Elasticsearch
        2. Création de l'index si absent
        3. Chargement des fichiers normalisés
        4. Indexation source par source
    """
    # sources = [
    #     ("FranceTravail", RACINE / "data" / "processed" / "francetravail"),
    #     ("WTTJ",          RACINE / "data" / "processed" / "welcometothejungle"),
    # ]

    sources = [("Offres normalisées", RACINE / "data" / "processed" / "normalise"),]

    rapport_final = {}

    # Connexion
    client = connecter_elasticsearch()

    # Créer l'index si absent
    creer_index(client)

    for nom_source, dossier in sources:
        print(f"\n=== Indexation Elasticsearch — {nom_source} ===")

        try:
            fichiers = sorted(dossier.glob("*.json"))
            if not fichiers:
                print(f"Aucun fichier trouvé pour {nom_source}")
                continue

            with open(fichiers[-1], "r", encoding="utf-8") as f:
                offres = json.load(f)

            print(f"{len(offres)} offres chargées")

            rapport = indexer_offres(offres, client)
            rapport_final[nom_source] = rapport

            print(f"Indexés  : {rapport['indexes']}")
            print(f"Erreurs  : {rapport['erreurs']}")

        except Exception as e:
            print(f"Erreur sur {nom_source} : {e}")
            rapport_final[nom_source] = {"erreur": str(e)}
            continue

    # # Vérification finale
    # total = client.count(index=NOM_INDEX)["count"]
    # print(f"\nTotal documents dans l'index '{NOM_INDEX}' : {total}")

    return rapport_final


# ─────────────────────────────────────────────────────────────
# POINT D'ENTRÉE
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    rapport = pipeline_indexation_elasticsearch()
    print("\n=== Rapport final ===")
    print(rapport)

# Pour lancer l'indexation
# python -m storage.elasticsearch.pipeline_insert_elasticsearch
