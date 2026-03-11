Ouvrir le terminal et naviguer jusqu’au dossier du projet (par exemple en tapant cd chemin/vers/le/dossier ou en glissant-déposant le dossier dans le terminal pour remplir automatiquement le chemin).

_________________________________________________________________________________________

EN local: 
---------------------------------
Pour macOS/Linux : source venv/bin/activate pour le dossier back et front (ou uvicorn main:api --reload --port 8000)
se mettre dans le dossier "back" et faire :  uvicorn api:app --reload --port 8000
se mettre dans le dossier "front" et faire : streamlit run app.py
_________________________________________________________________________________________


Installer les dépendances :
---------------------------------
python -m pip install -r requirements.txt
!!! sur certaines installations macOS/Linux, il peut être nécessaire de remplacer "python" par "python3" !!!
_________________________________________________________________________________________

