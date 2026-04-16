import logging
from elasticsearch import Elasticsearch
from config import ELASTIC_HOST, ELASTIC_PORT

# ─────────────────────────────────────────────────────────────
# CONNEXION
# ─────────────────────────────────────────────────────────────

def connecter_elasticsearch() -> Elasticsearch:
    """
    Crée et retourne une connexion Elasticsearch.
    Vérifie que le cluster est accessible avant de retourner le client.
    """
    host = ELASTIC_HOST
    port = ELASTIC_PORT

    client = Elasticsearch(
        f"http://{host}:{port}",
        request_timeout=30,   # secondes avant abandon
        retry_on_timeout=True,
        max_retries=3,        # nombre de tentatives automatiques
    )

    # Vérifier que le cluster répond
    if not client.ping():
        raise ConnectionError(
            f"Impossible de joindre Elasticsearch sur {host}:{port}. "
            f"Vérifiez que le conteneur Docker est démarré."
        )

    info = client.info()
    logging.info(
        f"Connecté à Elasticsearch "
        f"v{info['version']['number']} "
        f"sur {host}:{port}"
    )

    return client
