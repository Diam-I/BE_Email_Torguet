import os
import socket
import threading

HOST = "localhost"
PORT_POP3 = 110  # Port POP3 #
DOSSIER_RACINE = "boite_mail"


### fonction permettant de gerer un client  ###
def gerer_client(connexion, adresse):
    print("Connecte par", adresse)
    connexion.send(b"+OK POP3 server ready\r\n")

    utilisateur = None  # utilisateur POP3 (email)

    while True:
        donnees = connexion.recv(1024)
        ## si le client deconnecte ##
        if not donnees:
            print("Client deconnecte...")
            break

        ligne = donnees.decode("utf-8").strip()

        ## traitement des commandes ##
        if ligne.upper().startswith("QUIT"):
            # si une commande QUIT est recue #
            print("Commande QUIT recue")
            connexion.send(b"+OK Fermeture de la connexion\r\n")
            break

        elif ligne.upper().startswith("USER"):
            # si une commande USER est recue #
            utilisateur = ligne.split(" ", 1)[1]
            connexion.send(b"+OK Utilisateur reconnu\r\n")

        elif ligne.upper().startswith("STAT"):
            # si une commande STAT est recue #
            print("Commande STAT recue")

            if utilisateur is None:
                connexion.send(b"-ERR USER requis\r\n")
                continue

            dossier_utilisateur = os.path.join(DOSSIER_RACINE, utilisateur)
            os.makedirs(dossier_utilisateur, exist_ok=True)
            nb_emails = len(os.listdir(dossier_utilisateur))
            connexion.send(f"+OK {nb_emails} messages\r\n".encode("utf-8"))

        elif ligne.upper() == "LIST":
            # si une commande LIST est recue #
            print("Commande LIST recue")

            if utilisateur is None:
                connexion.send(b"-ERR USER requis\r\n")
                continue

            dossier_utilisateur = os.path.join(DOSSIER_RACINE, utilisateur)
            os.makedirs(dossier_utilisateur, exist_ok=True)
            emails = os.listdir(dossier_utilisateur)
            reponse = f"+OK {len(emails)} messages\r\n"
            for i, email in enumerate(emails, start=1):
                taille = os.path.getsize(os.path.join(dossier_utilisateur, email))
                reponse += f"{i} {taille}\r\n"
            reponse += ".\r\n"
            connexion.send(reponse.encode("utf-8"))

        elif ligne.upper().startswith("RETR"):
            # si une commande RETR est recue #
            print("Commande RETR recue")

            if utilisateur is None:
                connexion.send(b"-ERR USER requis\r\n")
                continue

            dossier_utilisateur = os.path.join(DOSSIER_RACINE, utilisateur)
            os.makedirs(dossier_utilisateur, exist_ok=True)
            try:
                numero_email = int(ligne.split()[1]) - 1
                emails = os.listdir(dossier_utilisateur)
                if 0 <= numero_email < len(emails):
                    with open(
                        os.path.join(dossier_utilisateur, emails[numero_email]),
                        "r",
                        encoding="utf-8",
                    ) as f:
                        contenu = f.read()
                    reponse = f"+OK {len(contenu)} octets\r\n{contenu}\r\n.\r\n"
                else:
                    reponse = "-ERR Numero de message invalide\r\n"
            except (IndexError, ValueError):
                reponse = "-ERR Commande RETR mal formée\r\n"

            connexion.send(reponse.encode("utf-8"))

        # sinon commande inconnue #
        else:
            connexion.send(b"-ERR Commande inconnue\r\n")

    connexion.close()
    print(f"Connexion fermée pour {adresse}")


### fonction principale du serveur ###
if __name__ == "__main__":
    ## creation du dossier racine des boites mail s'il n'existe pas ##
    os.makedirs(DOSSIER_RACINE, exist_ok=True)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ecoute:
        ecoute.bind((HOST, PORT_POP3))
        ecoute.listen()
        print(f"Serveur ecoute sur {HOST}:{PORT_POP3}")
        # permet de cree un thread par client #
        while True:
            connexion, adresse = ecoute.accept()
            thread_client = threading.Thread(
                target=gerer_client, args=(connexion, adresse)
            )
            thread_client.daemon = True
            thread_client.start()
