# storage/sql/create_tables.py
import psycopg2
from config import POSTGRES_HOST,POSTGRES_PORT,POSTGRES_DB,POSTGRES_USER,POSTGRES_PASSWORD,SCHEMA_PATH

def connecter_postgresql():
    """Crée et retourne une connexion PostgreSQL."""
    return psycopg2.connect(
        host     = POSTGRES_HOST,
        port     = POSTGRES_PORT,
        dbname   = POSTGRES_DB,
        user     = POSTGRES_USER,
        password = POSTGRES_PASSWORD,
    )

def creer_tables():
    """
    Lit le fichier schema.sql et exécute toutes les instructions.
    Utilise IF NOT EXISTS — safe à appeler plusieurs fois.
    """
    conn   = None
    cursor = None

    try:
        # Connexion
        conn   = connecter_postgresql()
        cursor = conn.cursor()

        # Lire le fichier SQL
        sql = SCHEMA_PATH.read_text(encoding="utf-8")

        # Exécuter toutes les instructions d'un coup
        cursor.execute(sql)

        # Valider les changements
        conn.commit()

        print("Tables creees avec succes :")
        print("  offres, competences, missions, avantages")
        print("  + tous les index")

    except Exception as e:
        print(f"Erreur lors de la creation des tables : {e}")
        if conn:
            conn.rollback()
        raise

    finally:
        # Toujours fermer proprement
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    creer_tables()
