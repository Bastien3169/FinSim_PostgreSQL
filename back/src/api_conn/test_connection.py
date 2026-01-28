'''
import os
from dotenv import load_dotenv

# Charge le .env
load_dotenv()

print("🔍 Variables d'environnement chargées :")
print(f"PGHOST: {os.getenv('PGHOST')}")
print(f"PGDATABASE: {os.getenv('PGDATABASE')}")
print(f"PGUSER: {os.getenv('PGUSER')}")
print(f"PGPASSWORD: {'***' if os.getenv('PGPASSWORD') else '(vide)'}")
print(f"PGPORT: {os.getenv('PGPORT')}")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")

print("\n🔗 Test de connexion PostgreSQL...")

try:
    import psycopg2
    
    conn = psycopg2.connect(
        host=os.getenv('PGHOST'),
        database=os.getenv('PGDATABASE'),
        user=os.getenv('PGUSER'),
        password=os.getenv('PGPASSWORD', ''),  # Vide si pas de mot de passe
        port=os.getenv('PGPORT')
    )
    
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    
    print(f"✅ Connexion réussie !")
    print(f"📊 Version PostgreSQL : {version[0]}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Erreur de connexion : {e}")
'''

"""
Script de test de connexion PostgreSQL avec SQLAlchemy Core
À lancer pour vérifier que la connexion fonctionne
"""
import os
import sys
from dotenv import load_dotenv

# Charge les variables d'environnement
load_dotenv()

# Ajoute le chemin du projet
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

print("🔍 Variables d'environnement chargées :")
print(f"PGHOST: {os.getenv('PGHOST')}")
print(f"PGDATABASE: {os.getenv('PGDATABASE')}")
print(f"PGUSER: {os.getenv('PGUSER')}")
print(f"PGPASSWORD: {'***' if os.getenv('PGPASSWORD') else '(vide)'}")
print(f"PGPORT: {os.getenv('PGPORT')}")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")

print("\n🔗 Test de connexion PostgreSQL avec SQLAlchemy...")

try:
    from sqlalchemy import text
    from src.api_conn.database_conn import engine
    
    # Test 1 : Connexion basique
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()
        
        print(f"✅ Connexion réussie !")
        print(f"📊 Version PostgreSQL : {version[0]}")
    
    # Test 2 : Liste des tables existantes
    print("\n📋 Tables existantes dans la base 'finsim' :")
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        
        tables = result.fetchall()
        
        if tables:
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("  ⚠️  Aucune table trouvée (base vide)")
    
    # Test 3 : Compter les lignes dans chaque table
    if tables:
        print("\n📊 Nombre de lignes par table :")
        with engine.connect() as conn:
            for table in tables:
                table_name = table[0]
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.fetchone()[0]
                    print(f"  - {table_name}: {count} ligne(s)")
                except Exception as e:
                    print(f"  - {table_name}: Erreur - {e}")
    
    print("\n✅ Tous les tests sont passés !")
    print("🎉 SQLAlchemy Core fonctionne correctement")
    
except ImportError as e:
    print(f"❌ Erreur d'import : {e}")
    print("\n💡 Solution : Installe SQLAlchemy")
    print("   pip install sqlalchemy psycopg2-binary")
    
except Exception as e:
    print(f"❌ Erreur de connexion : {e}")
    print("\n💡 Vérifications à faire :")
    print("   1. PostgreSQL est-il démarré ? → brew services list")
    print("   2. La base 'finsim' existe-t-elle ? → psql -U postgres -l")
    print("   3. Le fichier .env est-il bien configuré ?")