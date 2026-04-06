


from datetime import datetime

from ingestion.francetravail.extraction_offres_brutes import extraire_offres
from ingestion.francetravail.sauvegarde_offres_brutes import sauvegarder_brut
from ingestion.francetravail.parser_offres_brutes import parser_brutes
from ingestion.francetravail.sauvegarde_offres_processed import sauvegarder_processed
# ─────────────────────────────────────────────────────────────────────
# PIPELINE COMPLET
# ─────────────────────────────────────────────────────────────────────

def pipeline_complet(
    mots_cles:    str  = "data engineer",
    nb_pages_max: int  = 5,
    avec_details: bool = False,
):
    """
    Pipeline complet : extraction → sauvegarde brute → parsing → sauvegarde processed.

    Le timestamp est généré une seule fois et partagé entre les deux fichiers
    de sortie — ce qui permet de faire le lien entre brut et processed.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ── Étape 1 : Extraction brute ────────────────────────
    print("=== ÉTAPE 1 : Extraction ===")
    offres_brutes = extraire_offres(
        mots_cles    = mots_cles,
        nb_pages_max = nb_pages_max
    )

    if not offres_brutes:
        print("Aucune offre récupérée. Arrêt.")
        return

    # ── Étape 2 : Sauvegarde brute ────────────────────────
    print("\n=== ÉTAPE 2 : Sauvegarde brute ===")
    sauvegarder_brut(offres_brutes, mots_cles, timestamp)

    # ── Étape 3 : Parsing ─────────────────────────────────
    print("\n=== ÉTAPE 3 : Parsing ===")
    offres_parsees = parser_brutes(offres_brutes)

    # ── Étape 4 : Sauvegarde processed ───────────────────
    print("\n=== ÉTAPE 4 : Sauvegarde processed ===")
    sauvegarder_processed(offres_parsees, timestamp)

    # ── Résumé ────────────────────────────────────────────
    print(f"""
╔══════════════════════════════════════╗
  Pipeline FranceTravail terminé
  Offres brutes   : {len(offres_brutes)}
  Offres parsées  : {len(offres_parsees)}
  Timestamp       : {timestamp}
╚══════════════════════════════════════╝
    """)

    return offres_parsees


# ─────────────────────────────────────────────────────────────────────
# POINT D'ENTRÉE
# ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    pipeline_complet(
        mots_cles    = "data engineer",
        nb_pages_max = 20,
        avec_details = False,  # passer à True pour les descriptions complètes
    )
