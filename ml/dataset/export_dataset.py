import pandas as pd
import psycopg2
from pathlib import Path
from datetime import datetime
from config import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, \
                   POSTGRES_USER, POSTGRES_PASSWORD

RACINE      = Path(__file__).parent.parent.parent
DATASET_DIR = RACINE / "data" / "ml" / "dataset"
DATASET_DIR.mkdir(parents=True, exist_ok=True)
TIMESTAMP   = datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_PATH = DATASET_DIR / f"dataset_ml_csv_{TIMESTAMP}.csv"


def export_csv_dataset():
    conn = psycopg2.connect(
        host=POSTGRES_HOST, port=POSTGRES_PORT,
        dbname=POSTGRES_DB, user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

    # Jointure des 3 tables en une seule requête
    query = """
        SELECT
            o.id,
            o.source,
            o.titre,
            o.description,
            o.type_contrat,
            o.localisation_ville,
            o.salaire_min,
            o.salaire_max,
            o.experience_min,
            o.secteur,
            o.date_publication,
            ml.ml_keyword,
            ml.ml_label_binaire,
            ml.ml_label_categorie,
            STRING_AGG(DISTINCT c.competence, ', ') AS competences,
            STRING_AGG(DISTINCT m.mission,    ' | ') AS missions
        FROM offres o
        LEFT JOIN competences c ON c.offre_id = o.id
        LEFT JOIN missions    m ON m.offre_id = o.id
        LEFT JOIN ml_labels   ml ON ml.offre_id = o.id
        GROUP BY o.id, o.source, o.titre, o.description,
                o.type_contrat, o.localisation_ville,
                o.salaire_min, o.salaire_max, o.experience_min,
                o.secteur, o.date_publication, ml.ml_keyword,
                ml.ml_label_binaire, ml.ml_label_categorie
    """

    df = pd.read_sql(query, conn)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    print(f"Dataset exporté : {len(df)} offres")

    conn.close()


if __name__ == "__main__":
    export_csv_dataset()
