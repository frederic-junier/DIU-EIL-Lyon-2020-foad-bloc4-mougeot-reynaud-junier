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
        print(profil, user)
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
