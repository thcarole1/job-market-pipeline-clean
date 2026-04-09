from storage.sql.insert_offre import inserer_offre
from storage.sql.insert_competences import inserer_competences
from storage.sql.insert_missions import inserer_missions
from storage.sql.insert_avantages import inserer_avantages

# ─────────────────────────────────────────────────────────────
# PIPELINE COMPLET — UNE OFFRE
# ─────────────────────────────────────────────────────────────

def inserer_offre_complete(offre: dict, cursor) -> dict:
    """
    Insère une offre complète dans toutes les tables.

    Ordre respecté :
        1. offres (table principale)
        2. competences, missions, avantages (tables de jointure)

    Retourne un rapport d'insertion pour cette offre.
    """
    rapport = {
        "id":          offre.get("id"),
        "offre":       False,
        "competences": 0,
        "missions":    0,
        "avantages":   0,
    }

    # 1. Insérer l'offre principale en premier
    rapport["offre"] = inserer_offre(offre, cursor)

    # 2. Insérer les tables de jointure
    # (même si l'offre existait déjà — elle est en base dans tous les cas)
    rapport["competences"] = inserer_competences(offre, cursor)
    rapport["missions"]    = inserer_missions(offre, cursor)
    rapport["avantages"]   = inserer_avantages(offre, cursor)

    return rapport
