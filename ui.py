## Ce fichier gère l'authentification et l'inscription des utilisateurs en leur
#  proposant un menu pour se connecter ou créer un nouveau compte.

## Il assure la sécurité des mots de passe en les chiffrant (hachage MD5)
# avant de vérifier leur validité ou de les enregistrer dans le fichier users.json via le module users.

# Il permet au programme client (client.py) de récupérer l'adresse e-mail de l'utilisateur
# connecté afin de l'utiliser comme expéditeur lors de l'envoi de messages.

import hashlib
import users


### hacher le mot de passe avec MD5 ###
def hash_mot_de_passe(mot_de_passe):
    return hashlib.md5(mot_de_passe.encode()).hexdigest()


### authentifier un utilisateur existant ###
def authentification():
    while True:
        print("Authentification de l'utilisateur :")
        print("Veuillez entrer votre mail :")
        mail = input()
        print("Veuillez entrer votre mot de passe :")
        mot_de_passe = input()
        ## charger les donnees utilisateur ##
        json_data = users.charger_donnees()
        ## verifier si l'utilisateur existe et si le mot de passe est correct ##
        if mail in json_data:
            if json_data[mail]["password_hash"] == hash_mot_de_passe(mot_de_passe):
                print(f"Authentification réussie pour : {mail}")
                return mail
            else:
                print("Mot de passe incorrect. Réessayez.\n")
        else:
            print("Utilisateur inconnu. Réessayez.\n")


### inscrire un nouvel utilisateur ###
def inscription():
    print("Inscription d'un nouvel utilisateur :")
    print("Veuillez entrer votre mail :")
    ## saisie du mail et mot de passe ##
    mail = input()
    print("Veuillez entrer votre mot de passe :")
    mot_de_passe = input()
    json_data = users.charger_donnees()
    ## verifier si l'utilisateur existe deja ##
    if mail in json_data:
        print("Cet utilisateur existe déjà.")
        return None
    ## ajouter le nouvel utilisateur ##
    password_hash = hash_mot_de_passe(mot_de_passe)
    json_data[mail] = {"password_hash": password_hash, "inbox": f"boite_mail/{mail}"}
    # sauvegarder les donnees utilisateur #
    users.sauvegarder_donnees(json_data)
    print(f"Inscription réussie pour : {mail}")
    return mail


### fonction principale ###
def main():
    choix = input("Voulez-vous vous authentifier (1) ou vous inscrire (2) ? ")
    while choix not in ["1", "2"]:
        print("Choix invalide. Veuillez entrer 1 ou 2.")
        choix = input("Voulez-vous vous authentifier (1) ou vous inscrire (2) ? ")
    if choix == "1":
        mail_utilisateur = authentification()
    else:
        mail_utilisateur = inscription()
    return mail_utilisateur
