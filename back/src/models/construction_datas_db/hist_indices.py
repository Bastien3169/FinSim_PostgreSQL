import pandas as pd
import yfinance as yf
import os


def recuperer_et_clean_indices(csv_bdd):

    # Charger les tickers
    df_infos = pd.read_csv(os.path.join(csv_bdd, "indices_infos.csv"), encoding="utf-8")
    tickers_yahoo = df_infos["ticker_indice_yf"].dropna().unique().tolist()

    dfs = []

    for i in tickers_yahoo:
        try:
            # Crée un objet ticker
            ticker = yf.Ticker(i)

            # Récupération des données historiques
            hist = ticker.history(period="max", interval="1mo")
        
            # Ajoute la colonne "Short_Name_Indice"
            hist['short_name_indice'] = ticker.info.get("shortName", "N/A")
        
            if hist.empty:
                print(f"⚠️ Historique vide pour {i}.")
                continue

            hist['ticker_indice_yf'] = i
            dfs.append(hist)
              
        except Exception as e:
            print(f"Erreur de récupération pour {i}: {e}")
            continue  # Passe au suivant même en cas d'erreur

    # Si aucun historique n'a été récupéré, crée un DataFrame vide avec les bonnes colonnes
    if not dfs:
        print("❌ Aucun historique récupéré, création d'un fichier CSV vide.")
        df = pd.DataFrame(columns=["date", "close", "ticker_indice_yf", "short_name_indice"])
        df.to_csv(os.path.join(csv_bdd, "historique_indices.csv"), index=False, encoding="utf-8")
        return df

    # Fusion de tous les historiques
    df = pd.concat(dfs)
    df.reset_index(inplace=True)

    ############################################ NETTOYAGE DATAFRAME ############################################
    
    # après concat des dfs et reset_index
    df.reset_index(inplace=True)

    # Supprimer colonnes inutiles
    df = df.drop(columns=["Open", "High", "Low", "Volume", "Dividends", "Stock Splits"], errors="ignore")

    # Convertir l’index date (ou la colonne Date si reset_index) en datetime et garder que la date
    df["date"] = pd.to_datetime(df["Date"], utc=True).dt.date

    # Arrondir la colonne "Close"
    df["close"] = df["Close"].round(4)

    # Réorganiser colonnes
    df = df[["date", "close", "ticker_indice_yf", "short_name_indice"]]

    # Sauvegarder CSV
    df.to_csv(os.path.join(csv_bdd, "historique_indices.csv"), index=False, encoding="utf-8")

    print(f"✅ Données récupérées et nettoyées enregistrées dans dossier")
    
    return df

if __name__ == "__main__":
    recuperer_et_clean_indices = recuperer_et_clean_indices(csv_bdd = "csv/csv_bdd/")
