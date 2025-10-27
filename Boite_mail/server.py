import socket

### variables d'environnement ###
HOST = "localhost"
PORT = 8025

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ecoute:
        ### creation de la socket d'ecoute ###
        ecoute.bind((HOST, PORT))
        ecoute.listen()
        print(f"Serveur ecoute sur {HOST}:{PORT}")
        ## boucle pour les connexions entrantes ##
        while True:
            # nouvelle connexion #
            connexion, adresse = ecoute.accept()
            print("Connecte par", adresse)
            # envoie du message pour indiquer que le service est pret #
            connexion.send(b"220 Service pret\r\n")
            # tant que la connexion est active #
            while True:
                # donnees recues #
                donnees = connexion.recv(1024)
                # si le client a ferme la connexion #
                if not donnees:
                    print("Client deconnecte")  #####
                    break
                # stocker la ligne recue dans la variable ligne #
                ligne = donnees.decode("utf-8").strip()
                # si la ligne commence par MAIL FROM: #
                if ligne.upper().startswith("MAIL FROM:"):
                    print("Commande MAIL FROM recue")  #####
                    # stocker dans sender le texte apres MAIL FROM: et qui contient l'adresse de l'expediteur #
                    emetteur = ligne[10:].strip()
                    connexion.send(b"250 OK\r\n")
                # si la ligne commence par RCPT TO: #
                elif ligne.upper().startswith("RCPT TO:"):
                    print("Commande RCPT TO recue")  #####
                    # stocker dans destinataire le texte apres RCPT TO: et qui contient l'adresse du destinataire #
                    destinataire = ligne[8:].strip()
                    connexion.send(b"250 OK\r\n")
                # si la ligne est DATA #
                elif ligne.upper() == "DATA":
                    print("Commande DATA recue")  #####
                    connexion.send(
                        b"354 Commencez a saisir le message, terminez par une ligne avec un point seul\r\n"
                    )
                    messages = []
                    client_fichier = connexion.makefile("r")
                    for ligne in client_fichier:
                        ligne = ligne.strip()
                        if ligne == ".":
                            # si le client a ferme la connexion #
                            break
                        messages.append(ligne)
                    # stocker le message dans un fichier texte sous la forme de email_de_<emetteur>_a_<destinataire>.txt #
                    contenu_message = "\n".join(messages)
                    filename = f"email_de_{emetteur.replace('<','').replace('>','')}_a_{destinataire.replace('<','').replace('>','')}.txt"
                    with open(filename, "w") as f:
                        f.write(
                            f"From: {emetteur}\nTo: {destinataire}\n\n{contenu_message}"
                        )
                    connexion.send(b"250 OK: Message enregistre")
                # si la ligne est QUIT #
                elif ligne == "QUIT":
                    # envoyer le message de fermeture de connexion #
                    connexion.send(b"221 Fermeture de la connexion")
                    break
                else:
                    # pour toute autre commande envoyer le code d'erreur 500 #
                    connexion.send(b"500")
            # fermer la connexion #
            connexion.close()
