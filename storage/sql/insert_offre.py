import logging


# ─────────────────────────────────────────────────────────────
# INSERTION OFFRE PRINCIPALE
# ─────────────────────────────────────────────────────────────

def inserer_offre(offre: dict, cursor) -> bool:
    """
    Insère une offre dans la table principale offres.
    ON CONFLICT DO NOTHING — ignore les doublons silencieusement.
    Retourne True si l'offre a été insérée, False si elle existait déjà.
    """
    try:
        cursor.execute("""
            INSERT INTO offres (
                id, source, titre, entreprise,
                description,
                localisation_ville, localisation_dept,
                type_contrat, teletravail,
                salaire_min, salaire_max, experience_min,
                secteur, nb_employes,
                date_publication, date_extraction, url
            )
            VALUES (
                %s, %s, %s, %s,
                %s,
                %s, %s,
                %s, %s,
                %s, %s, %s,
                %s, %s,
                %s, %s, %s
            )
            ON CONFLICT (id) DO NOTHING
        """, (
            offre.get("id"),
            offre.get("source"),
            offre.get("titre"),
            offre.get("entreprise"),
            offre.get("description"),
            offre.get("localisation_ville"),
            offre.get("localisation_dept"),
            offre.get("type_contrat"),
            offre.get("teletravail"),
            offre.get("salaire_min"),
            offre.get("salaire_max"),
            offre.get("experience_min"),
            offre.get("secteur"),
            offre.get("nb_employes"),
            offre.get("date_publication"),
            offre.get("date_extraction"),
            offre.get("url")
        ))
        return cursor.rowcount > 0

    except Exception as e:
        logging.error(f"Erreur insertion offre {offre.get('id')} : {e}")
        raise
