# ml/retrieval/tfidf_retriever.py

import logging
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ml.retrieval.base_retriever import BaseRetriever, FiltresRecherche

logging.basicConfig(
    level  = logging.INFO,
    format = "%(asctime)s — %(levelname)s — %(message)s"
)


class TFIDFRetriever(BaseRetriever):
    """
    Moteur TF-IDF + Similarité cosinus avec filtres.

    Initialisation :
        retriever = TFIDFRetriever(df_offres)

    Recherche :
        resultats = retriever.search("data engineer Python", n=10)
        resultats = retriever.search(
            "data engineer",
            n       = 10,
            filtres = FiltresRecherche(ville="Paris", contrat="CDI")
        )
    """

    def __init__(self, df_offres: pd.DataFrame):
        self.df    = df_offres.reset_index(drop=True)
        self.tfidf = TfidfVectorizer(
            max_features = 10000,
            ngram_range  = (1, 2),
            sublinear_tf = True,
        )
        logging.info("TFIDFRetriever — vectorisation du corpus...")
        self.X = self.tfidf.fit_transform(self.df["texte"])
        logging.info(f"TFIDFRetriever prêt — matrice {self.X.shape}")

    @property
    def nom(self) -> str:
        return "TF-IDF + Cosinus"

    def _appliquer_filtres(
        self,
        scores:  np.ndarray,
        filtres: FiltresRecherche,
    ) -> np.ndarray:
        """
        Met le score à -1 pour les offres qui ne correspondent
        pas aux filtres — elles seront exclues des résultats.
        """
        if filtres is None or filtres.est_vide():
            return scores

        scores_filtres = scores.copy()

        for idx, row in self.df.iterrows():
            exclure = False

            if filtres.ville and filtres.ville.lower() not in \
               str(row.get("localisation_ville", "")).lower():
                exclure = True

            if filtres.contrat and \
               str(row.get("type_contrat", "")).upper() != filtres.contrat.upper():
                exclure = True

            if filtres.salaire_min and row.get("salaire_min") is not None:
                if float(row.get("salaire_min", 0)) < filtres.salaire_min:
                    exclure = True

            if filtres.teletravail and \
               str(row.get("teletravail", "")).lower() != filtres.teletravail.lower():
                exclure = True

            if exclure:
                scores_filtres[idx] = -1.0

        return scores_filtres

    def search(
        self,
        requete:  str,
        n:        int              = 10,
        filtres:  FiltresRecherche = None,
    ) -> list[dict]:
        """
        Recherche les n offres les plus similaires à la requête.

        Ordre :
            1. Vectoriser la requête
            2. Calculer les scores cosinus sur tout le corpus
            3. Appliquer les filtres (score → -1 si exclu)
            4. Retourner les n meilleurs scores restants
        """
        x_requete      = self.tfidf.transform([requete])
        scores         = cosine_similarity(x_requete, self.X).flatten()
        scores_filtres = self._appliquer_filtres(scores, filtres)
        indices        = scores_filtres.argsort()[-n:][::-1]

        # Exclure les offres filtrées
        indices = [i for i in indices if scores_filtres[i] >= 0]

        resultats = []
        for idx in indices:
            offre = self.df.iloc[idx]
            resultats.append({
                "id":                str(offre["id"]),
                "titre":             str(offre.get("titre", "")),
                "localisation_ville":str(offre.get("localisation_ville", "") or ""),
                "type_contrat":      str(offre.get("type_contrat", "") or ""),
                "salaire_min":       _nettoyer_valeur(offre.get("salaire_min")),
                "salaire_max":       _nettoyer_valeur(offre.get("salaire_max")),
                "teletravail":       str(offre.get("teletravail", "") or ""),
                "source":            str(offre.get("source", "") or ""),
                "score":             round(float(scores_filtres[idx]), 4),
            })

        return resultats

    def mettre_a_jour(self, df_offres: pd.DataFrame):
        """Reconstruit la matrice TF-IDF avec les nouvelles offres."""
        logging.info("TFIDFRetriever — mise à jour du corpus...")
        self.df = df_offres.reset_index(drop=True)
        self.X  = self.tfidf.fit_transform(self.df["texte"])
        logging.info(f"TFIDFRetriever mis à jour — matrice {self.X.shape}")

import math

def _nettoyer_valeur(valeur):
    """
    Convertit les NaN et inf en None pour la sérialisation JSON.
    None devient null en JSON — valeur valide et lisible.
    """
    if valeur is None:
        return None
    try:
        if math.isnan(float(valeur)) or math.isinf(float(valeur)):
            return None
    except (TypeError, ValueError):
        pass
    return valeur
