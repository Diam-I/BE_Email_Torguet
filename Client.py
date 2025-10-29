import socket
import sys

### variables d'environnement ###
HOST = "localhost"
PORT = 8025

HELP_TEXT = """
Commandes SMTP supportées (exemples) :
  HELO <nom>                -> HELO monclient
  EHLO <nom_client>         -> Version étendue du protocole (non implémentée dans cette version).
  MAIL FROM: <adresse>      -> MAIL FROM: <alice@example.com>
  RCPT TO: <adresse>        -> RCPT TO: <bob@example.com>
  DATA                      -> Passe en mode saisie du corps du message (terminer par une ligne contenant uniquement un point '.')
  QUIT                      -> Termine la session
  HELP                      -> Affiche cette aide
Remarques :
  - Tapez exactement les mots-clefs (MAIL FROM:, RCPT TO:) suivis d'un espace et de l'adresse entre <>.
  - Après DATA, écris ton message ligne par ligne, puis une ligne avec uniquement . pour envoyer.
"""


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


def aide():
    """Affichage du menu des commandes"""
    print("\n               --- MENU ---                    ")
    print("Tape HELP pour afficher les commandes disponibles.")
    print("Commandes: HELO, EHLO, MAIL FROM:, RCPT TO:, DATA, QUIT")
    print("----------------------------------------------")


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

    # afficher l'aide
    print(HELP_TEXT)

    while True:
        try:
            line = input("Entrez une commande SMTP (ou help/quit): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nInterruption locale. Envoi QUIT puis fermeture.")
            try:
                env_msg(s, "QUIT")
            except Exception:
                pass
            break

        if not line:
            continue

        # HELP : afficher l'aide et continuer
        if line.upper() == "HELP":
            print(HELP_TEXT)
            continue

        # QUIT : fermeture de la connexion
        if line.upper() == "QUIT":
            env_msg(s, "QUIT")
            resp = recv_rep(s)
            print("Serveur:", resp.strip())
            break

        # DATA : mode corps du message
        if line.upper() == "DATA":
            env_msg(s, "DATA")
            resp = recv_rep(s)
            print("Serveur:", resp.strip())
            if not resp:
                print("Plus de réponse du serveur, fermeture.")
                break
            print("Saisissez le corps du message. Terminez par une ligne seule '.'")
            while True:
                try:
                    msg_line = input()
                except (EOFError, KeyboardInterrupt):
                    # si interruption pendant la saisie on terminera quand meme le message
                    msg_line = "."
                    print()
                env_msg(s, msg_line)
                if msg_line == ".":
                    break
            # lire la réponse finale
            resp = recv_rep(s)
            print("Serveur:", resp.strip())
            continue

        # Sinon autres commandes (HELO, EHLO, MAIL FROM:, RCPT TO:, etc.)
        env_msg(s, line)
        resp = recv_rep(s)
        if resp == "":
            print("Aucune réponse (connexion fermée).")
            break
        print("Serveur:", resp.strip())

    print("Fermeture du client.")
    s.close()

if __name__ == "__main__":
      main()