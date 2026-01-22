import pandas as pd
import yfinance as yf
import os


def hist_etfs(csv_bdd):
    # Charger le fichier de tickers et infos
    df = pd.read_csv(os.path.join(csv_bdd, "etfs_infos.csv"), encoding="utf-8")

    dfs = []
    for idx, row in df.iterrows():
        ticker_yf = row["Ticker_Etf_Yf"]
        short_name = row["Short_Name_Etf"]
        
        try:
            ticker = yf.Ticker(ticker_yf)
            hist = ticker.history(period="max", interval="1mo")

            if hist.empty:
                print(f"⚠️ Historique vide pour {ticker_yf}.")
                continue

            hist = hist.reset_index() # Reset index pour que la date devienne une colonne
            hist["Date"] = pd.to_datetime(hist["Date"], errors="coerce").dt.strftime("%d-%m-%Y") # Conversion de la colonne Date au format souhaité
            hist["Close"] = hist["Close"].round(4)  # Ne garder que les colonnes souhaitées
            hist = hist.dropna(subset=["Close"]) # Supprimer les lignes où Close est NaN
            
            # Vérifier qu'il reste des données
            if hist.empty:
                print(f"⚠️ Pas de données Close valides pour {ticker_yf}.")
                continue
            
            hist["Ticker_Etf_Yf"] = ticker_yf
            hist["Short_Name_Etf"] = short_name

            dfs.append(hist)
            print(f"✅ Historique récupéré pour {ticker_yf}.")
        
        except Exception as e:
            print(f"Erreur pour {ticker_yf}: {e}")
            continue

    if dfs:
        # Concaténer tous les DataFrames de la liste
        df_hist = pd.concat(dfs, ignore_index=True)
        # Ne garder que les colonnes souhaitées
        df_hist = df_hist[["Date", "Close", "Ticker_Etf_Yf", "Short_Name_Etf"]]
        # Sauvegarde du fichier csv
        df_hist.to_csv(os.path.join(csv_bdd, "historique_etfs.csv"), index=False, encoding="utf-8")
        print(f"[✅] CSV de l'historique des ETFs récupéré avec {len(df_hist)} entrées.")
    else:
        print("❌ Aucun historique récupéré.")
        df_hist = pd.DataFrame(columns=["Date", "Close", "Ticker_Etf_Yf", "Short_Name_Etf"]) # Retourner un DataFrame vide si aucun historique
    
    return df_hist

def infos_etfs_clean(csv_bdd, df_hist):
    # Filtrer le fichier infos pour ne garder que les tickers des ETFs avec historique
    df_infos = pd.read_csv(os.path.join(csv_bdd, "etfs_infos.csv"), encoding="utf-8")
    # Compter avant/après
    nb_avant = len(df_infos)
    
    df_infos = df_infos[df_infos["Ticker_Etf_Yf"].isin(df_hist["Ticker_Etf_Yf"])]
    
    # Afficher les stats
    nb_apres = len(df_infos)
    print(f"🔄 Synchronisation : {nb_avant} → {nb_apres} ETFs ({nb_avant - nb_apres} supprimés)")
    
    df_infos.to_csv(os.path.join(csv_bdd, "etfs_infos.csv"), index=False, encoding="utf-8")

    return df_infos


if __name__ == "__main__":
    df_hist = hist_etfs(csv_bdd="csv/csv_bdd/")
    infos_etfs_clean(csv_bdd="csv/csv_bdd/", df_hist=df_hist)