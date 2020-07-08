from flask import *

import sqlite3


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

##################################
### Atelier 1 eleve            ###
##################################

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

###################################
### Atelier 2 eleve (niveau 2)  ###
###################################

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
        #on met à jour le statut de la candidature de cet élève
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



###########################
### Lancement Serveur  ####
###########################

#si le programme n'est pas importé dans un autre script Python
if __name__ == "__main__":
  # on ouvre un serveur en local sur le port 8000
  app.run(debug = True, host='127.0.0.1', port=5000)

