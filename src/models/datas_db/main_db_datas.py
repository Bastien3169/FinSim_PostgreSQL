# main.py
import os
from src.models.datas_db import scraping_tickers
from src.models.datas_db import composition_indices
from src.models.datas_db import infos_indices
from src.models.datas_db import infos_stocks
from src.models.datas_db import infos_cryptos
from src.models.datas_db import infos_etfs
from src.models.datas_db import hist_indices
from src.models.datas_db import hist_stocks
from src.models.datas_db import hist_cryptos
from src.models.datas_db import hist_etfs
from src.models.datas_db import sql_datas
'''
from . import scraping_tickers  # Pour récupérer les tickers
from . import composition_indices  # Pour obtenir les infos des entreprises par indice
from . import infos_stocks  # Pour concaténer les informations des entreprises et les stocker en CSV
from . import infos_indices  # Pour récupérer les infos des indices et les stocker en CSV
from . import hist_indices  # Pour récupérer l'historique des prix des indices
from . import infos_cryptos  # Pour récupérer les infos des cryptomonnaies
from . import hist_cryptos  # Pour récupérer l'historique des prix des cryptomonnaies
from . import hist_stocks  # Pour récupérer l'historique des prix des entreprises
from . import sql_datas # Pour créer la base de donnée sql
'''

def main_db_datas(dossier_csv = "csv", csv_bdd = "csv/csv_bdd", db_path = "data.db"):

    #scraping_tickers.all_tickers_yf()

    # Étape 1: Scraper les tickers de chaque indice et Récupérer les informations des entreprises pour chaque indice
    composition_indices.csv_indices(dossier_csv)
    print("[✅] Les tickers des indices et les informations des entreprises ont été récupérés et sauvegardés.")

    # Étape 2: Concaténer et sauvegarder les données des entreprises
    infos_stocks.infos_stocks(dossier_csv, csv_bdd) 
    print("[✅] Les informations des entreprises ont été concaténées et sauvegardées.")

    # Étape 3: Récupérer et sauvegarder les informations des indices
    infos_indices.infos_indices(dossier_csv, csv_bdd)
    print("[✅] Les informations des indices ont été récupérées et sauvegardées.")

    # Étape 4: Récupérer et sauvegarder les informations des cryptomonnaies
    infos_cryptos.infos_cryptos(dossier_csv, csv_bdd)
    print("[✅] Les informations des cryptomonnaies ont été récupérées et sauvegardées.")

    # Étape 5: Récupérer et sauvegarder l'historique des prix des indices
    hist_indices.recuperer_et_clean_indices(csv_bdd)
    print("[✅] L'historique des indices a été récupéré et sauvegardé.")

    # Étape 6: Récupérer et sauvegarder l'historique des prix des entreprises
    hist_stocks.recuperer_et_clean_stocks(csv_bdd)
    print("[✅] L'historique des entreprises a été récupéré et sauvegardé.")

    # Étape 7: Récupérer et sauvegarder l'historique des prix des cryptomonnaies
    hist_cryptos.hist_cryptos(csv_bdd)
    print("[✅] L'historique des cryptomonnaies a été récupéré et sauvegardé.")
    
     # Étape 8: Récupérer et sauvegarder les informations des etfs
    infos_etfs.infos_etf(csv_bdd)
    print("[✅] Les informations des etfs ont été récupérées et sauvegardées.")

    # Étape 9: Récupérer et sauvegarder l'historique des prix des etfs
    hist_etfs.hist_etfs(csv_bdd)
    print("[✅] L'historique des etfs a été récupéré et sauvegardé.")

    # Étape 10 : Création de la base de donnée
    sql_datas.main_creation_db(csv_bdd, db_path)
    print("[✅] La base de données a été créée et les données ont été importées.")

    print("[✅]✅] Toutes les étapes ont été exécutées avec succès.")

if __name__ == "__main__":
    main_db_datas("csv", "csv/csv_bdd", "data.db")

