
import re

def valider_offre(offre: dict) -> list:
    """
    Vérifie qu'une offre normalisée respecte le schéma commun.

    Retourne une liste d'erreurs (vide si l'offre est valide).
    Permet de détecter les anomalies avant insertion en base de données.

    Règles vérifiées :
        - Champs obligatoires présents et non vides
        - salaire_min <= salaire_max si les deux sont présents
        - date_publication au format YYYY-MM-DD
        - source dans les valeurs connues
    """
    erreurs = []

    # Champs obligatoires — doivent être présents et non vides
    champs_obligatoires = [
        "id", "source", "titre", "entreprise",
        "description", "localisation_ville",
        "type_contrat", "date_publication", "url"
    ]
    for champ in champs_obligatoires:
        if not offre.get(champ):
            erreurs.append(f"Champ obligatoire manquant ou vide : '{champ}'")

    # Cohérence du salaire
    sal_min = offre.get("salaire_min")
    sal_max = offre.get("salaire_max")
    if sal_min and sal_max and sal_min > sal_max:
        erreurs.append(
            f"salaire_min ({sal_min}) > salaire_max ({sal_max})"
        )

    # Format de la date
    date = offre.get("date_publication", "")
    if date and not re.match(r"\d{4}-\d{2}-\d{2}", date):
        erreurs.append(
            f"date_publication '{date}' n'est pas au format YYYY-MM-DD"
        )

    # Source connue
    sources_connues = {"francetravail", "welcometothejungle"}
    if offre.get("source") not in sources_connues:
        erreurs.append(
            f"Source inconnue : '{offre.get('source')}'"
        )

    return erreurs


def valider_batch(offres: list) -> dict:
    """
    Valide toutes les offres normalisées et retourne un rapport.

    Retourne un dictionnaire avec :
        - "valides"  : nombre d'offres sans erreur
        - "invalides": nombre d'offres avec au moins une erreur
        - "erreurs"  : liste détaillée des erreurs par offre
    """
    rapport = {"valides": 0, "invalides": 0, "erreurs": []}

    for i, offre in enumerate(offres):
        erreurs = valider_offre(offre)
        if erreurs:
            rapport["invalides"] += 1
            rapport["erreurs"].append({
                "index":  i,
                "id":     offre.get("id", "?"),
                "source": offre.get("source", "?"),
                "detail": erreurs
            })
        else:
            rapport["valides"] += 1

    return rapport
