

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
# NORMALISATION WELCOME TO THE JUNGLE
# ─────────────────────────────────────────────────────────────────────

def normaliser_offre_wttj(offre_parsee: dict) -> dict:
    """
    Traduit une offre WTTJ parsée vers le schéma commun.

    Entrée  : dict produit par parser_offre_wttj() — déjà nettoyé
    Sortie  : dict conforme au schéma normalisé commun

    Correspondances clés :
        objectID           → id (préfixé "wttj_")
        name               → titre
        organization.name  → entreprise (déjà aplati par le parser)
        offices[0].city    → localisation_ville (déjà extrait)
        contract_type      → type_contrat (via table CONTRATS)
        published_at_date  → date_publication (déjà au bon format)
        salary_minimum     → salaire_min (déjà en entier)
        salary_maximum     → salaire_max (déjà en entier)
        remote             → teletravail (via table TELETRAVAIL)
        tags[].name        → competences (approximation — text mining à l'étape 3)
    """
    return {
        # ── Identifiants ──────────────────────────────────────────────
        # Même logique que FT : préfixe "wttj_" pour garantir l'unicité.
        "id":     f"wttj_{offre_parsee.get('id', '')}",
        "source": "welcometothejungle",
        "url":    offre_parsee.get("url", ""),

        # ── Contenu principal ─────────────────────────────────────────
        "titre":       offre_parsee.get("titre", ""),
        "entreprise":  offre_parsee.get("entreprise", ""),

        # WTTJ sépare le résumé (summary) du profil recherché (profile).
        # Le parser les a déjà concaténés en une seule description.
        # C'est cette description qui alimentera le modèle ML.
        "description": offre_parsee.get("description", ""),

        # ── Compétences ───────────────────────────────────────────────
        # WTTJ ne fournit pas de liste de compétences structurée.
        # Les tags Algolia sont une approximation acceptable pour l'instant.
        # L'extraction fine se fera par text mining à l'étape 3 du projet.
        "competences": [],  # sera rempli à l'étape 3 par NLP

        # ── Localisation ──────────────────────────────────────────────
        "localisation_ville": offre_parsee.get("localisation_ville", ""),
        "localisation_dept":  offre_parsee.get("localisation_region", ""),
        "latitude":           offre_parsee.get("latitude"),
        "longitude":          offre_parsee.get("longitude"),

        # ── Contrat ───────────────────────────────────────────────────
        # WTTJ utilise "full_time", "internship" etc.
        # La table CONTRATS les traduit vers "CDI", "Stage" etc.
        "type_contrat": CONTRATS.get(
            offre_parsee.get("type_contrat", ""),
            offre_parsee.get("type_contrat", "")
        ),

        # ── Télétravail ───────────────────────────────────────────────
        # WTTJ fournit "partial", "full" ou "none".
        # La table TELETRAVAIL les traduit vers "hybrid", "remote", "onsite".
        "teletravail": TELETRAVAIL.get(
            offre_parsee.get("teletravail", ""),
            offre_parsee.get("teletravail", "")
        ) or None,

        # ── Salaire ───────────────────────────────────────────────────
        # WTTJ fournit directement des entiers — pas besoin de regex.
        # Le parser les a déjà extraits proprement.
        "salaire_min":    offre_parsee.get("salaire_min"),
        "salaire_max":    offre_parsee.get("salaire_max"),
        "salaire_devise": offre_parsee.get("salaire_devise", "EUR"),

        # ── Expérience ────────────────────────────────────────────────
        # WTTJ fournit directement un entier (ex: 5 pour "5 ans+").
        "experience_min": offre_parsee.get("experience_min"),

        # ── Secteur et métier ─────────────────────────────────────────
        # WTTJ structure les secteurs en parent/enfant.
        # Ex: parent = "Tech", enfant = "Intelligence artificielle / ML"
        "secteur":      offre_parsee.get("secteur", ""),
        "sous_secteur": offre_parsee.get("sous_secteur", ""),
        "rome_code":    "",  # non disponible chez WTTJ

        # ── Entreprise ────────────────────────────────────────────────
        # WTTJ fournit un entier, FT fournit une tranche texte.
        # On conserve les deux formats dans le même champ —
        # la normalisation fine se fera si besoin lors de l'analyse.
        "nb_employes": offre_parsee.get("nb_employes"),

        # ── Missions et avantages ─────────────────────────────────────
        # WTTJ structure les missions dans un champ dédié — rare et précieux.
        # Les avantages (télétravail, team building...) aussi.
        "missions":  offre_parsee.get("missions", []),
        "avantages": offre_parsee.get("avantages", []),

        # ── Qualification ─────────────────────────────────────────────
        # Non disponible chez WTTJ.
        "qualification": "",

        # ── Dates ─────────────────────────────────────────────────────
        "date_publication": offre_parsee.get("date_publication", ""),
        "date_extraction":  datetime.now().isoformat(),
    }
