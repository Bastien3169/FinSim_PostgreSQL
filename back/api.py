"""
API FastAPI pour FinSim avec PostgreSQL
Version corrigée : Pydantic + HTTPException + noms unifiés
"""
import sys
import os
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Cookie, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from fastapi.responses import HTMLResponse
from pathlib import Path

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# ============================================
# IMPORTS DES MANAGERS
# ============================================
from src.models.users_db.users_queries import AuthManager, AdminManager
from src.models.datas_db.datas_queries import (
    FinanceDatabaseCryptos,
    FinanceDatabaseIndice,
    FinanceDatabaseStocks,
    FinanceDatabaseEtfs
)
from src.models.construction_datas_db.sql_datas import main_creation_db

# ============================================
# CONFIGURATION FASTAPI
# ============================================
app = FastAPI(title="FinSim API", version="1.0.0")

# CORS pour Streamlit et Flet
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation des managers
auth = AuthManager()
admin = AdminManager()
cryptos = FinanceDatabaseCryptos()
indices = FinanceDatabaseIndice()
stocks = FinanceDatabaseStocks()
etfs = FinanceDatabaseEtfs()

# ============================================
# NETTOYAGE AU DÉMARRAGE
# ============================================
@app.on_event("startup")
def startup():
    auth.clean_expired_sessions()
    print("✅ Sessions expirées nettoyées au démarrage")

    # ⚠️ Le chargement des CSV n'est PLUS fait automatiquement au démarrage.
    #
    # main_creation_db() enchaîne 10 DROP TABLE puis réimporte ~91 Mo de CSV
    # (plus de 2 millions de lignes). Joué à chaque redémarrage Railway — donc
    # à chaque déploiement, chaque redémarrage de conteneur, chaque reprise
    # après veille — cela rendait l'API indisponible le temps de l'import, et
    # si le conteneur était tué en cours de route (health check dépassé) on
    # repartait sur des tables de données à moitié vides.
    #
    # Pour (re)charger les données, deux options :
    #   - lancer `python init_db.py` à la main ;
    #   - ou définir RELOAD_CSV_ON_STARTUP=true sur Railway le temps d'un
    #     démarrage, puis retirer la variable.
    if os.getenv("RELOAD_CSV_ON_STARTUP", "").strip().lower() in ("1", "true", "yes", "oui"):
        print("🔄 RELOAD_CSV_ON_STARTUP actif : rechargement des CSV...")
        csv_path = Path(__file__).parent / "csv" / "csv_bdd"
        main_creation_db(str(csv_path))
        print("✅ Données CSV chargées avec succès.")
    else:
        print("⏭️  Chargement des CSV ignoré "
              "(RELOAD_CSV_ON_STARTUP non défini) — démarrage immédiat.")

# ============================================
# MODELS PYDANTIC
# ============================================
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    stay_connected: bool = False

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class UserUpdate(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None

# ============================================
# ROUTES AUTH
# ============================================
@app.post("/api/auth/login")
def login(data: UserLogin):
    # AuthManager.login() renvoie desormais TOUJOURS 4 valeurs :
    #   (success, message, role, session_id)
    # Avant le correctif il n'en renvoyait que 3 en cas d'echec : le
    # depaquetage ci-dessous levait un ValueError et l'API repondait
    # HTTP 500 au lieu de HTTP 401 sur un mauvais mot de passe.
    success, message, role, session_id = auth.login(
        data.email, data.password, data.stay_connected
    )
    if not success:
        raise HTTPException(status_code=401, detail=message)
    return {"success": True, "message": message, "session_id": session_id, "role": role}

@app.post("/api/auth/register")
def register(data: UserRegister):
    success, message = auth.register(data.username, data.email, data.password)
    if success:
        return {"success": True, "message": message}
    raise HTTPException(status_code=400, detail=message)

@app.post("/api/auth/logout")
def logout(session_id: Optional[str] = Cookie(None)):
    auth.logout(session_id)
    return {"success": True, "message": "Déconnexion réussie"}

@app.get("/api/auth/me")
def get_current_user(session_id: Optional[str] = Cookie(None)):
    user = auth.get_current_user(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="Non authentifié")
    return user

@app.post("/api/auth/forgot-password")
def forgot_password(data: PasswordReset):
    success, message = auth.forgot_password(data.email)
    if success:
        return {"success": True, "message": message}
    raise HTTPException(status_code=400, detail=message)

@app.post("/api/auth/reset-password")
def reset_password(data: PasswordResetConfirm):
    success, message = auth.reset_password_with_token(data.token, data.new_password)
    if success:
        return {"success": True, "message": message}
    raise HTTPException(status_code=400, detail=message)

# ============================================
# SECURITE DES ROUTES ADMIN
# ============================================
def require_admin(session_id: Optional[str] = Cookie(None)):
    """Dependance FastAPI : n'autorise que les administrateurs connectes.

    Avant ce correctif les trois routes /api/admin/* etaient publiques :
    n'importe qui connaissant l'URL pouvait lister tous les utilisateurs,
    changer un mot de passe, se donner le role admin ou vider la table.
    """
    user = auth.get_current_user(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="Non authentifie")
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acces reserve aux administrateurs")
    return user

# ============================================
# ROUTES ADMIN
# ============================================
@app.get("/api/admin/users")
def get_all_users(_admin: dict = Depends(require_admin)):
    users = admin.get_all_users()
    return {
        "users": [
            {"id": u[0], "username": u[1], "email": u[2], "role": u[3], "registration_date": u[4]}
            for u in users]}

@app.get("/api/admin/users/search")
def search_user(query: str, _admin: dict = Depends(require_admin)):
    user = admin.get_user_by_email_username(query)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return {"id": user[0], "username": user[1], "email": user[2], "role": user[3], "registration_date": user[4]}

@app.put("/api/admin/users/update")
def update_user(data: UserUpdate, _admin: dict = Depends(require_admin)):
    message = admin.update_user(email=data.email, username=data.username, password=data.password, role=data.role)
    return {"success": True, "message": message}

@app.delete("/api/admin/users/delete")
def delete_user(email: str, _admin: dict = Depends(require_admin)):
    message = admin.delete_user(email)
    return {"success": True, "message": message}

# ============================================
# ROUTES DATA - STOCKS (NOMS UNIFIÉS SUR ticker)
# ============================================
@app.get("/api/stocks/list")
def get_stocks_list():
    return {"stocks": stocks.get_list_stocks()}

@app.get("/api/stocks/infos")
def get_stocks_infos(name: str):
    df = stocks.get_infos_stocks(name)
    if df.empty:
        raise HTTPException(status_code=404, detail="Stock non trouvé")
    return df.to_dict(orient="records")

@app.get("/api/stocks/prix")
def get_stocks_prix(name: str):
    df = stocks.get_prix_date(name)
    if df.empty:
        raise HTTPException(status_code=404, detail="Données de prix non trouvées")
    df["date"] = df["date"].astype(str)
    return df.to_dict(orient="records")

# ============================================
# ROUTES DATA - INDICES (NOMS UNIFIÉS SUR ticker)
# ============================================
@app.get("/api/indices/list")
def get_indices_list():
    return {"indices": indices.get_list_indices()}

@app.get("/api/indices/infos")
def get_indices_infos(name: str):
    df = indices.get_infos_indices(name)
    if df.empty:
        raise HTTPException(status_code=404, detail="Indice non trouvé")
    return df.to_dict(orient="records")

@app.get("/api/indices/prix")
# J'ai enelevé le /{ticker} pour correspondre au front
def get_indices_prix(name: str):
    df = indices.get_prix_date(name)
    if df.empty:
        raise HTTPException(status_code=404, detail="Données de prix non trouvées")
    return df.to_dict(orient="records")

@app.get("/api/indices/composition")
def get_indices_composition(name: str):
    df = indices.get_composition_indice(name)
    if df.empty:
        raise HTTPException(status_code=404, detail="Composition non trouvée")
    return df.to_dict(orient="records")

# ============================================
# ROUTES DATA - CRYPTOS (NOMS UNIFIÉS SUR ticker)
# ============================================
@app.get("/api/cryptos/list")
def get_cryptos_list():
    return {"cryptos": cryptos.get_list_cryptos()}

@app.get("/api/cryptos/infos")
def get_cryptos_infos(name: str):
    df = cryptos.get_infos_cryptos(name)
    if df.empty:
        raise HTTPException(status_code=404, detail="Crypto non trouvée")
    return df.to_dict(orient="records")

@app.get("/api/cryptos/prix")
def get_cryptos_prix(name: str):
    df = cryptos.get_prix_date(name)
    if df.empty:
        raise HTTPException(status_code=404, detail="Données de prix non trouvées")
    return df.to_dict(orient="records")

# ============================================
# ROUTES DATA - ETFS (NOMS UNIFIÉS SUR ticker)
# ============================================
@app.get("/api/etfs/list")
def get_etfs_list():
    return {"etfs": etfs.get_list_etfs()}

@app.get("/api/etfs/infos")
def get_etfs_infos(name: str):
    df = etfs.get_infos_etfs(name)
    if df.empty:
        raise HTTPException(status_code=404, detail="ETF non trouvé")
    return df.to_dict(orient="records")

@app.get("/api/etfs/prix")
def get_etfs_prix(name: str):
    df = etfs.get_prix_date(name)
    if df.empty:
        raise HTTPException(status_code=404, detail="Données de prix non trouvées")
    return df.to_dict(orient="records")


# ============================================
# POLITIQUE DE CONFIDENTIALITÉ
# ============================================
@app.get("/privacy", response_class=HTMLResponse)
def privacy_policy():
    html_content = Path("politique_confidentialite.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html_content)

# ============================================
# SUPPRESSION DE COMPTE
# ============================================
@app.get("/delete-account", response_class=HTMLResponse)
def delete_account():
    html_content = Path("suppression_compte.html").read_text(encoding="utf-8") 
    return HTMLResponse(content=html_content)


# ============================================
# HEALTH CHECK
# ============================================
@app.get("/")
def root():
    return {"status": "FinSim API v1.0 - Corrigée", "message": "OK", "database": "PostgreSQL"}

@app.get("/health")
def health():
    return {"status": "healthy", "database": "PostgreSQL"}