import streamlit as st

# ---------------------------------------------------------
# CONFIG GLOBALE
# ---------------------------------------------------------
st.set_page_config(layout="wide", page_title="FinSim", page_icon="🏛️")

# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------
from src.views.auth import login_page
from src.views.home import home_page
from src.views.indices import indices_page
from src.views.stocks import stocks_page
from src.views.cryptos import cryptos_page
from src.views.ETFs import etfs_page
from src.views.dca_vs_ls import dca_vs_ls_page
from src.views.comparaison_actifs import actifs_page
from src.views.admin import admin_page
from src.api_client.api_client import AuthManager
from src.views.forgot_password import forgot_password_page
from src.views.reset_password import reset_password_page
from src.views.confidentialite import confidentialite_page

# ---------------------------------------------------------
# AUTH MANAGER
# ---------------------------------------------------------
# ⚠️ CORRECTIF PERSISTANCE — ne PAS mettre l'AuthManager dans st.session_state.
#
# Ancien code :
#     if "auth_manager" not in st.session_state:
#         st.session_state.auth_manager = AuthManager()
#     auth_manager = st.session_state.auth_manager
#
# EncryptedCookieManager n'est pas un simple objet Python : c'est un COMPOSANT
# Streamlit. Son __init__ appelle _component_func(...), qui est ce qui déclare
# l'iframe chargée de lire et d'écrire document.cookie dans le navigateur.
# Un composant doit être re-rendu à CHAQUE exécution du script, sinon Streamlit
# le retire de l'arbre et l'iframe disparaît côté navigateur.
#
# En le mettant en cache, on ne l'instanciait qu'une fois : aux reruns suivants
# le composant n'était plus déclaré, les écritures de cookies mises en file dans
# st.session_state['CookieManager.queue'] n'étaient jamais envoyées au
# navigateur, et tout disparaissait au premier F5.
auth_manager = AuthManager()

# S'assurer que les cookies sont prêts (1er run : le composant renvoie None)
if not auth_manager.cookies.ready():
    st.stop()

# Filet de sécurité : si une écriture de cookie est restée en attente parce que
# le run précédent a été coupé avant que le navigateur ait pu l'appliquer, on la
# rejoue. save() ne fait rien si la file est vide, et le CookieManager vient de
# retirer de cette file tout ce qui est déjà présent dans le navigateur.
auth_manager.cookies.save()

# ---------------------------------------------------------
# ⭐ RÉCUPÉRER LES QUERY PARAMS DEPUIS L'URL
# ---------------------------------------------------------
query_params = st.query_params
url_page = query_params.get("page", None)

# ⭐ Si la page est dans l'URL, l'utiliser en priorité
if url_page:
    st.session_state.page = url_page

# ---------------------------------------------------------
# ⭐ AUTO-LOGIN : vérifier si l'utilisateur a déjà un cookie valide
# ---------------------------------------------------------
# Un SEUL appel par run : l'ancien code interrogeait /api/auth/me deux fois
# (ici puis dans router()), soit deux allers-retours HTTP vers Railway à
# chaque interaction. On récupère l'utilisateur une fois et on le transmet.
user = auth_manager.get_current_user()

if user:
    # ✅ Utilisateur déjà connecté via cookie
    st.session_state.auth = True
    st.session_state.user_email = user["email"]
    st.session_state.user_role = user["role"]

    # ⭐ Page par défaut "home" si connecté (SEULEMENT si pas de page dans l'URL)
    if "page" not in st.session_state and not url_page:
        st.session_state.page = "home"
else:
    # ❌ Pas de cookie valide
    st.session_state.auth = False

    # ⭐ Page par défaut "auth" si non connecté (SEULEMENT si pas de page dans l'URL)
    if "page" not in st.session_state and not url_page:
        st.session_state.page = "auth"

# ---------------------------------------------------------
# NAVIGATION
# ---------------------------------------------------------
def go_to(page: str):
    st.session_state.page = page
    # ⭐ Nettoyer les query params quand on navigue
    st.query_params.clear()
    st.rerun()

# ---------------------------------------------------------
# ROUTER
# ---------------------------------------------------------
def router(user):
    page = st.session_state.page

    # ⭐ Pages publiques (accessibles sans authentification)
    if page == "auth":
        login_page(auth_manager, go_to=go_to)
        return

    if page == "forgot_password":
        forgot_password_page(auth_manager, go_to=go_to)
        return

    if page == "reset_password":
        reset_password_page(auth_manager, go_to=go_to)
        return

    # ⭐ Pages protégées (nécessitent authentification)
    # `user` vient du contrôle fait plus haut : pas de second appel réseau.
    if not user:
        # Si pas de session valide, rediriger vers auth
        st.session_state.page = "auth"
        st.session_state.auth = False
        st.rerun()
        return

    routes = {
        "home": lambda: home_page(go_to, auth_manager),
        "indices": lambda: indices_page(go_to),
        "stocks": lambda: stocks_page(go_to),
        "cryptos": lambda: cryptos_page(go_to),
        "etfs": lambda: etfs_page(go_to),
        "dca_vs_ls": lambda: dca_vs_ls_page(go_to),
        "comparaison_actifs": lambda: actifs_page(go_to),
        "admin": lambda: admin_page(go_to),
        "confidentialite": lambda: confidentialite_page(go_to)
    }

    # Si page inconnue → home
    if page not in routes:
        st.session_state.page = "home"
        st.rerun()

    # Vérifier les droits admin
    if page == "admin" and st.session_state.user_role != "admin":
        st.error("⛔ Accès interdit")
        return

    routes[page]()

# ---------------------------------------------------------
# APP
# ---------------------------------------------------------
router(user)
