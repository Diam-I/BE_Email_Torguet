import json
import os

USER_FILE = "users.json"


### charger les donnees utilisateur depuis le fichier JSON ###
def charger_donnees():
    if not os.path.exists(USER_FILE):
        return {"users": []}
    with open(USER_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


### sauvegarder les donnees utilisateur dans le fichier JSON ###
def sauvegarder_donnees(json_data):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)
