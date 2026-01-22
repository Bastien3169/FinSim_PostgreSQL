import sqlite3
import hashlib
import bcrypt
import re
import streamlit as st
from datetime import datetime


############################################# CLASS AUTHMANAGER #############################################

class AuthManager:  
#--------------------------- Attribut : chemin et nom bdd et lancement de "init_db()" --------------------------#
    def __init__(self, db_path="user.db"):
        self.db_path = db_path
        self.init_db()

    
#--------------------------- Initialisation bdd ---------------------------#
    def init_db(self):
        with sqlite3.connect(self.db_path) as conn: # Avec "with", fermeture automatique et donc pas besoin de "conn.close()"
            c = conn.cursor()
            c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                registration_date TEXT NOT NULL
                )
            ''')
            conn.commit()

    
#--------------------------- Hachage mdp ---------------------------#
    def hash_password(self, password):
        # Génère un sel + hash le mot de passe
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')
        return hashed  # c'est un bytes, tu peux .decode() si tu veux l'enregistrer en texte


#--------------------------- Vérification mdp au moment de la connexion ---------------------------#
    def check_password(self, password, hashed_password):
        # hashed_password doit être en bytes (donc re-encodé si c'était enregistré en texte)
        check = bcrypt.checkpw(password.encode(), hashed_password.encode('utf-8'))
        return check


#--------------------------- Enreistrement ---------------------------#
    def register(self, username, email, password):
        
        # Validation mdp via regex : 5 caractères, majuscule, minuscule, chiffre, caractère spécial
        password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*?])[\S\s]{5,}$'
        if not re.match(password_pattern, password):
            return "❌ Mot de passe trop faible. Il doit contenir au moins 5 caractères, 1 majuscule, 1 minuscule, 1 chiffre et 1 caractère spécial."

        # Validation de l'email via regex : structure mail valide
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
        if not re.match(email_pattern, email):
            return "❌ Email invalide"

        # Ouverture connexion (et fermeture automatique)
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()

            # Vérifie si l'email existe déjà
            c.execute("SELECT * FROM users WHERE email = ?", (email,))
            if c.fetchone():
                return "❌ Email déjà utilisé"

            # Hachage mdp
            hashed = self.hash_password(password)

            # Insertion des infos users
            c.execute("INSERT INTO users (username, email, password, role, registration_date) VALUES (?, ?, ?, ?)",
                      (username, email, hashed, 'user', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

            # Enregistrement user
            conn.commit()
            return f"✅ Compte '{username}' créé avec succès !"
  
   
#--------------------------- login ---------------------------#
    def login(self, email, password):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT password FROM users WHERE email = ?", (email,)) # récupère le mdp_hasché de la db associé au username donné
            result = c.fetchone() # result[0] contient le mdp_hasché (car fetchone() retourne un tuple avec une seule colonne, donc result est un tuple de la forme ('mdp_haché',))
            
        if not result: # Vérifie si l'utilisateur existe
            return "Erreur : Utilisateur non trouvé"

        # Vérifie si le mot de passe est correct
        if not self.check_password(password, result[0]): # Utilise check_password pour vérifier le mot de passe
            return "Erreur : Mot de passe incorrect"
        return None  # Connexion réussie

    
#--------------------------- logout ---------------------------#
    def logout(self):
        if 'user' in st.session_state:
            if st.button("Se déconnecter"):
                st.session_state.pop('user', None) # Efface la session user de st.session_state
                st.success("Déconnexion réussie !")
                st.rerun()  # Recharge la page
        else:
            st.warning("Aucun utilisateur connecté.")


############################################# CLASS ADMINMANAGER #############################################

class AdminManager:
#--------------------------- Initialisation ---------------------------#
    def __init__(self, db_path="user.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn: # Avec "with", fermeture automatique et donc pas besoin de "conn.close()"
            c = conn.cursor()
            c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                registration_date TEXT NOT NULL
                )
            ''')
            conn.commit()
    
#--------------------------- Hachage du mot de passe ---------------------------#
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')


#--------------------------- Créer l'admin ---------------------------#
    def create_admin_user(self, username, email, password):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()

            # Vérifie si l'utilisateur existe déjà
            c.execute("SELECT * FROM users WHERE email = ?", (email,))
            if c.fetchone():
                print("❌ Cet utilisateur existe déjà.")
                return False

            # Hachage mdp
            hashed = self.hash_password(password)

            # Insertion des infos users
            c.execute("INSERT INTO users (username, email, password, role, registration_date) VALUES (?, ?, ?, ?, ?)", 
                      (username, email, hashed, 'admin', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            # Enregistrement admin
            conn.commit()
            return f"✅ Admin '{username}' créé avec succès !"


#--------------------------- Créer un utilisateur ---------------------------#
    def create_user(self, username, email, password, role='user'):
        
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            
            c.execute("SELECT * FROM users WHERE email = ?", (email,))
            if c.fetchone():
                return "❌ Email déjà utilisé"

            hashed = self.hash_password(password)
            
            c.execute("""
                INSERT INTO users (username, email, password, role, registration_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, email, hashed, 'user', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            conn.commit()
            return f"✅ Utilisateur '{username}' créé avec succès"

    
#--------------------------- Afficher tous les utilisateurs ---------------------------#
    def get_all_users(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id, username, email, role, registration_date FROM users")
            return c.fetchall()

    
#--------------------------- Trouver un utilisateur par email ---------------------------#
    def get_user_by_email(self, email):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id, username, email, role, registration_date FROM users WHERE email = ?", (email,))
            return c.fetchone()  # Récupère l'utilisateur par son email

     
#--------------------------- Modifier un utilisateur ---------------------------#
    def update_user(self, email, username=None, password=None, role=None):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            
            # Requête de mise à jour pour un utilisateur en fonction de l'email
            fields = []
            values = []
    
            if username:
                fields.append("username = ?")
                values.append(username)
            if password:
                hashed = self.hash_password(password)
                fields.append("password = ?")
                values.append(hashed)
            if role:
                fields.append("role = ?")
                values.append(role)
    
            # Vérification si au moins un champ a été modifié
            if not fields:
                return "Aucune modification à effectuer."
    
            # Ajout de l'email pour effectuer la mise à jour sur l'utilisateur trouvé par email
            values.append(email)
            query = f"UPDATE users SET {', '.join(fields)} WHERE email = ?"
            c.execute(query, values)
            conn.commit()
            return f"✅ Utilisateur avec l'email '{email}' modifié avec succès."

    
#--------------------------- Supprimer un utilisateur ---------------------------#
    def delete_user(self, email):
        
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            
            c.execute("DELETE FROM users WHERE email = ?", (email,))
            
            conn.commit()
            return f"🗑️ Utilisateur avec email {email} supprimé."
