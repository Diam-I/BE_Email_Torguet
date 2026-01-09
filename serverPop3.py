import os
import socket
import threading

HOST = "localhost"
PORT_POP3 = 2000
DOSSIER_RACINE = "boite_mail"

def gerer_client(connexion, adresse):
    print("Connecte par", adresse)
    connexion.send(b"+OK POP3 server ready\r\n")
    utilisateur = None

    while True:
        donnees = connexion.recv(1024)
        if not donnees: break
        ligne = donnees.decode("utf-8").strip()

        if ligne.upper().startswith("QUIT"):
            connexion.send(b"+OK Fermeture de la connexion\r\n")
            break

        elif ligne.upper().startswith("USER"):
            utilisateur = ligne.split(" ", 1)[1].strip()
            connexion.send(b"+OK Utilisateur reconnu\r\n")

        elif ligne.upper().startswith("STAT"):
            if utilisateur is None:
                connexion.send(b"-ERR USER requis\r\n")
                continue

            dossier_utilisateur = os.path.join(DOSSIER_RACINE, "reception", utilisateur)
            if os.path.exists(dossier_utilisateur):
                emails = os.listdir(dossier_utilisateur)
                nb_emails = len(emails)
                taille_totale = sum(os.path.getsize(os.path.join(dossier_utilisateur, f)) for f in emails)
                connexion.send(f"+OK {nb_emails} {taille_totale}\r\n".encode("utf-8"))
            else:
                connexion.send(b"+OK 0 0\r\n")

        elif ligne.upper() == "LIST":
            if utilisateur is None:
                connexion.send(b"-ERR USER requis\r\n")
                continue
            dossier_utilisateur = os.path.join(DOSSIER_RACINE, "reception", utilisateur)
            if not os.path.exists(dossier_utilisateur):
                connexion.send(b"+OK 0 messages\r\n")
            else:
                emails = os.listdir(dossier_utilisateur)
                reponse = f"+OK {len(emails)} messages\r\n"
                for i, email in enumerate(emails, start=1):
                    taille = os.path.getsize(os.path.join(dossier_utilisateur, email))
                    reponse += f"{i} {taille}\r\n"
                connexion.send(reponse.encode("utf-8"))

        elif ligne.upper().startswith("RETR"):
            dossier_utilisateur = os.path.join(DOSSIER_RACINE, "reception", utilisateur)
            try:
                numero_email = int(ligne.split()[1]) - 1
                emails = os.listdir(dossier_utilisateur)
                if 0 <= numero_email < len(emails):
                    with open(os.path.join(dossier_utilisateur, emails[numero_email]), "r", encoding="utf-8") as f:
                        contenu = f.read()
                    connexion.send(f"+OK {len(contenu)} octets\r\n{contenu}\r\n".encode("utf-8"))
                else:
                    connexion.send(b"-ERR Numero invalide\r\n")
            except:
                connexion.send(b"-ERR Erreur RETR\r\n")
        elif ligne.upper().startswith("DELE"):
            print("Commande DELE recue")
            if utilisateur is None:
                connexion.send(b"-ERR USER requis\r\n")
                continue

            dossier_utilisateur = os.path.join(DOSSIER_RACINE,"reception", utilisateur)
            os.makedirs(dossier_utilisateur, exist_ok=True)
            try:
                numero_email = int(ligne.split()[1]) - 1
                emails = os.listdir(dossier_utilisateur)
                if 0 <= numero_email < len(emails):
                    os.remove(os.path.join(dossier_utilisateur, emails[numero_email]))
                    reponse = "+OK Message supprime\r\n"
                else:
                    reponse = "-ERR Numero de message invalide\r\n"
            except (IndexError, ValueError):
                reponse = "-ERR Commande DELE mal formée\r\n"

            connexion.send(reponse.encode("utf-8"))

    connexion.close()

if __name__ == "__main__":
    os.makedirs(os.path.join(DOSSIER_RACINE, "reception"), exist_ok=True)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((HOST, PORT_POP3))
            s.listen()
            print(f"\n=== SERVEUR POP3 Lancer - Ecoute sur {HOST}:{PORT_POP3} ===")
            print("\n=> Utilisez CTRL+C pour arrêter proprement.")
            while True:
                conn, addr = s.accept()
                threading.Thread(target=gerer_client, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("\n==> Arrêt du serveur POP3 demandé.")
        finally:
            print("Serveur éteint, port libéré")