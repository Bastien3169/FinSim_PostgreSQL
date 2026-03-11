import streamlit as st
from src.api_client.api_client import *
from src.components.components_views import *


def confidentialite_page(go_to):
    # ================= CSS + Variables =================
    load_css()

    # =============== Titre de la page ================
    display_page_title("Politique de Confidentialité")
    
    # =============== Texte spécifique ================
    PRIVACY_POLICY_FR = """
    Cette politique de confidentialité s'applique à l'application FinSim (ci-après « Application ») créée par Bastien Maurieres (ci-après « Fournisseur de service ») en tant que service gratuit. Cette application est fournie "EN L'ÉTAT".

    **Collecte et Utilisation des Informations**

    L'Application collecte des informations lors de votre utilisation. Ces informations peuvent inclure :

    * L'adresse IP de votre appareil
    * Les pages de l'Application que vous consultez, la date et l'heure de votre visite, le temps passé sur ces pages
    * Le temps total passé sur l'Application
    * Le système d'exploitation de votre appareil

    L'Application ne collecte pas d'informations précises sur la localisation de votre appareil.  
    L'Application n'utilise pas de technologies d'intelligence artificielle (IA) pour traiter vos données ou fournir des fonctionnalités.

    Le Fournisseur de service peut utiliser les informations fournies pour vous contacter occasionnellement afin de vous transmettre des informations importantes, des notifications légales ou des promotions.

    Pour une meilleure expérience, le Fournisseur de service peut nécessiter certaines informations personnelles identifiables, notamment : email, nom d'utilisateur, mot de passe haché (hashed_password), user_id, session_id. Ces informations seront conservées et utilisées conformément à cette politique de confidentialité.

    **Accès par des Tiers**

    Seules des données agrégées et anonymisées peuvent être transmises à des services externes afin d'améliorer l'Application. Le Fournisseur de service peut divulguer des informations dans les cas suivants :

    * Si la loi l'exige (assignation, procédure légale, etc.) ;
    * Pour protéger ses droits, votre sécurité ou celle d’autrui, ou pour enquêter sur une fraude ;
    * À ses prestataires de confiance qui travaillent pour lui, sans usage indépendant des informations.

    **Droits d'Option / Désinscription**

    Vous pouvez arrêter toute collecte d’informations en désinstallant l’Application.

    **Conservation des Données**

    Les données fournies par l’utilisateur sont conservées tant que vous utilisez l’Application et pour une durée raisonnable après. Pour demander la suppression de vos données, contactez : jolie.mountain@gmail.com.

    **Protection des Enfants**

    Le Fournisseur de service ne collecte pas sciemment d’informations personnelles d’enfants de moins de 13 ans. Les parents et tuteurs doivent surveiller l’utilisation de l’Internet par leurs enfants et leur expliquer de ne jamais fournir d’informations personnelles sans autorisation.

    **Sécurité**

    Le Fournisseur de service met en place des mesures physiques, électroniques et procédurales pour protéger vos informations.

    **Modifications**

    Cette politique peut être mise à jour à tout moment. L'utilisation continue de l'Application vaut acceptation des changements.

    Date d'entrée en vigueur : 11 mars 2026

    **Consentement**

    En utilisant l’Application, vous consentez au traitement de vos informations tel que décrit dans cette politique de confidentialité.

    **Contact**

    Pour toute question concernant la confidentialité, contactez le Fournisseur de service : jolie.mountain@gmail.com

    * * *

    Cette page de politique de confidentialité a été générée par [App Privacy Policy Generator](https://app-privacy-policy-generator.nisrulz.com/)
    """

    st.markdown(PRIVACY_POLICY_FR, unsafe_allow_html=True)



    # =============== Bouton retour accueil ================
    bout_accueil(back_callback=go_to)

    
    # =============== Footer ================
    footer()