import hashlib
import users


def hash_mot_de_passe(mot_de_passe):
    return hashlib.md5(mot_de_passe.encode()).hexdigest()


def authentification():

    while True:
        print("Authentification de l'utilisateur :")
        print("Veuillez entrer votre mail :")
        mail = input()
        print("Veuillez entrer votre mot de passe :")
        mot_de_passe = input()
        json_data = users.charger_donnees()

        if mail in json_data:
            if json_data[mail]["password_hash"] == hash_mot_de_passe(mot_de_passe):
                print(f"Authentification réussie pour : {mail}")
                return mail
            else:
                print("Mot de passe incorrect. Réessayez.\n")
        else:
            print("Utilisateur inconnu. Réessayez.\n")


def inscription():
    print("Inscription d'un nouvel utilisateur :")
    print("Veuillez entrer votre mail :")
    mail = input()
    print("Veuillez entrer votre mot de passe :")
    mot_de_passe = input()
    json_data = users.charger_donnees()

    if mail in json_data:
        print("Cet utilisateur existe déjà.")
        return None

    password_hash = hash_mot_de_passe(mot_de_passe)
    json_data[mail] = {"password_hash": password_hash, "inbox": f"boite_mail/{mail}"}
    users.sauvegarder_donnees(json_data)
    print(f"Inscription réussie pour : {mail}")
    return mail


def main():
    choix = input("Voulez-vous vous authentifier (1) ou vous inscrire (2) ? ")
    if choix == "1":
        mail_utilisateur = authentification()
    elif choix == "2":
        mail_utilisateur = inscription()
    else:
        print("Choix invalide.")
