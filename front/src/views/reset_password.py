import streamlit as st
from src.components.components_views import *
from src.api_client.api_client import *

def reset_password_page(auth_manager, go_to=None):
    load_css()
    display_page_title("🔄 RÉINITIALISER LE MOT DE PASSE")

    # Récupérer le token depuis les query params
    query_params = st.query_params
    token = query_params.get("token", None)

    if not token:
        st.error("❌ Lien invalide ou expiré")
        if st.button("⬅️ Retour à la connexion"):
            if go_to:
                go_to("auth")
        return

    st.markdown("""
        <div class="main-container">
            <p>Choisissez un nouveau mot de passe sécurisé.</p>
        </div>
    """, unsafe_allow_html=True)

    new_password = st.text_input("🔒 Nouveau mot de passe", type="password", key="new_password")
    confirm_password = st.text_input("🔒 Confirmez le mot de passe", type="password", key="confirm_new_password")

    st.info("ℹ️ Le mot de passe doit contenir :\n- Au moins 5 caractères\n- Une majuscule\n- Une minuscule\n- Un chiffre\n- Un caractère spécial (!@#$%^&*?)")

    if st.button("✅ Réinitialiser le mot de passe", use_container_width=True):
        if not new_password or not confirm_password:
            st.error("❌ Veuillez remplir tous les champs")
        elif new_password != confirm_password:
            st.error("❌ Les mots de passe ne correspondent pas")
        else:
            success, message = auth_manager.reset_password_with_token(token, new_password)
            if success:
                st.success(message)
                st.success("✅ Vous pouvez maintenant vous connecter avec votre nouveau mot de passe")
                import time
                time.sleep(2)
                if go_to:
                    go_to("auth")
            else:
                st.error(message)

    footer()