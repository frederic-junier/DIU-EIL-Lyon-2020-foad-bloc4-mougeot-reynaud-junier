#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import *    #framework pour construire une application web 
import sqlite3         #module d'interconnexion avec une base de données Sqlite


MAX_CANDIDATURE = 20

#création d'une instance de l'application
app = Flask(__name__)

#clef de session
app.secret_key = "clef secrète"

#paramétrage du chemin pour les fichiers 'static' : images, feuilles de styles ...
app.static_folder = 'static'


#######################
### Connexion      ####
#######################


#controleur de route / URL (route dans le langage de Flask)
@app.route('/')
def accueil():
    "Controleur de la  route '/'"
    #retourne la vue associée : la page accueil.html
    return render_template('accueil.html')


#controleur de route / URL
@app.route('/connexion',methods = ['POST'])
def connexion():
    "Controleur de la route '/connexion' "
    if request.method == 'POST':
        #les valeurs des paramètres sont dans le dictionnaire request.form 
        result = request.form
        profil = result['profil']
        login = result['login']
        password = result['password']
        conn = sqlite3.connect('monavenir.db')     
        conn.row_factory =  sqlite3.Row  #pour récupérer les lignes sous forme de dictionnaire     
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {profil} WHERE login=? and password=? ;",(login, password))
        user = cur.fetchone()
        conn.close()       
        if user:
            #dictionnaire de session
            session['user'] = dict(user)  #les objets de type ROW retournés ne sont pas sérialisables et stockables dans le dictionnaire du cookie de session  
            session['profil'] = profil    #on stocke le profil dans le cookie de session
            #renvoi du template
            return render_template("{}.html".format(profil)) 
        #Si l'utilisateur n'existe pas pour ce profil  
        #on renvoie le code d'erreur 500 et on passe la main au gestionnaire d'erreur ci-dessous
        abort(500)    


#controleur de route / URL
@app.route('/deconnexion')
def deconnexion():
    #on vide le dictionnaire de session
    print(session)     #debug
    session.clear()    #on vide le dictionnaire de session
    print(session)     #debug
    #redirection vers la route controlée par la fonction accueil
    #return render_template('/')
    return redirect(url_for('accueil'))

#######################
### Commun         ####
#######################


#controleur de route / URL
@app.route('/interface')
def interface():
    "Controleur de la route '/interface' "
    if 'profil' in session and session['profil']:
        return render_template("{}.html".format(session['profil']))
    

#gestion des erreurs 404
@app.errorhandler(404)
def page_not_found(error):
    return render_template('erreur.html', code = 404), 404


#gestion des erreurs 500
@app.errorhandler(500)
def internal_servor_error(error):
    return render_template('erreur.html', code = 500), 500



#######################
### Profil eleve   ####
#######################


#controleur de route / URL
@app.route('/rechercheFormation')
def rechercheFormation():
    "Controleur de la route '/rechercheFormation' "

    def requeteListeTypeEtabSuperieur(conn, cur):
        """Liste des types distinctes d'établissements du supérieurs"""
        cur.execute("SELECT DISTINCT type FROM superieur ;")
        return cur.fetchall()
    
    def requeteListeCommuneEtab(conn, cur):
        """Liste des communes distinctes d'établissements du supérieurs"""
        cur.execute("SELECT DISTINCT commune FROM superieur ;")
        return cur.fetchall()

    
    #ouverture de connexion à la BDD
    conn = sqlite3.connect('monavenir.db')     
    conn.row_factory =  sqlite3.Row  #pour récupérer les lignes sous forme de dictionnaire     
    cur = conn.cursor()
    #requetes
    list_type = requeteListeTypeEtabSuperieur(conn, cur)
    list_commune = requeteListeCommuneEtab(conn, cur)
    #fermeture de connexion ) la BDD
    cur.close()
    conn.close()
    #renvoi du template avec paramètres
    return render_template("rechercheFormation.html", list_type = list_type,  list_commune = list_commune)


#controleur de route / URL
@app.route('/resultatRecherche', methods = ['POST'])
def resultatRecherche():
    "Controleur de la route '/resultatFRecherche' "
    
    def requeteListeEtabSup(conn, cur, result):
        if result['type'] == 'indifferent':
            if result['commune'] != 'indifferent':
                requete = """
                        SELECT nom, idSuperieur, type, commune 
                            FROM superieur  WHERE commune = ?    
                                ORDER BY type;
                            """
                cur.execute(requete, (result['commune'],))                
            else:
                requete = """
                        SELECT idSuperieur,nom, type, commune 
                            FROM superieur ORDER BY commune, type;
                            """  
                cur.execute(requete)                
        elif result['commune'] == 'indifferent':
            requete = """
                    SELECT idSuperieur,nom, type, commune 
                        FROM superieur WHERE type = ?  
                            ORDER BY commune;
                      """
            cur.execute(requete, (result['type'],))   
        else:
            requete = """
                    SELECT idSuperieur,nom, type, commune 
                        FROM superieur 
                            WHERE commune = ? and type = ?;
                      """
            cur.execute(requete, (result['commune'] , result['type']))
        return cur.fetchall()

    #analyse du formulaire
    if request.method == 'POST':
        #ouverture du formulaire
        result = request.form
        #ouverture de connexion à la BDD
        conn = sqlite3.connect('monavenir.db')     
        conn.row_factory =  sqlite3.Row  #pour récupérer les lignes sous forme de dictionnaire     
        cur = conn.cursor()
        #requetes
        liste_sup = requeteListeEtabSup(conn, cur, result)       
        #fermeture de connexion à la BDD
        cur.close()
        conn.close()
        return render_template("resultatRecherche.html", liste_sup = liste_sup,  result = result)

#controleur de route / URL
@app.route('/consulterCompte')
def consulterCompte():
    "Controleur de la route '/consulterCompte' "
    return render_template("compte.html")


#controleur de route / URL
@app.route('/modifierCompte', methods = ['POST'])
def modifierCompte():
    "Controleur de la route '/modifierCompte' "

    def requeteMajCompte(conn, cur, result, idEleve):
        for name, value in result.items(): #pour chaque champ du formulaire
            if result[name]:  #si l'attribut/champ du formulaire a été modifié
                #on met à jour la table eleve avec la nouvelle valeur
                cur.execute("UPDATE  eleve SET {} = ? WHERE idEleve = ? ;".format(name), (value, idEleve))
                #on met à jour le dictionnaire du cookie de session voir https://flask.palletsprojects.com/en/1.1.x/api/#sessions
                session['user'][name] = value 
                session.modified = True
        
    #analyse du formulaire
    if request.method == 'POST':
        #ouverture du formulaire
        result = request.form
        #ouverture de connexion à la BDD
        conn = sqlite3.connect('monavenir.db')      
        cur = conn.cursor()
        #on récupère l'idEleve dans le dictionnaire de session
        idEleve = session['user']['idEleve'] 
        requeteMajCompte(conn, cur, result, idEleve)
        #enregistrement des modifications dans la BDD
        conn.commit()
        #fermeture de connexion à la BDD
        cur.close()
        conn.close()
    return render_template("compte.html")


#controleur de route / URL
@app.route('/candidature')
def candidature():
    "Controleur de la route '/candidature' "

    def requeteListeCandidature(conn, cur, idEleve):
        requete = """
                SELECT  idSuperieur, nom, type, commune 
                    FROM candidature 
                        JOIN superieur USING(idSuperieur)
                             WHERE idEleve = ? ;"""
        cur.execute(requete, (idEleve,))
        return cur.fetchall()
 
    #ouverture de connexion à la BDD
    conn = sqlite3.connect('monavenir.db')  
    conn.row_factory =  sqlite3.Row  #pour récupérer les lignes sous forme de dictionnaire         
    cur = conn.cursor()
    #on récupère l'idEleve dans le cookie de session
    idEleve = session['user']['idEleve'] 
    #requete
    liste_candidature = requeteListeCandidature(conn, cur, idEleve)
    #mise à jour du dictionnaire du cookie de session pour récupérer liste_candidature dans modifierCandidature voir https://flask.palletsprojects.com/en/1.1.x/api/#sessions
    session['liste_candidature'] = [dict(candidature) for candidature in liste_candidature]
    session.modified = True
    #fermeture de connexion à la BDD
    cur.close()
    conn.close()
    #renvoi du template
    return render_template("candidature.html", MAX_CANDIDATURE = MAX_CANDIDATURE)

#controleur de route / URL
@app.route('/modifierCandidature', methods = ['POST'])
def modifierCandidature():
    "Controleur de la route '/modifierCandidature' "

    def requeteListeCandidatureApresSuppression(conn, cur, result, idEleve):
        """Supprime les candidatures abandonnées
        et retourne la liste des identifiants des établissements demandés par l'élève
        """
        #recupération de données dans le dictionnaire de session
        liste_idSuperieur = [candidature['idSuperieur']  for candidature in session['liste_candidature'] ]
        for name, value in result.items():
            if name != 'newCandid' and value == 'on': #en fait les cases à cocher non cochées ne sont pas transmises voir https://developer.mozilla.org/fr/docs/Web/HTML/Element/input/checkbox
                cur.execute("DELETE FROM candidature WHERE idSuperieur = ? and idEleve = ? ;", (name, session['user']['idEleve']))
                liste_idSuperieur.remove(int(name))
        return liste_idSuperieur
   
    def requeteTraitementNouvelleCandidature(conn, cur, result, liste_idSuperieur):
        #nouvelle candidature avec dépassement du nombre de maximal de candidatures MAX_CANDIDATURE
        #message d'erreur d'alerte transmis à la page retournée
        # voir https://flask.palletsprojects.com/en/1.1.x/patterns/flashing/ 
        if len(liste_idSuperieur) == MAX_CANDIDATURE and result['newCandid']:
            flash('Nombre maximal de voeux atteint !')  
        #sinon traitement de la nouvelle candidature
        elif result['newCandid']:
            idSuperieur = int(result['newCandid']) #récupération de l'identifiant de la formation du supérieur saisi dans le formulaire
            if idSuperieur not in liste_idSuperieur:
                cur.execute("INSERT INTO candidature(idEleve, idSuperieur) VALUES (?,?);", (session['user']['idEleve'], idSuperieur))
            else:
                #message d'erreur d'alerte transmis à la page suivante voir https://flask.palletsprojects.com/en/1.1.x/patterns/flashing/
                flash('Ajout impossible, candidature déjà formulée ?')      

    #analyse du formulaire
    if request.method == 'POST':  
        #ouverture du formulaire      
        result = request.form
        #connexion à la BDD
        conn = sqlite3.connect('monavenir.db')           
        cur = conn.cursor()
        #récupration de idEleve dans le dictionnaire de session
        idEleve = session['user']['idEleve']
        #Mise à jour de la liste des candidatures
        liste_idSuperieur = requeteListeCandidatureApresSuppression(conn, cur, result, idEleve)
        requeteTraitementNouvelleCandidature(conn, cur, result, liste_idSuperieur)
        #enregistrement des modifications dans la BDD
        conn.commit()
        #fermeture de la base de données 
        cur.close()
        conn.close()
    #renvoi du template (redirection par le nom de la fonction controleur de route)
    return redirect(url_for('candidature')) #redirection vers l'URL gérée par candidature 


#controleur de route / URL
@app.route('/reponses')
def reponses():
    "Controleur de la route '/reponses' "

    def requeteListeReponsesCandidatures(conn, cur, idEleve):
        #renommage nécessaire pour superieur.nom pour affichage dans reponses.html
        requete = """
                SELECT  idSuperieur, superieur.nom AS nomEtab, type, commune, idEleve, statut 
                    FROM (candidature  JOIN superieur USING(idSuperieur)) JOIN eleve USING(idEleve) 
                            WHERE idEleve = ?  ORDER BY statut;
                  """
        cur.execute(requete, (idEleve,))
        return  cur.fetchall()
        
    #connexion à la BDD
    conn = sqlite3.connect('monavenir.db')  
    conn.row_factory =  sqlite3.Row  #pour récupérer les lignes sous forme de dictionnaire         
    cur = conn.cursor()
    idEleve = session['user']['idEleve'] #on récupère l'idEleve dans le cookie de session
    #requete
    liste_reponses = requeteListeReponsesCandidatures(conn, cur, idEleve)
    #mise à jour du dictionnaire du cookie de session 
    session['liste_reponses'] = [dict(reponse) for reponse in liste_reponses]
    #fermeture de la base de données 
    cur.close()
    conn.close()
    #renvoi du template
    return render_template("reponses.html")


#controleur de route / URL
@app.route('/modifierReponses', methods = ['POST'])
def modifierReponses():
    "Controleur de la route '/modifierReponses' "

    def requeteAbandonCandidature(conn, cur, result, idSuperieur, idEleve):
        requete = """
                    UPDATE  candidature SET statut='abandonne' 
                        WHERE  idSuperieur = ? AND idEleve = ?;
                  """
        cur.execute(requete, (int(idSuperieur), int(idEleve)))
        #on enregistre
        conn.commit()

    def requeteMajListeAppel(conn, cur,  idSuperieur, idEleve):
        #on récupère les quotats de l'établissement concerné
        cur.execute("SELECT nbAdmis, nbAppel FROM superieur WHERE idSuperieur = ?;", (idSuperieur,))
        quotas = cur.fetchone()
        nbAdmis = int(quotas[0])
        nbAppel = int(quotas[1])
        #on récupère l'identifiant du premier de la liste d'attente et on change son statut
        requete1 = """
        SELECT candidature.idEleve AS idAttente, (note1 * coefNote1 + note2 * coefNote2)/(coefNote1 + coefNote2) AS moyenne
            FROM (superieur JOIN candidature USING(idSuperieur)) JOIN eleve USING(idEleve) 
                WHERE idSuperieur = ? AND statut = 'enAttente'
                    ORDER BY moyenne DESC 
                        LIMIT 1;
                """
        cur.execute(requete1, (idSuperieur,))
        idAttente = cur.fetchone()[0]
        requete2 = """
                  UPDATE candidature 
                    SET statut = 'admis' 
                        WHERE idSuperieur = ? AND idEleve = ? ;
                  """
        cur.execute(requete2, (idSuperieur,idAttente))
        #on enregistre
        conn.commit()    

    #analyse du formulaire
    if request.method == 'POST':        
        #ouverture du formulaire
        result = request.form
        #connexion à la BDD
        conn = sqlite3.connect('monavenir.db')           
        cur = conn.cursor()
        #Modification du staut d'une candidature (abandon)
        for name, value in result.items():
            #en fait les cases à cocher non cochées ne sont pas transmises voir https://developer.mozilla.org/fr/docs/Web/HTML/Element/input/checkbox
            #récupération des informations stockées dans les paramètres de chaque candidature formulaire
            idSuperieur, idEleve, statut = name.rstrip(')').lstrip('(').split(',')
            #mise à jour de la base avec le statut 'abandonne' pour les candidatures de cet élève
            requeteAbandonCandidature(conn, cur, result, idSuperieur, idEleve)
            #si pour cette candidature le statut de la candidature de l'élève était 'admis'
            if statut == 'admis':
                requeteMajListeAppel(conn, cur,  idSuperieur, idEleve)

        #fermeture de la BDD
        cur.close()
        conn.close()
        #renvoi du template
        return redirect(url_for('reponses')) #redirection vers l'URL gérée par reponses


#######################
### Profil admin   ####
#######################

#controleur de route / URL
@app.route('/statsEtabAvant')
def statsEtabAvant():
    return render_template("statsEtabAvant.html")


#controleur de route / URL
@app.route('/resultatStatsEtabAvant', methods = ['POST'])
def resultatStatsEtabAvant():
    "Controleur de la route '/resultatStatsEtabAvant' "

    def requeteNomEtab(conn, cur, idSuperieur):
        cur.execute("SELECT nom FROM superieur WHERE idSuperieur = ? ;", (idSuperieur,))
        return cur.fetchone()['nom']

    def requeteTotalCandidature(conn, cur, idSuperieur):
        cur.execute("SELECT COUNT(*) AS total FROM candidature WHERE idSuperieur = ? ;", (idSuperieur,))
        return int(cur.fetchone()['total'])

    def requeteSeuilAdmis(conn, cur, idSuperieur):
        requete = """
           SELECT min(m) AS seuil FROM (
	                SELECT (note1 * coefNote1 + note2 * coefNote2)/(coefNote1 + coefNote2) AS m
                        FROM (superieur JOIN candidature USING(idSuperieur)) JOIN eleve USING(idEleve) 
                             WHERE idSuperieur = ?
                                ORDER BY m DESC
                                    LIMIT (SELECT nbAdmis FROM superieur WHERE idSuperieur = ?)
                                );
            """
        cur.execute(requete, (idSuperieur,idSuperieur))
        return float(cur.fetchone()['seuil'])

    def requeteSeuilAttente(conn, cur, idSuperieur):
        requete = """
            SELECT min(m) AS seuil FROM (
	                SELECT (note1 * coefNote1 + note2 * coefNote2)/(coefNote1 + coefNote2) AS m
                        FROM (superieur JOIN candidature USING(idSuperieur)) JOIN eleve USING(idEleve) 
                             WHERE idSuperieur = ?
                                ORDER BY m DESC
                                    LIMIT (SELECT nbAppel FROM superieur WHERE idSuperieur = ?)
                                );
            """
        cur.execute(requete, (idSuperieur,idSuperieur))
        return float(cur.fetchone()['seuil'])
    
    def requeteListeCandidatureLycee(conn, cur, idSuperieur):
        requete = """
            SELECT COUNT(*) AS nb, lycee.nom AS nom
                FROM (candidature JOIN eleve USING(idEleve)) JOIN lycee USING(idLycee)
                    WHERE idSuperieur = ? 
                        GROUP BY idLycee
                            ORDER BY nb DESC ;
            """
        cur.execute(requete, (idSuperieur,))
        return cur.fetchall()

    #analyse du formulaire
    if request.method == 'POST':   
        #ouverture du formulaire
        result = request.form
        idSuperieur = result['idSuperieur']
        #ouverture de la BDD
        conn = sqlite3.connect('monavenir.db')  
        conn.row_factory =  sqlite3.Row  #pour récupérer les lignes sous forme de dictionnaire           
        cur = conn.cursor()
        #requete sur le nom de l'établissement
        nom = requeteNomEtab(conn, cur, idSuperieur)
        #initialisation du dictionnaire de statistiques
        stats = dict()
        stats['nom'] = nom
        #on peuple stats avec les résultats des requetes, une  par paramètre transmis par le formulaire
        if 'total' in result:            
            stats['total'] = requeteTotalCandidature(conn, cur, idSuperieur)
        if 'seuilAdmis'  in result:
            stats['seuilAdmis'] = requeteSeuilAdmis(conn, cur, idSuperieur)
        if 'seuilAttente'  in result:            
            stats['seuilAttente'] = requeteSeuilAttente(conn, cur, idSuperieur)
        if 'candidLycee'  in result:
            stats['candidLycee'] = requeteListeCandidatureLycee(conn, cur, idSuperieur)
        #fermeture de la BDD
        cur.close()
        conn.close()
        #renvoi du template
        return render_template("resultatStatsEtabAvant.html", stats = stats)



#controleur de route / URL
@app.route('/statsGeneralAvant')
def statsGeneralAvant():
    return render_template("statsGeneralAvant.html")

#controleur de route / URL
@app.route('/resultatStatsGeneralAvant', methods = ['POST'])
def resultatStatsGeneralAvant():
    "Controleur de la route '/resultatStatsGeneralAvant' "

    def requeteNombreCandidatureParEtab(conn, cur):
        requete = """
           SELECT nom, COUNT(*) AS nb
                FROM superieur JOIN candidature USING(idSuperieur)
                    GROUP BY idSuperieur
                        ORDER BY nb ASC;
            """
        cur.execute(requete)
        return cur.fetchall()

    def requeteEtabAvecSousAppel(conn, cur):
        requete = """
            SELECT nom, COUNT(*) AS  nb, nbAppel
                FROM superieur JOIN candidature USING(idSuperieur)
                    GROUP BY idSuperieur
                        HAVING COUNT(*) < nbAppel;
            """
        cur.execute(requete)
        return cur.fetchall()

    def requeteMoyParEtab(conn, cur):
        requete = """
            SELECT superieur.nom AS nomEtab, ROUND(SUM((note1 * coefNote1 + note2 * coefNote2)/(coefNote1 + coefNote2))/COUNT(*), 2) AS moyEtab 
                FROM (superieur JOIN candidature USING(idSuperieur)) JOIN eleve USING(idEleve)
                    GROUP BY idSuperieur
                        ORDER BY moyEtab DESC;
            """
        cur.execute(requete)
        return cur.fetchall()

    def requeteNbMoyenCandidatures(conn, cur):
        requete = """
            SELECT  COUNT(*) / COUNT(DISTINCT idEleve) AS moyVoeux
                FROM candidature;
            """
        cur.execute(requete)
        return int(cur.fetchone()['moyVoeux'])
    
    def requeteListeEtabMaxCandidatures(conn, cur):
        requete = """
            SELECT nom, COUNT(*) AS nb
                FROM superieur JOIN candidature USING(idSuperieur)
                    GROUP BY idSuperieur
                        HAVING nb = (SELECT MAX(nb) 
                                        FROM (SELECT COUNT(*) AS nb
                                                FROM superieur JOIN candidature USING(idSuperieur)
                                                    GROUP BY idSuperieur)
                                    );
            """
        cur.execute(requete)
        return cur.fetchall()

    #analyse du formulaire
    if request.method == 'POST':   
        #ouverture du formulaire
        result = request.form
        #ouverture de la BDD
        conn = sqlite3.connect('monavenir.db')  
        conn.row_factory =  sqlite3.Row  #pour récupérer les lignes sous forme de dictionnaire           
        cur = conn.cursor()
        #initialisation du dictionnaire conteneur de stats
        stats = dict()
        if 'totalEtab' in result:            
            stats['totalEtab'] = requeteNombreCandidatureParEtab(conn, cur)
        if 'sousAppel'  in result:            
            stats['sousAppel'] = requeteEtabAvecSousAppel(conn, cur)
        if 'moyEtab'  in result:            
            stats['moyEtab'] = requeteMoyParEtab(conn, cur)
        if 'moyVoeux' in result:            
            stats['moyVoeux'] = requeteNbMoyenCandidatures(conn, cur)    
        if 'maxCandid'  in result:            
            stats['maxCandid'] = requeteListeEtabMaxCandidatures(conn, cur)
        #fermeture de la BDD
        cur.close()
        conn.close()
        return render_template('resultatStatsGeneralAvant.html', stats = stats)


#controleur de route / URL
@app.route('/classement')
def classement():
    """Fonction de classement des candidatures
    Temps d'exécution long ! 
    """
    conn = sqlite3.connect('monavenir.db')        
    cur = conn.cursor()
    #on récupère tous les idSuperieur des établissements du supérieur
    cur.execute("SELECT idSuperieur FROM superieur ;")
    #pour chaque établissement
    liste_idSuperieur = cur.fetchall()
    #ici on a récupéré une liste de tuple
    requeteClassement = """
        SELECT candidature.idEleve AS idAttente, (note1 * coefNote1 + note2 * coefNote2)/(coefNote1 + coefNote2) AS moyenne
            FROM (superieur JOIN candidature USING(idSuperieur)) JOIN eleve USING(idEleve) 
                WHERE idSuperieur = ?
                    ORDER BY moyenne DESC
                        LIMIT  ? ;
            """
    for etab in liste_idSuperieur:        
        idSuperieur = int(etab[0])
        #on récupère les quotas d'admis et de file d'attente
        cur.execute("SELECT nbAdmis, nbAppel FROM superieur WHERE idSuperieur = ?;", (idSuperieur,))
        quotas = cur.fetchone()
        nbAdmis = int(quotas[0])
        nbAppel = int(quotas[1])
        #on fixe le statut des en attente        
        cur.execute(requeteClassement, (idSuperieur,  nbAppel))
        liste_attente = cur.fetchall()
        #on fixe le statut des candidats dans la liste d'appel
        for k in range(nbAppel):
            if k < nbAdmis: 
                cur.execute("UPDATE candidature SET statut = 'admis' WHERE idEleve = ? AND idSuperieur = ? ;", (liste_attente[k][0],idSuperieur))
            else:
                cur.execute("UPDATE candidature SET statut = 'enAttente' WHERE idEleve = ? AND idSuperieur = ? ;", (liste_attente[k][0],idSuperieur))
        #on enregistre les modifs précédentes
        conn.commit()
        #enfin on fixe le statut des refusés
        cur.execute("UPDATE candidature SET statut = 'refuse' WHERE idSuperieur = ? AND statut = 'nonTraite';", (idSuperieur,))
        #on enregistre 
        conn.commit()
    return redirect(url_for('interface')) #redirection vers l'URL gérée par interface


#######################
### Profil superieur####
#######################


#controleur de route / URL
@app.route('/appel')
def appel():
    return render_template("appel.html")


#controleur de route / URL
@app.route('/resultatAppel', methods = ['POST'])
def resultatAppel():
    "Controleur de la route '/resultatAppel' "

    def requeteListeAppelClasse(conn, cur, result):
        values = (session['user']['idSuperieur'],) + tuple([champ for champ in result])
        if len(values) == 2:
            values = values + (values[1],)
        requete = """
                SELECT statut, eleve.nom AS nomCandidat, eleve.prenom AS prenomCandidat, lycee.nom AS nomLycee, (note1 * coefNote1 + note2 * coefNote2)/(coefNote1 + coefNote2) AS moyenne
                     FROM ((superieur JOIN candidature USING(idSuperieur)) JOIN eleve USING(idEleve)) JOIN lycee USING(idLycee)
                         WHERE idSuperieur = ?  AND statut IN (?, ?)
                          ORDER BY moyenne DESC ;
                 """
        cur.execute(requete, values)
        return cur.fetchall()

    #analyse du formulaire    
    if request.method == 'POST':   
        #ouverture du formulaire      
        result = request.form
        #ouverture de la BDD
        conn = sqlite3.connect('monavenir.db')  
        conn.row_factory =  sqlite3.Row  #pour récupérer les lignes sous forme de dictionnaire           
        cur = conn.cursor()
        #requete       
        liste_appel = requeteListeAppelClasse(conn, cur, result)
        #fermeture de la BDD
        cur.close()
        conn.close()
        return render_template("resultatAppel.html", liste_appel = liste_appel)


#######################
### Profil lycee   ####
#######################


#controleur de route / URL
@app.route('/listeEleveEtab', methods = ['POST'])

#controleur de route / URL
@app.route('/listeEleveEtab')
def listeEleveEtab():
    return render_template("listeEleveEtab.html")


#controleur de route / URL
@app.route('/resultatListeEleveEtab', methods = ['POST'])
def resultatListeEleveEtab():
    "Controleur de la route '/resultatListeEleveEtab'"

    def requeteTriListeEleve(conn, cur, idLycee, result):
        if result['tri'] == 'moyenne':
            requete = """
                SELECT superieur.nom As nomEtab, idEleve, eleve.nom AS nomEleve, eleve.prenom AS prenomEleve,  (note1 * coefNote1 + note2 * coefNote2)/(coefNote1 + coefNote2) AS moyenne
                     FROM ((superieur JOIN candidature USING(idSuperieur)) JOIN eleve USING(idEleve)) JOIN lycee USING(idLycee)
                         WHERE idLycee = ?  
                                ORDER BY nomEleve, moyenne DESC ;
                 """
        #tri selon le nombre de candidatures
        else:
            requete = """
                SELECT idEleve, eleve.nom AS nomEleve, eleve.prenom AS prenomEleve, COUNT(*) AS nbCandid
                     FROM (candidature  JOIN eleve USING(idEleve)) JOIN lycee USING(idLycee)
                         WHERE idLycee = ?  
                            GROUP BY idEleve
                                ORDER BY nbCandid DESC ;
                 """
        cur.execute(requete, (idLycee,))
        return cur.fetchall()

    #analyse du formulaire
    if request.method == 'POST':
        #ouverture du formulaire  
        result = request.form
        #ouverture de la BDD
        conn = sqlite3.connect('monavenir.db')  
        conn.row_factory =  sqlite3.Row  #pour récupérer les lignes sous forme de dictionnaire           
        cur = conn.cursor()
        #récupération de l'idLycee dans le dictionnaire de session
        idLycee = session['user']['idLycee']
        #requete        
        liste_eleve = requeteTriListeEleve(conn, cur, idLycee, result)     
        #fermeture de la BDD
        cur.close()
        conn.close()
        return render_template("resultatListeEleveEtab.html", liste_eleve = liste_eleve)



#controleur de route / URL
@app.route('/listeCandidatureEleveEtab')
def listeCandidatureEleveEtab():
    return render_template("listeCandidatureEleveEtab.html")


#controleur de route / URL
@app.route('/resultatCandidatureListeEleveEtab', methods = ['POST'])
def resultatCandidatureListeEleveEtab():
    
    def requeteListeCandidatureEleve(conn, cur, result,  idLycee):
        requete = """
            SELECT idEleve, eleve.nom AS nomEleve, eleve.prenom AS prenomEleve, superieur.nom AS nomEtab,  type, statut
                    FROM ((superieur JOIN candidature USING(idSuperieur)) JOIN eleve USING(idEleve)) JOIN lycee USING(idLycee)
                        WHERE idLycee = ?  AND idEleve = ?
                            ORDER BY {};
                """.format(result['tri'])  #on ne peut passer de valeur avec le pattern ? pour un ORDER BY
        cur.execute(requete, (idLycee, result['idEleve']))
        return cur.fetchall()  

    #analyse du formulaire
    if request.method == 'POST':  
        #ouverture du formulaire
        result = request.form
        #ouverture de la BDD
        conn = sqlite3.connect('monavenir.db')  
        conn.row_factory =  sqlite3.Row  #pour récupérer les lignes sous forme de dictionnaire           
        cur = conn.cursor()
        #récupération de l'idLycee dans le dictionnaire de session
        idLycee = session['user']['idLycee']
        liste_candid = requeteListeCandidatureEleve(conn, cur, result,  idLycee)    
        #fermeture de la BDD
        cur.close()
        conn.close()
        return render_template("resultatCandidatureListeEleveEtab.html", liste_candid = liste_candid)



###########################
### Lancement Serveur  ####
###########################

#Le serveur est lancé uniquement si le script est appelé exécuté directement
#Si le script est importé dans un autre  programme, on suppose qu'un autre serveur est exécuté
if __name__ == "__main__":
  # on ouvre un serveur en local sur le port 8000
  app.run(debug = True, host='127.0.0.1', port=8000)
