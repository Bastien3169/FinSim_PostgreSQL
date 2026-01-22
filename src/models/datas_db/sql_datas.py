import os
import glob
import sqlite3
import pandas as pd


#=========================== Création bdd ===========================#
def creation_db(db_path):
    
    # Connexion à la base de données SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ----------- Création des tables infos ----------- #

    # Infos stocks
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stocks_infos_par_indice (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Short_Name_Stocks TEXT,
        Ticker_Stocks_Yf TEXT,
        Ticker_Stocks TEXT,
        Secteur_Activite TEXT,
        Pays_Stocks TEXT,
        Place_Boursiere TEXT,
        Capitalisation_Boursiere REAL,
        Ticker_Indice_Yf TEXT,
        Ponderation TEXT,
        FOREIGN KEY (Ticker_Indice_Yf) REFERENCES indices_infos(Ticker_Indice_Yf)
    )
    ''')

    # Infos indices
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS indices_infos (
        Short_Name_Indice TEXT,
        Ticker_Indice_Yf TEXT PRIMARY KEY,  -- (clé primaire),
        Nom_Indice TEXT,
        Devise TEXT,
        Place_Boursiere_Indice TEXT,
        Nombres_Entreprises INTEGER
    )
    ''')

    # Infos cryptos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cryptos_infos (
        Short_Name_Cryptos TEXT,
        Ticker_Cryptos_Yf TEXT PRIMARY KEY,  -- (clé primaire),
        Ticker_Cryptos TEXT,
        Prix_actuel REAL,
        Capitalisation_Boursiere REAL,
        Offre_En_Circulation REAL,
        ATH REAL,
        MAJ TEXT
    )
    ''')

    # Infos etfs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS etfs_infos (
        Short_Name_Etf TEXT,
        Ticker_Etf_Yf TEXT PRIMARY KEY,  -- (clé primaire),
        Ticker_Etf TEXT,
        Devise TEXT,
        Place_Boursiere_Etf TEXT,
        Volume_Moyen REAL,
        Frais_pct REAL
    )
    ''')

    # ----------- Création des tables historiques ----------- #

    # Historique indices
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS historique_indices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Date TEXT,
        Close REAL,
        Ticker_Indice_Yf TEXT,
        Short_Name_Indice
    )
    ''')

    # Historique stocks
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS historique_stocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Date TEXT,
        Close REAL,
        Ticker_Stocks_Yf TEXT,
        Short_Name_Stocks TEXT
    )
    ''')
    
    # Historique cryptos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS historique_cryptos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Date TEXT,
        Close REAL,
        Ticker_Cryptos_Yf TEXT,
        Short_Name_Cryptos TEXT
    )
    ''')

    # Historique etfs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS historique_etfs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Date TEXT,
        Close REAL,
        Ticker_Etf_Yf TEXT,
        Short_Name_Etf TEXT
    )
    ''')


    # Création des index pour optimiser les performances
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hist_indices_date_ticker ON historique_indices(Date, Ticker_Indice_Yf)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hist_stocks_date_ticker ON historique_stocks(Date, Ticker_Stocks_Yf)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hist_indices_close ON historique_indices(Close)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hist_stocks_close ON historique_stocks(Close)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_stocks_infos_ticker ON stocks_infos_par_indice(Ticker_Stocks_Yf)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hist_cryptos_date_ticker ON historique_cryptos(Date, Ticker_Cryptos_Yf)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hist_cryptos_close ON historique_cryptos(Close)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hist_etfs_date_ticker ON historique_etfs(Date, Ticker_Etf_Yf)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hist_etfs_close ON historique_etfs(Close)")


    # Valider les changements
    conn.commit()
    
    # Fermer la connexion
    conn.close()
    print("[✅] Tables créées avec succès.")



#=========================== Impor fichiers csv ===========================#
def import_csv_compo_indices(csv_bdd, db_path):
    
    # Connexion à la base de données SQLite
    conn = sqlite3.connect(db_path)
    
    # Parcours des fichiers CSV dans le dossier et sous-dossiers
    for i in glob.glob(os.path.join(csv_bdd, "*.csv"), recursive=True):
        try:
            # Lecture du fichier CSV
            df = pd.read_csv(i)
            
            # Création du nom de la table en fonction du nom du fichier
            table_name = os.path.basename(i).split('.')[0]
            
            # Enregistrement des données dans la base SQLite
            df.to_sql(table_name, conn, if_exists='append', index=False)
            print(f"Table {table_name} ajoutée avec succès.")
            
        except Exception as e:
            print(f"Erreur lors de l'importation du fichier {i}: {e}")

    # Fermer la connexion
    conn.close()
    
    print("[✅] Importation des CSV dans la base de données terminée.")


#=========================== Fichier main pour création ===========================#
def main_creation_db(csv_bdd, db_path):
    
    # Étape 1: Créer la base de données et les tables
    creation_db(db_path)

    # Étape 2: Importer les fichiers CSV dans la base de données
    import_csv_compo_indices(csv_bdd, db_path)

if __name__ == "__main__":
    main_creation_db(csv_bdd = "csv/csv_bdd", db_path = "data.db")