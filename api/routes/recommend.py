# api/routes/recommend.py
"""
Endpoint de recommandation d'offres similaires.

GET /recommend/{id} → offres similaires via PostgreSQL
"""

from fastapi import APIRouter, Depends, Query, HTTPException
import psycopg2
from api.dependencies import get_postgresql

router = APIRouter(prefix="/recommend", tags=["Recommandations"])


@router.get("/{offre_id}")
def recommander_offres(
    offre_id: str,
    nb:       int  = Query(5, description="Nombre de recommandations"),
    conn      = Depends(get_postgresql),
):
    """
    Recommande des offres similaires basées sur :
    - même type de contrat
    - même ville
- compétences communes

    Note : cette version est une recommandation simple basée sur des règles.
    Le modèle ML (similarité cosinus) sera intégré à l'étape suivante.
    """
    cursor = conn.cursor()

    # Récupérer l'offre de référence
    cursor.execute("""
        SELECT localisation_ville, type_contrat
        FROM offres
        WHERE id = %s
    """, (offre_id,))

    offre_ref = cursor.fetchone()

    if not offre_ref:
        raise HTTPException(
            status_code=404,
            detail=f"Offre '{offre_id}' introuvable."
        )

    ville, contrat = offre_ref

    # Trouver les offres avec les mêmes compétences
    cursor.execute("""
        SELECT
            o.id,
            o.titre,
            o.entreprise,
            o.localisation_ville,
            o.type_contrat,
            o.salaire_min,
            o.salaire_max,
            COUNT(c.competence) AS competences_communes
        FROM offres o
        JOIN competences c ON c.offre_id = o.id
        WHERE o.id != %s
          AND c.competence IN (
              SELECT competence FROM competences WHERE offre_id = %s
          )
        GROUP BY o.id, o.titre, o.entreprise, o.localisation_ville,
                 o.type_contrat, o.salaire_min, o.salaire_max
        ORDER BY competences_communes DESC, o.date_publication DESC
        LIMIT %s
    """, (offre_id, offre_id, nb))

    colonnes = [desc[0] for desc in cursor.description]
    resultats = [dict(zip(colonnes, row)) for row in cursor.fetchall()]

    return {
        "offre_reference": offre_id,
        "nb_recommandations": len(resultats),
        "recommandations": resultats,
    }
