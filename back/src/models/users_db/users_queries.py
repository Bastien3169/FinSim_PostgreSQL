import os
import uuid
import re
import bcrypt
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy import text
from src.api_conn.database_conn import engine
from dotenv import load_dotenv

load_dotenv() # Charge les variables d'environnement du .env

# ==========================================================================
# CORRECTIF PERSISTANCE DE SESSION
# ==========================================================================
# Nombre maximum de sessions actives simultanees par utilisateur.
# Une session = UN appareil (Streamlit dans le navigateur, Flet sur le
# telephone, un autre navigateur...). Le code d'origine supprimait toutes
# les sessions du compte a chaque login : se connecter sur Flet deconnectait
# Streamlit, et inversement.
MAX_SESSIONS_PAR_USER = 5

# Duree de validite d'une session, en jours
DUREE_SESSION_COURTE = 1    # sans "Rester connecte"
DUREE_SESSION_LONGUE = 30   # avec "Rester connecte"


def _utcnow() -> datetime:
    """datetime UTC naif, compatible avec les colonnes TIMESTAMP sans fuseau.

    _utcnow() est deprecie depuis Python 3.12. On passe par
    datetime.now(timezone.utc) puis on retire le fuseau, pour rester
    coherent avec les lignes deja presentes en base.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)

# Récupérer depuis variables d'environnement
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@finsim.com')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'Admin123!')

class BaseDBManager:
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        """Crée les tables si elles n'existent pas"""
        with engine.begin() as conn:
            # Table users
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    registration_date TIMESTAMP NOT NULL
                )
            """))
            
            # Table sessions
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """))

            # --- Migration NON DESTRUCTIVE de la table sessions ---------------
            # ADD COLUMN IF NOT EXISTS : rejouable a chaque demarrage, aucune
            # donnee perdue, aucune session existante invalidee.
            # created_at    : sert a supprimer les sessions les plus anciennes
            # duration_days : sert a l'expiration glissante (on doit savoir de
            #                 combien repousser : 1 jour ou 30 jours)
            conn.execute(text(
                "ALTER TABLE sessions ADD COLUMN IF NOT EXISTS created_at TIMESTAMP"))
            conn.execute(text(
                "ALTER TABLE sessions ADD COLUMN IF NOT EXISTS duration_days INTEGER"))
            conn.execute(
                text("UPDATE sessions SET created_at = :now WHERE created_at IS NULL"),
                {"now": _utcnow()}
            )
            conn.execute(
                text("UPDATE sessions SET duration_days = :d WHERE duration_days IS NULL"),
                {"d": DUREE_SESSION_COURTE}
            )

            # get_current_user() est appele a chaque rerun Streamlit : on indexe.
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)"))
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at)"))
            
            # Table password_resets
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS password_resets (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """))
        
        print("✅ Tables users/sessions/password_resets créées")

######################################################## 
# CLASSE AUTH
########################################################
class AuthManager(BaseDBManager):
    def __init__(self):
        super().__init__()
        self.clean_expired_sessions() # supprime les sessions expirées au démarrage
        self.create_first_admin()  # Crée admin s'il y en a p as
    

    # --------------------------- first admin --------------------------- #
    def create_first_admin(self):
        if not ADMIN_USERNAME or not ADMIN_EMAIL or not ADMIN_PASSWORD:
            print("⚠️ Variables admin non configurées - Aucun admin créé")
            return

        # Vérifier si un admin existe déjà
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM users WHERE role = 'admin'"))
            admin_count = result.fetchone()[0]

        if admin_count > 0:
            return  # Au moins un admin existe déjà

        # Utilisation directe des variables globales
        print(f"⚠️  Aucun admin trouvé, création automatique...")
        print(f"   Username : {ADMIN_USERNAME}")
        print(f"   Email    : {ADMIN_EMAIL}")

        success, message = self.register(ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD)

        if success:
            with engine.begin() as conn:
                conn.execute(
                    text("UPDATE users SET role = 'admin' WHERE email = :email"),
                    {"email": ADMIN_EMAIL}
                )
            print(f"✅ Admin créé avec succès !")
        else:
            print(f"❌ Erreur : {message}")

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
        
        with engine.begin() as conn:
            # Vérifier si l'email existe
            result = conn.execute(
                text("SELECT * FROM users WHERE email = :email"),
                {"email": email}
            )
            if result.fetchone():
                return False, "❌ Email déjà utilisé"
            
            # Créer l'utilisateur
            hashed = self.hash_password(password)
            conn.execute(
                text("""
                    INSERT INTO users (username, email, password, role, registration_date)
                    VALUES (:username, :email, :password, :role, :date)
                """),
                {
                    "username": username,
                    "email": email,
                    "password": hashed,
                    "role": "user",
                    "date": datetime.now()
                }
            )
        
        return True, f"✅ Compte '{username}' créé avec succès !"
    
    # --------------------------- Login / Logout --------------------------- #
    def login(self, email, password, stay_connected=False):
        with engine.begin() as conn:
            # Récupérer l'utilisateur
            result = conn.execute(
                text("SELECT id, password, role FROM users WHERE email = :email"),
                {"email": email}
            )
            user = result.fetchone()
            
            if not user:
                return False, "❌ Utilisateur non trouvé", None, None
            
            user_id, hashed, role = user
            
            if not self.check_password(password, hashed):
                return False, "❌ Mot de passe incorrect", None, None
            
            # /!\ CORRECTIF PRINCIPAL
            # Avant : DELETE FROM sessions WHERE user_id = :user_id
            # -> toutes les sessions du compte etaient effacees a chaque login,
            #    donc un seul appareil connecte a la fois. On ne purge plus que
            #    les sessions REELLEMENT expirees de cet utilisateur.
            conn.execute(
                text("DELETE FROM sessions WHERE user_id = :user_id AND expires_at <= :now"),
                {"user_id": user_id, "now": _utcnow()}
            )

            # Garde-fou : on plafonne le nombre de sessions actives par compte,
            # en supprimant les plus anciennes au-dela de MAX_SESSIONS_PAR_USER.
            conn.execute(
                text("""
                    DELETE FROM sessions
                    WHERE session_id IN (
                        SELECT session_id FROM sessions
                        WHERE user_id = :user_id
                        ORDER BY created_at DESC NULLS LAST
                        OFFSET :garde
                    )
                """),
                {"user_id": user_id, "garde": MAX_SESSIONS_PAR_USER - 1}
            )

            # Creer la nouvelle session
            session_id = str(uuid.uuid4())
            now = _utcnow()
            duration_days = DUREE_SESSION_LONGUE if stay_connected else DUREE_SESSION_COURTE
            expires_at = now + timedelta(days=duration_days)

            conn.execute(
                text("""
                    INSERT INTO sessions (session_id, user_id, expires_at, created_at, duration_days)
                    VALUES (:session_id, :user_id, :expires_at, :created_at, :duration_days)
                """),
                {
                    "session_id": session_id,
                    "user_id": user_id,
                    "expires_at": expires_at,
                    "created_at": now,
                    "duration_days": duration_days
                }
            )
        
        return True, "✅ Connexion réussie", role, session_id
    
    def logout(self, session_id):
        if not session_id:
            return
        
        with engine.begin() as conn:
            conn.execute(
                text("DELETE FROM sessions WHERE session_id = :session_id"),
                {"session_id": session_id}
            )
    
    # --------------------------- Check current user --------------------------- #
    def get_current_user(self, session_id):
        """Renvoie l'utilisateur d'une session valide, et prolonge la session.

        Expiration glissante : tant que l'utilisateur revient, sa date
        d'expiration est repoussee. On ne fait l'UPDATE que si moins de la
        moitie de la fenetre reste, pour ne pas ecrire en base a chaque
        rerun Streamlit (le front appelle cette route tres souvent).
        """
        if not session_id:
            return None

        now = _utcnow()

        with engine.begin() as conn:
            result = conn.execute(
                text("""
                    SELECT u.id, u.username, u.email, u.role,
                           s.expires_at, s.duration_days
                    FROM users u
                    JOIN sessions s ON u.id = s.user_id
                    WHERE s.session_id = :session_id AND s.expires_at > :now
                """),
                {"session_id": session_id, "now": now}
            )
            row = result.fetchone()

            if not row:
                return None

            expires_at = row[4]
            fenetre = timedelta(days=row[5] or DUREE_SESSION_COURTE)

            if expires_at - now < fenetre / 2:
                conn.execute(
                    text("UPDATE sessions SET expires_at = :expires_at "
                         "WHERE session_id = :session_id"),
                    {"expires_at": now + fenetre, "session_id": session_id}
                )

            return {
                "id": row[0],
                "username": row[1],
                "email": row[2],
                "role": row[3]
            }
    
    # --------------------------- Supprimer sessions expirées --------------------------- #
    def clean_expired_sessions(self):
        with engine.begin() as conn:
            conn.execute(
                text("DELETE FROM sessions WHERE expires_at <= :now"),
                {"now": _utcnow()}
            )
    
    # --------------------------- Mot de passe oublié --------------------------- #
    def create_password_reset_token(self, email):
        with engine.begin() as conn:
            result = conn.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": email}
            )
            user = result.fetchone()
            
            if not user:
                return False, "❌ Aucun utilisateur trouvé avec cet email"
            
            user_id = user[0]
            token = secrets.token_urlsafe(32)
            expires_at = _utcnow() + timedelta(hours=1)
            
            # Supprimer anciens tokens
            conn.execute(
                text("DELETE FROM password_resets WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            
            # Créer nouveau token
            conn.execute(
                text("""
                    INSERT INTO password_resets (user_id, token, expires_at, created_at)
                    VALUES (:user_id, :token, :expires_at, :created_at)
                """),
                {
                    "user_id": user_id,
                    "token": token,
                    "expires_at": expires_at,
                    "created_at": _utcnow()
                }
            )
        
        return True, token
    
    def forgot_password(self, email):
        success, result = self.create_password_reset_token(email)
        if not success:
            return False, result
        
        token = result
        
        try:
            print(f"🔗 Token de réinitialisation : {token}")
            return True, "✅ Email de réinitialisation envoyé !"
        except Exception as e:
            return False, f"❌ Erreur lors de l'envoi de l'email : {str(e)}"
    
    def reset_password_with_token(self, token, new_password):
        password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*?])[\S\s]{5,}$'
        if not re.match(password_pattern, new_password):
            return False, "❌ Mot de passe trop faible."
        
        with engine.begin() as conn:
            # Vérifier le token
            result = conn.execute(
                text("""
                    SELECT user_id FROM password_resets
                    WHERE token = :token AND expires_at > :now
                """),
                {"token": token, "now": _utcnow()}
            )
            row = result.fetchone()
            
            if not row:
                return False, "❌ Lien de réinitialisation invalide ou expiré."
            
            user_id = row[0]
            hashed = self.hash_password(new_password)
            
            # Mettre à jour le mot de passe
            conn.execute(
                text("UPDATE users SET password = :password WHERE id = :user_id"),
                {"password": hashed, "user_id": user_id}
            )
            
            # Supprimer le token utilisé
            conn.execute(
                text("DELETE FROM password_resets WHERE user_id = :user_id"),
                {"user_id": user_id}
            )


        return True, "✅ Mot de passe réinitialisé avec succès."

######################################################## 
# CLASSE ADMIN
########################################################
class AdminManager(BaseDBManager):
    def __init__(self):
        super().__init__()
    
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')
    
    def get_all_users(self):
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, username, email, role, registration_date FROM users")
            )
            return result.fetchall()
    
    def get_user_by_email_username(self, search):
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT id, username, email, role, registration_date
                    FROM users
                    WHERE email = :search OR username = :search
                """),
                {"search": search}
            )
            return result.fetchone()
    
    def update_user(self, email, username=None, password=None, role=None):
        fields = []
        params = {"email": email}
        
        if username:
            fields.append("username = :username")
            params["username"] = username
        if password:
            hashed = self.hash_password(password)
            fields.append("password = :password")
            params["password"] = hashed
        if role:
            fields.append("role = :role")
            params["role"] = role
        
        if not fields:
            return "Aucune modification à effectuer."
        
        query = f"UPDATE users SET {', '.join(fields)} WHERE email = :email"
        
        with engine.begin() as conn:
            conn.execute(text(query), params)
        
        return f"✅ Utilisateur avec l'email '{email}' modifié avec succès."
    
    def delete_user(self, email):
        with engine.begin() as conn:
            user_id = conn.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email}).scalar()
            if user_id is None:
                return f"❌ Aucun utilisateur trouvé avec l'email {email}."
            
            conn.execute(text("DELETE FROM sessions WHERE user_id = :user_id"), {"user_id": user_id})
            conn.execute(text("DELETE FROM password_resets WHERE user_id = :user_id"), {"user_id": user_id})
            conn.execute(text("DELETE FROM users WHERE id = :user_id"), {"user_id": user_id})
        
        return f"🗑️ Utilisateur avec email {email} supprimé."