import streamlit as st
import sqlite3
import bcrypt



####################################### CONNEXION BD POUR ENREGISTREMENT USER #######################################

# Connexion à la base de données
conn = sqlite3.connect("sql/user.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute(
    """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password BLOB NOT NULL
    )"""
)
conn.commit()

# Hachage et vérification du mot de passe
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password)

# Inscription
def register(username, password):
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        return "Nom d'utilisateur déjà pris"
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
    conn.commit()
    return "Compte créé avec succès !"

# Connexion
def login(username, password):
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if user and check_password(password, user[0]):
        st.session_state["user"] = username
        st.rerun()
    else:
        st.error("Identifiants incorrects")

# Déconnexion
def logout():
    st.session_state.pop("user", None)
    st.rerun()



####################################### STREAMLIT INTERFACE #######################################

# Chargement du fichier CSS
with open("css/streamlit.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

# CSS titre et sous-titre
st.markdown(f"""<div class="main-container"><h1>CONNEXION ET INSCRIPTION</h1></div>""", unsafe_allow_html=True)
st.markdown(f"""<div class="main-container"><h2>👤 Connexion</h2></div>""", unsafe_allow_html=True)

if "user" in st.session_state:
    st.success(f"Bienvenue, {st.session_state['user']} !")
    if st.button("Se déconnecter"):
        logout()
else:
    choice = st.radio("Connexion ou Inscription ?", ["Connexion", "Inscription"])
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")

    if choice == "Inscription":
        confirm_password = st.text_input("Confirmez le mot de passe", type="password")
        if st.button("S'inscrire") and password == confirm_password:
            st.success(register(username, password))

    if choice == "Connexion":
        if st.button("Se connecter"):
            login(username, password) 