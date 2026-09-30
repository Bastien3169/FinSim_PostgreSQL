import streamlit as st
from base64 import b64encode
from src.api_client.api_client import *
from src.components.components_views import *


BACKTESTING_URL = "https://backtesting.up.railway.app/"

ENCART_BACKTESTING = f"""
<div class="main-container">
  <div style="border:2px solid #00B388; border-radius:10px; padding:18px 24px;
              margin:40px auto 10px; max-width:760px;">
    <div style="color:#00B388; font-size:1.3rem; font-weight:700; margin-bottom:4px;">
      📈 Plutôt trading ?
    </div>
    <p style="padding:0; margin:0 0 14px;">
      Construisez et testez vos stratégies (RSI, moyennes mobiles, MACD, Bollinger),
      optimisez take profit et stop loss, et vérifiez qu'elles tiennent sur plusieurs actifs.
    </p>
    <a href="{BACKTESTING_URL}" target="_blank" rel="noopener"
       style="display:inline-block; padding:8px 18px; border:1px solid #00B388;
              border-radius:5px; color:#00B388; text-decoration:none; font-weight:600;">
      Découvrir Backtesting →
    </a>
  </div>
</div>
"""


def home_page(go_to, auth_manager):

    load_css()

    # ---------------------------------------------------------
    # TITRE
    # ---------------------------------------------------------
    st.markdown( """<div class="main-container"><h1>🏠 Bienvenue sur FinSim</h1></div>""",unsafe_allow_html=True,)

    # ---------------------------------------------------------
    # IMAGE
    # ---------------------------------------------------------
    # Logo vectoriel (SVG) : net à toutes les tailles, fond transparent, couleurs du CSS
    image_path = "src/assets/images/finsim_logo.svg"
    with open(image_path, "rb") as img_file:
        encoded = b64encode(img_file.read()).decode()

    st.markdown(f""" <div class="main-container"><img src="data:image/svg+xml;base64,{encoded}" class="center-image" alt="FinSim"> </div> """, unsafe_allow_html=True,)

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
            Outil pédagogique sans risque : aucun conseil en investissement.<br><br>
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
    # ENCART BACKTESTING (site frère, orienté trading)
    # ---------------------------------------------------------
    st.markdown(ENCART_BACKTESTING, unsafe_allow_html=True)

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
