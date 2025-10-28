import socket

### variables d'environnement ###
HOST = "localhost"
PORT = 8025

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        ## creation de la socket cliente ##
        s.connect((HOST, PORT))

        # lecture du premier message du serveur #
        reponse = s.recv(1024)
        print("Serveur:", reponse.decode("utf-8").strip())

        while True:
            # lire une commande SMTP #
            message = input("Entrez une commande SMTP (ou QUIT pour quitter): ").strip()
            # si la commande est QUIT #
            if message.upper() == "QUIT":
                s.sendall(b"QUIT\r\n")
                reponse = s.recv(1024)
                print("Serveur:", reponse.decode("utf-8").strip())
                break
            # si la commande est DATA #
            elif message.upper() == "DATA":
                # envoie de la commande DATA #
                s.sendall(b"DATA\r\n")
                # reception de la réponse du serveur #
                reponse = s.recv(1024)
                print("Serveur:", reponse.decode("utf-8").strip())
                print("Saisissez le corps du message. Terminez par un point seul (.)")

                # envoie du message ligne par ligne #
                while True:
                    ligne = input()
                    s.sendall(ligne.encode("utf-8") + b"\r\n")
                    if ligne.strip() == ".":
                        break

                # reception de la réponse finale #
                reponse = s.recv(1024)
                print("Serveur:", reponse.decode("utf-8").strip())

            else:
                # autres commandes SMTP #
                s.sendall(message.encode("utf-8") + b"\r\n")
                reponse = s.recv(1024)
                print("Serveur:", reponse.decode("utf-8").strip())
