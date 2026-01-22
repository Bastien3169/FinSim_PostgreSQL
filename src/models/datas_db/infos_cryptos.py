from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
import numpy as np
import html5lib
import os
import glob


def infos_cryptos(dossier_csv="csv", csv_bdd="csv/csv_bdd"):

    # URL API CoinGecko
    url = "https://api.coingecko.com/api/v3/coins/markets"

    # Paramètres de la requête
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",  # Tri par capitalisation décroissante
        "per_page": 60,              # 50 premières cryptos
        "page": 1,
        "sparkline": False
    }

    # Requête GET
    response = requests.get(url, params=params)
    data = response.json()

    '''
    # Pas besoin ?
    for i in data:
        info_crypto = (i["name"], i["symbol"], i["current_price"],i["market_cap"], i["total_volume"], i["circulating_supply"],i["ath"],i["last_updated"])
        #print(info_crypto)
    '''

    df = pd.DataFrame()
    df["Short_Name_Cryptos"] = [i["name"] for i in data]
    df["Ticker_cryptos_Yf"] = [i["symbol"].upper()+ "-USD" for i in data]
    df["Ticker_Cryptos"] = [i["symbol"] for i in data]
    df["Prix_actuel"] = [i["current_price"] for i in data]
    df["Capitalisation_Boursiere"] = [i["market_cap"] for i in data]
    df["Offre_En_Circulation"] = [i["circulating_supply"] for i in data]
    df["Offre_En_Circulation"] = df["circulating_supply"].round(1)
    df["ATH"] = [i["ath"] for i in data]
    df["MAJ"] = [i["last_updated"].split("T")[0] for i in data]

    # Suppression de la ligne "Wrapped SOL" car probleme yfinance (en fait garde toute la ligne où le Short_Name_Cryptos est différents "Wrapped SOL")
    #df = df[df["Short_Name_Cryptos"] != "Wrapped SOL"]

    # Sauvegarde du fichier
    df.to_csv(("csv/csv_bdd/cryptos_infos.csv"), index=False, encoding="utf-8")

    return df

if __name__ == "__main__":
    infos_cryptos("csv", "csv/csv_bdd")
    print("[✅] Les informations des cryptomonnaies ont été récupérées et sauvegardées.")
        