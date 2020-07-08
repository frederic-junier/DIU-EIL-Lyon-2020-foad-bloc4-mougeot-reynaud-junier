#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from faker import Faker                   # pour créer de faux noms, adresses,...
from random import *                      # pour des générateurs de nombres pseudo-aléatoires
import csv                                # pour parcourir des fichiers csv
from pathlib import Path                  # pour déterminer si un fichier existe
import sqlite3                            # pour accéder à une base de données sqlite

MAX_CANDIDATURE = 20

def creer_base_monavenir(base = 'monavenir.db', sql = "creer_base_monavenir.sql") :
    """Création de la base monavenir.db à partir du script SQL"""
    # TODO Établissement de la connexion  
    conn = sqlite3.connect(base)
    # TODO Ouverture du fichier sql en lecture
    f =  open(sql, 'r') 
    # TODO On importe le contenu entier du fichier SQL dans la variable script
    script = f.read()
    # TODO On ferme le fichier sql
    f.close()
    conn.executescript(script)
    # TODO On transfert les enregistrements dans la BD
    conn.commit()
    # TODO On ferme le fichier bd
    conn.close()

def peupler_eleves(cur, idEleve, fichierEleve):
    """On peuple la base eleve à partir du fichier csv fichierEleve
    idEleve est l'identifiant du premier élève"""
    f = open(fichierEleve,'r')
    csvEleve = csv.DictReader(f, delimiter=';')
    for eleve in csvEleve : 
        cur.execute("INSERT INTO eleve(idEleve, idLycee, login, password, nom, prenom, anneeNaissance, note1, note2) VALUES (?,?,?,?,?,?,?,?,?)",
            (idEleve, eleve['idLycee'], eleve['login'], eleve['password'], eleve['nom'], eleve['prenom'],
             eleve['naissance'], eleve['note1'], eleve['note2'] ) )
        idEleve += 1
    f.close()
    return idEleve

def peupler_lycee(cur, fichierLycee = 'csv/lycee-rhone.csv') :
    """On peuple la base lycee à partir du fichier csv des lycées du rhone"""
    #TODO on donne rien, ils s'inspirent de peupler_eleve
    f = open(fichierLycee,'r')
    csvLycee = csv.DictReader(f, delimiter=';')
    for lycee in csvLycee :       
        cur.execute("INSERT INTO lycee(idLycee, login, password, nom, commune) VALUES (?,?,?,?,?)",
            (lycee['idLycee'], lycee['login'], lycee['password'], lycee['Appellation officielle'], lycee['Commune'] ) )
    #login et password fixés pour le premier lycée
    cur.execute("UPDATE lycee  SET  login='lycee', password='monavenir' WHERE idLycee = 1")
    f.close()
    
def peupler_superieur(cur, fichierSup = 'csv/superieur-rhone.csv') :
    #TODO on donne rien, ils s'inspirent de peupler_eleve
    f = open(fichierSup,'r')
    csvSup = csv.DictReader(f, delimiter=';')
    for etab in csvSup :
        cur.execute("INSERT INTO superieur(idSuperieur, login, password, nom, type, commune, latitude, longitude, coefNote1, coefNote2) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (etab['idSuperieur'], etab['login'], etab['password'], etab['nom'], etab['type'],  
             etab['commune'], etab['latitude (Y)'], etab['longitude (X)'],etab['coefNote1'],etab['coefNote2'] ) )
    #login et password fixés pour le premier établissement du supérieur
    cur.execute("UPDATE superieur SET  login='superieur', password='monavenir' WHERE idSuperieur = 1")
    f.close()
    
def peupler_admin(cur, fichierAdmin = 'csv/admin.csv') :
    #TODO on donne rien, ils s'inspirent de peupler_eleve
    f = open(fichierAdmin,'r')
    csvAdmin = csv.DictReader(f, delimiter=';')
    for admin in csvAdmin :
        cur.execute("INSERT INTO admin(idAdmin, login, password, nom, prenom) VALUES (?,?,?,?,?)",
            (admin['idAdmin'], admin['login'], admin['password'], admin['nom'], admin['prenom'] ) )
    #login et password fixés pour le premier admin
    cur.execute("UPDATE  admin SET login='admin', password='monavenir' WHERE idAdmin = 1")
    f.close()

def peupler_candidature(base = 'monavenir.db') :
    # TODO Établissement de la connexion
    conn = sqlite3.connect(base)
    # TODOD création du curseur
    cur = conn.cursor()
    #on récupère une sélection dans la table Eleve
    cur.execute("SELECT idEleve FROM Eleve;")
    #on prépare pour le report dans la table candidature
    tuple_idEleve = cur.fetchall()
    # TODO on récupère une selction dans la table Superieur
    cur.execute("SELECT idSuperieur FROM Superieur;")
    # TODO on prépare pour le report dans la table candidature
    tuple_idSup = cur.fetchall()
    #on récupère l'idEleve de l'élève test pour fixer son nombre de voeux à 20
    cur.execute("SELECT MAX(idEleve) FROM eleve ;")  
    idTest = cur.fetchone()[0]
    #on reporte le informations dans la table candidature
    for idEleve in tuple_idEleve :
        if idEleve == idTest:
            nbCandid = MAX_CANDIDATURE
        else:
            nbCandid = randint(1, MAX_CANDIDATURE)
        for idSup in sample(tuple_idSup, nbCandid) : #à quoi sert sample?
            cur.execute("INSERT INTO candidature VALUES (?,?,?);", (idEleve[0], idSup[0], 'nonTraite'))  
    # TODO On transfert les enregistrements dans la BD
    conn.commit()
    # TODO On ferme le fichier bd
    conn.close()

def peupler_base_monavenir(base= 'monavenir.db', repeleve  ='csv', fichierLycee = 'csv/lycee-rhone.csv', 
                            fichierSup = 'csv/superieur-rhone.csv', fichierAdmin = 'csv/admin.csv') :
    fake = Faker('fr_FR')
    conn = sqlite3.connect(base)
    cur = conn.cursor()
    peupler_admin(cur, fichierAdmin)
    peupler_lycee(cur, fichierLycee)
    idEleve = 1
    for fichierEleve in Path(repeleve).glob('eleves*.csv'):
        idEleve = peupler_eleves(cur, idEleve, fichierEleve)
    #insertion d'un élève test avec le plus grand idEleve
    cur.execute("INSERT INTO eleve(idEleve, idLycee, login, password, nom, prenom, anneeNaissance, note1, note2) VALUES (?,?,?,?,?,?,?,?,?)",
            (idEleve, 1,'eleve','test', 'test', 'eleve', 2002, 5, 12) )
    peupler_superieur(cur, fichierSup)    
    conn.commit()
    conn.close()

creer_base_monavenir()
peupler_base_monavenir()
peupler_candidature()

