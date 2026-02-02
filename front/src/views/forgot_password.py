import streamlit as st
from src.components.components_views import *
from src.api_client.api_client import *

def forgot_password_page(auth_manager, go_to=None):

    load_css()
    
    display_page_title("🔑 MOT DE PASSE OUBLIÉ")

    st.markdown("""<div class="main-container"><p>Entrez votre adresse email et nous vous enverrons un lien pour réinitialiser votre mot de passe.</p></div>""", unsafe_allow_html=True)

    email = st.text_input("📧 Votre email", key="forgot_email")

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📨 Envoyer le lien", use_container_width=True):
            if not email:
                st.error("❌ Veuillez entrer votre email")
            else:
                # ✅ AJOUT : Spinner pour montrer que ça travaille
                with st.spinner("📤 Envoi en cours..."):
                    try:
                        success, message = auth_manager.forgot_password(email)
                        if success:
                            st.success(message)
                            st.info("📧 Vérifiez votre boîte mail (pensez aux spams)")
                        else:
                            st.error(message)
                    except Exception as e:
                        # ✅ AJOUT : Capture les erreurs inattendues
                        st.error(f"❌ Erreur inattendue : {str(e)}")
                        # 🔍 Pour le débogage (à retirer en production)
                        st.exception(e)
    
    with col2:
        if st.button("⬅️ Retour à la connexion", use_container_width=True):
            if go_to:
                go_to("auth")

    footer()