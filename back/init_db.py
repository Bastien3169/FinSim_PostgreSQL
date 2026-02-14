import sys
import os
from pathlib import Path
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

    # 2. Crée le gestionnaire de base de données
    base_manager = BaseDBManager()
    
    # 3. Crée les tables de données financières
    print("📊 Création des tables de données financières...")

    # ✅ Chemin relatif à init_db.py (qui est dans /app/)
    csv_path = Path(__file__).parent / "csv" / "csv_bdd"
    
    print(f"📂 CSV PATH = {csv_path}")
    print(f"✅ EXISTS = {csv_path.exists()}")
    
    # 4. Importe les données CSV dans la base de données
    main_creation_db(str(csv_path))
    
    print("✅ Base de données initialisées avec succès !")