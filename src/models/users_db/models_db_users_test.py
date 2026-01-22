import sqlite3
import bcrypt
import re
import uuid
from datetime import datetime, timedelta
from streamlit_cookies_manager import EncryptedCookieManager
from src.services.envoie_mails import envoie_password_reset_email
import secrets
import streamlit as st


class BaseDBManager:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            # Table users
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
            # Table sessions
            c.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    expires_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')

            # Table password_resets (ajoutée ici)
            c.execute('''
                CREATE TABLE IF NOT EXISTS password_resets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            ''')

            conn.commit()


######################################################## CLASSE ADMIN ########################################################
class AuthManager(BaseDBManager):
    def __init__(self, db_path="users.db", cookie_name="session_id", cookie_secret="Toulouse31"):
        super().__init__(db_path)
        self.cookie_name = cookie_name
        # Persistance côté client via EncryptedCookieManager
        self.cookies = EncryptedCookieManager(prefix="", password=cookie_secret)
        if not self.cookies.ready():
            st.stop()
        self.clean_expired_sessions()

    # --------------------------- Utilitaires --------------------------- #
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password, hashed):
        return bcrypt.checkpw(password.encode(), hashed.encode('utf-8'))

    # --------------------------- CRUD Users --------------------------- #
    def register(self, username, email, password):
        username = username.strip()
        if not username:
            return False, "❌ Le nom d'utilisateur est obligatoire."

        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,}$'
        if not re.match(email_pattern, email):
            return False, "❌ Email invalide"

        password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*?])[\S\s]{5,}$'
        if not re.match(password_pattern, password):
            return False, "❌ Mot de passe trop faible."

        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email = ?", (email,))
            if c.fetchone():
                return False, "❌ Email déjà utilisé"

            hashed = self.hash_password(password)
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute(
                "INSERT INTO users (username, email, password, role, registration_date) VALUES (?, ?, ?, ?, ?)",
                (username, email, hashed, 'user', date)
            )
            conn.commit()

        return True, f"✅ Compte '{username}' créé avec succès !"

    # --------------------------- Login / Logout --------------------------- #
    def login(self, email, password, stay_connected=False):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id, password, role FROM users WHERE email = ?", (email,))
            user = c.fetchone()

            if not user:
                return False, "❌ Utilisateur non trouvé", None

            user_id, hashed, role = user
            if not self.check_password(password, hashed):
                return False, "❌ Mot de passe incorrect", None

            # Supprime anciennes sessions
            c.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
            # Créé nouvelle session
            session_id = str(uuid.uuid4())
            expires_at = (datetime.utcnow() + timedelta(days=30 if stay_connected else 1)).strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO sessions (session_id, user_id, expires_at) VALUES (?, ?, ?)",
                      (session_id, user_id, expires_at))
            conn.commit()

        # Stockage cookie
        self.cookies[self.cookie_name] = session_id
        self.cookies.save()

        return True, "✅ Connexion réussie", role

    def logout(self):
        session_id = self.cookies.get(self.cookie_name)
        if session_id:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
                conn.commit()
            self.cookies[self.cookie_name] = ""
            self.cookies.save()

    # --------------------------- Check current user --------------------------- #
    def get_current_user(self):
        session_id = self.cookies.get(self.cookie_name)
        if not session_id:
            return None

        date_now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT u.id, u.username, u.email, u.role
                FROM users u
                JOIN sessions s ON u.id = s.user_id
                WHERE s.session_id = ? AND s.expires_at > ?
            ''', (session_id, date_now))
            user_session = c.fetchone()

        if user_session:
            return {"id": user_session[0], "username": user_session[1], "email": user_session[2], "role": user_session[3]}
        return None

    # --------------------------- Supprimer sessions expirées --------------------------- #
    def clean_expired_sessions(self):
        date_now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM sessions WHERE expires_at <= ?", (date_now,))
            conn.commit()

# --------------------------- Mot de passe oublié --------------------------- #
    def create_password_reset_token(self, email):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id FROM users WHERE email = ?", (email,))
            user = c.fetchone()
            
            if not user:
                return False, "❌ Aucun utilisateur trouvé avec cet email"
            
            user_id = user[0]
            
            # Génère un token sécurisé
            token = secrets.token_urlsafe(32)
            expires_at = (datetime.utcnow() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
            created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            # Supprimer les anciens tokens pour cet utilisateur
            c.execute("DELETE FROM password_resets WHERE user_id = ?", (user_id,))
            
            # Insérer le nouveau token
            c.execute("INSERT INTO password_resets (user_id, token, expires_at, created_at) VALUES (?, ?, ?, ?)", (user_id, token, expires_at, created_at))
            
            conn.commit()
            
            return True, token


    def forgot_password(self, email):
        """Envoie un email de réinitialisation de mot de passe"""
        #from src.services.envoie_mails import envoie_password_reset_email
        
        success, result = self.create_password_reset_token(email)
        if not success:
            return False, result
        
        token = result
        
        try:
            envoie_password_reset_email(email, token)
            return True, "✅ Email de réinitialisation envoyé !"
        except Exception as e:
            return False, f"❌ Erreur lors de l'envoi de l'email : {str(e)}"


    def reset_password_with_token(self, token, new_password):
        """Réinitialise le mot de passe avec un token"""
        # Vérifier le format du mot de passe
        password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*?])[\S\s]{5,}$'
        if not re.match(password_pattern, new_password):
            return False, "❌ Mot de passe trop faible."
        
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            
            # Vérifier que le token existe et n'est pas expiré
            c.execute("""SELECT pr.user_id FROM password_resets pr WHERE pr.token = ? AND pr.expires_at > ?""", (token, now))
            
            row = c.fetchone()
            if not row:
                return False, "❌ Lien de réinitialisation invalide ou expiré."
            
            user_id = row[0]
            
            # Mettre à jour le mot de passe
            hashed = self.hash_password(new_password)
            c.execute("UPDATE users SET password = ? WHERE id = ?", (hashed, user_id))
            
            # Supprimer tous les tokens pour cet utilisateur
            c.execute("DELETE FROM password_resets WHERE user_id = ?", (user_id,))
            
            conn.commit()
            
            return True, "✅ Mot de passe réinitialisé avec succès."
        


######################################################## CLASSE ADMIN ########################################################

class AdminManager(BaseDBManager):
#--------------------------- Initialisation et et lancement de "super().init_db()" ---------------------------#
    def __init__(self, db_path="users.db"):
        super().__init__(db_path) # appelle init_db via la classe parente

   
#--------------------------- Hachage du mot de passe ---------------------------#
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')


#--------------------------- Afficher tous les utilisateurs ---------------------------#
    def get_all_users(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id, username, email, role, registration_date FROM users")
            return c.fetchall()

    
#--------------------------- Trouver un utilisateur par email/username ---------------------------#
    def get_user_by_email_username(self, search):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT id, username, email, role, registration_date FROM users WHERE email = ? OR username = ?", (search, search))
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