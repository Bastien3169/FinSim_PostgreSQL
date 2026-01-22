Ouvrir le terminal et naviguer jusqu’au dossier du projet (par exemple en tapant cd chemin/vers/le/dossier ou en glissant-déposant le dossier dans le terminal pour remplir automatiquement le chemin).

_________________________________________________________________________________________

Créer un environnement virtuel : 
---------------------------------
python -m venv venv
!!! sur certaines installations macOS/Linux, il peut être nécessaire de remplacer "python" par "python3" !!!
_________________________________________________________________________________________


Activer l'environnement virtuel :
---------------------------------
Pour macOS/Linux : source venv/bin/activate
Pour Windows : venv\Scripts\activate
_________________________________________________________________________________________


Installer les dépendances :
---------------------------------
python -m pip install -r requirements.txt
!!! sur certaines installations macOS/Linux, il peut être nécessaire de remplacer "python" par "python3" !!!
_________________________________________________________________________________________

Ensuite entrer :
---------------------------------
streamlit run app.py 

_________________________________________________________________________________________


Lien vers site via Render (Attention, render build le repo, ça peut prendre quelques minutes):
https://projectfinance.onrender.com/
