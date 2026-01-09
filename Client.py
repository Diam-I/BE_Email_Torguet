import socket
import os
import ui
import datetime

### Variables d'environnement ###
HOST = "localhost"
PORT_SMTP = 3000
PORT_POP3 = 2000
DOSSIER_RACINE = "boite_mail"

def recv_rep(sock: socket.socket) -> str:
    """Lit la réponse du serveur sur le socket."""
    try:
        data = sock.recv(4096)
        if not data: return ""
        return data.decode("utf-8", errors="replace")
    except Exception as e:
        return f"(erreur: {e})"

def env_msg(sock: socket.socket, text: str):
    """Envoie un message formaté au serveur."""
    if not text.endswith("\r\n"):
        text = text + "\r\n"
    sock.sendall(text.encode("utf-8"))

def afficher_tableau(titre, dossiers, type_mail, mail_utilisateur):
    """Affiche un tableau des emails (Réception ou Envoi)."""
    print("\n" + "="*75)
    print(f" {titre} ".center(75, "="))
    colonnes = "Expéditeur" if type_mail == "reception" else "Destinataire"
    print(f"{'N°':<3} | {colonnes:<25} | {'Date & Heure':<20} | {'Taille'}")
    print("-" * 75)
    
    path = os.path.join(DOSSIER_RACINE, type_mail, mail_utilisateur)
    if not os.path.exists(path) or not os.listdir(path):
        print(" Aucun message trouvé.".center(75))
        print("="*75)
        return False
    
    files = sorted(os.listdir(path), reverse=True)
    for i, f in enumerate(files, 1):
        taille = os.path.getsize(os.path.join(path, f))
        parts = f.replace(".txt", "").split("_")
        
        # Formatage : mail_From/To_contact_date_heure.txt
        contact = parts[2] if len(parts) > 2 else "Inconnu"
        raw_date = parts[3] + "_" + parts[4] if len(parts) > 4 else "---"
        
        try:
            date_obj = datetime.datetime.strptime(raw_date, "%Y%m%d_%H%M%S")
            date_f = date_obj.strftime("%d/%m/%Y %H:%M")
        except:
            date_f = raw_date
            
        print(f"{i:<3} | {contact:<25} | {date_f:<20} | {taille} octets")
    print("="*75)
    return True

def consulter_envoi(dossier,mail):

    if afficher_tableau("MESSAGES ENVOYÉS", dossier, "envoi", mail):
        print("\n" + "Voulez-vous :")
        print("1- Consulter un message ")
        print("2- Supprimer un message ")
        print("=> Appuyez sur n'importe quelle autre touche pour revenir à l'accueil ")
        
        choix_env = input("\nVeuillez renseigner une option : ").strip()
        return choix_env
    return 0

def main():
    mail_utilisateur = ui.main()
    if not mail_utilisateur: return
    mail_utilisateur = mail_utilisateur.strip()
    
    print(f"\n Connecté en tant que : {mail_utilisateur}")

    while True:
        print("\n" + "--- MENU PRINCIPAL ---".center(30))
        print("1- Envoyer un email ")
        print("2- Consulter la Boîte de réception ")
        print("3- Consulter les Messages envoyés ")
        print("4- Se deconnecter")
        
        choix = input("\nVeuillez renseigner une option : ").strip()

        if choix == "1":
            try:
                ## Utilisation de SMTP pour l'envoie de mail 
                smtp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                smtp_socket.connect((HOST, PORT_SMTP))
                recv_rep(smtp_socket)

                # Code version 2 #
                env_msg(smtp_socket, "EHLO localhost")
                resp = recv_rep(smtp_socket)

                if resp.startswith("502"):
                    env_msg(smtp_socket, "HELO localhost")
                    resp = recv_rep(smtp_socket)

                if not resp.startswith("250"):
                    print("Erreur identification SMTP.")
                    smtp_socket.close()
                    continue
                #Fin code V2#

                dest = input("Destinataire : ").strip()
                sujet = input("Sujet : ").strip()
                
                env_msg(smtp_socket, f"MAIL FROM: <{mail_utilisateur}>")
                recv_rep(smtp_socket)
                env_msg(smtp_socket, f"RCPT TO: <{dest}>")
                recv_rep(smtp_socket)

                env_msg(smtp_socket, "DATA")
                recv_rep(smtp_socket)
                
                # Ajout de l'en-tête sujet directement dans le DATA
                env_msg(smtp_socket, f"Subject: {sujet}")

                print("Saisissez le corps (finissez par '.' seul sur une ligne) :")
                while True:
                    msg_line = input()
                    env_msg(smtp_socket, msg_line)
                    if msg_line.strip() == ".": break
                
                print("Serveur SMTP :", recv_rep(smtp_socket).strip())
                smtp_socket.close()
            except Exception as e: print(f"Erreur SMTP: {e}")

        elif choix == "2":
            try:
                pop3_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                pop3_socket.connect((HOST, PORT_POP3))
                recv_rep(pop3_socket) 

                env_msg(pop3_socket, f"USER {mail_utilisateur}")
                recv_rep(pop3_socket)

                if afficher_tableau("BOÎTE DE RÉCEPTION", DOSSIER_RACINE, "reception", mail_utilisateur):
                    print("\n" + "Voulez-vous :")
                    print("1- Consulter un mail ")
                    print("2- Supprimer un mail ")
                    print("=> Appuyer sur m'importe quel autre touche pour revenir a la page d'acceuil ")
                    choix = input("\nVeuillez renseigner une option : ").strip()
                    if choix=="1":
                        num = input("\nQuel email lire (numéro) ou Entrée pour retour : ").strip()
                        if num.isdigit():
                            env_msg(pop3_socket, f"RETR {num}")
                            contenu = recv_rep(pop3_socket)
                            print("\n" + "╔" + "═"*60 + "╗")
                            print("║" + " CONTENU DU MESSAGE ".center(60) + "║")
                            print("╚" + "═"*60 + "╝")
                            print(contenu)
                    elif choix=="2":
                        num = input("\nNuméro du mail à supprimer : ").strip()
                        if num.isdigit():
                            confirm = input(f"Confirmer la suppression du message {num} ? (y/n) : ").lower()
                            if confirm == 'y':
                                env_msg(pop3_socket, f"DELE {num}")
                                reponse = recv_rep(pop3_socket)
                                if "+OK" in reponse:
                                    print(f" Succès : {reponse.strip()}")
                                else:
                                    print(f" Erreur serveur : {reponse.strip()}")
                            else:
                                print("Suppression annulée.")
                
                env_msg(pop3_socket, "QUIT")
                pop3_socket.close()
            except Exception as e: print(f"Erreur POP3: {e}")

        elif choix == "3":
            path_envoi = os.path.join(DOSSIER_RACINE, "envoi", mail_utilisateur)
            option=consulter_envoi(DOSSIER_RACINE,mail_utilisateur)
            if option!=0:
                if os.path.exists(path_envoi):
                    files = sorted(os.listdir(path_envoi), reverse=True)
                else:
                    files = []

                if option == "1":
                    num = input("\nQuel message consulter (numéro) : ").strip()
                    if num.isdigit() and 0 < int(num) <= len(files):
                        with open(os.path.join(path_envoi, files[int(num)-1]), "r", encoding="utf-8") as f:
                            print("\n" + "📂 " + f" MESSAGE {num} ".center(56, "-"))
                            print(f.read())
                            print("-" * 60)
                    else:
                        print("=>  Numéro invalide !! ")

                elif option == "2":
                    num = input("\nNuméro du message à supprimer de l'historique : ").strip()
                    if num.isdigit() and 0 < int(num) <= len(files):
                        nom_fichier = files[int(num)-1]
                        confirm = input(f"Confirmer la suppression définitive du message {num} ? (y/n) : ").lower()
                        
                        if confirm == 'y':
                            try:
                                os.remove(os.path.join(path_envoi, nom_fichier))
                                print(f"=> Message {num} supprimé avec succès de l'historique.")
                            except Exception as e:
                                print(f"=> Erreur lors de la suppression : {e}")
                        else:
                            print("Suppression annulée.")
                    else:
                        print("=> Numéro invalide !!")
        elif choix == "4":
            print("Deconnection...."); break
    main()

if __name__ == "__main__":
    main()
