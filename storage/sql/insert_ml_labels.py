# storage/sql/insert_ml_labels.py
import logging

def inserer_ml_labels(offre: dict, cursor) -> int:
    """
    Insère les labels ML dans la table ml_labels.
    ON CONFLICT DO NOTHING — si (offre_id, keyword) existe déjà, on ignore.
    """
    inseres = 0
    # Ne traiter que les offres avec des labels ML
    try:
        cursor.execute("""
            INSERT INTO ml_labels
                (offre_id, ml_keyword, ml_label_binaire, ml_label_categorie)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (offre_id, ml_keyword) DO NOTHING
        """, (
            offre.get("id"),
            offre.get("ml_keyword"),
            offre.get("ml_label_binaire"),
            offre.get("ml_label_categorie")
        ))
        inseres += 1

    except Exception as e:
        logging.error(f"Erreur ml_label offre {offre.get('id')} : {e}")

    return inseres
