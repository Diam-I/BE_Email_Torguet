import socket
import sys

import ui

### variables d'environnement ###
HOST = "localhost"
PORT_SMTP = 25  # Port SMTP #
PORT_POP3 = 110  # Port POP3 #


### lire une reponse du serveur ###
def recv_rep(sock: socket.socket) -> str:
    try:
        data = sock.recv(4096)
        if not data:
            return ""
        return data.decode("utf-8", errors="replace")
    except Exception as e:
        return f"(erreur lecture socket: {e})"


### envoyer un message au serveur ###
def env_msg(sock: socket.socket, text: str):
    if not text.endswith("\r\n"):
        text = text + "\r\n"
    sock.sendall(text.encode("utf-8"))


### fonction principale ###
def main():

    ## authentification / Inscription ##
    mail_utilisateur = ui.main()
    print(f"Connecté en tant que {mail_utilisateur}\n")
    ## interaction avec le serveur ##
    while True:
        try:
            choix = input(
                "Voulez-vous : \n1- Envoyer un email\n2- Lire les emails\n3- Quitter\n"
            ).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nInterruption locale.")
            break

        if not choix:
            continue
        ## envoi d'un email ##
        if choix == "1":
            ## connexion au serveur SMTP ##
            try:
                smtp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                smtp_socket.connect((HOST, PORT_SMTP))
            except Exception as e:
                print(f"Impossible de se connecter à {HOST}:{PORT_SMTP} -> {e}")
                sys.exit(1)
            # lire le message d'accueil #
            welcome = recv_rep(smtp_socket)
            if welcome:
                print("Serveur:", welcome.strip())
            else:
                print("Aucune réponse du serveur. Fermeture.")
                smtp_socket.close()
                return

            # Tenter EHLO #
            env_msg(smtp_socket, "EHLO localhost")
            resp = recv_rep(smtp_socket)

            if resp.startswith("502"):
                env_msg(smtp_socket, "HELO localhost")
                resp = recv_rep(smtp_socket)

            if not resp.startswith("250"):
                print("Erreur identification SMTP.")
                smtp_socket.close()
                continue

            print(f"Connecté au serveur SMTP {HOST}:{PORT_SMTP}")
            # saisir le destinataire #
            dest = input("Destinataire : ").strip()
            # saisir l'onjet #
            sujet = input("Sujet : ").strip()
            # envoyer les commandes SMTP et lire les reponses #
            env_msg(smtp_socket, f"MAIL FROM: <{mail_utilisateur}>")
            resp = recv_rep(smtp_socket)
            print("Serveur:", resp.strip())
            env_msg(smtp_socket, f"RCPT TO: <{dest}>")
            resp = recv_rep(smtp_socket)
            print("Serveur:", resp.strip())

            # saisir le contenu du message #
            env_msg(smtp_socket, "DATA")
            resp = recv_rep(smtp_socket)
            env_msg(smtp_socket, f"Subject: {sujet}")

            print("Saisissez le corps du message. Terminez par une ligne seule '.'")
            if not resp:
                print("Plus de réponse du serveur, fermeture.")
                smtp_socket.close()
                continue
            print("Saisissez le corps du message. Terminez par une ligne seule '.'")
            while True:
                # lire une ligne du message #
                try:
                    msg_line = input()
                except (EOFError, KeyboardInterrupt):
                    # si interruption pendant la saisie on terminera quand meme le message #
                    msg_line = "."
                    print()
                env_msg(smtp_socket, msg_line)

                if msg_line == ".":
                    # fin du message #
                    break
            resp = recv_rep(smtp_socket)
            print("Serveur:", resp.strip())
            env_msg(smtp_socket, "QUIT")
            recv_rep(smtp_socket)
            smtp_socket.close()
            continue

        ## lire les emails ##
        if choix == "2":
            ## connexion au serveur POP3 ##
            try:
                pop3_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                pop3_socket.connect((HOST, PORT_POP3))
            except Exception as e:
                print(f"Impossible de se connecter à {HOST}:{PORT_POP3} -> {e}")
                sys.exit(1)
            # lire le message d'accueil #
            welcome = recv_rep(pop3_socket)
            if welcome:
                print("Serveur:", welcome.strip())
            else:
                print("Aucune réponse du serveur. Fermeture.")
                pop3_socket.close()
                return
            print(f"Connecté au serveur POP3 {HOST}:{PORT_POP3}")
            # envoyer STAT #
            env_msg(pop3_socket, f"USER {mail_utilisateur}")
            resp = recv_rep(pop3_socket)
            print("Serveur:", resp.strip())
            # envoyer LIST #
            env_msg(pop3_socket, "LIST")
            resp = recv_rep(pop3_socket)
            print("Serveur:", resp.strip())
            # demander quel email lire #
            num_email = input("Quel email lire (numéro) ? ").strip()
            if not num_email.isdigit():
                print("Numéro invalide.")
                env_msg(pop3_socket, "QUIT")
                recv_rep(pop3_socket)
                pop3_socket.close()
                continue
            # envoyer RETR #
            env_msg(pop3_socket, f"RETR {num_email}")
            resp = recv_rep(pop3_socket)
            print("Serveur:", resp.strip())
            env_msg(pop3_socket, "QUIT")
            recv_rep(pop3_socket)
            pop3_socket.close()
            continue

        ## quitter : fermeture de la connexion ##
        if choix == "3":
            print("Fermeture du client.")
            break


### lancement du programme ###
if __name__ == "__main__":
    main()
