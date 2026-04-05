from ingestion.francetravail.parser_offre_francetravail import parser_offre_ft


# ─────────────────────────────────────────────────────────────────────
# ÉTAPE 3 — PARSING
# ─────────────────────────────────────────────────────────────────────

def parser_brutes(offres_brutes: list) -> list:
    """
    Parse toutes les offres brutes via parser_offre_ft().
    Les erreurs de parsing sont loguées sans interrompre le traitement —
    une offre mal formée ne doit pas bloquer les suivantes.

    Retourne la liste des offres parsées et structurées.
    """
    offres_parsees = []
    erreurs        = 0

    for i, offre in enumerate(offres_brutes):
        try:
            offres_parsees.append(parser_offre_ft(offre))
        except Exception as e:
            print(f"Erreur parsing offre {i} (id: {offre.get('id', '?')}) : {e}")
            erreurs += 1

    print(f"Parsing terminé : {len(offres_parsees)} offres OK, {erreurs} erreurs")
    return offres_parsees
