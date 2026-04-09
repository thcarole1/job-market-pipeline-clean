import logging

# ─────────────────────────────────────────────────────────────
# INSERTION MISSIONS
# ─────────────────────────────────────────────────────────────

def inserer_missions(offre: dict, cursor) -> int:
    """
    Insère les missions d'une offre dans la table missions.
    Une ligne par mission.
    Retourne le nombre de missions insérées.
    """
    missions = offre.get("missions", [])

    if not isinstance(missions, list):
        logging.warning(
            f"Offre {offre.get('id')} : missions n'est pas une liste "
            f"({type(missions)}) — ignoré"
        )
        return 0

    inseres = 0
    for mission in missions:

        if not mission or not str(mission).strip():
            continue

        try:
            cursor.execute("""
                INSERT INTO missions (offre_id, mission)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (offre.get("id"), str(mission).strip()))
            inseres += 1

        except Exception as e:
            logging.error(
                f"Erreur insertion mission pour offre "
                f"{offre.get('id')} : {e}"
            )

    return inseres
