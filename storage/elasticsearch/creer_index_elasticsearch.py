import logging
from elasticsearch import Elasticsearch

from config import NOM_INDEX

# ─────────────────────────────────────────────────────────────
# MAPPING DE L'INDEX
# ─────────────────────────────────────────────────────────────

# Le mapping définit le type de chaque champ.
# text     → analysé linguistiquement — pour la recherche full-text
#            "engineers" et "engineer" sont considérés identiques
# keyword  → valeur exacte — pour les filtres et agrégations
#            "CDI" reste "CDI", pas analysé
# integer  → nombre entier — pour les filtres de plage (salaire >= 40000)
# date     → date — pour le tri et les filtres temporels

MAPPING = {
    "mappings": {
        "properties": {

            # ── Identifiants ──────────────────────────────────
            "id":     {"type": "keyword"},
            "source": {"type": "keyword"},
            "url":    {"type": "keyword"},

            # ── Champs textuels analysés ──────────────────────
            # Ces champs alimentent la recherche full-text.
            # L'analyseur "french" gère les accents et la conjugaison.
            "titre": {
                "type":     "text",
                "analyzer": "french",
                "fields": {
                    "keyword": {"type": "keyword"}  # pour le tri exact
                }
            },
            "description": {
                "type":     "text",
                "analyzer": "french"
            },
            "competences": {
                "type":     "text",
                "analyzer": "french",
                "fields": {
                    "keyword": {"type": "keyword"}
                }
            },
            "missions": {
                "type":     "text",
                "analyzer": "french"
            },

            # ── Champs exacts (filtres) ────────────────────────
            # Ces champs ne sont pas analysés — valeur exacte uniquement.
            "entreprise":          {"type": "keyword"},
            "localisation_ville":  {"type": "keyword"},
            "localisation_dept":   {"type": "keyword"},
            "type_contrat":        {"type": "keyword"},
            "teletravail":         {"type": "keyword"},
            "secteur":             {"type": "keyword"},
            "rome_code":           {"type": "keyword"},

            # ── Champs numériques ──────────────────────────────
            # Pour les filtres de plage : salaire >= 40000
            "salaire_min":    {"type": "integer"},
            "salaire_max":    {"type": "integer"},
            "experience_min": {"type": "integer"},

            # ── Coordonnées GPS ───────────────────────────────
            # geo_point permet des recherches géographiques
            # "offres dans un rayon de 50km autour de Paris"
            "localisation": {"type": "geo_point"},

            # ── Dates ─────────────────────────────────────────
            "date_publication": {"type": "date"},
            "date_extraction":  {"type": "date"},
        }
    },
    "settings": {
        "number_of_shards":   1,  # 1 shard suffit pour un projet de formation
        "number_of_replicas": 0,  # 0 replica en développement local
    }
}


# ─────────────────────────────────────────────────────────────
# CRÉATION DE L'INDEX
# ─────────────────────────────────────────────────────────────

def creer_index(
    client: Elasticsearch,
    nom_index: str = NOM_INDEX):
    """
    Crée l'index Elasticsearch avec le mapping défini.
    Si l'index existe déjà, ne fait rien — idempotent.
    """
    if client.indices.exists(index=nom_index):
        logging.info(f"Index '{nom_index}' existe déjà — pas de recréation.")
        return

    client.indices.create(index=nom_index, body=MAPPING)
    logging.info(f"Index '{nom_index}' créé avec succès.")
