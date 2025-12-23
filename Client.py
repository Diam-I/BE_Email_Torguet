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
            print("\nInterruption locale. Envoi QUIT puis fermeture.")
            try:
                env_msg(s, "QUIT")
            except Exception:
                pass
            break

        if not choix:
            continue
        ## envoi d'un email ##
        if choix == "1":
            ## connexion au serveur SMTP ##
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((HOST, PORT_SMTP))
            except Exception as e:
                print(f"Impossible de se connecter à {HOST}:{PORT_SMTP} -> {e}")
                sys.exit(1)
            # lire le message d'accueil #
            welcome = recv_rep(s)
            if welcome:
                print("Serveur:", welcome.strip())
            else:
                print("Aucune réponse du serveur. Fermeture.")
                s.close()
                return
            print(f"Connecté au serveur SMTP {HOST}:{PORT_SMTP}")
            # saisir le destinataire #
            dest = input("Destinataire : ").strip()
            # envoyer les commandes SMTP et lire les reponses #
            env_msg(s, f"MAIL FROM: <{mail_utilisateur}>")
            resp = recv_rep(s)
            print("Serveur:", resp.strip())
            env_msg(s, f"RCPT TO: <{dest}>")
            resp = recv_rep(s)
            print("Serveur:", resp.strip())
            env_msg(s, "DATA")
            resp = recv_rep(s)
            # print("Serveur:", resp.strip())
            if not resp:
                print("Plus de réponse du serveur, fermeture.")
                break
            print("Saisissez le corps du message. Terminez par une ligne seule '.'")
            while True:
                # lire une ligne du message #
                try:
                    msg_line = input()
                except (EOFError, KeyboardInterrupt):
                    # si interruption pendant la saisie on terminera quand meme le message #
                    msg_line = "."
                    print()
                env_msg(s, msg_line)

                if msg_line == ".":
                    # fin du message #
                    s.sendall(b".\r\n")
                    break
            resp = recv_rep(s)
            print("Serveur:", resp.strip())
            continue

        ## lire les emails ##
        if choix == "2":
            ## connexion au serveur POP3 ##
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((HOST, PORT_POP3))
            except Exception as e:
                print(f"Impossible de se connecter à {HOST}:{PORT_POP3} -> {e}")
                sys.exit(1)
            # lire le message d'accueil #
            welcome = recv_rep(s)
            if welcome:
                print("Serveur:", welcome.strip())
            else:
                print("Aucune réponse du serveur. Fermeture.")
                s.close()
                return
            print(f"Connecté au serveur POP3 {HOST}:{PORT_POP3}")
            # envoyer STAT #
            env_msg(s, "STAT")
            resp = recv_rep(s)
            print("Serveur:", resp.strip())
            # envoyer LIST #
            env_msg(s, "LIST")
            resp = recv_rep(s)
            print("Serveur:", resp.strip())
            # demander quel email lire #
            num_email = input("Quel email lire (numéro) ? ").strip()
            if not num_email.isdigit():
                print("Numéro invalide.")
                continue
            # envoyer RETR #
            env_msg(s, f"RETR {num_email}")
            resp = recv_rep(s)
            print("Serveur:", resp.strip())
            continue

        ## quitter : fermeture de la connexion ##
        if choix == "3":
            env_msg(s, "QUIT")
            resp = recv_rep(s)
            print("Serveur:", resp.strip())
            break

    # Tenter EHLO #
    env_msg(s, f"EHLO")
    resp = recv_rep(s)
    print("Serveur:", resp.strip())

    # Verification de la reponse #
    if resp.startswith("502"):
        print("Serveur a refusé EHLO (502). Basculement sur HELO...")
        env_msg(s, f"HELO")
        resp = recv_rep(s)
        print("Serveur:", resp.strip())

        # Si le serveur répond 250 (succès), nous sommes identifiés #
        if not resp.startswith("250"):
            print(
                "ERREUR FATALE: Le serveur a échoué l'identification HELO. Fermeture."
            )
            s.close()
            return
        print("Identification réussie par HELO.")
        print("Serveur:", resp.strip())

    print("Fermeture du client.")
    s.close()


### lancement du programme ###
if __name__ == "__main__":
    main()
