import os
import socket
import datetime
import threading

HOST = "localhost"
PORT_SMTP = 25  # Port SMTP #
DOSSIER_RACINE = "boite_mail"


### fonction permettant de gerer un client  ###
def gerer_client(connexion, adresse):
    print("Connecte par", adresse)
    connexion.send(b"220 Service pret\r\n")

    emetteur = None
    destinataire = None
    dossier_emetteur = None
    ehlo_recu = False

    while True:
        donnees = connexion.recv(1024)
        ## si le client deconnecte ##
        if not donnees:
            print("Client deconnecte...")
            break

        ligne = donnees.decode("utf-8").strip()

        ## traitement des commandes ##
        if ligne.upper().startswith("MAIL FROM:"):
            # si une commande MAIL FROM est recue #
            print("Commande MAIL FROM recue")
            emetteur = ligne[10:].strip()
            dossier_emetteur = os.path.join(
                DOSSIER_RACINE, emetteur.replace("<", "").replace(">", "")
            )
            # creation du dossier de l'emetteur s'il n'existe pas #
            os.makedirs(dossier_emetteur, exist_ok=True)
            connexion.send(b"250 OK\r\n")

        elif ligne.upper().startswith("RCPT TO:"):
            # si une commande RCPT TO est recue #
            print("Commande RCPT TO recue")
            destinataire = ligne[8:].strip()
            # creation du dossier du destinataire s'il n'existe pas #
            dossier_recepteur = os.path.join(
                DOSSIER_RACINE, destinataire.replace("<", "").replace(">", "")
            )
            os.makedirs(dossier_recepteur, exist_ok=True)

            connexion.send(b"250 OK\r\n")

        elif ligne.upper() == "DATA":
            # si une commande DATA est recue #
            print("Commande DATA recue")
            connexion.send(
                b"354 Commencez a saisir le message, terminez par une ligne avec un point seul\r\n"
            )
            messages = []
            # lecture du message ligne par ligne #
            client_fichier = connexion.makefile("r")
            for ligne_msg in client_fichier:
                ligne_msg = ligne_msg.strip()
                if ligne_msg == ".":
                    break
                messages.append(ligne_msg)
            # sauvegarde du message dans les dossiers de l'emetteur et du destinataire #
            contenu_message = "\n".join(messages)

            date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nom_fichier_recu = (
                f"email_de_{emetteur.replace('<','').replace('>','')}_{date_str}.txt"
            )
            nom_fichier_envoye = (
                f"email_a_{destinataire.replace('<','').replace('>','')}_{date_str}.txt"
            )
            chemin_envoye = os.path.join(dossier_emetteur, nom_fichier_envoye)
            with open(chemin_envoye, "w", encoding="utf-8") as f:
                f.write(f"From: {emetteur}\nTo: {destinataire}\n\n{contenu_message}")
            chemin_recu = os.path.join(dossier_recepteur, nom_fichier_recu)
            with open(chemin_recu, "w", encoding="utf-8") as f:
                f.write(f"From: {emetteur}\nTo: {destinataire}\n\n{contenu_message}")
            connexion.send(b"250 Message bien recu\r\n")
        # si une commande QUIT est recue #
        elif ligne.upper() == "QUIT":
            connexion.send(b"221 Fermeture de la connexion")
            break
        # si une commande HELO est recue #
        elif ligne.upper().startswith("HELO"):
            print("Commande HELO recue.")
            if ehlo_recu:
                # si un EHLO a ete envoye avant #
                connexion.send(b"250 OK\r\n")
                # reset du flag #
                ehlo_recu = False
            else:
                # sinon repondre normalement #
                connexion.send(b"250 OK\r\n")
        # si une commande EHLO est recue #
        elif ligne.upper().startswith("EHLO"):
            print("Commande EHLO recue.")
            ehlo_recu = True
            connexion.send(b"502 commande not implemented\r\n")
        # sinon commande inconnue #
        else:
            connexion.send(b"500 Commande inconnue\r\n")

    connexion.close()
    print(f"Connexion fermée pour {adresse}")


### fonction principale du serveur ###
if __name__ == "__main__":
    ## creation du dossier racine des boites mail s'il n'existe pas ##
    os.makedirs(DOSSIER_RACINE, exist_ok=True)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ecoute:
        ecoute.bind((HOST, PORT_SMTP))
        ecoute.listen()
        print(f"Serveur ecoute sur {HOST}:{PORT_SMTP}")
        # permet de cree un thread par client #
        while True:
            connexion, adresse = ecoute.accept()
            thread_client = threading.Thread(
                target=gerer_client, args=(connexion, adresse)
            )
            thread_client.daemon = True
            thread_client.start()
