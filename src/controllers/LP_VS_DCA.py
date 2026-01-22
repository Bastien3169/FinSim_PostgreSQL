import yfinance as yf
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors as pc
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from src.models.control_datas.connexion_db_datas import *



def calcul_rendement(duree_invest=1, somme_investie=100000, mois_dca=6, ticker="S&P 500"):

    #=============================== Variables ===============================
    somme_par_mois = somme_investie / mois_dca
    date_debut = datetime.now() - relativedelta(months=(duree_invest * 12))
    date_fin = datetime.now()

    datas_indices = FinanceDatabaseIndice(db_path="data.db")
    data_financiere = datas_indices.get_prix_date(ticker)
    data_financiere = data_financiere[(data_financiere['Date'] >= date_debut) &
                                      (data_financiere['Date'] <= date_fin)]

    if data_financiere.empty:
        return pd.DataFrame()

    # Remplace NaN par 0 pour pct_change
    rendements_mois = data_financiere['Close'].pct_change().fillna(0)
    data_financiere['Rendement du mois'] = rendements_mois

    #=============================== DCA ===============================
    rendements_dca = []
    portefeuille_dca = 0
    for i in range(len(rendements_mois)):
        if i < mois_dca:
            portefeuille_dca += somme_par_mois
        portefeuille_dca *= (1 + rendements_mois.iloc[i])
        rendements_dca.append(round(portefeuille_dca, 2))

    #=============================== LumpSum ===============================
    rendements_lumpsum = []
    portefeuille_lumpsum = somme_investie
    for i in range(len(rendements_mois)):
        portefeuille_lumpsum *= (1 + rendements_mois.iloc[i])
        rendements_lumpsum.append(round(portefeuille_lumpsum, 2))

    #=============================== Alignement ===============================
    data_financiere['LS'] = rendements_lumpsum
    data_financiere['DCA'] = rendements_dca

    return data_financiere


df = calcul_rendement(duree_invest = 1 , somme_investie = 100000, mois_dca = 6, ticker = "^GSPC")

################################### DF POUR GRAPHIQUE BAR ###################################
def calcul_rendements_durations(durees=range(1, 26), mois_dca_list=[3, 6, 12, 24], somme_investie=100000, ticker="S&P 500"):
    
    # Je crée mes listes vides
    annees = []
    lumpsum = []
    listes_dca = [] # Je crée une liste vide pour chaque DCA

    for mois in mois_dca_list:
        listes_dca.append([])
    
    # Pour chaque durée
    for duree in durees:
        # J'ajoute l'année
        annees.append(duree)
        
        # Je calcule chaque DCA
        for i, mois in enumerate(mois_dca_list):
            df = calcul_rendement(duree_invest=duree, somme_investie=somme_investie, mois_dca=mois, ticker=ticker)
            if df.empty:
                listes_dca[i].append(None)
            else:
                listes_dca[i].append(round(df["DCA"].iloc[-1], 1))
        
        # Je calcule LumpSum (je prends le premier DCA)
        df = calcul_rendement(duree_invest=duree, somme_investie=somme_investie, mois_dca=mois_dca_list[0], ticker=ticker)
        if df.empty:
            lumpsum.append(None)
        else:
            lumpsum.append(round(df["LS"].iloc[-1], 1))
    
    # Je crée mon dictionnaire pour le DataFrame
    data = {'Année': annees}
    
    # J'ajoute chaque colonne DCA
    for i, mois in enumerate(mois_dca_list):
        data[f'DCA ({mois} mois)'] = listes_dca[i]
    
    # J'ajoute la colonne LumpSum
    data['LumpSum'] = lumpsum
    
    # Je crée mon DataFrame
    resultat = pd.DataFrame(data)
        
    return resultat

################################### DF POUR GRAPHIQUE LIGNE ###################################

def calcul_multiple_rendements(durees = [25, 20, 15, 10, 5], mois_dca_list = [3, 6, 12, 24], somme_investie  = 100000, ticker = "S&P 500"):
    
    # Je crée ma liste vide pour stocker tous mes DataFrames
    tous_les_df = []

    # Pour chaque DCA
    for mois in mois_dca_list:
        # Pour chaque durée de chaque DCA
        for duree in durees:
            # Calcule le rendement
            df = calcul_rendement(duree_invest=duree, somme_investie=somme_investie, mois_dca=mois, ticker=ticker)
            df = df.copy()
            # J'ajoute la colonne durée
            df["Durée"] = f"{duree} ans"
            # J'ajoute la colonne mois DCA
            df["Mois DCA"] = f"{mois} mois"
            # J'ajoute ce DataFrame à ma liste de Dataframe
            tous_les_df.append(df)

    df_resultat = pd.concat(tous_les_df)

    return df_resultat


################################### GRAPH BARRE ###################################

def graphe_barre(df_resultats):
    
    # Création graphique vide
    fig = go.Figure()
    
    # Couleurs graph 
    mes_couleurs = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    # Trouver colonnes DCA ds DF car toutes les colonnes DCA n'ont pas la même durée et donc le même nom (ex : DCA (3 mois), DCA (6 mois)...)
    colonnes_dca = []
    for colonne in df_resultats.columns:
        if colonne.startswith("DCA"): # La colonne DCA commence par "DCA" puis sa durée ex : "DCA (6 mois)". Si on veut toutes les colonnes DCA, on fait startswith
            colonnes_dca.append(colonne)
    
    # Ajouter colonne DCA
    for i in range(len(colonnes_dca)):
        colonne_dca = colonnes_dca[i]      
        # Choix couleur (recommence la liste si pas assez de couleurs)
        quelle_couleur = mes_couleurs[i % len(mes_couleurs)]   
        # Ajouter les barres
        fig.add_trace(go.Bar(
            x=df_resultats["Année"],
            y=df_resultats[colonne_dca],
            name=colonne_dca,
            marker_color=quelle_couleur
        ))
    
    # Ajouter LumpSum si elle existe
    if "LumpSum" in df_resultats.columns:
        fig.add_trace(go.Bar(
            x=df_resultats["Année"],
            y=df_resultats["LumpSum"],
            name="Lump Sum",
            marker_color="#000000"
        ))
    
    # Configuration graphique
    fig.update_layout(
        barmode='group',
        #title="Comparaison des rendements DCA vs Lump Sum sur différentes périodes",
        xaxis_title="Durée de l'investissement (années)",
        yaxis_title="Valeur finale (€)",
        legend_title="Méthode d'investissement",
        template="plotly_white",
        height=800,
        width=1200
    )
    
    # Configuration axe X
    fig.update_xaxes(
        tickmode='array',
        tickvals=list(df_resultats["Année"]),
        tickangle=45,
        autorange='reversed'
    )
    
    # Configuration police
    fig.update_layout(
        font=dict(family="Arial", size=14)
    )
    
    return fig


################################### GRAPH LINE ###################################

def graphe_line(df, somme_investie=100000):

    # Initialisation du graphique vide
    fig = go.Figure()
    
    # Définition des palettes de couleurs
    couleurs_dca = pc.qualitative.Bold      # Couleurs vives pour DCA
    couleurs_lump = pc.qualitative.Dark24   # Couleurs sombres pour LumpSum
    
    # Récupération des durées uniques triées (ex: [5, 10, 15, 20])
    durees = sorted(df['Durée'].unique())
    
    # Liste pour tracker quelle durée correspond à chaque trace (pour les boutons)
    trace_info = []

# ================================== CRÉATION DU TRACE DCA ================================== #
    # Traces DCA
    for i, (duree, mois) in enumerate(df.groupby(['Durée', 'Mois DCA'])):
        if mois['Mois DCA'].iloc[0] != 1:  # Exclure LumpSum
            nom_trace = f"DCA {mois['Mois DCA'].iloc[0]} - {mois['Durée'].iloc[0]} ans"

            # Ajout de la trace au graphique
            fig.add_trace(go.Scatter(
                x=mois['Date'],
                y=mois['DCA'],
                 mode='lines',
                name=nom_trace,
                line=dict(width=1.5, dash='dash', color=couleurs_dca[i % len(couleurs_dca)]), # Couleur cyclique
                hovertemplate="Date: %{x}<br>Valeur: %{y:,.0f}€<extra></extra>" # Template du tooltip au survol
            ))

            # Enregistrement de la durée pour les boutons de filtrage
            trace_info.append(mois['Durée'].iloc[0]) 

    
# ================================== CRÉATION DES TRACES LUMPSUM ================================== #
    # Double boucle nécessaire pour récupérer toutes les données temporelles
    for j, duree in enumerate(df['Durée'].unique()):
        # On prend le premier groupe de mois_dca pour avoir la série temporelle complète
        for mois_dca in df['Mois DCA'].unique():
            # Filtrage: durée spécifique + un mois DCA particulier
            df_filtered = df[(df['Durée'] == duree) & (df['Mois DCA'] == mois_dca)]
        nom_trace = f"LumpSum - {duree} ans"

        # Ajout de la trace au graphique
        fig.add_trace(go.Scatter(
            x=df_filtered['Date'],
            y=df_filtered['LS'],
            mode='lines',
            name=nom_trace,
            line=dict(width=2, color=couleurs_lump[j % len(couleurs_lump)]), # Couleur cyclique
            hovertemplate="Date: %{x}<br>Valeur: %{y:,.0f}€<extra></extra>" # Template du tooltip au survol
        ))

        # Enregistrement de la durée pour les boutons de filtrage
        trace_info.append(duree)  # Durée


# ============================= CRÉATION DES BOUTONS DE FILTRAGE ============================= #
    # Liste des boutons qui permettront de filtrer par durée avec le 1er bouton "Tout voir"
    boutons_menu = [dict(
        label="Tout voir",                      # Texte du bouton
        method="update",                        # Méthode Plotly pour mettre à jour
        args=[
            {"visible": [True] * len(trace_info)},  # Rendre toutes les traces visibles
            #{"title": f"Performance DCA vs LumpSum (Investissement: {somme_investie:,.0f}€)"}
            ])]

    # Création d'un bouton pour chaque durée
    for duree in durees:
        # Création du masque de visibilité: True si la trace correspond à cette durée
        visible_traces = [d == duree for d in trace_info]
        # Ajout du bouton à la liste
        boutons_menu.append(dict(
            label=f"{duree} ans", # Texte du bouton (ex: "10 ans")
            method="update", # Méthode Plotly de maj
            args=[
                {"visible": visible_traces}, # Masque de visibilité des traces
                #{"title": f"Performance DCA vs LumpSum - {duree} ans"} 
            ])) 
    
# ================================== CONFIGURATION GRAPH ================================== #
    fig.update_layout(

        # Configuration du titre
        title=dict(
            text=" ",
            x=0.5,
            y=0.95,  # Monte le titre
            xanchor='center',
            yanchor="top",
            font=dict(size=20)
        ),

        # Configuration de l'axe X (dates)
        xaxis=dict(
            title="Date",
            tickangle=-45,
            tickformat="%Y",
            dtick="M12",  # Un tick tous les 12 mois
            showgrid=True,
            gridcolor="LightGrey"
        ),

        # Configuration de l'axe Y
        yaxis_title="Valeur du portefeuille (€)",

        # Titre de la légende
        legend_title="Stratégie",

        # Template de style général blanc
        template="plotly_white",

        # Mode de survol unifié sur toute la largeur
        hovermode="x unified",

        # Dimensions du graphique
        height=700,
        width=1200,

        # Configuration de la légende
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.5,
            xanchor="center",
            x=0.5
        ),

        # Configuration du menu de boutons
        updatemenus=[
            dict(
                type="buttons",  # Boutons côte à côte
                direction="right",
                buttons=boutons_menu,
                showactive=True,
                x=0.5,
                xanchor="center",
                y=1.1,
                yanchor="top"
            )]
    )
    
    #fig.show()
    return fig

