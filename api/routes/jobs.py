# api/routes/jobs.py

from fastapi import APIRouter, Depends, Query, HTTPException
from pymongo.database import Database
from ml.search import SearchEngine
from api.dependencies import get_mongo, get_search_engine

router = APIRouter(prefix="/jobs", tags=["Offres"])


def filtres_communs(
    ville:       str = Query(None, description="Filtrer par ville"),
    contrat:     str = Query(None, description="CDI / CDD / Alternance / Stage"),
    salaire_min: int = Query(None, description="Salaire minimum annuel en euros"),
    teletravail: str = Query(None, description="remote / hybrid / onsite"),
) -> dict:
    return {
        "ville":       ville,
        "contrat":     contrat,
        "salaire_min": salaire_min,
        "teletravail": teletravail,
    }


@router.get("/search")
def recherche(
    q:       str          = Query(..., description="Mots-clés de recherche"),
    taille:  int          = Query(10,  description="Nombre de résultats"),
    filtres: dict         = Depends(filtres_communs),
    engine:  SearchEngine = Depends(get_search_engine),
):
    """Recherche d'offres via TF-IDF + similarité cosinus."""
    try:
        resultats = engine.search(q, taille, **filtres)
        return {
            "moteur":    "TF-IDF + Cosinus",
            "requete":   q,
            "filtres":   {k: v for k, v in filtres.items() if v is not None},
            "nb":        len(resultats),
            "resultats": resultats,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{offre_id}")
def detail_offre(
    offre_id: str,
    db:       Database = Depends(get_mongo),
):
    """Détail complet d'une offre depuis MongoDB."""
    offre = db["offres"].find_one({"id": offre_id}, {"_id": 0})
    if not offre:
        raise HTTPException(
            status_code = 404,
            detail      = f"Offre '{offre_id}' introuvable."
        )
    return offre
