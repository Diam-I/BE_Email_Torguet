import hashlib
import users
import sys

def hash_mot_de_passe(mot_de_passe):
    return hashlib.md5(mot_de_passe.encode()).hexdigest()

def afficher_bienvenue():
    largeur = 50
    print("\n" + "╔" + "═"*(largeur-2) + "╗")
    print("║" + "BIENVENU SUR VOTRE SERVICE MAIL".center(largeur-2) + "║")
    print("╚" + "═"*(largeur-2) + "╝")

def authentification():
    """Fonctionnalite permettant a un utilisateur de s'authentifier aupres du serveur Smtp"""
    tentatives = 0
    while tentatives < 3:
        print(f"\n--- Connexion ---".center(30))
        mail = input("Mail : ").strip()
        mot_de_passe = input("Mot de passe : ").strip()
        json_data = users.charger_donnees() 
        if mail in json_data:
            if json_data[mail]["password_hash"] == hash_mot_de_passe(mot_de_passe):
                print(f"\n==> Authentification réussie !! ")
                return mail
            else:
                print(" Mot de passe incorrect.")
        else:
            print(" Utilisateur inconnu.")
        tentatives += 1
    print("\n==> 3 échecs consécutifs. Retour au menu principal.")
    return None

def inscription():
    print("\n" + "--- INSCRIPTION ---".center(30))
    mail = input("Renseigner votre mail : ").strip()
    mot_de_passe = input("Renseigner un mot de passe : ").strip()
    
    json_data = users.charger_donnees()
    
    if mail in json_data:
        print("\n==> Cet utilisateur existe déjà.")
        return None
    password_hash = hash_mot_de_passe(mot_de_passe)
    json_data[mail] = {"password_hash": password_hash}
    users.sauvegarder_donnees(json_data)
    print(f"\n==> Inscription réussie !!")
    return mail

def main():
    afficher_bienvenue()
    while True:
        print(" 1. Se Connecter")
        print(" 2. S'inscrire")
        print(" 3. Quitter l'application")
        
        choix = input("\nVotre choix : ").strip()
        
        if choix == "1":
            mail_utilisateur = authentification()
            if mail_utilisateur:
                return mail_utilisateur
        elif choix == "2":
            mail_utilisateur = inscription()
            if mail_utilisateur:
                return mail_utilisateur
        elif choix == "3":
            print("Fermeture du service !")
            sys.exit(0)
        else:
            print(" Choix invalide. Veuillez choisir 1, 2 ou 3.")