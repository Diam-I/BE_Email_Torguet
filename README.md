Projet E-Mail — Déploiement de Services et Interopérabilité

Présentation
Ce projet a pour objectif de concevoir et implémenter un service de messagerie électronique local, basé sur
les protocoles SMTP et POP3, conformément aux spécifications de la RFC 5321 et de la RFC 1081.
Il s’agit d’un projet d’étude réalisé dans le cadre du module Interopérabilité et Déploiement de Services,
visant à comprendre les mécanismes de transmission, de réception et de stockage d’e-mails.

Fonctionnalités principales

Version 1 – Serveur SMTP simple

Réception et stockage local des messages.
Communication via socket TCP/IP sur le port 25.
Support de plusieurs connexions simultanées grâce aux threads.

Version 2 – Améliorations prévues
Gestion des commandes HELO / EHLO.
Meilleure gestion des erreurs et journalisation.
Extension vers le protocole POP3 (consultation de mails).
