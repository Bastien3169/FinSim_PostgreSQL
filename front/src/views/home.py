import streamlit as st
from base64 import b64encode
from src.api_client.api_client import *
from src.components.components_views import *


def home_page(go_to, auth_manager):

    load_css()

    # ---------------------------------------------------------
    # TITRE
    # ---------------------------------------------------------
    st.markdown( """<div class="main-container"><h1>🏠 Bienvenue sur FinSim</h1></div>""",unsafe_allow_html=True,)

    # ---------------------------------------------------------
    # IMAGE
    # ---------------------------------------------------------
    image_path = "src/assets/images/finsim.png"
    with open(image_path, "rb") as img_file:
        encoded = b64encode(img_file.read()).decode()

    st.markdown(f""" <div class="main-container"><img src="data:image/png;base64,{encoded}" class="center-image"> </div> """, unsafe_allow_html=True,)

    # ---------------------------------------------------------
    # TEXTE INTRO
    # ---------------------------------------------------------
    st.markdown(
        """
        <div class="main-container">
            <p>
            Analysez les performances historiques des indices, actions, cryptos et ETF en un clin d'œil.<br>
            Simulez vos stratégies DCA (investissement progressif) ou Lump Sum (investissement en une fois).<br>
            Construisez votre portefeuille pour simuler des rendements passés.<br>
            Outil pédagogique sans risque : apprenez à investir sans conseil financier.<br><br>
            Bonne visite !
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------------------------------------------------------
    # BOUTON LOGOUT
    # ---------------------------------------------------------
    if st.session_state.get("auth"):
        if st.button("🔓 Déconnection"):
            auth_manager.logout()  # supprime la session dans la BDD et le cookie
            # Nettoie session_state
            for key in ["auth", "user_role", "user_email"]:
                if key in st.session_state:
                    del st.session_state[key]
            go_to("auth")  # redirige vers la page login
            st.stop()  # stoppe le script pour forcer reload


    # ---------------------------------------------------------
    # TUILES DE NAVIGATION
    # ---------------------------------------------------------
    st.markdown("## 📊 Explorer les actifs")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📈 Indices", use_container_width=True):
            go_to("indices")
            st.rerun()

    with col2:
        if st.button("🏢 Stocks", use_container_width=True):
            go_to("stocks")
            st.rerun()

    with col3:
        if st.button("💼 ETFs", use_container_width=True):
            go_to("etfs")
            st.rerun()

    col4, col5, col6 = st.columns(3)

    with col4:
        if st.button("₿ Cryptos", use_container_width=True):
            go_to("cryptos")
            st.rerun()

    with col5:
        if st.button("👛 Simulation Portefeuille", use_container_width=True):
            go_to("comparaison_actifs")
            st.rerun()

    with col6:
        if st.button("⚖️ DCA vs LS", use_container_width=True):
            go_to("dca_vs_ls")
            st.rerun() 

    col7, col8, col9 = st.columns(3)
    # ---------------------------------------------------------
    # TUile ADMIN (VISIBLE UNIQUEMENT SI ADMIN)
    # ---------------------------------------------------------
    if st.session_state.get("user_role") == "admin":
        with col8:
            if st.button("🛠️ Admin", use_container_width=True):
                go_to("admin")
                st.rerun()
    
    # ---------------------------------------------------------
    # POLITIQUE DE CONFIDENTIALITÉ
    # ---------------------------------------------------------
    st.markdown("---")
    if st.button("📄 Politique de confidentialité", key="privacy_link", help="Aller à la politique de confidentialité"):
        go_to("confidentialite")
        st.rerun()

    # ---------------------------------------------------------
    # FOOTER
    # ---------------------------------------------------------
    footer()
