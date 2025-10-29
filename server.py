import os
import socket
import datetime
import threading

HOST = "localhost"
PORT = 8025
DOSSIER_RACINE = "boite_mail"

##fonction permettant de gere un client 
def gerer_client(connexion, adresse):
    print("Connecte par", adresse)
    connexion.send(b"220 Service pret\r\n")

    emetteur = None
    destinataire = None
    dossier_emetteur = None

    while True:
        donnees = connexion.recv(1024)
        if not donnees:
            print("Client deconnecte...")
            break

        ligne = donnees.decode("utf-8").strip()

        if ligne.upper().startswith("MAIL FROM:"):
            print("Commande MAIL FROM recue")
            emetteur = ligne[10:].strip()
            dossier_emetteur = os.path.join(DOSSIER_RACINE, emetteur.replace("<", "").replace(">", ""))
            os.makedirs(dossier_emetteur, exist_ok=True)
            connexion.send(b"250 OK\r\n")

        elif ligne.upper().startswith("RCPT TO:"):
            print("Commande RCPT TO recue")
            destinataire = ligne[8:].strip()
            connexion.send(b"250 OK\r\n")

        elif ligne.upper() == "DATA":
            print("Commande DATA recue")
            connexion.send(b"354 Commencez a saisir le message, terminez par une ligne avec un point seul\r\n")
            messages = []
            client_fichier = connexion.makefile("r")
            for ligne_msg in client_fichier:
                ligne_msg = ligne_msg.strip()
                if ligne_msg == ".":
                    break
                messages.append(ligne_msg)

            contenu_message = "\n".join(messages)
            date_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nom_fichier = f"email_a_{destinataire.replace('<','').replace('>','')}_{date_str}.txt"
            chemin = os.path.join(dossier_emetteur, nom_fichier)
            with open(chemin, "w", encoding="utf-8") as f:
                f.write(f"From: {emetteur}\nTo: {destinataire}\n\n{contenu_message}")
            print(f"Message enregistré -> {chemin}")
            connexion.send(b"250 OK: Message enregistre")

        elif ligne.upper() == "QUIT":
            connexion.send(b"221 Fermeture de la connexion")
            break

        elif ligne.upper() == "HELLO":
            connexion.send(b"250 Hello , la connexion est maintenue")

        else:
            connexion.send(b"500 Commande inconnue\r\n")

    connexion.close()
    print(f"Connexion fermée pour {adresse}")


if __name__ == "__main__":
    os.makedirs(DOSSIER_RACINE, exist_ok=True)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ecoute:
        ecoute.bind((HOST, PORT))
        ecoute.listen()
        print(f"Serveur ecoute sur {HOST}:{PORT}")
        #permet de cree un thread par client 
        while True:
            connexion, adresse = ecoute.accept()
            thread_client = threading.Thread(target=gerer_client, args=(connexion, adresse))
            thread_client.daemon = True
            thread_client.start()
