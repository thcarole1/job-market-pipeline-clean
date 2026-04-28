# api/routes/jobs.py
"""
Endpoints liés aux offres d'emploi.

GET /jobs              → recherche full-text via Elasticsearch
GET /jobs/{id}         → détail d'une offre via MongoDB
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from elasticsearch import Elasticsearch
from pymongo.database import Database
from api.dependencies import get_elasticsearch, get_mongo

router = APIRouter(prefix="/jobs", tags=["Offres"])

@router.get("/")
def rechercher_offres(
    q:           str  = Query(..., description="Mots-clés de recherche"),
    ville:       str  = Query(None, description="Filtrer par ville"),
    contrat:     str  = Query(None, description="Filtrer par type de contrat"),
    salaire_min: int  = Query(None, description="Salaire minimum"),
    teletravail: str  = Query(None, description="remote / hybrid / onsite"),
    taille:      int  = Query(10,   description="Nombre de résultats"),
    es: Elasticsearch = Depends(get_elasticsearch),
):
    """
    Recherche d'offres via Elasticsearch.
    Combine recherche full-text et filtres exacts.
    """
    # Construction de la requête Elasticsearch
    must   = []
    filter = []

    # Recherche full-text sur titre, description et compétences
    must.append({
        "multi_match": {
            "query":  q,
            "fields": ["titre^3", "description", "competences^2"],
        }
    })

    # Filtres optionnels
    if ville:
        filter.append({"term": {"localisation_ville": ville}})
    if contrat:
        filter.append({"term": {"type_contrat": contrat}})
    if teletravail:
        filter.append({"term": {"teletravail": teletravail}})
    if salaire_min:
        filter.append({"range": {"salaire_min": {"gte": salaire_min}}})

    body = {
        "query": {
            "bool": {
                "must":   must,
                "filter": filter,
            }
        },
        "size": taille,
    }

    try:
        res  = es.search(index="offres", body=body)
        hits = res["hits"]["hits"]

        return {
            "total":   res["hits"]["total"]["value"],
            "resultats": [
                {
                    "id":     h["_source"].get("id"),
                    "score":  round(h["_score"], 3),
                    "titre":  h["_source"].get("titre"),
                    "entreprise":         h["_source"].get("entreprise"),
                    "localisation_ville": h["_source"].get("localisation_ville"),
                    "type_contrat":       h["_source"].get("type_contrat"),
                    "salaire_min":        h["_source"].get("salaire_min"),
                    "salaire_max":        h["_source"].get("salaire_max"),
                    "teletravail":        h["_source"].get("teletravail"),
                    "date_publication":   h["_source"].get("date_publication"),
                }
                for h in hits
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{offre_id}")
def detail_offre(
    offre_id: str,
    db: Database = Depends(get_mongo),
):
    """
    Retourne le détail complet d'une offre depuis MongoDB.
    MongoDB est la source de vérité — il contient tous les champs.
    """
    offre = db["offres"].find_one(
        {"id": offre_id},
        {"_id": 0}  # exclure l'identifiant interne MongoDB
    )

    if not offre:
        raise HTTPException(
            status_code=404,
            detail=f"Offre '{offre_id}' introuvable."
        )

    return offre
