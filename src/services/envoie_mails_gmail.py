import smtplib
from email.message import EmailMessage
import os

# Configuration SMTP
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "jolie.mountain@gmail.com")
SMTP_PASS = os.getenv("SMTP_PASS", "oxwp quqm exbt bgjx")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587  # ⭐ PORT 587 au lieu de 465

# URL dynamique selon l'environnement
BASE_URL = os.getenv("APP_URL", "http://localhost:8501")

def envoie_password_reset_email(to_email, token):
    print(f"🔄 [EMAIL] Tentative d'envoi à {to_email}")
    print(f"📧 [EMAIL] SMTP utilisé: {SMTP_EMAIL}")
    print(f"🌐 [EMAIL] URL de base: {BASE_URL}")
    print(f"🔑 [EMAIL] Token: {token[:10]}...")
    
    # Génération du lien
    reset_link = f"{BASE_URL}/?token={token}&page=reset_password"
    print(f"🔗 [EMAIL] Lien: {reset_link}")
    
    # Création du message
    msg = EmailMessage()
    msg['Subject'] = "Réinitialisation de votre mot de passe - FinSim"
    msg['From'] = SMTP_EMAIL
    msg['To'] = to_email
    
    msg.set_content(
        f"Bonjour,\n\n"
        f"Vous avez demandé à réinitialiser votre mot de passe pour FinSim.\n\n"
        f"Cliquez sur ce lien pour réinitialiser votre mot de passe :\n"
        f"{reset_link}\n\n"
        f"⚠️ Ce lien expire dans 1 heure.\n\n"
        f"Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.\n\n"
        f"Cordialement,\nL'équipe FinSim"
    )

    try:
        print("🔌 [EMAIL] Connexion au serveur SMTP (port 587)...")
        # ⭐ SMTP (pas SMTP_SSL) avec port 587
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as smtp:
            print("🔐 [EMAIL] Activation STARTTLS...")
            smtp.starttls()  # Active le chiffrement
            
            print("🔑 [EMAIL] Authentification...")
            smtp.login(SMTP_EMAIL, SMTP_PASS)
            
            print("📤 [EMAIL] Envoi du message...")
            smtp.send_message(msg)
            
            print(f"✅ [EMAIL] Email envoyé avec succès à {to_email}")
            
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ [EMAIL] Erreur d'authentification: {e}")
        raise Exception(f"Authentification Gmail échouée. Vérifiez vos identifiants.")
    
    except smtplib.SMTPException as e:
        print(f"❌ [EMAIL] Erreur SMTP: {e}")
        raise Exception(f"Erreur d'envoi SMTP: {str(e)}")
    
    except Exception as e:
        print(f"❌ [EMAIL] Erreur inattendue: {e}")
        raise Exception(f"Erreur lors de l'envoi: {str(e)}")