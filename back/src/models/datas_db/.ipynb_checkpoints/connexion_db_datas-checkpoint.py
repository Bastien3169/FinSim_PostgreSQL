import sqlite3
import pandas as pd
import hashlib

""" Les guillemets autour de '{}', n'est pas nécessaire dans la requête SQL mais pour s'aasurer qu'il n'y ait aucune erreur due à des noms de tables ayant des caractères spéciaux ou des espaces, c'est une bonne pratique."""


################################## CONNEXION BD POUR DATAS ET HIST STOCKS  ##################################

class FinanceDatabaseStocks:
#Classe pour gérer les interactions avec la base de données SQLite des actifs financiers.

    # Chemin de la base de données (modifiable à un seul endroit)
    def __init__(self, db_path="data.db"):
        self.db_path = db_path

    
    def get_list_stocks(self):
        #Récupérer la liste des entreprises
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql("SELECT DISTINCT Short_Name_Stocks FROM stocks_infos_par_indice", conn)
        return df["Short_Name_Stocks"].tolist()
    
  
    def get_infos_stocks(self):
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql("SELECT * FROM stocks_infos_par_indice", conn)
        # Supprimer les doublons sur la colonne d'identification de l'entreprise
        df = df.drop_duplicates(subset=["Short_Name_Stocks"])
        return df


    def get_prix_date(self, actif):
        #Récupérer les données de l'actif pour le graphique
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT Date, Close FROM historique_stocks WHERE Short_Name_Stocks = ? ORDER BY Date"
            df = pd.read_sql(query, conn, params=(actif,))
        if not df.empty:
            df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")
            df = df.set_index("Date").resample("W").last().reset_index()
        return df



################################## CONNEXION BD POUR DATAS ET HIST INDICES  ##################################

class FinanceDatabaseIndice:
#Classe pour gérer les interactions avec la base de données SQLite des actifs financiers.

    # Chemin de la base de données (modifiable à un seul endroit)
    def __init__(self, db_path="data.db"):
        self.db_path = db_path
        

    def get_list_indices(self):
        #Récupérer la liste des entreprises
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql("SELECT DISTINCT Short_Name_Indice FROM indices_infos", conn)
        return df["Short_Name_Indice"].tolist()
    
  
    def get_infos_indices(self):
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql("SELECT * FROM indices_infos", conn)
        return df


    def get_prix_date(self, selected_indice):
        #Récupérer les données de l'actif pour le graphique
        with sqlite3.connect(self.db_path) as conn:
            query = "SELECT Date, Close FROM historique_indices WHERE Short_Name_Indice = ? ORDER BY Date"
            df = pd.read_sql(query, conn, params=(selected_indice,))
        if not df.empty:
            df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y")
            df = df.set_index("Date").resample("W").last().reset_index()
        return df

    
    def get_composition_indice(self, selected_indice):
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
               SELECT 
                	s.*
                FROM stocks_infos_par_indice s
                JOIN indices_infos i ON s.Ticker_Indice_Yf = i.Ticker_Indice_Yf
                WHERE i.Short_Name_Indice =  ?
                ORDER BY s.Short_Name_Stocks
                """
                df = pd.read_sql(query, conn, params=(selected_indice,))
            return df
        except Exception as e:
            print(f"Erreur: {e}")
            return pd.DataFrame()


####################################### CALCUL RENDEMENTS ACTIFS #######################################

def calculate_rendement(df, periods):
    """ Calculer les rendements pour chaque période """
    rendement = {}
    for period_months in periods:
        start_date = df["Date"].max() - pd.DateOffset(months=period_months)
        df_period = df[df["Date"] >= start_date]
        if len(df_period) > 1:  # Si on a plus d'une donnée dans la période
            start_close = df_period.iloc[0]["Close"]
            end_close = df_period.iloc[-1]["Close"]
            rendement[f"{period_months} mois"] = "{:.2f}".format((end_close - start_close) / start_close * 100) # arrondie 2 chif
        else:
            rendement[f"{period_months} mois"] = None
    return rendement



####################################### STYLE DU TABLEAU DE RENDEMENT #######################################

def style_rendement(df, periods):
    """ Appliquer un style de couleur sur les rendements """
    def color_rendement(val):
        color = 'green' if float(val) > 0 else ('red' if float(val) < 0 else 'black')
        return f'color: {color}'  
    return df.style.applymap(color_rendement, subset=[f"{p} mois" for p in periods])





