import pandas as pd
import yfinance as yf
import os

def recuperer_et_clean_stocks(csv_bdd):
    # Charger le fichier de tickers et infos
    df_tickers = pd.read_csv(os.path.join(csv_bdd, "stocks_infos.csv"), encoding="utf-8")
    tickers_yahoo = df_tickers["ticker_stocks_yf"].dropna().unique().tolist()
    
    dfs = []
   
    for i in tickers_yahoo:
        try:
            ticker = yf.Ticker(i)
            hist = ticker.history(period="max", interval="1mo")
    
            if hist.empty:
                print(f"⚠️ Historique vide pour {i}.")
                continue

            # Ajoute la colonne du ticker
            hist["ticker_stocks_yf"] = i

            # Ajoute directement le Short_Name_Stocks
            short_name = df_tickers.loc[df_tickers["ticker_stocks_yf"] == i, "short_name_stocks"].values
            hist["short_name_stocks"] = short_name[0] if len(short_name) > 0 else "N/A"
    
            dfs.append(hist)
          
        except Exception as e:
            print(f"Erreur lors de la récupération des données pour {i}: {e}")
            continue
    
    if not dfs:
        print("❌ Aucun historique récupéré, création d'un fichier CSV vide.")
        df = pd.DataFrame(columns=["date", "close", "ticker_stocks_yf", "short_name_stocks"])
        df.to_csv(os.path.join(csv_bdd, "historique_stocks.csv"), index=False, encoding="utf-8")
        return df
    
    # Concaténation de tous les historiques
    df = pd.concat(dfs)
    df.reset_index(inplace=True)
    
    ############################################ NETTOYAGE DATAFRAME ############################################
    
    # Supprimer colonnes inutiles
    df = df.drop(columns=["Open", "High", "Low", "Volume", "Dividends", "Stock Splits", "Capital Gains", "Adj Close"], errors="ignore")
    
    # Convertir la colonne "Date" en format datetime et reformater en "JJ-MM-AAAA"
    df["date"] = pd.to_datetime(df["Date"], utc=True).dt.date
    
    # Arrondir la colonne "Close"
    df["close"] = df["Close"].round(4)
    
    # Réorganiser les colonnes
    df = df[["date", "close", "ticker_stocks_yf", "short_name_stocks"]]
    
    # Sauvegarde
    df.to_csv(os.path.join(csv_bdd, "historique_stocks.csv"), index=False, encoding="utf-8")
    print(f"[✅] Le fichier historique stocks a bien été enregistré sous le nom 'historique_stocks.csv'")
    
    return df

if __name__ == "__main__":
    recuperer_et_clean_stocks(csv_bdd = "csv/csv_bdd/")
