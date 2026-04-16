
from pathlib import Path
import json

from config import RACINE
from storage.mongodb.insert_offres_mongodb import inserer_offres
from storage.mongodb.connecter_mongodb import connecter_mongodb


def pipeline_insertion_mongodb(collection):
    """
    Insère les offres dans MongoDB source par source.
    Une panne sur une source ne bloque pas les autres.
    """
    # sources = [
    # ("FranceTravail", RACINE / "data" / "processed" / "francetravail"),
    # ("WTTJ",          RACINE / "data" / "processed" / "welcometothejungle"),
    # ]

    sources = [("offres_normalisees", RACINE / "data" / "processed" / "normalise"),]

    rapport_global = {}

    for nom_source, dossier in sources:
        print(f"\n=== Insertion {nom_source} ===")
        try:
            # Charger le fichier le plus récent de la source
            fichiers = sorted(Path(dossier).glob("*.json"))
            if not fichiers:
                print(f"Aucun fichier trouvé pour {nom_source}")
                continue

            with open(fichiers[-1], "r", encoding="utf-8") as f:
                offres = json.load(f)

            # Insérer dans MongoDB
            rapport = inserer_offres(offres, collection, ordered=False)
            rapport_global[nom_source] = rapport

        except Exception as e:
            print(f"Erreur sur {nom_source} : {e}")
            rapport_global[nom_source] = {"erreur": str(e)}
            # On continue avec la source suivante
            continue

    return rapport_global


if __name__ == "__main__":

    # connexion à la base mongodb
    client = connecter_mongodb()

    # Création de la bd
    db = client["job_market"]

    # Création de la collection souhaitée
    collection = db["normalisées"]

    # Insertion des données dans la collection souhaitée
    rapport_global = pipeline_insertion_mongodb(collection)

    # affichage rapport final
    print(rapport_global)


'''
Lancer le pipelin d'insertion en base MongoDB

python -m storage.mongodb.pipeline_insert_mongodb


'''
