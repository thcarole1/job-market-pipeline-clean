# streamlit/app.py
"""
Point d'entrée Streamlit — Job Market Explorer.

Lancement :
    streamlit run streamlit/app.py
"""

import streamlit as st

st.set_page_config(
    page_title = "Job Market Explorer",
    page_icon  = "💼",
    layout     = "wide",
)

# Rediriger vers la page de recherche par défaut
from vues.recherche import afficher_page_recherche
afficher_page_recherche()
