
from ingestion.normalizer.normaliser_offre_ft import normaliser_offre_ft
from ingestion.normalizer.normaliser_offre_wttj import normaliser_offre_wttj

# ─────────────────────────────────────────────────────────────────────
# POINT D'ENTRÉE UNIFIÉ
# ─────────────────────────────────────────────────────────────────────

def normaliser(offre_parsee: dict) -> dict:
    """
    Point d'entrée unique de la normalisation.

    Détecte automatiquement la source de l'offre via le champ "source"
    et appelle la fonction de normalisation correspondante.

    Entrée  : dict parsé — doit contenir un champ "source"
    Sortie  : dict normalisé conforme au schéma commun
    Raises  : ValueError si la source est inconnue

    Utilisation :
        offre_normalisee = normaliser(offre_parsee)
    """
    source = offre_parsee.get("source", "")

    if source == "francetravail":
        return normaliser_offre_ft(offre_parsee)

    elif source == "welcometothejungle":
        return normaliser_offre_wttj(offre_parsee)

    else:
        # On lève une erreur explicite plutôt que de retourner
        # silencieusement un dict vide — plus facile à déboguer.
        raise ValueError(
            f"Source inconnue : '{source}'. "
            f"Valeurs acceptées : 'francetravail', 'welcometothejungle'."
        )
