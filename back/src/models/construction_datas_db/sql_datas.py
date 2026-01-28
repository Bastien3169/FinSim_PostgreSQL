"""
Gestion des tables de données financières avec SQLAlchemy Core
- Création des tables (indices, stocks, cryptos, ETFs + historiques)
- Import des CSV vers PostgreSQL
"""
import os
import glob
import pandas as pd
from sqlalchemy import text
from src.api_conn.database_conn import engine

# =====================================================
# CRÉATION DES TABLES (SQLAlchemy Core)
# =====================================================
def creation_db():
    """Crée toutes les tables de données financières"""
    
    with engine.begin() as conn:
        # Pour accepter le format DD-MM-YYYY
        conn.execute(text("SET datestyle = dmy;"))

        # DROP TABLES dans l'ordre inverse des dépendances
        conn.execute(text("DROP TABLE IF EXISTS historique_etfs CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS historique_cryptos CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS historique_stocks CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS historique_indices CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS etfs_infos CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS cryptos_infos CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS stocks_infos CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS indices_infos CASCADE;"))

        # ----------- Tables INFOS ----------- #
        
        # Indices (DOIT être créé avant stocks à cause de la FK)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS indices_infos (
                Short_Name_Indice TEXT,
                Ticker_Indice_Yf TEXT PRIMARY KEY,
                Nom_Indice TEXT,
                Devise TEXT,
                Place_Boursiere_Indice TEXT,
                Nombres_Entreprises INTEGER
            )
        """))

        #  stocks_infos_par_indice 
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS stocks_infos_par_indice (
                id SERIAL PRIMARY KEY,
                Short_Name_Stocks TEXT,
                Ticker_Stocks_Yf TEXT,
                Ticker_Stocks TEXT,
                Secteur_Activite TEXT,
                Pays_Stocks TEXT,
                Place_Boursiere TEXT,
                Capitalisation_Boursiere NUMERIC(18,2),
                Ticker_Indice_Yf TEXT,
                Ponderation NUMERIC(10,4),
                FOREIGN KEY (Ticker_Indice_Yf) 
                    REFERENCES indices_infos(Ticker_Indice_Yf)
                    ON DELETE CASCADE
            )
            """))

        # Stocks
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS stocks_infos (
                id SERIAL PRIMARY KEY,
                Short_Name_Stocks TEXT,
                Ticker_Stocks_Yf TEXT,
                Ticker_Stocks TEXT,
                Secteur_Activite TEXT,
                Pays_Stocks TEXT,
                Place_Boursiere TEXT,
                Capitalisation_Boursiere NUMERIC(18,2),
                Ticker_Indice_Yf TEXT,
                Ponderation NUMERIC(10,4),
                FOREIGN KEY (Ticker_Indice_Yf) REFERENCES indices_infos(Ticker_Indice_Yf)
            )
        """))
        



        # Cryptos
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS cryptos_infos (
                Short_Name_Cryptos TEXT,
                Ticker_Cryptos_Yf TEXT PRIMARY KEY,
                Ticker_Cryptos TEXT,
                Prix_actuel NUMERIC(18,6),
                Capitalisation_Boursiere NUMERIC(18,2),
                Offre_En_Circulation NUMERIC(18,2),
                ATH NUMERIC(18,6),
                MAJ DATE
            )
        """))
        
        # ETFs
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS etfs_infos (
                Short_Name_Etf TEXT,
                Ticker_Etf_Yf TEXT PRIMARY KEY,
                Ticker_Etf TEXT,
                Devise TEXT,
                Place_Boursiere_Etf TEXT,
                Volume_Moyen NUMERIC(18,2),
                Frais_pct NUMERIC(6,4)
            )
        """))
        
        # ----------- Tables HISTORIQUES ----------- #
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS historique_indices (
                id SERIAL PRIMARY KEY,
                Date DATE NOT NULL,
                Close NUMERIC(18,6),
                Ticker_Indice_Yf TEXT,
                Short_Name_Indice TEXT,
                UNIQUE (Date, Ticker_Indice_Yf)
            )
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS historique_stocks (
                id SERIAL PRIMARY KEY,
                Date DATE NOT NULL,
                Close NUMERIC(30,6),
                Ticker_Stocks_Yf TEXT,
                Short_Name_Stocks TEXT,
                UNIQUE (Date, Ticker_Stocks_Yf)
            )
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS historique_cryptos (
                id SERIAL PRIMARY KEY,
                Date DATE NOT NULL,
                Close NUMERIC(18,6),
                Ticker_Cryptos_Yf TEXT,
                Short_Name_Cryptos TEXT,
                UNIQUE (Date, Short_Name_Cryptos) 
            )
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS historique_etfs (
                id SERIAL PRIMARY KEY,
                Date DATE NOT NULL,
                Close NUMERIC(18,6),
                Ticker_Etf_Yf TEXT,
                Short_Name_Etf TEXT,
                UNIQUE (Date, Ticker_Etf_Yf)
            )
        """))
        
        # ----------- Index utiles ----------- #
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_hist_indices_name_date 
            ON historique_indices(Short_Name_Indice, Date)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_hist_stocks_name_date 
            ON historique_stocks(Short_Name_Stocks, Date)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_hist_cryptos_name_date 
            ON historique_cryptos(Short_Name_Cryptos, Date)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_hist_etfs_name_date 
            ON historique_etfs(Short_Name_Etf, Date)
        """))
    
    print("[✅] Tables PostgreSQL créées avec succès.")

# =====================================================
# IMPORT CSV AVEC PANDAS + SQLAlchemy
# =====================================================
IMPORT_ORDER = [
    "indices_infos.csv",
    "stocks_infos.csv",
    "etfs_infos.csv",
    "cryptos_infos.csv",
    "historique_indices.csv",
    "historique_stocks.csv",
    "historique_etfs.csv",
    "historique_cryptos.csv",
]

def import_csv_compo_indices(csv_bdd):
    print(f"[📁] Import CSV dans l’ordre contrôlé")

    for filename in IMPORT_ORDER:
        path = os.path.join(csv_bdd, filename)

        if not os.path.exists(path):
            print(f"[⚠️] Fichier manquant : {filename}")
            continue

        try:
            df = pd.read_csv(path)

            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date

            table_name = filename.replace(".csv", "")

            df.to_sql(table_name, engine, if_exists="append", index=False, method="multi")

            print(f"[✅] Table '{table_name}' importée ({len(df)} lignes)")

        except Exception as e:
            print(f"[❌] Erreur import {filename} : {e}")

    print("[✅] Importation CSV terminée.")


# =====================================================
# FONCTION PRINCIPALE
# =====================================================
def main_creation_db(csv_bdd):
    """
    Initialise la base de données complète :
    1. Crée les tables
    2. Importe les CSV
    """
    print("🔧 Initialisation de la base de données...")
    print(f"📂 Dossier CSV : {csv_bdd}")
    
    # Étape 1 : Créer les tables
    creation_db()
    
    # Étape 2 : Importer les CSV
    import_csv_compo_indices(csv_bdd)
    
    print("✅ Base de données initialisée avec succès !")

if __name__ == "__main__":
    # Chemin relatif depuis la racine du projet backend
    csv_path = os.path.join(
        os.path.dirname(__file__), 
        "..", "..", "..", "CSV", "csv_bdd"
    )
    
    main_creation_db(csv_bdd=csv_path)