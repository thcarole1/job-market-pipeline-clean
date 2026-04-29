# streamlit/pages/recherche.py
"""
Page de recherche d'offres d'emploi.
Consomme l'API FastAPI via requests.
"""

import streamlit as st
import requests

API_URL = "http://localhost:8000"


def afficher_page_recherche():

    st.title("💼 Job Market Explorer")
    st.caption("Recherche d'offres d'emploi — propulsé par TF-IDF")

    # ─────────────────────────────────────────────────────────
    # FORMULAIRE DE RECHERCHE
    # ─────────────────────────────────────────────────────────

    with st.form("recherche"):

        # Barre de recherche principale
        q = st.text_input(
            "🔍 Mots-clés",
            placeholder = "data engineer Python Paris...",
            help        = "Décrivez librement le poste recherché",
        )

        st.markdown("**Filtres**")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            ville = st.text_input(
                "📍 Ville",
                placeholder = "Paris, Lyon...",
            )

        with col2:
            contrat = st.selectbox(
                "📄 Contrat",
                options      = ["", "CDI", "CDD", "Alternance", "Stage", "Freelance"],
                index        = 0,
                format_func  = lambda x: "Tous" if x == "" else x,
            )

        with col3:
            salaire_min = st.number_input(
                "💶 Salaire min (€/an)",
                min_value = 0,
                max_value = 200000,
                value     = 0,
                step      = 5000,
            )

        with col4:
            teletravail = st.selectbox(
                "🏠 Télétravail",
                options     = ["", "remote", "hybrid", "onsite"],
                index       = 0,
                format_func = lambda x: {
                    "":       "Tous",
                    "remote": "100% remote",
                    "hybrid": "Hybride",
                    "onsite": "Présentiel",
                }.get(x, x),
            )

        col_nb, col_btn = st.columns([1, 3])
        with col_nb:
            taille = st.number_input(
                "Nombre de résultats",
                min_value = 1,
                max_value = 50,
                value     = 10,
            )
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            lancer = st.form_submit_button(
                "🔍 Rechercher",
                type            = "primary",
                use_container_width = True,
            )

    # ─────────────────────────────────────────────────────────
    # APPEL À L'API
    # ─────────────────────────────────────────────────────────

    if lancer:

        if not q.strip():
            st.warning("Veuillez entrer des mots-clés pour lancer la recherche.")
            return

        # Construire les paramètres
        params = {"q": q, "taille": int(taille)}
        if ville.strip():
            params["ville"]       = ville.strip()
        if contrat:
            params["contrat"]     = contrat
        if salaire_min > 0:
            params["salaire_min"] = int(salaire_min)
        if teletravail:
            params["teletravail"] = teletravail

        # Appel API
        with st.spinner("Recherche en cours..."):
            try:
                response = requests.get(
                    f"{API_URL}/jobs/search",
                    params  = params,
                    timeout = 30,
                )
                response.raise_for_status()
                data = response.json()

            except requests.exceptions.ConnectionError:
                st.error(
                    "❌ Impossible de contacter l'API. "
                    "Vérifiez que le conteneur Docker est démarré."
                )
                return
            except requests.exceptions.Timeout:
                st.error("❌ L'API met trop de temps à répondre.")
                return
            except requests.exceptions.HTTPError as e:
                st.error(f"❌ Erreur API : {e}")
                return
            except Exception as e:
                st.error(f"❌ Erreur inattendue : {e}")
                return

        # ─────────────────────────────────────────────────────
        # AFFICHAGE DES RÉSULTATS
        # ─────────────────────────────────────────────────────

        resultats = data.get("resultats", [])
        nb        = data.get("nb", 0)
        filtres   = data.get("filtres", {})

        # En-tête résultats
        col_info, col_filtres = st.columns([2, 3])
        with col_info:
            if nb == 0:
                st.warning("Aucun résultat trouvé pour cette recherche.")
                return
            st.success(f"**{nb} offre{'s' if nb > 1 else ''}** trouvée{'s' if nb > 1 else ''}")

        with col_filtres:
            if filtres:
                tags = " ".join([
                    f"`{k} : {v}`"
                    for k, v in filtres.items()
                    if v is not None
                ])
                st.markdown(f"Filtres actifs : {tags}")

        st.divider()

        # Cartes résultats
        for i, offre in enumerate(resultats, start=1):
            _afficher_carte_offre(i, offre)


def _afficher_carte_offre(rang: int, offre: dict):
    """Affiche une offre sous forme de carte expansible."""

    # Construire le titre de l'expander
    titre        = offre.get("titre", "Titre non renseigné")
    ville        = offre.get("localisation_ville", "")
    contrat      = offre.get("type_contrat", "")
    score        = offre.get("score", 0)

    label_ville   = f"📍 {ville}"  if ville   else ""
    label_contrat = f"📄 {contrat}" if contrat else ""
    label_score   = f"Score : {score:.3f}"

    header = f"**{rang}.** {titre}"
    if label_ville or label_contrat:
        header += f"  —  {label_ville}  {label_contrat}"

    with st.expander(header, expanded=(rang <= 3)):

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "📍 Ville",
                offre.get("localisation_ville") or "N/A"
            )
        with col2:
            st.metric(
                "📄 Contrat",
                offre.get("type_contrat") or "N/A"
            )
        with col3:
            sal_min = offre.get("salaire_min")
            sal_max = offre.get("salaire_max")
            if sal_min:
                salaire = f"{int(sal_min):,}€".replace(",", " ")
                if sal_max:
                    salaire += f" — {int(sal_max):,}€".replace(",", " ")
            else:
                salaire = "Non renseigné"
            st.metric("💶 Salaire", salaire)

        with col4:
            teletravail = offre.get("teletravail", "")
            label_tt = {
                "remote": "🏠 100% remote",
                "hybrid": "🏠 Hybride",
                "onsite": "🏢 Présentiel",
            }.get(teletravail, "N/A")
            st.metric("🏠 Télétravail", label_tt)

        # Informations secondaires
        col5, col6 = st.columns(2)
        with col5:
            st.caption(f"Source : {offre.get('source', 'N/A')}")
        with col6:
            st.caption(label_score)

        # Bouton détail
        offre_id = offre.get("id", "")
        if offre_id:
            if st.button(
                "Voir le détail complet",
                key  = f"detail_{offre_id}_{rang}",
            ):
                _afficher_detail_offre(offre_id)


@st.cache_data(ttl=300)
def _charger_detail(offre_id: str) -> dict:
    """
    Charge le détail complet d'une offre depuis MongoDB via l'API.
    Résultat mis en cache 5 minutes pour éviter les appels répétés.
    """
    response = requests.get(
        f"{API_URL}/jobs/{offre_id}",
        timeout = 10,
    )
    response.raise_for_status()
    return response.json()


def _afficher_detail_offre(offre_id: str):
    """Affiche le détail complet d'une offre dans un dialogue."""
    try:
        offre = _charger_detail(offre_id)
    except Exception as e:
        st.error(f"Impossible de charger le détail : {e}")
        return

    st.markdown("---")
    st.subheader(f"📋 {offre.get('titre', 'Détail offre')}")

    # Description
    description = offre.get("description", "")
    if description:
        with st.expander("📝 Description complète", expanded=True):
            st.markdown(description[:3000])
            if len(description) > 3000:
                st.caption("(description tronquée à 3000 caractères)")

    # Compétences
    competences = offre.get("competences", [])
    if competences:
        st.markdown("**🛠️ Compétences requises**")
        st.markdown(" ".join([f"`{c}`" for c in competences[:20]]))

    # Missions
    missions = offre.get("missions", [])
    if missions:
        st.markdown("**🎯 Missions**")
        for mission in missions[:5]:
            st.markdown(f"- {mission}")

    # Lien
    url = offre.get("url", "")
    if url:
        st.link_button("🔗 Voir l'offre originale", url)
