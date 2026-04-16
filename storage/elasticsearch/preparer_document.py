# ─────────────────────────────────────────────────────────────
# PRÉPARATION DES DOCUMENTS
# ─────────────────────────────────────────────────────────────

def preparer_document(offre: dict) -> dict:
    """
    Prépare une offre normalisée pour l'indexation Elasticsearch.

    Transformations appliquées :
    - Fusion latitude/longitude en geo_point si disponibles
    - Nettoyage des champs None (Elasticsearch préfère les champs absents)
    - Utilisation de l'id métier comme _id Elasticsearch
    """
    doc = {}

    # Copier tous les champs non None
    for cle, valeur in offre.items():
        if valeur is not None and valeur != "" and valeur != []:
            doc[cle] = valeur

    # Fusionner latitude et longitude en geo_point si disponibles
    lat = offre.get("latitude")
    lon = offre.get("longitude")
    if lat and lon:
        doc["localisation"] = {"lat": lat, "lon": lon}
        # Supprimer les champs séparés — geo_point les remplace
        doc.pop("latitude", None)
        doc.pop("longitude", None)

    return doc
