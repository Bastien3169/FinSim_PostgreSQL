import sqlite3
import hashlib
import bcrypt
import streamlit as st
from datetime import datetime

db_path = 'user.db'
####################################### INITIALISE LA BASE DE DONNEE "users.db" #######################################

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        registration_date TEXT
        )
    ''')
    conn.commit()
    conn.close()


############################################### HASHAGE DU MDP ###############################################

# Hachage du mot de passe
def hash_password(password):
    # Génère un sel + hash le mot de passe
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')
    return hashed  # c'est un bytes, tu peux .decode() si tu veux l'enregistrer en texte

# Vérification du mot de passe au moment de la connexion
def check_password(password, hashed_password):
    # hashed_password doit être en bytes (donc re-encodé si c'était enregistré en texte)
    return bcrypt.checkpw(password.encode(), hashed_password.encode('utf-8'))


############################################### ENREGISTREMENT DU CLIENT ###############################################

def register(username, password, db_path):
    with sqlite3.connect(db_path) as conn: # with permet de refermet la requete automatiquement à la fin du bloc
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,)) # Envoie une requete pour savoir si 'username' es dans la table
        if c.fetchone(): #fetchone envoie une seule requete, celle qu'on vient de faire pour voir si 'username' existe
            return "❌ Nom d'utilisateur déjà pris"

        c.execute("INSERT INTO users (username, password, registration_date) VALUES (?, ?, ?)",
                  (username, hash_password(password), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))) #requete d'insertion pour 3 colonnes
        conn.commit() # commit = enregistrement
        return f"✅ Compte '{username}' créé avec succès !"


############################################### CONNECTION CLIENT ###############################################

def login(username, password, db_path):
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username=?", (username,))  # récupère le mdp_hasché de la db associé au username donné
        result = c.fetchone()  # result[0] contient le mdp_hasché (car fetchone() retourne un tuple avec une seule colonne, donc result est un tuple de la forme ('mdp_haché',)).
    
    # Vérifie si l'utilisateur existe
    if not result:  
        return "Erreur : Utilisateur non trouvé"
    
    # Vérifie si le mot de passe est correct
    if not check_password(password, result[0]):  # Utilise check_password pour vérifier le mot de passe
        return "Erreur : Mot de passe incorrect"
    
    return None  # Connexion réussie


########################################## DECONNEXION CLIENT ##########################################

def logout():
    if st.button("Se déconnecter"): # Bouton se deconnecter
        st.session_state.pop('user', None) # Efface la session user de st.session_state
        st.rerun() # recharge la page

