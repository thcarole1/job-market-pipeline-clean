

from ingestion.welcometothejungle.parser_offre_wttj import parser_offre_wttj


def parser_brutes(offres_brutes: list) -> list:
    """
    Parse toutes les offres brutes et sauvegarde le résultat.
    Retourne la liste des offres parsées.
    """
    offres_parsees = []
    erreurs = 0

    for i, offre_brute in enumerate(offres_brutes):
        try:
            offre_parsee = parser_offre_wttj(offre_brute)
            offres_parsees.append(offre_parsee)
        except Exception as e:
            print(f"Erreur parsing offre {i} : {e}")
            erreurs += 1
            continue

    print(f"\nParsing terminé : {len(offres_parsees)} offres OK, {erreurs} erreurs")
    return offres_parsees
