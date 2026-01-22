import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors as pc
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from src.models.control_datas.connexion_db_datas import *



def calcul_rendement(duree_invest = 1 , somme_investie = 100000, mois_dca = 6, ticker = "S&P 500"):
    
#=============================== On prépare les variables ===============================  
    # Somme à investir par mois
    somme_par_mois = somme_investie / mois_dca

    # Définir les dates de début et de fin
    date_debut = datetime.now() - relativedelta(months=((duree_invest * 12) + 1)) # +1 pour s'assurer d'avoir un mois entier
    date_fin = datetime.now()

    # Création instance de l'objet
    datas_indices = FinanceDatabaseIndice(db_path="data.db")
    
    # Appel méthodes
    liste_indices = datas_indices.get_list_indices()
    infos_indices = datas_indices.get_infos_indices()
    data_financiere = datas_indices.get_prix_date(ticker)
    
    # Télécharger les données financières pour la période
    data_financiere = data_financiere[(data_financiere['Date'] >= date_debut) & (data_financiere['Date'] <= date_fin)]
 
#=============================== On calcul le rendement par mois ===============================
     # Remplace les cases vides par '0'
    if data_financiere.empty:
        return 0, 0
    # Remplace les cases NaN par '0'
    data_financiere = data_financiere.fillna(0)

    # Rendements mensuels en % (avec colonne 'Close' du df 'data_financiere')
    rendements_mois = data_financiere['Close'].pct_change().dropna()

    # Ajout colonne rendemenbt mensuel au df data_financiere
    data_financiere['Rendement du mois'] = rendements_mois

#=============================== On calcul le DCA et le LumpSum ===============================
    # Calcul du rendement DCA
    rendements_dca = []
    portefeuille_dca = 0
    
    # Investissement mensuel pendant la période DCA
    for i in range(min(mois_dca, len(rendements_mois))):
        portefeuille_dca += somme_par_mois * (1 + rendements_mois.iloc[i])
        rendements_dca.append(round(portefeuille_dca, 2))
   
    # Croissance après la période DCA
    for i in range(mois_dca, len(rendements_mois)):
        portefeuille_dca *= (1 + rendements_mois.iloc[i])
        rendements_dca.append(round(portefeuille_dca, 2))

    # Calcul du rendement LP
    rendements_lumpsum = []
    portefeuille_lumpsum = somme_investie
    for i in range(len(rendements_mois)):
        portefeuille_lumpsum *= (1 + rendements_mois.iloc[i])
        rendements_lumpsum.append(round(portefeuille_lumpsum, 1))
    
    # On aligne la taille avec df_rendement, car pct_change() enlève le premier mois
    data_financiere = data_financiere.iloc[1:]  # on enlève le premier mois (NaN dans pct_change)
    data_financiere['Rendement LS'] = rendements_lumpsum
    data_financiere['Rendement DCA'] = rendements_dca

    return data_financiere

df = calcul_rendement(duree_invest = 1 , somme_investie = 100000, mois_dca = 6, ticker = "^GSPC")


################################### DF POUR GRAPHIQUE BAR ###################################

def calcul_rendements_durations(durees, mois_dca_list, somme_investie, ticker):
                               
    resultats = {
        'Année': [],
        'Date de début': []
    }

    for dca_mois in mois_dca_list:
        resultats[f'DCA ({dca_mois} mois)'] = []

    resultats['LumpSum'] = []

    for duree in durees:
        resultats['Année'].append(duree)
        date_debut = datetime.now() - relativedelta(months=(duree * 12))
        resultats['Date de début'].append(date_debut.strftime("%Y-%m-%d"))

        rendement_ls = None

        for dca_mois in mois_dca_list:
            df = calcul_rendement(
                duree_invest=duree,  # Paramètre corrigé ici
                somme_investie=somme_investie,
                mois_dca=dca_mois,
                ticker=ticker
            )

            if df.empty:
                print(f"Erreur: Pas de données pour DCA {dca_mois} mois pour la période de {duree} ans")
                resultats[f'DCA ({dca_mois} mois)'].append(None)
                continue

            # Corrigez aussi ces noms de colonnes si nécessaire
            dca_value = round(df["Rendement DCA"].iloc[-1], 1)  # Nom corrigé
            resultats[f'DCA ({dca_mois} mois)'].append(dca_value)

            if rendement_ls is None:
                rendement_ls = round(df["Rendement LS"].iloc[-1], 1)  # Nom corrigé

        resultats['LumpSum'].append(rendement_ls)

    df_resultats = pd.DataFrame(resultats)
    return df_resultats



df_resultats = calcul_rendements_durations(durees=range(1, 26), mois_dca_list=[3, 6, 12, 24], somme_investie=100000, ticker="S&P 500")



################################### DF POUR GRAPHIQUE LIGNE ###################################

def calcul_multiple_rendements(durees, mois_dca_list, somme_investie, ticker):
    resultats = []
    
    for mois in mois_dca_list:
        for duree in durees:
            df = calcul_rendement(
                duree_invest=duree,
                somme_investie=somme_investie,
                mois_dca=mois,
                ticker=ticker
            )
            df = df.copy()
            df["Durée"] = f"{duree} ans"
            df["Mois DCA"] = f"{mois} mois"
            resultats.append(df)

    df_resultat = pd.concat(resultats)

    return df_resultat


df = calcul_multiple_rendements(durees = [25, 20, 15, 10, 5], mois_dca_list = [3, 6, 12, 24], somme_investie  = 100000, ticker = "S&P 500")



################################### GRAPH BARRE ###################################

def graphe_barre(df_resultats):
    import plotly.graph_objects as go

    fig = go.Figure()

    # Couleurs personnalisées
    couleurs = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b',
        '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]

    # Détecter les colonnes DCA dynamiquement
    dca_colonnes = [col for col in df_resultats.columns if col.startswith("DCA")]

    # Ajout des barres DCA
    for i, col in enumerate(dca_colonnes):
        fig.add_trace(go.Bar(
            x=df_resultats["Année"],
            y=df_resultats[col],
            name=col,
            marker_color=couleurs[i % len(couleurs)]
        ))

    # Ajout des barres Lump Sum si présente
    if "LumpSum" in df_resultats.columns:
        fig.add_trace(go.Bar(
            x=df_resultats["Année"],
            y=df_resultats["LumpSum"],
            name="Lump Sum",
            marker_color="#000000"
        ))

    # Configuration du graphique
    fig.update_layout(
        barmode='group',  # ou 'stack' si tu veux empiler les barres
        title="Comparaison des rendements DCA vs Lump Sum sur différentes périodes",
        xaxis_title="Durée de l'investissement (années)",
        yaxis_title="Valeur finale (€)",
        legend_title="Méthode d'investissement",
        template="plotly_white",
        font=dict(family="Arial", size=14),
        height=800,
        width=1200,
        xaxis=dict(
            tickmode='array',
            tickvals=list(df_resultats["Année"]),
            tickangle=45,
            autorange='reversed'
        )
    )

    #fig.show()
    return fig



################################### GRAPH LINE ###################################

def graphe_line(df, somme_investie=100000):
    import plotly.graph_objects as go
    fig = go.Figure()
    
    couleurs_dca = pc.qualitative.Bold
    couleurs_lump = pc.qualitative.Dark24
    durees = sorted(df['Durée'].unique())

    trace_info = []  # Pour stocker (durée, nom_trace)

    
    # Traces DCA
    for i, (duree, mois) in enumerate(df.groupby(['Durée', 'Mois DCA'])):
        if mois['Mois DCA'].iloc[0] != 1:  # Exclure LumpSum
            nom_trace = f"DCA {mois['Mois DCA'].iloc[0]} - {mois['Durée'].iloc[0]} ans"
            
            fig.add_trace(go.Scatter(
                x=mois['Date'],
                y=mois['Rendement DCA'],
                mode='lines',
                name=nom_trace,
                line=dict(width=1.5, dash='dash', color=couleurs_dca[i % len(couleurs_dca)]),
                hovertemplate="Date: %{x}<br>Valeur: %{y:,.0f}€<extra></extra>"
            ))
            trace_info.append(mois['Durée'].iloc[0])  # Durée

    # Traces LumpSum
    for j, duree in enumerate(df['Durée'].unique()):
        for mois_dca in df['Mois DCA'].unique():
            df_filtered = df[(df['Durée'] == duree) & (df['Mois DCA'] == mois_dca)]
        nom_trace = f"LumpSum - {duree} ans"
        
        fig.add_trace(go.Scatter(
            x=df_filtered['Date'],
            y=df_filtered['Rendement LS'],
            mode='lines',
            name=nom_trace,
            line=dict(width=2, color=couleurs_lump[j % len(couleurs_lump)]),
            hovertemplate="Date: %{x}<br>Valeur: %{y:,.0f}€<extra></extra>"
        ))
        trace_info.append(duree)  # Durée

    
    # Création des boutons avec filtrage par durée (DCA + LumpSum)
    boutons_menu = []

    for duree in durees:
        visible_traces = [d == duree for d in trace_info]
        boutons_menu.append(dict(
            label=f"{duree} ans",
            method="update",
            args=[
                {"visible": visible_traces},
                {"title": f"Performance DCA vs LumpSum - {duree} ans"}
            ]
        ))

    # Bouton "Tout voir"
    boutons_menu.insert(0, dict(
        label="Tout voir",
        method="update",
        args=[
            {"visible": [True] * len(trace_info)},
            {"title": f"Performance DCA vs LumpSum (Investissement: {somme_investie:,.0f}€)"}
        ]
    ))

    # Layout
    fig.update_layout(
        title=dict(
            text=f"Performance DCA vs LumpSum (Investissement: {somme_investie:,.0f}€)",
            x=0.5,
            y=0.95,  # Monte le titre
            xanchor='center',
            yanchor="top",
            font=dict(size=20)
        ),
        xaxis=dict(
            title="Date",
            tickangle=-45,
            tickformat="%Y",
            dtick="M12",  # Un tick tous les 12 mois
            showgrid=True,
            gridcolor="LightGrey"
        ),
        yaxis_title="Valeur du portefeuille (€)",
        legend_title="Stratégie",
        template="plotly_white",
        hovermode="x unified",
        height=700,
        width=1200,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.5,
            xanchor="center",
            x=0.5
        ),
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
            )
        ]
    )
    
    #fig.show()
    return fig

