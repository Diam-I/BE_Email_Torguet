BE_Email_Torguet

Ce projet implémente un serveur SMTP minimal et un client Python pour envoyer des emails en local. Il supporte les commandes SMTP de base (HELO, MAIL FROM, RCPT TO, DATA, QUIT) et peut gérer plusieurs clients simultanément grâce aux threads.


Fonctionnalités

Serveur SMTP capable de gérer plusieurs clients en parallèle.
Gestion des commandes SMTP suivantes :
HELO / HELLO
MAIL FROM: <adresse>
RCPT TO: <adresse>
DATA pour saisir le corps du message
QUIT pour fermer la connexion
Sauvegarde des emails dans des fichiers texte organisés par expéditeur.
Client interactif permettant de se connecter au serveur et d’envoyer des emails ligne par ligne.

Le serveur écoute par défaut sur localhost:Num_port. Les emails reçus sont stockés dans boite_mail/reception/<@User> et les emails envoyés dans  boite_mail/envoi/<@User>.

Architecture
serverSMTP.py : serveur multiclient basé sur socket et threading responsable de l'envoi des email.
serverPop3.py : serveur  multiclient basé sur socket et threading responsable de la consultation et la manipulation(suppression) des mail après envoi.
client.py : client interactif pour envoyer des emails et gerer la communication avec les 2 serveurs.
boite_mail/ : répertoire contenant les messages envoyer et reçu.
ui.py: responsable de l'authentification et de l'inscription des user aupres du serveur smtp/POP
user.py: permet grâce a ces deux fontionnalite d'interagir avec la speudo base de donnée


Version 1 : SMTP simple

Objectif : Implémenter un serveur SMTP minimal capable de recevoir des emails.
Fonctionnalités demandées :
    Support des commandes SMTP de base :
    MAIL FROM:
    RCPT TO:
    DATA
    Stocker les emails dans un fichier correspondant au destinataire (RCPT) dans un dossier local.

Version 2 : Gestion des commandes HELO/EHLO

Objectif : Identifier la version du protocole SMTP utilisée par le client pour permettre une compatibilité minimale avec des clients mail réels.
Fonctionnalités demandées :
    Support de HELO : réponse 250 OK.
    Support partiel de EHLO : réponse 502 Command not implemented.
    Maintien de toutes les fonctionnalités de la version 1 (MAIL, RCPT, DATA).
    Serveur capable de communiquer avec des clients comme Thunderbird pour l’envoi.


Version 3 : Ajout de POP3

Objectif :Permettre aux clients de consulter à distance les courriers stockés via POP3.
Fonctionnalités demandées :
    Mise en place d’un serveur POP3 (port séparé).
        Gestion minimale des commandes POP3 :
        QUIT
        STAT
        LIST
        RETR
    Les emails envoyés par SMTP sont accessibles depuis le dossier reception/ du destinataire.

Version 4 : Options avancées
Nous avons rajouter et pour ameliorer des fonctionnalités deja existante afin d'améliorer l'experience utilisateur et la qualite de code.
    Authentification des utilisateurs.
    Support de commandes avancées SMTP ou POP3.
    Hachage MD5 : Les mots de passe ne sont jamais stockés en clair.
    Limitation des tentatives : ui.py bloque l'accès après 3 échecs consécutifs
    Processus d'inscription: gestion des doublons
    SMTP - RSET : Capacité de réinitialiser une transaction sans fermer la connexion TCP.
    Pop3 - DEL : Suppression d'un message 

Ce projet a ete realiser dans le cadre du Bureau d'etude du module interoperabilite par : 
- Traore Fatoumata Salia 
- Didane Amina.
Periode: Octobre 2025 - janvier 2026
