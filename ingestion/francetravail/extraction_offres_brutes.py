import time

from ingestion.francetravail.api_client import FranceTravailClient
from config import NB_PAGES

# Nombre maximum d'offres par page autorisé par l'API FranceTravail
PAGE_SIZE = 100

# ─────────────────────────────────────────────────────────────────────
# ÉTAPE 1 — EXTRACTION BRUTE
# ─────────────────────────────────────────────────────────────────────

def extraire_offres(
    mots_cles:    str  = "data engineer",
    nb_pages_max: int  = 10
) -> list:
    """
    Extrait les offres FranceTravail pour un mot-clé donné.

    mots_cles    : termes de recherche
    nb_pages_max : nombre de pages à parcourir (100 offres par page)
    avec_details : si True, récupère le détail complet de chaque offre
                   (description complète + toutes les compétences)

    Retourne une liste de dictionnaires bruts tels que retournés par l'API.
    """
    client = FranceTravailClient()
    offres = []
    page   = 0

    while page < NB_PAGES:
        debut = page * PAGE_SIZE
        fin   = debut + PAGE_SIZE - 1

        params = {
            "motsCles": mots_cles,
            "range":    f"{debut}-{fin}",
            "sort":     "1",  # tri par date de publication
        }

        print(f"Page {page + 1} — offres {debut} à {fin}...")

        try:
            data = client.rechercher_offres(params)
        except Exception as e:
            print(f"Erreur page {page + 1} : {e}")
            break

        resultats = data.get("resultats", [])

        if not resultats:
            print("Plus d'offres disponibles, arrêt.")
            break

        offres.extend(resultats)
        page += 1

        # Délai poli entre les pages pour respecter le rate limit
        time.sleep(0.5)

    print(f"\nTotal extrait : {len(offres)} offres")
    return offres
