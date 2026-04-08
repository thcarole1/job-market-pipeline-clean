from pymongo.errors import BulkWriteError
import logging

def inserer_offres(
    offres:      list,
    collection,
    ordered:     bool = False
) -> dict:
    """
    Insère une liste d'offres dans MongoDB de façon sécurisée.

    - Crée un index unique sur "id" avant l'insertion pour eviter les doublons.
    - ordered=False : continue l'insertion même si une offre échoue.
    - ordered=True  : s'arrête à la première erreur.

    Retourne un rapport avec le nombre d'insertions réussies et les erreurs.
    """
    if not offres:
        logging.warning("Liste vide — rien à insérer.")
        return {"inseres": 0, "erreurs": 0}

    rapport = {"inseres": 0, "erreurs": 0, "detail_erreurs": []}

    # Créer l'index unique sur "id" avant toute insertion.
    # Si l'index existe déjà, MongoDB l'ignore silencieusement —
    # cette ligne est donc safe à appeler à chaque fois.
    collection.create_index("id", unique=True)

    try:
        resultat = collection.insert_many(offres, ordered=ordered)
        rapport["inseres"] = len(resultat.inserted_ids)
        logging.info(f"{rapport['inseres']} offres inserees avec succes.")

    except BulkWriteError as e:
        # Certaines insertions ont réussi, d'autres ont échoué
        rapport["inseres"] = e.details.get("nInserted", 0)
        rapport["erreurs"] = len(e.details.get("writeErrors", []))
        rapport["detail_erreurs"] = e.details.get("writeErrors", [])
        logging.warning(
            f"Insertion partielle : {rapport['inseres']} OK, "
            f"{rapport['erreurs']} erreurs."
        )

    except Exception as e:
        logging.error(f"Erreur inattendue lors de l'insertion : {e}")
        rapport["erreurs"] = len(offres)

    return rapport
