import sys
import os
from dotenv import load_dotenv

# Charge les variables d'environnement
load_dotenv()

# Ajoute le chemin du projet
sys.path.append(os.path.dirname(__file__))

from src.models.users_db.users_queries import BaseDBManager
from src.models.construction_datas_db.sql_datas import main_creation_db

if __name__ == "__main__":
    print("🔧 Initialisation de la base de données...")
    
    # 1. Crée les tables users/sessions
    print("📝 Création des tables utilisateurs...")
    base_manager = BaseDBManager()
    
    # 2. Crée les tables de données financières
    print("📊 Création des tables de données financières...")
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    csv_path = os.path.join(BASE_DIR, "csv", "csv_bdd")
    main_creation_db(csv_path)
    
    print("✅ Base de données initialisées avec succès !")