
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────
# TABLES DE CORRESPONDANCE
# ─────────────────────────────────────────────────────────────────────

# Correspondance des types de contrat vers un vocabulaire commun.
# FranceTravail utilise déjà "CDI", "CDD" etc.
# WTTJ utilise "full_time", "part_time", "internship" etc.
# On unifie tout vers : CDI, CDD, Alternance, Stage, Freelance
CONTRATS = {
    # Valeurs WTTJ → valeur normalisée
    "full_time":       "CDI",
    "part_time":       "CDI temps partiel",
    "internship":      "Stage",
    "apprenticeship":  "Alternance",
    "freelance":       "Freelance",
    "temporary":       "CDD",
    # Valeurs FranceTravail (déjà lisibles, on les conserve telles quelles)
    "CDI":             "CDI",
    "CDD":             "CDD",
    "MIS":             "Mission intérimaire",
    "SAI":             "Saisonnier",
}

# Correspondance des modalités de télétravail vers un vocabulaire commun.
# WTTJ utilise "full", "partial", "none".
# FranceTravail ne fournit généralement pas cette information.
TELETRAVAIL = {
    "full":    "remote",   # 100% télétravail
    "partial": "hybrid",   # télétravail partiel
    "none":    "onsite",   # présentiel uniquement
}



# ─────────────────────────────────────────────────────────────────────
# NORMALISATION FRANCETRAVAIL
# ─────────────────────────────────────────────────────────────────────

def normaliser_offre_ft(offre_parsee: dict) -> dict:
    """
    Traduit une offre FranceTravail parsée vers le schéma commun.

    Entrée  : dict produit par parser_offre_ft() — déjà nettoyé
    Sortie  : dict conforme au schéma normalisé commun

    Correspondances clés :
        appellationlibelle → titre
        entreprise.nom     → entreprise (déjà aplati par le parser)
        lieuTravail.libelle→ localisation_ville (déjà extrait par le parser)
        typeContrat        → type_contrat (via table CONTRATS)
        dateCreation       → date_publication (déjà tronqué par le parser)
        salaire.libelle    → salaire_min / salaire_max (déjà extraits)
        competences[].libelle → competences (déjà extraites par le parser)
    """
    return {
        # ── Identifiants ──────────────────────────────────────────────
        # On préfixe l'id avec "ft_" pour garantir l'unicité globale.
        # Sans préfixe, un id "12345" de FT pourrait entrer en collision
        # avec un id "12345" de WTTJ.
        "id":     f"ft_{offre_parsee.get('id', '')}",
        "source": "francetravail",
        "url":    offre_parsee.get("url", ""),

        # ── Contenu principal ─────────────────────────────────────────
        "titre":       offre_parsee.get("titre", ""),
        "entreprise":  offre_parsee.get("entreprise", ""),
        "description": offre_parsee.get("description", ""),

        # ── Compétences ───────────────────────────────────────────────
        # FranceTravail fournit une liste structurée — directement utilisable.
        # WTTJ ne la fournit pas — elle sera extraite par text mining (étape 3).
        "competences": offre_parsee.get("competences", []),

        # ── Localisation ──────────────────────────────────────────────
        "localisation_ville": offre_parsee.get("localisation_ville", ""),
        "localisation_dept":  offre_parsee.get("localisation_dept", ""),
        "latitude":           offre_parsee.get("latitude"),
        "longitude":          offre_parsee.get("longitude"),

        # ── Contrat ───────────────────────────────────────────────────
        # On passe par la table CONTRATS pour uniformiser.
        # Si la valeur n'est pas dans la table, on la conserve telle quelle
        # plutôt que de perdre l'information.
        "type_contrat": CONTRATS.get(
            offre_parsee.get("type_contrat", ""),
            offre_parsee.get("type_contrat", "")
        ),

        # ── Télétravail ───────────────────────────────────────────────
        # FranceTravail ne fournit généralement pas cette information.
        # On met None plutôt qu'une valeur inventée.
        "teletravail": None,

        # ── Salaire ───────────────────────────────────────────────────
        # Déjà extrait en entiers par le parser via regex.
        # Le parser a géré le cas "Annuel de 35000.0 Euros sur 12.0 mois".
        "salaire_min":   offre_parsee.get("salaire_min"),
        "salaire_max":   offre_parsee.get("salaire_max"),
        "salaire_devise": "EUR",  # FranceTravail est toujours en euros

        # ── Expérience ────────────────────────────────────────────────
        # Déjà extrait en entier par le parser depuis "3 An(s)".
        "experience_min": offre_parsee.get("experience_min"),

        # ── Secteur et métier ─────────────────────────────────────────
        "secteur":      offre_parsee.get("secteur", ""),
        "sous_secteur": "",  # non disponible chez FranceTravail
        "rome_code":    offre_parsee.get("rome_code", ""),

        # ── Entreprise ────────────────────────────────────────────────
        "nb_employes": offre_parsee.get("nb_employes", ""),

        # ── Missions et avantages ─────────────────────────────────────
        # FranceTravail ne structure pas les missions séparément —
        # elles sont dans la description libre.
        "missions":   [],
        "avantages":  [],  # non disponible chez FranceTravail

        # ── Qualification ─────────────────────────────────────────────
        # Spécifique à FranceTravail (ex: "Cadre", "Employé").
        # Absent chez WTTJ — on le conserve car utile pour le ML.
        "qualification": offre_parsee.get("qualification", ""),

        # ── Dates ─────────────────────────────────────────────────────
        # date_publication : déjà au format YYYY-MM-DD grâce au parser.
        # date_extraction  : moment où le script a tourné — utile pour
        #                    tracer l'historique des extractions Airflow.
        "date_publication": offre_parsee.get("date_publication", ""),
        "date_extraction":  datetime.now().isoformat(),
    }
