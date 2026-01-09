import json
import os

USER_FILE = "users.json"

def charger_donnees():
    """Fonction permettant de charger la base de donnée des utilisateur du serveur, dans notre cas joue le role de base centrale"""
    if not os.path.exists(USER_FILE):
        return {}  
    try:
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return {}

def sauvegarder_donnees(json_data):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)