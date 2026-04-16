
import logging
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, BulkIndexError
from storage.elasticsearch.generer_actions import generer_actions
from config import NOM_INDEX
# ─────────────────────────────────────────────────────────────
# INDEXATION EN BATCH
# ─────────────────────────────────────────────────────────────

def indexer_offres(
    offres:     list,
    client:     Elasticsearch,
    nom_index:  str = NOM_INDEX,
    chunk_size: int = 500,
) -> dict:
    """
    Indexe une liste d'offres dans Elasticsearch via l'API bulk.

    L'API bulk envoie plusieurs documents en une seule requête HTTP
    — beaucoup plus performant qu'un insert par document.

    chunk_size : nombre de documents par requête bulk (500 par défaut).
    Retourne un rapport d'indexation.
    """
    rapport = {"indexes": 0, "erreurs": 0, "detail_erreurs": []}

    if not offres:
        logging.warning("Liste vide — rien à indexer.")
        return rapport

    try:
        succes, erreurs = bulk(
            client,
            generer_actions(offres, nom_index),
            chunk_size=chunk_size,
            raise_on_error=False,   # ne pas planter sur les erreurs partielles
            stats_only=False,
        )

        rapport["indexes"] = succes
        rapport["erreurs"] = len(erreurs)
        rapport["detail_erreurs"] = erreurs

        logging.info(f"{succes} documents indexés, {len(erreurs)} erreurs.")

    except BulkIndexError as e:
        rapport["erreurs"] = len(e.errors)
        rapport["detail_erreurs"] = e.errors
        logging.error(f"Erreur bulk : {len(e.errors)} documents non indexés.")

    except Exception as e:
        logging.error(f"Erreur inattendue : {e}")
        raise

    return rapport
