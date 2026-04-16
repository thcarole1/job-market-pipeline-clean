import logging
from elasticsearch import Elasticsearch
from config import NOM_INDEX

def supprimer_index(
    client: Elasticsearch,
    nom_index: str = NOM_INDEX):
    """
    Supprime l'index — utile pour repartir proprement si le mapping change.
    """
    if client.indices.exists(index=nom_index):
        client.indices.delete(index=nom_index)
        logging.info(f"Index '{nom_index}' supprimé.")
    else:
        logging.info(f"Index '{nom_index}' n'existe pas — rien à supprimer.")
