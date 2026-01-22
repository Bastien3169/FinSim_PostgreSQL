import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from base64 import b64encode # Convertir le chemin en une URL utilisable avec `st.markdown()` pour les photos
from def_app import *
#connect_to_db, get_list_actif, get_infos_actif,  get_prix_date, calculate_rendement, style_rendement, get_composition_indice
#import stocks_app  # Import du fichier contenant le code des stocks
#import indices_app  # Si tu as aussi du code pour les indices
#import etf_app  # Si tu as du code pour les ETF
#import lp_dca_app  # Si tu as du code pour DCA vs LumpSum
#import con_user_app



############################################### MISE EN PLACE DU CSS + IMAGE ###############################################

# Chargement du fichier CSS
with open("css/streamlit.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

# CSS titre principal
#st.title("📊 LES INDICES BOURSIERS")
st.markdown(f"""<div class="main-container"><h1>LES INDICES BOURSIERS</h1></div>""", unsafe_allow_html=True)

####################################### CONNEXION .db ET RECUPERATION DATAS ET VARIABLES STREAMLIT #######################################

# Connexion à la base SQLite
db_path = "sql/data_indices_stocks.db"
conn = connect_to_db(db_path)

# Mise en place des paramètre pour les fonctions des requêtes SQL
table_hist_actif = "historique_indices"
table_infos_actif = "infos_indices"

# Récupérer la liste des indices et leurs infos
liste_indices = get_list_actif(conn, table_hist_actif)
df_infos_indices = get_infos_actif(conn, table_infos_actif)

# Indice par défaut pour graph et tableau 
indice_default = "S&P 500"



############################################### GRAPHIQUE ###############################################

# CSS sous titre
#st.header("📈 Graphiques des indices")
st.markdown(f"""
<div class="main-container">
    <h2>📈 Graphiques des indices</h2>
</div>
""", unsafe_allow_html=True)

# st.selectbox permet de choisir une seule option.
default_index = indice_default # "index=indices.index(default_index)" attent un int pour index
selected_indice = st.selectbox("Choisissez un indice pour le graphique", liste_indices, index=liste_indices.index(default_index)) # arg1 : nom liste déroulante / arg2 : liste pour la liste déroulante / arg3 : opt par défaut de l'actif pour visualisation graph.

# Récupération des données "Dates" et "Close" de la base de donnée pour le graphique en dataframe
df = get_prix_date(conn, table_hist_actif, selected_indice)

# S'il y a des données dans les colonnes, graphique, sinon message d'erreur.
if not df.empty:
    fig = go.Figure(go.Scatter(x=df["Date"], y=df["Close"], mode='lines', name=selected_indice, line=dict(color='#6DBE8C', width=2)))
    fig.update_layout(title=f"Évolution de {selected_indice} - Clôture hebdomadaire", xaxis_title="Date", yaxis_title="Prix de clôture")
    st.plotly_chart(fig)
else:
    st.error("Aucune donnée trouvée pour cet indice.")



############################################### TABLEAU RENDEMENT ###############################################

# CSS sous titre
#st.header("📈 Rendements des indices (%)")
st.markdown(f"""<div class="main-container"><h2>💯 Rendements des indices (%)</h2></div>""", unsafe_allow_html=True)

# st.multiselect permet de choisir plusieurs options. 
default_indices = indice_default 
indice_selectionner_pour_tableau = st.multiselect("Ajoutez des indices au tableau pour comparer", liste_indices, default= [default_indices]) # arg1 : nom liste déroulante / arg2 : liste pour la liste déroulante / arg3 : opt par défaut de l'actif sur le tableau. "default= [default_indices]" entre [] car attend une liste.

# st.session_state : dictionnaire persistant de Streamlit. Stock et conserve interactions de l'utilisateur pour ne pas avoir à recharger la page.
if "rendement_data" not in st.session_state: 
    st.session_state.rendement_data = pd.DataFrame() # ici, "rendement_data" est la clé du dico "st.session_state" et sa valeur est un dataframe vide.

# Suppression des indices qui ne sont plus sélectionnés dasn "indice_selectionner_pour_tableau"
for i in st.session_state.rendement_data.index:
    if i not in indice_selectionner_pour_tableau:
        st.session_state.rendement_data.drop(index=i, inplace=True)


# Ajout des indices qui sont sélectionnés dasn "indice_selectionner_pour_tableau"
# 1. liste contenant les indices à ajouter, pas encore présent dans la valeur du dico de "st.session_state.rendement_data" qui est un df.
indices_a_ajouter = []
for i in indice_selectionner_pour_tableau:
    if i not in st.session_state.rendement_data.index: # Vérifie si l'indice n'est pas ds "st.rendement_data" avec ".index".
        indices_a_ajouter.append(i)

# 2. Calculer et ajouter les rendements pour la liste des indices ds "indices_to_add" pas encore présent dans la valeur du dico de "st.session_state.rendement_data" qui est un df. pour chaque indice de la liste "indices_to_add"
periods = [6, 12, 24, 60, 120, 180]  # Périodes en mois
for i in indices_a_ajouter:
    df_prix_date = get_prix_date(conn, table_hist_actif, i) # On crée le df avec en colonne "Date" et "Close" pour chaque indice selectionnés ds "indices_to_add"
    if not df.empty:
        df_rendement = calculate_rendement(df_prix_date, periods)
        df_info = df_infos_indices[df_infos_indices["Short_Name"] == i]  # Filtres les infos sur l'indice
        
        if not df_info.empty:
            df_rendement["Pays"] = df_info.iloc[0]["Pays"]
            df_rendement["Ticker"] = df_info.iloc[0]["Ticker"]
            df_rendement["Ticker_Yahoo_Finance"] = df_info.iloc[0]["Ticker_Yahoo_Finance"]
            df_rendement["Place_Boursiere"] = df_info.iloc[0]["Place_Boursiere"]
            df_rendement["Nombres_Entreprises"] = df_info.iloc[0]["Nombres_Entreprises"]
            df_rendement["Devise"] = df_info.iloc[0]["Devise"]
        else:
            df_rendement["Pays"] = "Inconnu"

        # 3. Ajout et écrase st.session_state.rendement_data avec rendement. C'est ici qu'on met en index "Ticker_Yahoo_Finance"
        st.session_state.rendement_data = pd.concat([st.session_state.rendement_data, pd.DataFrame(df_rendement, index=[i])])



######################################### ORGANISATION ET STYLISATION DU TABLEAU RENDEMENT #########################################

# Réorganiser les colonnes (sans la colonne "Ticker_Yahoo_Finance")
# Réorganiser les colonnes en mettant "Pays" avant les rendements
st.session_state.rendement_data = st.session_state.rendement_data[["Pays"] + [f"{p} mois" for p in periods] + ["Ticker", "Ticker_Yahoo_Finance", "Place_Boursiere", "Nombres_Entreprises", "Devise"]]

# Appliquer la mise en forme et le style sur les rendements
styled_df = style_rendement(st.session_state.rendement_data, periods)

# Afficher le tableau avec les rendements stylisés
st.dataframe(styled_df)



############################################### COMPOSITION INDICE ###############################################

# CSS sous titre
#st.header("🗂 Composition des indices")
st.markdown(f"""<div class="main-container"><h2>🗂 Composition des indices</h2></div>""", unsafe_allow_html=True)

# st.selectbox permet de choisir une seule option.
default_index = indice_default # "index=indices.index(default_index)" attent un int pour index
selected_indice = st.selectbox("Choisissez un indice pour voir sa composition", liste_indices, index=liste_indices.index(default_index)) # arg1 : nom liste déroulante / arg2 : liste pour la liste déroulante / arg3 : opt par défaut de l'actif pour visualisation graph.

# Afficher la composition de l'indice sélectionné
if selected_indice:
    df_composition_indice = get_composition_indice(conn, selected_indice)
    
    if not df_composition_indice.empty:
        st.write(f"Composition de l'indice {selected_indice}:")
        st.dataframe(df_composition_indice)  # Affiche la composition sous forme de tableau
    else:
        st.write(f"Pas de données disponibles pour l'indice {selected_indice}.")


conn.close()