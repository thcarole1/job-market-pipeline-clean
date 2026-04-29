# api/routes/recommend.py
"""
Endpoint de recommandation d'offres similaires.

GET /recommend/{id} → offres similaires via PostgreSQL + compétences communes
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from api.dependencies import get_postgresql

router = APIRouter(prefix="/recommend", tags=["Recommandations"])


@router.get("/{offre_id}")
def recommander_offres(
    offre_id: str,
    nb:       int  = Query(5, description="Nombre de recommandations"),
    conn           = Depends(get_postgresql),
):
    """
    Recommande des offres similaires basées sur les compétences communes.

    Logique :
        - Récupère les compétences de l'offre de référence
        - Trouve les offres qui partagent le plus de compétences
        - Trie par nombre de compétences communes décroissant

    Note :
        Version basée sur les règles — pas de modèle ML.
        Le modèle Sentence Transformers sera intégré
        à l'étape suivante pour une similarité sémantique.
    """
    cursor = conn.cursor()

    # Vérifier que l'offre existe
    cursor.execute("SELECT id, titre FROM offres WHERE id = %s", (offre_id,))
    offre_ref = cursor.fetchone()

    if not offre_ref:
        raise HTTPException(
            status_code = 404,
            detail      = f"Offre '{offre_id}' introuvable."
        )

    # Trouver les offres avec les compétences communes
    cursor.execute("""
        SELECT
            o.id,
            o.titre,
            o.entreprise,
            o.localisation_ville,
            o.type_contrat,
            o.salaire_min,
            o.salaire_max,
            o.teletravail,
            o.source,
            COUNT(c.competence) AS competences_communes
        FROM offres o
        JOIN competences c ON c.offre_id = o.id
        WHERE o.id != %s
          AND c.competence IN (
              SELECT competence
              FROM competences
              WHERE offre_id = %s
          )
        GROUP BY
            o.id, o.titre, o.entreprise,
            o.localisation_ville, o.type_contrat,
            o.salaire_min, o.salaire_max,
            o.teletravail, o.source
        ORDER BY competences_communes DESC, o.date_publication DESC
        LIMIT %s
    """, (offre_id, offre_id, nb))

    colonnes  = [desc[0] for desc in cursor.description]
    resultats = [dict(zip(colonnes, row)) for row in cursor.fetchall()]

    return {
        "offre_reference":   offre_id,
        "titre_reference":   offre_ref[1],
        "nb_recommandations": len(resultats),
        "recommandations":   resultats,
    }
