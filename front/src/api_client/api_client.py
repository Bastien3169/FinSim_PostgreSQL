import os
import requests
import pandas as pd
from streamlit_cookies_manager import EncryptedCookieManager 
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

def get_api_url():
    """Retourne l'URL de l'API (utilisée par les classes de données)"""
    return API_URL

# ============================================
#  AUTH MANAGER AVEC COOKIES (FRONTEND)
# ============================================
class AuthManager:
    """Gestion auth via API avec cookies Streamlit"""
    
    def __init__(self, cookie_name="session_id", cookie_secret="Toulouse31"):
        self.api_url = API_URL
        self.cookie_name = cookie_name
        self.cookies = EncryptedCookieManager(prefix="", password=cookie_secret)
        if not self.cookies.ready():
            st.stop()
    
    def login(self, email, password, stay_connected=False):
        try:
            response = requests.post(
                f"{self.api_url}/api/auth/login",
                json={"email": email, "password": password, "stay_connected": stay_connected},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "session_id" in data:
                    self.cookies[self.cookie_name] = data["session_id"]
                    self.cookies.save()
                return True, data["message"], data["role"]
            
            return False, response.json().get("detail", "Erreur"), None
        except Exception as e:
            return False, f"Erreur serveur: {str(e)}", None
    
    def register(self, username, email, password):
        try:
            response = requests.post(
                f"{self.api_url}/api/auth/register",
                json={"username": username, "email": email, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()["message"]
            
            return False, response.json().get("detail", "Erreur")
        except Exception as e:
            return False, f"Erreur serveur: {str(e)}"
    
    def get_current_user(self):
        session_id = self.cookies.get(self.cookie_name)
        if not session_id:
            return None
        
        try:
            response = requests.get(
                f"{self.api_url}/api/auth/me",
                cookies={self.cookie_name: session_id},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
    
    def logout(self):
        session_id = self.cookies.get(self.cookie_name)
        if session_id:
            try:
                requests.post(
                    f"{self.api_url}/api/auth/logout",
                    cookies={self.cookie_name: session_id},
                    timeout=10
                )
            except Exception:
                pass
        
        self.cookies[self.cookie_name] = ""
        self.cookies.save()
    
    def forgot_password(self, email):
        try:
            response = requests.post(
                f"{self.api_url}/api/auth/forgot-password",
                json={"email": email},
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()["message"]
            
            return False, response.json().get("detail", "Erreur")
        except Exception as e:
            return False, f"Erreur serveur: {str(e)}"
    
    def reset_password_with_token(self, token, new_password):
        try:
            response = requests.post(
                f"{self.api_url}/api/auth/reset-password",
                json={"token": token, "new_password": new_password},
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()["message"]
            
            return False, response.json().get("detail", "Erreur")
        except Exception as e:
            return False, f"Erreur serveur: {str(e)}"

# ============================================
# CLIENT ADMIN
# ============================================
class AdminManager:
    """Gestion admin via API"""
    
    def __init__(self):
        self.api_url = API_URL
    
    def get_all_users(self):
        response = requests.get(f"{self.api_url}/api/admin/users", timeout=30)
        response.raise_for_status()
        return response.json()["users"]
    
    def search_user(self, query):
        response = requests.get(f"{self.api_url}/api/admin/users/search", params={"query": query}, timeout=30)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    
    def update_user(self, email, username=None, password=None, role=None):
        payload = {"email": email, "username": username, "password": password, "role": role}
        response = requests.put(f"{self.api_url}/api/admin/users/update", json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def delete_user(self, email):
        response = requests.delete(f"{self.api_url}/api/admin/users/delete", params={"email": email}, timeout=30)
        response.raise_for_status()
        return response.json()

# ============================================
# CLASSES POUR LES DONNÉES FINANCIÈRES
# ============================================

################################## api_stocks ##################################
class FinanceDatabaseStocks:
    """Client API pour les stocks"""
    
    def __init__(self):
        self.api_url = get_api_url()
    
    def get_list_stocks(self):
        response = requests.get(f"{self.api_url}/api/stocks/list", timeout=30)
        response.raise_for_status()
        return response.json()["stocks"]
    
    def get_infos_stocks(self, short_name):
        if not short_name:
            return pd.DataFrame()
        response = requests.get(f"{self.api_url}/api/stocks/infos", params={"name": short_name}, timeout=30)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def get_prix_date(self, actif):
        response = requests.get(f"{self.api_url}/api/stocks/prix", params={"name": actif}, timeout=30)
        response.raise_for_status()
        df = pd.DataFrame(response.json())
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date").reset_index(drop=True)
        return df


################################## api_indices ##################################
class FinanceDatabaseIndice:
    """Client API pour les indices"""
    
    def __init__(self):
        self.api_url = get_api_url()
    
    def get_list_indices(self):
        response = requests.get(f"{self.api_url}/api/indices/list", timeout=30)
        response.raise_for_status()
        return response.json()["indices"]
    
    def get_infos_indices(self, selected_indice):
        response = requests.get(f"{self.api_url}/api/indices/infos", params={"name": selected_indice}, timeout=30)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def get_prix_date(self, selected_indice):
        #response = requests.get(f"{self.api_url}/api/indices/prix/{selected_indice}", timeout=30)
        response = requests.get(f"{self.api_url}/api/indices/prix",params={"name": selected_indice},timeout=30)
        response.raise_for_status()
        df = pd.DataFrame(response.json())
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date").reset_index(drop=True)
        return df
    
    def get_composition_indice(self, selected_indice):
        #response = requests.get(f"{self.api_url}/api/indices/composition/{selected_indice}", timeout=30)
        response = requests.get(f"{self.api_url}/api/indices/composition", params={"name": selected_indice}, timeout=30)
        response.raise_for_status()
        return pd.DataFrame(response.json())


################################## api_cryptos ##################################
class FinanceDatabaseCryptos:
    """Client API pour les cryptos"""
    
    def __init__(self):
        self.api_url = get_api_url()
    
    def get_list_cryptos(self):
        response = requests.get(f"{self.api_url}/api/cryptos/list", timeout=30)
        response.raise_for_status()
        return response.json()["cryptos"]
    
    def get_infos_cryptos(self, short_name):
        if not short_name:
            return pd.DataFrame()
        response = requests.get(f"{self.api_url}/api/cryptos/infos", params={"name": short_name}, timeout=30)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def get_prix_date(self, actif):
        response = requests.get(f"{self.api_url}/api/cryptos/prix", params={"name": actif}, timeout=30)
        response.raise_for_status()
        df = pd.DataFrame(response.json())
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date").reset_index(drop=True)
        return df

################################## api_etfs ##################################

class FinanceDatabaseEtfs:
    """Client API pour les ETFs"""
    
    def __init__(self):
        self.api_url = get_api_url()
    
    def get_list_etfs(self):
        response = requests.get(f"{self.api_url}/api/etfs/list", timeout=30)
        response.raise_for_status()
        return response.json()["etfs"]
    
    def get_infos_etfs(self, short_name=None):
        if not short_name:
            return pd.DataFrame()
        response = requests.get(f"{self.api_url}/api/etfs/infos", params={"name": short_name}, timeout=30)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    
    def get_prix_date(self, actif):
        response = requests.get(f"{self.api_url}/api/etfs/prix", params={"name": actif}, timeout=30)
        response.raise_for_status()
        df = pd.DataFrame(response.json())
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date").reset_index(drop=True)
        return df

# ============================================
# FONCTIONS UTILITAIRES
# ============================================
def calculate_rendement(df, periods):
    rendement = {}
    for period_months in periods:
        start_date = df["date"].max() - pd.DateOffset(months=period_months)
        df_period = df[df["date"] >= start_date]
        if len(df_period) > 1:
            start_close = df_period.iloc[0]["close"]
            end_close = df_period.iloc[-1]["close"]
            rendement[f"{period_months} mois"] = "{:.2f}".format((end_close - start_close) / start_close * 100)
        else:
            rendement[f"{period_months} mois"] = None
    return rendement

def style_rendement(df, periods):
    def color_rendement(val):
        color = 'green' if float(val) > 0 else ('red' if float(val) < 0 else 'black')
        return f'color: {color}'
    return df.style.map(color_rendement, subset=[f"{p} mois" for p in periods])