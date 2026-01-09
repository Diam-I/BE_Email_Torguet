import os
import socket
import datetime
import threading
import json
import users

### Variables d'environnement ###
HOST = "localhost"
PORT_SMTP = 3000
DOSSIER_RACINE = "boite_mail"


def chemin_utilisateur(type_mail, utilisateur):
    """Retourne le chemin vers le dossier 'reception' ou 'envoi' d'un utilisateur"""
    return os.path.join(DOSSIER_RACINE, type_mail, utilisateur)


def sauvegarder_message(utilisateur, type_mail, nom_fichier, contenu):
    """Enregistre un message dans le dossier correspondant (reception/envoi)"""
    path = chemin_utilisateur(type_mail, utilisateur)
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, nom_fichier), "w", encoding="utf-8") as f:
        f.write(contenu)


def gerer_client(connexion, adresse):
    """Fonction permettant de gerer une session client"""
    print("Connecte par", adresse)
    connexion.send(b"220 Service pret\r\n")
    emetteur = None
    destinataire = None
    destinataires_valides = []

    while True:
        donnees = connexion.recv(1024)
        if not donnees:
            print("Client deconnecte...")
            break
        ligne = donnees.decode("utf-8").strip()

        # Traitement des commandes SMTP #
        if ligne.upper().startswith("MAIL FROM:"):
            # reception de l'expéditeur #
            emetteur = ligne[10:].strip().replace("<", "").replace(">", "")
            connexion.send(b"250 OK\r\n")

        elif ligne.upper().startswith("RCPT TO:"):
            # reception d'un destinataire #
            dest = ligne[8:].strip().replace("<", "").replace(">", "")
            destinataire = dest
            if utilisateur_existe(dest):
                destinataires_valides.append(dest)
            connexion.send(b"250 OK \r\n")

        elif ligne.upper() == "DATA":
            # reception du message #
            print("Commande DATA recue")
            connexion.send(
                b"354 Commencez a saisir le message, terminez par une ligne avec un point seul\r\n"
            )
            sujet = "Sans sujet"
            messages = []

            # lecture du message ligne par ligne #
            client_fichier = connexion.makefile("r", encoding="utf-8")
            while True:
                ligne_msg = client_fichier.readline()
                if not ligne_msg:
                    break
                ligne_clean = ligne_msg.strip()
                # arrêter la saisie #
                if ligne_clean == ".":
                    break
                if ligne_clean.startswith("Subject:"):
                    sujet = ligne_clean.replace("Subject:", "").strip()
                else:
                    messages.append(ligne_clean)

            # Reconstruction du corps du message #
            contenu_message = "\n".join(messages)
            date_formatee = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            # Fonction utilitaire pour générer le contenu complet du message #
            def construire_message(emetteur, destinataire, sujet, contenu):
                # On utilise \r\n pour garantir la compatibilité universelle des sauts de ligne
                return f"From: {emetteur}\r\nTo: {destinataire}\r\nSubject: {sujet}\r\nDate: {date_formatee}\n\n{contenu}"

            # Vérification et sauvegarde pour tous les destinataires valides #
            if destinataires_valides:
                for d in destinataires_valides:
                    nom_fichier = f"mail_From_{emetteur}_{timestamp}.txt"
                    contenu_final = construire_message(
                        emetteur, d, sujet, contenu_message
                    )
                    sauvegarder_message(d, "reception", nom_fichier, contenu_final)
                destinataires_valides = []

            # Sauvegarde dans l'historique de l'expéditeur #
            if emetteur:
                nom_fichier = f"mail_To_{destinataire}_{timestamp}.txt"
                contenu_historique = construire_message(
                    emetteur, destinataire, sujet, contenu_message
                )
                sauvegarder_message(emetteur, "envoi", nom_fichier, contenu_historique)

            connexion.send(
                b"250 OK Message bien recu, et transmis au destinataire \r\n"
            )

        elif ligne.upper() == "QUIT":
            # fermeture de la connexion #
            connexion.send(b"221 Fermeture de la connexion")
            break

        elif ligne.upper().startswith("HELO"):
            # reception de la commande HELO #
            print("\n=> Commande HELO recue.")
            connexion.send(b"250 OK\r\n")

        elif ligne.upper().startswith("EHLO"):
            # reception de la commande EHLO #
            print("\n=> Commande EHLO recue.")
            connexion.send(b"502 commande not implemented\r\n")

        elif ligne.upper().startswith("RSET"):
            # reinitialisation de la session #
            print("\n=> Commande RSET recue.")
            emetteur = None
            destinataire = None
            destinataires_valides = []
            connexion.send(b"250 OK\r\n")

        elif ligne.upper().startswith("NOOP"):
            # commande NOOP #
            print("n=> Commande NOOP recue.")
            connexion.send(b"250 OK\r\n")

        else:
            # commande inconnue #
            connexion.send(b"500 Commande inconnue\r\n")

    connexion.close()
    print(f"Connexion fermée pour {adresse}")


def utilisateur_existe(email):
    """Vérifie si l'adresse mail est présente dans la base de données users.json"""
    try:
        data = users.charger_donnees()
        return email in data
    except Exception as e:
        print(f"Erreur lors de la lecture de la BD : {e}")
        return False


if __name__ == "__main__":
    """Fonction principale démarrant le serveur SMTP"""
    os.makedirs(DOSSIER_RACINE, exist_ok=True)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind((HOST, PORT_SMTP))
        server_socket.listen()
        print(f"\n=== Serveur SMTP démarré sur {HOST}:{PORT_SMTP} ===")
        print("\n=> Appuyez sur CTRL+C pour éteindre le serveur proprement.")
        while True:
            connexion, adresse = server_socket.accept()
            thread_client = threading.Thread(
                target=gerer_client, args=(connexion, adresse)
            )
            thread_client.daemon = True
            thread_client.start()
    except KeyboardInterrupt:
        print("\n==> Arrêt du serveur ...")
    except Exception as e:
        print(f"\n==> Une erreur est survenue : {e}")
    finally:
        server_socket.close()
        print(" Port libéré. Fermeture propre terminée.")
