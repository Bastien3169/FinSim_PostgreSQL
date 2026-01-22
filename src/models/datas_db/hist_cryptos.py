from bs4 import BeautifulSoup
import requests
import time
from datetime import datetime
import yfinance as yf
import pandas as pd
import numpy as np
import html5lib
import os
import glob

def hist_cryptos(csv_bdd):
    
    # Lecture des fichiers
    df_crypto_infos = pd.read_csv(os.path.join(csv_bdd, "crypto_infos.csv"), encoding="utf-8")

    # Sélection des 2 premières pour test
    cryptos_tickers = df_crypto_infos["Ticker_cryptos_Yf"].tolist()
    cryptos_nom = df_crypto_infos["Short_Name_Cryptos"].tolist()

    historique = [] # dictionnaire pour stocker les futurs df de chaque crypto. clé = ticker, valeur = liste de df (ici une seule valeur par clé)

    for ticker, nom in zip(cryptos_tickers, cryptos_nom):
        try:
            crypto = yf.Ticker(ticker)
            df = crypto.history(period="max", interval="1mo")

            if not df.empty:
                df = df.reset_index()  # pour avoir la colonne Date
                df["Ticker_cryptos_Yf"] = ticker
                df["Short_Name_Cryptos"] = nom
                historique.append(df)

                print(f"✅ {nom} : {len(df)} points récupérés (du {df['Date'].min().date()} au {df['Date'].max().date()})")
            else:
                print(f"⚠️ {nom} : aucune donnée disponible")

        except Exception as e:
            print(f"❌ Erreur pour {nom} ({ticker}): {e}")

    print(f"\n📊 Total cryptos récupérées : {len(historique)}/{len(cryptos_tickers)}")

    # Concaténer tous les historiques en un seul DataFrame

    # Concaténation de tous les historiques
    df_hist = pd.concat(historique, ignore_index=True)
    # Convertir la colonne "Date" en format datetime et reformater en "JJ-MM-AAAA"
    #df_hist["Date"] = df_hist["Date"].dt.strftime("%d-%m-%Y")
    df_hist["Date"] = pd.to_datetime(df_hist["Date"], errors="coerce").dt.strftime("%d-%m-%Y")
    
    # Arrondir la colonne "Close"
    df_hist["Close"] = df_hist["Close"].round(3)

    # Supprimer colonnes inutiles
    df_hist = df_hist.drop(columns=["Open", "High", "Low", "Volume", "Dividends", "Stock Splits"], errors="ignore")

    #display(df_hist)

    # Sauvegarde
    df_hist.to_csv(os.path.join(csv_bdd, "historique_cryptos.csv"), index=False, encoding="utf-8")
    print("\n💾 Fichier sauvegardé : csv/csv_bdd/historique_cryptos.csv")

    return df_hist

if __name__ == "__main__":
    hist_cryptos(csv_bdd = "csv/csv_bdd")
    print("[✅] Les historiques des cryptomonnaies ont été récupérés et sauvegardés.")
