import os
import glob
import pandas as pd


def infos_stocks(dossier_csv, csv_bdd) :
    
    # Créer le chemin complet avec un motif
    motif_fichiers = os.path.join(dossier_csv, "composition_*.csv")
    
    # Récupérer les fichiers
    fichiers_csv = glob.glob(motif_fichiers)
    
    # Liste pour stocker les DataFrames
    dfs = []
    
    # Chargement des fichiers CSV
    for i in fichiers_csv:
        df = pd.read_csv(i)
        dfs.append(df)
    
    # Concaténation de tous les DataFrames
    df_concat = pd.concat(dfs, ignore_index=True)
    
    # Enlever les colonnes qui ne ne veullent plus rien dire ici
    df_final = df_concat.drop(columns=["Nom_Indice", "Nombres_Entreprises"])
    
    # Sauvegarde du fichier fusionné sans doublons
    df_final.to_csv(os.path.join(csv_bdd, "stocks_infos.csv"), index=False, encoding="utf-8")
    
    # Affichage du DataFrame final
    return df_final

if __name__ == "__main__":
    infos_stocks = infos_stocks(dossier_csv = "csv/", csv_bdd = "csv/csv_bdd/") #Appel de la fonction
    display(infos_stocks)