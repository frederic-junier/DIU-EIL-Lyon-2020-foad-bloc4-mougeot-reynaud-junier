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
        ##### TO DO  requete SQL pour retrouver l'attribut nom d'un 
        ##### établissement du supérieur à partir de son identifiant idSuperieur
        requete = """ """
        return cur.fetchone()['nom']
 

    def requeteTotalCandidature(conn, cur, idSuperieur):
        ##### TO DO  requete SQL pour retrouver le nombre total de candidatures pour l'établissement
        ##### établissement du supérieur à partir de son identifiant idSuperieur
        requete = """ """
        return int(cur.fetchone()['total'])

    def requeteSeuilAdmis(conn, cur, idSuperieur):
        ##### TO DO  requete SQL pour calculer la moyenne du dernier admis de la liste d'appel 
        ##### renommage indispensable de cette moyenne avec le nom  'seuil'
        ##### Pour obtenir le nombre d'admis dans la liste d'appel :
        ##### "SELECT nbAdmis FROM superieur WHERE idSuperieur = ... "
        requete = """ """
        cur.execute(requete, (idSuperieur,idSuperieur))
        return float(cur.fetchone()['seuil'])
     

    def requeteSeuilAttente(conn, cur, idSuperieur):
        ##### TO DO  requete SQL pour calculer la moyenne du dernier en attente dans la liste d'appel
        ##### renommage indispensable de cette moyenne avec le nom  'seuil' 
        ##### Pour obtenir le nombre total (admis + en attente) dans la liste d'appel :
        ##### "SELECT nbAppel FROM superieur WHERE idSuperieur = ... ;"
        requete = """        """
        cur.execute(requete, (idSuperieur,idSuperieur))
        return float(cur.fetchone()['seuil'])
    
      
    def requeteListeCandidatureLycee(conn, cur, idSuperieur):
        ##### TO DO  requete SQL pour déterminer le nombre de candidatures 
        ##### pour un établissement du supérieur et par lycée 
        ##### renommage indispensable : nb pour le nombre et nom pour le nom du lycée 
        requete = """     """
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
        ##### TO DO  requete SQL pour déterminer le nombre de candidatures par établissement
        ##### Renommage obligatoire de ce nombre avec le nom 'nb'
        requete = """ """
        cur.execute(requete)
        return cur.fetchall()


    def requeteMoyParEtab(conn, cur):
        ##### TO DO  requete SQL pour déterminer le nombre de candidatures par établissement
        ##### Renommage obligatoire du nom de l'établissement en 'nomEtab'
        ##### Renommage obligatoire de la moyenne en 'moyEtab'
        requete = """   """
        cur.execute(requete)
        return cur.fetchall()



    def requeteNbMoyenCandidatures(conn, cur):
        ##### TO DO  requete SQL pour déterminer le nombre moyen  de candidatures par élève
        ##### Renommage obligatoire de la moyenne  en 'moyVoeux'
        requete = """  """
        cur.execute(requete)
        return int(cur.fetchone()['moyVoeux'])

    
    def requeteListeEtabMaxCandidatures(conn, cur):
        ##### TO DO  requete SQL pour déterminer la liste des établissements 
        ##### avec le nombre maximal de candidatures  
        requete = """   """        
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
#On désactive le classement dans ce fichier élève
#@app.route('/classement')
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




###########################
### Lancement Serveur  ####
###########################

#Le serveur est lancé uniquement si le script est appelé exécuté directement
#Si le script est importé dans un autre  programme, on suppose qu'un autre serveur est exécuté
if __name__ == "__main__":
  # on ouvre un serveur en local sur le port 8000
  app.run(debug = True, host='127.0.0.1', port=8000)
