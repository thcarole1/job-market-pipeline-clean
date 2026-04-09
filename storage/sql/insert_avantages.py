import logging

# ─────────────────────────────────────────────────────────────
# INSERTION AVANTAGES
# ─────────────────────────────────────────────────────────────

def inserer_avantages(offre: dict, cursor) -> int:
    """
    Insère les avantages d'une offre dans la table avantages.
    Une ligne par avantage.
    Retourne le nombre d'avantages insérés.
    """
    avantages = offre.get("avantages", [])

    if not isinstance(avantages, list):
        logging.warning(
            f"Offre {offre.get('id')} : avantages n'est pas une liste "
            f"({type(avantages)}) — ignoré"
        )
        return 0

    inseres = 0
    for avantage in avantages:

        if not avantage or not str(avantage).strip():
            continue

        try:
            cursor.execute("""
                INSERT INTO avantages (offre_id, avantage)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (offre.get("id"), str(avantage).strip()))
            inseres += 1

        except Exception as e:
            logging.error(
                f"Erreur insertion avantage pour offre "
                f"{offre.get('id')} : {e}"
            )

    return inseres
