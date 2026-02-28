import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from src.controllers.LP_VS_DCA import *
from src.api_client.api_client import *
from src.components.components_views import *


def dca_vs_ls_page(go_to):
    ############################################ MISE EN PLACE DU CSS + IMAGE ############################################
    load_css()

    display_page_title("LUMP SUM VS DCA")
        
    ################################## CONNEXION .db ET RECUPERATION DATAS ET VARIABLES STREAMLIT ##################################
        
    # Création d'une instance de l'objet
    datas_indices = FinanceDatabaseIndice()
    
    # Appel méthodes
    liste_indices = datas_indices.get_list_indices()

    
################################## STREAMLIT ##################################
    st.markdown(f"""<div class="main-container"><h2>⚙️ Paramètres pour la simulation</h2></div>""", unsafe_allow_html=True)
    
    # Sélection de l’indice
    indice_default = "S&P 500"
    ticker = st.selectbox("Choisissez un indice pour le graphique", liste_indices, index=liste_indices.index(indice_default)) # arg1 : nom liste déroulante / arg2 : liste pour la liste déroulante / arg3 : opt par défaut de l'actif pour visualisation graph.

    # Paramètres utilisateur
    somme_investie = st.number_input("Montant à investir (€)", value=100000, step=1000)
    
    # Durées d'investissement (en années) : saisie de l'utilisateur
    durees_input = st.text_input("⏳ Durées d'investissement (en années)", "5,10,15,20,25")  # Format : 5,10,15,...
    durees = [int(annee.strip()) for annee in durees_input.split(",")]
    
    # Mois de DCA : saisie de l'utilisateur
    mois_dca_list_input = st.text_input("📆 Mois de DCA", "6,12,24")  # Format : 6,12,24,...
    mois_dca_list = [int(mois.strip()) for mois in mois_dca_list_input.split(",")]

    # Prend l'hist des prix du ticker
    data_financiere = datas_indices.get_prix_date(ticker)
    
    if st.button("Lancer la simulation"):
        with st.spinner("Calcul en cours..."):
            df_resultats = calcul_rendements_durations(durees, mois_dca_list, somme_investie, ticker)
            df = calcul_multiple_rendements(durees, mois_dca_list, somme_investie, ticker)
            

            st.markdown(f"""<div class="main-container"><h2>📊 Montant de l'investissement en fonction de la durée du placement</h2></div>""", unsafe_allow_html=True)
            fig = graphe_barre(df_resultats)
            st.markdown(f"""<div class="main-container"><h3>Graphique du montant de l'investissement en fonction de la durée du placement</h3></div>""", unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("---")
            st.markdown(f"""<div class="main-container"><h3>Tableau du montant de l'investissement en fonction de la durée du placement</h3></div>""", unsafe_allow_html=True)
            st.dataframe(df_resultats, use_container_width=True)


            st.markdown(f"""<div class="main-container"><h2>📈 Evolution de l'actif en fonction du temps</h2></div>""", unsafe_allow_html=True)
            fig = graphe_line(df, somme_investie)
            st.markdown(f"""<div class="main-container"><h3>Graphique de l'évolution de l'actif en fonction du temps</h3></div>""", unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("---")
            st.markdown(f"""<div class="main-container"><h3>Tableau de l'évolution de l'actif en fonction du temps</h3></div>""", unsafe_allow_html=True)
            st.dataframe(df.tail(100), use_container_width=True)
    
    
    else:
        df_resultats = calcul_rendements_durations(durees=range(1, 26), mois_dca_list=[6, 12, 18, 24], somme_investie=100000, ticker="S&P 500")
        df = calcul_multiple_rendements(durees = [25, 20, 15, 10,5], mois_dca_list = [6, 12, 18, 24], somme_investie  = 100000, ticker = "S&P 500")


        st.markdown(f"""<div class="main-container"><h2>📊 Gains par durées d'investissement</h2></div>""", unsafe_allow_html=True)
        fig = graphe_barre(df_resultats)
        st.markdown(f"""<div class="main-container"><h3>Graphique des gains par durées d'investissement</h3></div>""", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("---")
        st.markdown(f"""<div class="main-container"><h3>Tableau des gains par durées d'investissement</h3></div>""", unsafe_allow_html=True)
        st.dataframe(df_resultats, use_container_width=True)


        st.markdown(f"""<div class="main-container"><h2>📈 Evolution de l'actif en fonction du temps</h2></div>""", unsafe_allow_html=True)
        fig = graphe_line(df, somme_investie)
        st.markdown(f"""<div class="main-container"><h3>Graphique de l'évolution de l'actif en fonction du temps</h3></div>""", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("---")
        st.markdown(f"""<div class="main-container"><h3>Tableau de l'évolution de l'actif en fonction du temps</h3></div>""", unsafe_allow_html=True)
        st.dataframe(df.tail(100), use_container_width=True)
    

        # =============== Bouton retour accueil ================
    bout_accueil(back_callback=go_to)

        
        # =============== Footer ================
    footer()