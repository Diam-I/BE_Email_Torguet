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

Le serveur écoute par défaut sur localhost:8025. Les emails reçus sont stockés dans boite_mail/<emetteur>.

Architecture
server.py : serveur SMTP multiclient basé sur socket et threading.
client.py : client interactif pour envoyer des emails.
boite_mail/ : répertoire contenant les messages stockés.


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
Objectif : Ajouter des fonctionnalités supplémentaires pour améliorer le serveur SMTP/POP3/IMAP.
    Possibilités :
        Authentification des utilisateurs.
        Support de commandes avancées SMTP ou POP3.
        Implémentation partielle d’IMAP.
        Journalisation et suivi des emails lus/non lus.
        Sécurisation TLS/SSL.