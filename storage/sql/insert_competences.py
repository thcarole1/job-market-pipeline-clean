import logging

# ─────────────────────────────────────────────────────────────
# INSERTION COMPÉTENCES
# ─────────────────────────────────────────────────────────────

def inserer_competences(offre: dict, cursor) -> int:
    """
    Insère les compétences d'une offre dans la table competences.
    Une ligne par compétence.
    Retourne le nombre de compétences insérées.
    """
    competences = offre.get("competences", [])

    # Garantir que c'est bien une liste
    if not isinstance(competences, list):
        logging.warning(
            f"Offre {offre.get('id')} : competences n'est pas une liste "
            f"({type(competences)}) — ignoré"
        )
        return 0

    inseres = 0
    for competence in competences:

        # Ignorer les valeurs vides ou None
        if not competence or not str(competence).strip():
            continue

        try:
            cursor.execute("""
                INSERT INTO competences (offre_id, competence)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (offre.get("id"), str(competence).strip()))
            inseres += 1

        except Exception as e:
            logging.error(
                f"Erreur insertion competence '{competence}' "
                f"pour offre {offre.get('id')} : {e}"
            )

    return inseres
