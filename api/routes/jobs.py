# api/routes/jobs.py

from fastapi import APIRouter, Depends, Query, HTTPException
from pymongo.database import Database
from ml.search import SearchEngine
from api.dependencies import get_mongo, get_search_engine, get_postgresql

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
    conn     = Depends(get_postgresql),
):
    """Détail complet d'une offre depuis PostgreSQL."""
    cursor = conn.cursor()

    # Récupérer l'offre principale
    cursor.execute("""
        SELECT
            o.id,
            o.source,
            o.titre,
            o.entreprise,
            o.description,
            o.localisation_ville,
            o.localisation_dept,
            o.type_contrat,
            o.teletravail,
            o.salaire_min,
            o.salaire_max,
            o.experience_min,
            o.secteur,
            o.nb_employes,
            o.date_publication,
            o.date_extraction,
            o.url
        FROM offres o
        WHERE o.id = %s
    """, (offre_id,))

    colonnes = [desc[0] for desc in cursor.description]
    row      = cursor.fetchone()

    if not row:
        raise HTTPException(
            status_code = 404,
            detail      = f"Offre '{offre_id}' introuvable."
        )

    offre = dict(zip(colonnes, row))

    # Récupérer les compétences
    cursor.execute("""
        SELECT competence FROM competences
        WHERE offre_id = %s
        GROUP BY competence
        ORDER BY competence
    """, (offre_id,))
    offre["competences"] = [r[0] for r in cursor.fetchall()]

    # Récupérer les missions
    cursor.execute("""
        SELECT mission FROM missions
        WHERE offre_id = %s
    """, (offre_id,))
    offre["missions"] = [r[0] for r in cursor.fetchall()]

    # Récupérer les avantages
    cursor.execute("""
        SELECT avantage FROM avantages
        WHERE offre_id = %s
    """, (offre_id,))
    offre["avantages"] = [r[0] for r in cursor.fetchall()]

    # Nettoyer les valeurs NaN non sérialisables en JSON
    import math
    def nettoyer(v):
        if v is None:
            return None
        try:
            if isinstance(v, float) and math.isnan(v):
                return None
        except TypeError:
            pass
        return v

    return {k: nettoyer(v) for k, v in offre.items()}
