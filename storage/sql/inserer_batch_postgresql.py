
import logging
from storage.sql.insert_offre_complete import inserer_offre_complete
from storage.sql.creer_tables_sql import connecter_postgresql

# ─────────────────────────────────────────────────────────────
# PIPELINE BATCH — TOUTES LES OFFRES
# ─────────────────────────────────────────────────────────────

def inserer_batch_postgresql(offres: list) -> dict:
    """
    Insère une liste d'offres normalisées dans PostgreSQL.

    Utilise une seule connexion et un seul commit pour toutes les offres
    — plus performant qu'un commit par offre.

    Retourne un rapport global d'insertion.
    """
    rapport_global = {
        "offres_inserees":      0,
        "offres_doublons":      0,
        "competences_inserees": 0,
        "missions_inserees":    0,
        "avantages_inseres":    0,
        "erreurs":              0,
    }

    conn   = None
    cursor = None

    try:
        conn   = connecter_postgresql()
        cursor = conn.cursor()

        for offre in offres:
            try:
                rapport = inserer_offre_complete(offre, cursor)

                if rapport["offre"]:
                    rapport_global["offres_inserees"] += 1
                else:
                    rapport_global["offres_doublons"] += 1

                rapport_global["competences_inserees"] += rapport["competences"]
                rapport_global["missions_inserees"]    += rapport["missions"]
                rapport_global["avantages_inseres"]    += rapport["avantages"]

            except Exception as e:
                logging.error(f"Erreur offre {offre.get('id')} : {e}")
                rapport_global["erreurs"] += 1
                # On continue avec l'offre suivante
                continue

        # Un seul commit pour toutes les insertions
        conn.commit()
        logging.info("Commit effectué — toutes les insertions validées.")

    except Exception as e:
        logging.error(f"Erreur inattendue : {e}")
        if conn:
            conn.rollback()
        raise

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return rapport_global
