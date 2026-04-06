
from ingestion.normalizer.normaliser_offre import normaliser

# ─────────────────────────────────────────────────────────────────────
# NORMALISATION EN BATCH
# ─────────────────────────────────────────────────────────────────────

def normaliser_batch(offres_parsees: list) -> list:
    """
    Normalise une liste d'offres parsées en une seule opération.

    Les erreurs de normalisation sont loguées sans interrompre
    le traitement — une offre mal formée ne bloque pas les suivantes.

    Entrée  : liste de dicts parsés (toutes sources mélangées acceptées)
    Sortie  : liste de dicts normalisés
    """
    offres_normalisees = []
    erreurs            = 0

    for i, offre in enumerate(offres_parsees):
        try:
            offres_normalisees.append(normaliser(offre))
        except Exception as e:
            print(f"Erreur normalisation offre {i} "
                  f"(source: {offre.get('source', '?')}, "
                  f"id: {offre.get('id', '?')}) : {e}")
            erreurs += 1

    print(f"Normalisation terminée : "
          f"{len(offres_normalisees)} offres OK, {erreurs} erreurs")

    return offres_normalisees
