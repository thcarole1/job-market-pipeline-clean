# streamlit/vues/recherche.py
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
    # INITIALISATION SESSION STATE
    # ─────────────────────────────────────────────────────────

    if "offre_selectionnee" not in st.session_state:
        st.session_state["offre_selectionnee"] = None
    if "details_cache" not in st.session_state:
        st.session_state["details_cache"] = {}

    # ─────────────────────────────────────────────────────────
    # FORMULAIRE DE RECHERCHE
    # ─────────────────────────────────────────────────────────

    with st.form("recherche"):
        q = st.text_input(
            "🔍 Mots-clés",
            placeholder = "data engineer Python Paris...",
            help        = "Décrivez librement le poste recherché",
        )

        st.markdown("**Filtres**")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            ville = st.text_input("📍 Ville", placeholder="Paris, Lyon...")

        with col2:
            contrat = st.selectbox(
                "📄 Contrat",
                options     = ["", "CDI", "CDD", "Alternance", "Stage", "Freelance"],
                format_func = lambda x: "Tous" if x == "" else x,
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
                type                = "primary",
                use_container_width = True,
            )

    # ─────────────────────────────────────────────────────────
    # APPEL À L'API
    # ─────────────────────────────────────────────────────────

    if lancer:

        if not q.strip():
            st.warning("Veuillez entrer des mots-clés pour lancer la recherche.")
            return

        params = {"q": q, "taille": int(taille)}
        if ville.strip():        params["ville"]       = ville.strip()
        if contrat:              params["contrat"]     = contrat
        if salaire_min > 0:      params["salaire_min"] = int(salaire_min)
        if teletravail:          params["teletravail"] = teletravail

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
                st.error("❌ Impossible de contacter l'API. Vérifiez que Docker tourne.")
                return
            except requests.exceptions.Timeout:
                st.error("❌ L'API met trop de temps à répondre.")
                return
            except Exception as e:
                st.error(f"❌ Erreur : {e}")
                return

        # Sauvegarder les résultats en session
        st.session_state["resultats"]        = data.get("resultats", [])
        st.session_state["nb"]               = data.get("nb", 0)
        st.session_state["filtres"]          = data.get("filtres", {})
        st.session_state["offre_selectionnee"] = None  # reset sélection

    # ─────────────────────────────────────────────────────────
    # AFFICHAGE DES RÉSULTATS
    # ─────────────────────────────────────────────────────────

    if "resultats" not in st.session_state:
        return

    resultats = st.session_state["resultats"]
    nb        = st.session_state["nb"]
    filtres   = st.session_state.get("filtres", {})

    if not resultats:
        st.warning("Aucun résultat trouvé pour cette recherche.")
        return

    # En-tête résultats
    col_info, col_filtres = st.columns([2, 3])
    with col_info:
        st.success(f"**{nb} offre{'s' if nb > 1 else ''}** trouvée{'s' if nb > 1 else ''}")
    with col_filtres:
        if filtres:
            tags = " ".join([
                f"`{k} : {v}`"
                for k, v in filtres.items() if v is not None
            ])
            st.markdown(f"Filtres actifs : {tags}")

    st.divider()

    # ── Deux colonnes : liste à gauche, détail à droite ───────
    col_liste, col_detail = st.columns([1, 1])

    with col_liste:
        for i, offre in enumerate(resultats, start=1):
            _afficher_carte_offre(i, offre)

    with col_detail:
        offre_id = st.session_state.get("offre_selectionnee")
        if offre_id:
            _afficher_detail_offre(offre_id)
        else:
            st.info("👈 Cliquez sur une offre pour voir son détail.")


# ─────────────────────────────────────────────────────────────
# CARTE OFFRE
# ─────────────────────────────────────────────────────────────

def _afficher_carte_offre(rang: int, offre: dict):
    """Affiche une offre sous forme de carte avec bouton de détail."""

    titre    = offre.get("titre", "Titre non renseigné")
    ville    = offre.get("localisation_ville", "")
    contrat  = offre.get("type_contrat", "")
    score    = offre.get("score", 0)
    offre_id = offre.get("id", "")

    label_ville   = f"📍 {ville}"   if ville   else ""
    label_contrat = f"📄 {contrat}" if contrat else ""

    # La carte est sélectionnée si c'est l'offre affichée à droite
    est_selectionnee = st.session_state.get("offre_selectionnee") == offre_id

    header = f"**{rang}.** {titre}"
    if label_ville or label_contrat:
        header += f"  —  {label_ville}  {label_contrat}"

    with st.expander(header, expanded=est_selectionnee):

        col1, col2, col3 = st.columns(3)

        with col1:
            sal_min = offre.get("salaire_min")
            sal_max = offre.get("salaire_max")
            if sal_min:
                salaire = f"{int(sal_min):,}€".replace(",", " ")
                if sal_max:
                    salaire += f" — {int(sal_max):,}€".replace(",", " ")
            else:
                salaire = "N/A"
            st.metric("💶 Salaire", salaire)

        with col2:
            teletravail = offre.get("teletravail", "")
            label_tt = {
                "remote": "🏠 Remote",
                "hybrid": "🏠 Hybride",
                "onsite": "🏢 Présentiel",
            }.get(teletravail, "N/A")
            st.metric("🏠 Télétravail", label_tt)

        with col3:
            st.metric("🎯 Score", f"{score:.3f}")

        st.caption(f"Source : {offre.get('source', 'N/A')}")

        # ── Bouton — stocke l'id dans session_state ───────────
        if offre_id:
            if st.button(
                "📋 Voir le détail",
                key  = f"detail_{offre_id}_{rang}",
                type = "primary" if est_selectionnee else "secondary",
            ):
                # Mémoriser l'offre sélectionnée
                # Si déjà sélectionnée → fermer (toggle)
                if st.session_state["offre_selectionnee"] == offre_id:
                    st.session_state["offre_selectionnee"] = None
                else:
                    st.session_state["offre_selectionnee"] = offre_id
                st.rerun()


# ─────────────────────────────────────────────────────────────
# DÉTAIL D'UNE OFFRE
# ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def _charger_detail(offre_id: str) -> dict:
    """
    Charge le détail depuis PostgreSQL via l'API.
    Mis en cache 5 minutes.
    """
    response = requests.get(
        f"{API_URL}/jobs/{offre_id}",
        timeout = 10,
    )
    response.raise_for_status()
    return response.json()


def _afficher_detail_offre(offre_id: str):
    """Affiche le détail complet dans la colonne droite."""

    with st.spinner("Chargement du détail..."):
        try:
            offre = _charger_detail(offre_id)
        except Exception as e:
            st.error(f"Impossible de charger le détail : {e}")
            return

    if not offre:
        st.error("Détail non disponible.")
        return

    st.subheader(f"📋 {offre.get('titre', 'Détail offre')}")

    # Infos principales
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📍 Ville",    offre.get("localisation_ville") or "N/A")
        st.metric("📄 Contrat",  offre.get("type_contrat") or "N/A")
    with col2:
        sal_min = offre.get("salaire_min")
        sal_max = offre.get("salaire_max")
        if sal_min:
            salaire = f"{int(sal_min):,}€".replace(",", " ")
            if sal_max:
                salaire += f" — {int(sal_max):,}€".replace(",", " ")
        else:
            salaire = "Non renseigné"
        st.metric("💶 Salaire", salaire)

        teletravail = offre.get("teletravail", "")
        label_tt = {
            "remote": "🏠 100% remote",
            "hybrid": "🏠 Hybride",
            "onsite": "🏢 Présentiel",
        }.get(teletravail, "N/A")
        st.metric("🏠 Télétravail", label_tt)

    st.divider()

    # Compétences
    competences = offre.get("competences", [])
    if competences:
        st.markdown("**🛠️ Compétences requises**")
        st.markdown(" ".join([f"`{c}`" for c in competences[:20]]))
        st.markdown("")

    # Description
    description = offre.get("description", "")
    if description:
        st.markdown("**📝 Description**")
        st.markdown(description[:2000])
        if len(description) > 2000:
            st.caption("(description tronquée à 2000 caractères)")

    # Missions
    missions = offre.get("missions", [])
    if missions:
        st.markdown("**🎯 Missions**")
        for mission in missions[:5]:
            st.markdown(f"- {mission}")

    st.divider()

    # Lien + bouton fermer
    col_url, col_close = st.columns([2, 1])
    with col_url:
        url = offre.get("url", "")
        if url:
            st.link_button("🔗 Voir l'offre originale", url)
    with col_close:
        if st.button("✕ Fermer", key=f"close_{offre_id}"):
            st.session_state["offre_selectionnee"] = None
            st.rerun()
