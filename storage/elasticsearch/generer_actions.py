from config import NOM_INDEX

from storage.elasticsearch.preparer_document import preparer_document

def generer_actions(
    offres: list,
    nom_index: str = NOM_INDEX):
    """
    Générateur d'actions pour l'insertion en bulk.

    bulk() d'Elasticsearch attend une liste d'actions formatées.
    On utilise l'id métier (ft_001, wttj_abc) comme _id Elasticsearch
    pour garantir l'unicité et permettre les mises à jour.
    """
    for offre in offres:
        doc = preparer_document(offre)
        yield {
            "_index": nom_index,
            "_id":    offre.get("id"),  # id métier = id Elasticsearch
            "_source": doc,
        }
