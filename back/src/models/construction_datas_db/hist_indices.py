import pandas as pd
import yfinance as yf
import os


def recuperer_et_clean_indices(csv_bdd):

    # Charger les tickers
    df_infos = pd.read_csv(os.path.join(csv_bdd, "indices_infos.csv"), encoding="utf-8")
    tickers_yahoo = df_infos["Ticker_Indice_Yf"].dropna().unique().tolist()

    dfs = []

    for i in tickers_yahoo:
        try:
            # Crée un objet ticker
            ticker = yf.Ticker(i)

            # Récupération des données historiques
            hist = ticker.history(period="max", interval="1mo")
        
            # Ajoute la colonne "Short_Name_Indice"
            hist['Short_Name_Indice'] = ticker.info.get("shortName", "N/A")
        
            if hist.empty:
                print(f"⚠️ Historique vide pour {i}.")
                continue

            hist['Ticker_Indice_Yf'] = i
            dfs.append(hist)
              
        except Exception as e:
            print(f"Erreur de récupération pour {i}: {e}")
            continue  # Passe au suivant même en cas d'erreur

    # Si aucun historique n'a été récupéré, crée un DataFrame vide avec les bonnes colonnes
    if not dfs:
        print("❌ Aucun historique récupéré, création d'un fichier CSV vide.")
        df = pd.DataFrame(columns=["Date", "Close", "Ticker_Indice_Yf", "Short_Name_Indice"])
        df.to_csv(os.path.join(csv_bdd, "historique_indices.csv"), index=False, encoding="utf-8")
        return df

    # Fusion de tous les historiques
    df = pd.concat(dfs)
    df.reset_index(inplace=True)

    ############################################ NETTOYAGE DATAFRAME ############################################
    
    # Supprimer colonnes inutiles
    df = df.drop(columns=["Open", "High", "Low", "Volume", "Dividends", "Stock Splits"], errors="ignore")

    # Convertir la colonne "Date" en format datetime et reformater en "JJ-MM-AAAA"
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", utc=True).dt.strftime("%d-%m-%Y")


    # Arrondir la colonne "Close"
    df["Close"] = df["Close"].round(4)

    # Réorganiser les colonnes dans l'ordre souhaité
    df = df[["Date", "Close", "Ticker_Indice_Yf", "Short_Name_Indice"]]

    # Sauvegarde
    df.to_csv(os.path.join(csv_bdd, "historique_indices.csv"), index=False, encoding="utf-8")
    print(f"✅ Données récupérées et nettoyées enregistrées dans dossier")
    
    return df

if __name__ == "__main__":
    recuperer_et_clean_indices = recuperer_et_clean_indices(csv_bdd = "csv/csv_bdd/")
