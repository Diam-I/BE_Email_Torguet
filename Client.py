import socket
import sys

import ui

### variables d'environnement ###
HOST = "localhost"
PORT = 8025


def recv_rep(sock: socket.socket) -> str:
    """Lit une réponse simple du serveur"""
    try:
        data = sock.recv(4096)
        if not data:
            return ""
        return data.decode("utf-8", errors="replace")
    except Exception as e:
        return f"(erreur lecture socket: {e})"


def env_msg(sock: socket.socket, text: str):
    """Envoi un msg au serveur"""
    if not text.endswith("\r\n"):
        text = text + "\r\n"
    sock.sendall(text.encode("utf-8"))


def main():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
    except Exception as e:
        print(f"Impossible de se connecter à {HOST}:{PORT} -> {e}")
        sys.exit(1)

    # lire le message d'accueil
    welcome = recv_rep(s)
    if welcome:
        print("Serveur:", welcome.strip())
    else:
        print("Aucune réponse du serveur. Fermeture.")
        s.close()
        return
    ## Authentification / Inscription ##
    mail_utilisateur = ui.main()
    print(f"Connecté en tant que {mail_utilisateur}\n")

    ## Interaction avec le serveur ##
    while True:
        try:
            choix = input("Voulez-vous : \n1- Envoyer un email\n2- Quitter\n").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nInterruption locale. Envoi QUIT puis fermeture.")
            try:
                env_msg(s, "QUIT")
            except Exception:
                pass
            break

        if not choix:
            continue
        # Envoi d'un email #
        if choix == "1":
            dest = input("Destinataire : ").strip()
            env_msg(s, f"MAIL FROM: <{mail_utilisateur}>")
            resp = recv_rep(s)
            print("Serveur:", resp.strip())
            env_msg(s, f"RCPT TO: <{dest}>")
            resp = recv_rep(s)
            print("Serveur:", resp.strip())
            env_msg(s, "DATA")
            if not resp:
                print("Plus de réponse du serveur, fermeture.")
                break
            print("Saisissez le corps du message. Terminez par une ligne seule '.'")
            while True:
                try:
                    msg_line = input()
                except (EOFError, KeyboardInterrupt):
                    # si interruption pendant la saisie on terminera quand meme le message #
                    msg_line = "."
                    print()
                env_msg(s, msg_line)
                if msg_line == ".":
                    break
            # Lire la réponse finale #
            resp = recv_rep(s)
            print("Serveur:", resp.strip())
            continue

        # Quitter : fermeture de la connexion
        if choix == "2":
            env_msg(s, "QUIT")
            resp = recv_rep(s)
            print("Serveur:", resp.strip())
            break

        # Sinon autres commandes (HELO, EHLO, MAIL FROM:, RCPT TO:, etc.)
        env_msg(s, choix)
        resp = recv_rep(s)
        if resp == "":
            print("Aucune réponse (connexion fermée).")
            break
        print("Serveur:", resp.strip())

    print("Fermeture du client.")
    s.close()


if __name__ == "__main__":
    main()
