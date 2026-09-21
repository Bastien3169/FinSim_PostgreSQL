import streamlit as st
from src.components.components_views import *
from src.api_client.api_client import *

def login_page(auth_manager, go_to=None):
    load_css()
    display_page_title("🔐 AUTHENTIFICATION FinSim")

    menu = st.radio("Connexion ou Inscription ?", ["Connexion", "Inscription"], horizontal=True)

    if menu == "Connexion":
        email = st.text_input("📧 Votre email", key="login_email")
        password = st.text_input("🔒 Mot de passe", type="password", key="login_password")
        stay_connected = st.checkbox("Rester connecté", value=False)

        if st.button("👤 Se connecter", use_container_width=True):
            if not email or not password:
                st.error("❌ Veuillez remplir tous les champs")
            else:
                success, message, role = auth_manager.login(email, password, stay_connected)
                if success:
                    st.session_state.auth = True
                    st.session_state.user_email = email
                    st.session_state.user_role = role
                    st.session_state.page = "home"
                    st.success(message)
                    st.info("⏳ Connexion en cours…")

                    # ⚠️ CORRECTIF PERSISTANCE — surtout PAS de st.rerun() ici.
                    #
                    # auth_manager.login() vient d'appeler cookies.save(), qui
                    # rend le composant Streamlit chargé d'écrire session_id
                    # dans document.cookie. st.rerun() interrompt le run
                    # immédiatement (RerunException) : le composant n'est jamais
                    # envoyé au navigateur, le cookie n'est jamais écrit, la
                    # valeur reste coincée dans st.session_state, et tout est
                    # perdu au premier rafraîchissement de la page.
                    #
                    # En laissant le run se terminer, le composant écrit le
                    # cookie puis renvoie sa valeur à Streamlit, ce qui
                    # déclenche de lui-même le rerun vers la page "home".
                else:
                    st.error(message)

        if st.button("🔑 Mot de passe oublié ?", key="forgot_password_link", use_container_width=True):
            go_to("forgot_password")



    # ============================================ S'INSCRIRE ============================================
    elif menu == "Inscription":
        username = st.text_input("👤 Nom d'utilisateur", key="register_username")
        email = st.text_input("📧 Votre email", key="register_email")
        password = st.text_input("🔒 Mot de passe", type="password", key="register_password")
        confirm_password = st.text_input("🔒 Confirmez le mot de passe", type="password", key="register_confirm_password")

        st.info("ℹ️ Le mot de passe doit contenir :\n- Au moins 5 caractères\n- Une majuscule\n- Une minuscule\n- Un chiffre\n- Un caractère spécial (!@#$%^&*?)")

        if st.button("📝 S'inscrire", use_container_width=True):
            if not username or not email or not password or not confirm_password:
                st.error("❌ Veuillez remplir tous les champs")
            elif password != confirm_password:
                st.error("❌ Les mots de passe ne correspondent pas")
            else:
                success, message = auth_manager.register(username, email, password)
                if success:
                    st.success(message)
                    st.info("✅ Vous pouvez maintenant vous connecter en utilisant l'onglet 'Connexion' ci-dessus")
                else:
                    st.error(message)

    footer()
