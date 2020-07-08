#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from faker import Faker                   # pour créer de faux noms, adresses,...
from random import *                      # pour des générateurs de nombres pseudo-aléatoires
import csv                                # pour parcourir des fichiers csv
from pathlib import Path                  # pour déterminer si un fichier existe

def generer_login(listLogin, fake):
    login = fake.user_name()
    #Afin de ne pas avoir d'erreur de contrainte d'intégrité, on vérifie que le login n'est 
    #pas déjà attibué et on en redonne un sinon...
    while login in listLogin:   #TODO faire écrire cette boucle...
        login = fake.user_name() 
    #on ajoute le nouveau login à la liste
    listLogin.append(login)     #TODO 
    return login

def generer_csv_lycee(listlogin, fichierdata = 'lycee-rhone-data.csv', fichier = 'csv/lycee-rhone.csv'):
    fake = Faker('fr_FR')      
    csvdata = open(fichierdata, 'r')                   # TODO on ouvre le fichier csvdata en lecture
    csv = open(fichier, 'w')                           # TODO on ouvre le fichier csv en écriture
    prem_ligne = csvdata.readline()                    # La premiere ligne contient les titres
    csv.write('idLycee;login;password;'+prem_ligne)    # On ajoute des descripteurs aux précédents
    i = 1
    for ligne in (csvdata) :
        login = generer_login(listlogin, fake)         # TODO création d'un login avec appelle de la fonction
        # TODO compléter la ligne suivante afin d'obtenir, pour chaque lycée, les 5-uplets de ce type :
        # 'idLycée';'login';'password';'appelation'; 'commune'
        csv.write(str(i) + ';' + login + ';' + fake.password(length=12) + ';' + ligne)
        i = i+1                                        #TODO on incrémente i
    csvdata.close()
    csv.close()

def generer_csv_superieur(listlogin, fichierdata = 'superieur-rhone-data.csv', fichier = 'csv/superieur-rhone.csv'):
    fake = Faker('fr_FR')      
    csvdata = open(fichierdata, 'r')                   # TODO on ouvre le fichier csvdata en lecture
    csv = open(fichier, 'w')                           # TODO on ouvre le fichier csv en écriture
    prem_ligne = csvdata.readline().rstrip('\n')                    # La premiere ligne contient les titres
    # On ajoute des descripteurs aux précédents
    csv.write('idSuperieur;login;password;'+prem_ligne+';nbAdmis;nbAppel;coefNote1;coefNote2\n')    
    i = 1
    for ligne in (csvdata) :
        login = generer_login(listlogin, fake)          # TODO création d'un login avec appelle de la fonction
        # TODO compléter la ligne suivante afin d'obtenir, pour chaque lycée, les 5-uplets de ce type :
        # 'idLycée';'login';'password';'appelation'; 'commune'
        c1 = randint(1,7)
        c2 = randint(0,2)
        csv.write(str(i) + ';' + login + ';' + fake.password(length=12) + ';' + ligne.rstrip('\n') + ';100;200;'+str(c1)+';'+str(c2)+'\n')
        i = i+1                                        #TODO on incrémente i
    csvdata.close()
    csv.close()


def generer_csv_admin(listlogin, fichier = 'csv/admin.csv', nbadmin = 3):
    fake = Faker('fr_FR')
    csv = open(fichier, 'w') 
    idAdmin= 1
    csv.write('idAdmin;login;password;nom;prenom\n')
    for k in range(nbadmin):
        login = generer_login(listlogin, fake)
        csv.write(str(idAdmin) + ';' + login + ';' +  fake.password(length=12) + ';' + fake.last_name() + ';' + fake.first_name() + '\n')
        idAdmin += 1
    csv.close()



def anneeNaiss(a):#appel avec a=2000 TODO
    n = random()
    if n<0.01:
        return a
    elif n<0.08 :
        return a+1
    elif n<0.91:
        return a+2
    elif n<0.99:
        return a+3
    else:
        return a+4

def generer_csv_eleves(listlogin, fichierLycee = 'csv/lycee-rhone.csv', nbEleve = 60):
    fake = Faker('fr_FR')
    Path('csv').glob('rm eleves*.csv')   #effacer les fichiers eleves*.csv précédents
    #Ouverture en lecture du fichierLycee
    csvLycee = open(fichierLycee,'r')   #TODO derrière le =
    #Pour garder le lien entre lidLycee et nomLycee, on utilise DictReader qui retourne un p-uplet pour chaque enregistrement :
    lyceeReader = csv.DictReader(csvLycee, delimiter=';') #TODO ??? moi je l'ai fais l'an dernier...
    #Pour chacun des 60 lycées... (on va créer nbEleves élèves)
    idLycee = 1
    for lycee in lyceeReader :  #mettre TODO à la place de lyceeReader
        #création du nom de fichier : variable de type str correspond à 'csv/eleves-NomDuLyceee.csv', par exemple 'csv/eleves-LyceeDuParc.csv' 
        fichierEleve = 'csv/eleves-' + lycee['Appellation officielle'] + '.csv' #TODO derrière le =
        #Ouverture en écriture du fichierEleve
        csvEleve = open(fichierEleve, 'w') #TODO derrière le =
        #Première ligne avec les 6 descripteurs du fichierEleve, voir la BD utilisée en classe...
        csvEleve.write('idLycee;login;password;nom;prenom;naissance;note1;note2\n') #TODO 
        #pour chaque lycée, on crée les nbEleves élèves
        for k in range(nbEleve): #TODO derrière le for, ou derrière le range...
            #création et initialisation de deux variables note1, note2
            #comme étant des nombres réelles aléatoires entre 0 et 20 arrondis au dixième 
            note1 = round((0.9 * random() + 0.1) * 20, 3)  #notes entre 2 et 20    #TODO derrière le =
            note2 = round((0.9 * random() + 0.1) * 20, 3)  #notes entre 2 et 20    #TODO derrière le =
            naissance = str(anneeNaiss(2000))              #TODO appel avec 2000
            login = generer_login(listlogin, fake)
            password = fake.password(length=12)
            champs = [str(idLycee),login, password, fake.last_name(), fake.first_name() , naissance, str(note1), str(note2)]
            csvEleve.write(';'.join(champs) + '\n')
        csvEleve.close()
        idLycee += 1
    csvLycee.close()  

listlogin = []    
generer_csv_lycee(listlogin)
generer_csv_superieur(listlogin)
generer_csv_eleves(listlogin)
generer_csv_admin(listlogin)
