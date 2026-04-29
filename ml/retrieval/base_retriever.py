# ml/retrieval/base_retriever.py

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class FiltresRecherche:
    """Critères de filtrage communs à tous les moteurs."""
    ville:       str = None
    contrat:     str = None
    salaire_min: int = None
    teletravail: str = None

    def est_vide(self) -> bool:
        return all([
            self.ville       is None,
            self.contrat     is None,
            self.salaire_min is None,
            self.teletravail is None,
        ])


class BaseRetriever(ABC):
    """Interface commune à tous les moteurs."""

    @property
    @abstractmethod
    def nom(self) -> str:
        pass

    @abstractmethod
    def search(
        self,
        requete:  str,
        n:        int              = 10,
        filtres:  FiltresRecherche = None,
    ) -> list[dict]:
        pass
