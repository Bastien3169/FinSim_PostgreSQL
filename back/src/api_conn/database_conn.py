"""
Connexion PostgreSQL avec SQLAlchemy Core
- Connection pooling automatique
- Gestion transactions sécurisée
- Compatible avec pandas.to_sql()
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv

# Charge le .env
load_dotenv()

# =====================================================
# CONFIGURATION ENGINE
# =====================================================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{os.getenv('PGUSER', 'postgres')}:"
    f"{os.getenv('PGPASSWORD', '')}@"
    f"{os.getenv('PGHOST', 'localhost')}:"
    f"{os.getenv('PGPORT', '5432')}/"
    f"{os.getenv('PGDATABASE', 'finsim')}"
)

# Engine avec connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,          # 5 connexions en pool
    max_overflow=10,      # +10 connexions si besoin
    pool_pre_ping=True,   # Vérifie que la connexion est vivante
    echo=False            # Mettre True pour débogger (affiche les requêtes SQL)
)

# =====================================================
# FONCTIONS UTILITAIRES
# =====================================================
def get_connection():
    """
    Retourne une connexion depuis le pool
    Usage: with get_connection() as conn:
    """
    return engine.connect()

def execute_query(query, params=None):
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        return result.fetchall()

def execute_insert_update(query, params=None):
    with engine.begin() as conn:  # Auto-commit
        result = conn.execute(text(query), params or {})
        return result.rowcount

# =====================================================
# TEST CONNEXION
# =====================================================
def test_connection():
    """Teste la connexion à la base de données"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Connexion PostgreSQL OK")
            return True
    except Exception as e:
        print(f"❌ Erreur connexion : {e}")
        return False

if __name__ == "__main__":
    test_connection()