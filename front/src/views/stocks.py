import streamlit as st
from src.api_client.api_client import *
from src.components.components_views import *

def stocks_page(go_to):
    # ================= CSS + Variables =================
    load_css()

    # Variables de configuration
    ACTIF_TYPE = "stock"
    ACTIF_DEFAULT = "Apple Inc."
    
    datas_actif = FinanceDatabaseStocks()
    liste_actif = datas_actif.get_list_stocks()
    infos_actif = datas_actif.get_infos_stocks(ACTIF_DEFAULT)


    # =============== Titre de la page ================
    display_page_title("LES ENTREPRISES BOURSIÈRES")
    
    # =============== Graphiques ================
    st.markdown(f"""<div class="main-container"><h2>📈 Graphiques des entreprises</h2></div>""", unsafe_allow_html=True)

    display_chart_section(datas_manager=datas_actif, liste_actifs=liste_actif, actif_default=ACTIF_DEFAULT, actif_type=ACTIF_TYPE)
    

    # =============== Rendement ================
    st.markdown(f"""<div class="main-container"><h2>💯 Rendements des entreprises (%)</h2></div>""", unsafe_allow_html=True)

    display_rendement_section(datas_manager=datas_actif,
                            infos_df=infos_actif,
                            liste_actifs=liste_actif,
                            actif_default=ACTIF_DEFAULT,
                            calculate_rendement_func=calculate_rendement,
                            style_rendement_func=style_rendement,
                            actif_type=ACTIF_TYPE,
                            default_periods=[6, 12, 24, 60, 120, 180])  # Optionnel (valeur par défaut)
    

   # =============== Composition ================
    st.markdown(f"""<div class="main-container"><h2>🗂 Infos des entreprises</h2></div>""", unsafe_allow_html=True)

    infos_actifs(datas_manager=datas_actif, liste_actifs=liste_actif,actif_default=ACTIF_DEFAULT, actif_type=ACTIF_TYPE)
    
    # =============== Bouton retour accueil ================
    bout_accueil(back_callback=go_to)

    
    # =============== Footer ================
    footer()