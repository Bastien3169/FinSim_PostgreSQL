import os
import glob
import pandas as pd
import yfinance as yf

def infos_indices(dossier_csv, csv_bdd):

    # Créer le chemin complet avec un motif
    motif_fichiers = os.path.join(dossier_csv, "composition_*.csv")
    
    # Récupérer les fichiers
    fichiers_csv = glob.glob(motif_fichiers)
    
    # Liste pour stocker les DataFrames
    dfs = []
    
    # Chargement des fichiers CSV
    for fichier in fichiers_csv:
        df = pd.read_csv(fichier)
        dfs.append(df)
    
    # Concaténation de tous les DataFrames
    df_concat = pd.concat(dfs, ignore_index=True)

    # Ne garder qu'une seule ligne par indice (avec ses infos associées)
    df_final = df_concat.drop_duplicates(subset=["Nom_Indice"])

    
    # Enlever les colonnes qui ne ne veullent plus rien dire ici
    df = df_final.drop(columns=["Short_Name_Stocks", "Ticker_Stocks_Yf", "Ticker_Stocks", "Secteur_Activite", 
                                "Pays_Stocks", "Place_Boursiere", "Capitalisation_Boursiere", "Ponderation"])


    # Listes pour stocker les nouvelles informations
    devise = []
    place_boursiere_indice = []
    short_name_indice = []
    
    # Récupération des informations via yfinance
    for i in df["Ticker_Indice_Yf"]:
        try:
            info = yf.Ticker(i).info  # Récupération des infos générales
            
            # Extraction des données
            devises = info.get("currency", "Non disponible")
            places_boursieres_indices = info.get("exchange", "Non disponible")
            shorts_names_indices = info.get('shortName', 'Non disponible')
            
        except Exception as e:
            devises = "Non disponible"
            places_boursieres_indices = "Non disponible"
            shorts_names_indices = "Non disponible"
            
        # Ajout des valeurs aux listes
        devise.append(devises)
        place_boursiere_indice.append(places_boursieres_indices)
        short_name_indice.append(shorts_names_indices)
    
    # Ajout des nouvelles colonnes au DataFrame
    df["Devise"] = devise
    df["Place_Boursiere_Indice"] = place_boursiere_indice
    df["Short_Name_Indice"] = short_name_indice
    
    # Réorganisation des colonnes
    df = df[
        ["Short_Name_Indice", "Ticker_Indice_Yf", 'Nom_Indice', 'Devise', 'Place_Boursiere_Indice', 'Nombres_Entreprises']
        ]

    # Sauvegarde du fichier
    df.to_csv(os.path.join(csv_bdd, "indices_infos.csv"), index=False, encoding="utf-8")

    
    # Affichage du DataFrame final
    return df

if __name__ == "__main__":
    infos_indices = infos_indices(dossier_csv = "csv/", csv_bdd = "csv/csv_bdd/")
    display(infos_indices)
