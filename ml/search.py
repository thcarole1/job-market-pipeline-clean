# ml/search.py

import logging
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

from config import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB,
    POSTGRES_USER, POSTGRES_PASSWORD,
)
from ml.retrieval.tfidf_retriever import TFIDFRetriever
from ml.retrieval.base_retriever import FiltresRecherche

logging.basicConfig(
    level  = logging.INFO,
    format = "%(asctime)s — %(levelname)s — %(message)s"
)


def charger_offres() -> pd.DataFrame:
    """Charge les offres depuis PostgreSQL via SQLAlchemy."""
    engine = create_engine(
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    df = pd.read_sql("""
        SELECT
            o.id,
            o.titre,
            o.description,
            o.localisation_ville,
            o.type_contrat,
            o.salaire_min,
            o.salaire_max,
            o.teletravail,
            o.source,
            STRING_AGG(DISTINCT c.competence, ' ') AS competences
        FROM offres o
        LEFT JOIN competences c ON c.offre_id = o.id
        GROUP BY
            o.id, o.titre, o.description,
            o.localisation_ville, o.type_contrat,
            o.salaire_min, o.salaire_max,
            o.teletravail, o.source
    """, engine)

    df["texte"] = (
        df["titre"].fillna("")       + " " +
        df["titre"].fillna("")       + " " +
        df["description"].fillna("") + " " +
        df["competences"].fillna("")
    )
    logging.info(f"{len(df)} offres chargées.")
    return df


class SearchEngine:
    """
    Moteur de recherche TF-IDF uniquement.

    Utilisation :
        engine = SearchEngine()
        engine.initialiser()
        resultats = engine.search("data engineer Paris", n=10)
    """

    def __init__(self):
        self.tfidf = None
        self._pret = False

    def initialiser(self, df_offres: pd.DataFrame = None):
        """Charge les offres et initialise le moteur TF-IDF."""
        if df_offres is None:
            df_offres = charger_offres()

        if df_offres.empty:
            raise ValueError("Aucune offre disponible.")

        self.tfidf = TFIDFRetriever(df_offres)
        self._pret = True
        logging.info("SearchEngine TF-IDF prêt.")

    def _verifier_pret(self):
        if not self._pret:
            raise RuntimeError(
                "SearchEngine non initialisé. Appeler initialiser() d'abord."
            )

    def search(
        self,
        requete:     str,
        n:           int  = 10,
        ville:       str  = None,
        contrat:     str  = None,
        salaire_min: int  = None,
        teletravail: str  = None,
    ) -> list[dict]:
        """Recherche avec filtres optionnels."""
        self._verifier_pret()
        filtres = FiltresRecherche(
            ville       = ville,
            contrat     = contrat,
            salaire_min = salaire_min,
            teletravail = teletravail,
        )
        return self.tfidf.search(requete, n, filtres)

    def mettre_a_jour(self, df_offres: pd.DataFrame = None):
        """Met à jour le moteur avec les nouvelles offres."""
        self._verifier_pret()
        if df_offres is None:
            df_offres = charger_offres()
        self.tfidf.mettre_a_jour(df_offres)
        logging.info("SearchEngine mis à jour.")
