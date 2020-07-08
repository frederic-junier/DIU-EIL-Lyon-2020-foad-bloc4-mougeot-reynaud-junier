from flask import *  #module pour développer une application web
import sqlite3       #module pour interagir avec une base de données sqlite

#création d'une instance de l'application
app = Flask(__name__)

#clef de session
app.secret_key = "clef secrète"

@app.route('/')
def accueil():
    "Controleur de la  route '/'"
    return render_template("accueil2.html")

#dispatcheur de route / URL
@app.route('/connexion',methods = ['POST'])
def connexion():
    "Controleur de la route '/connexion' "
    if request.method == 'POST':
        #les valeurs des paramètres sont dans le dictionnaire request.form 
        result = request.form
        #récupération de la valeur du paramètre profil
        profil = result['profil'] 
        #récupération de la valeur du paramètre login
        login = result['login']   
        #récupération de la valeur du paramètre password
        password = result['password']  
        #connexion à la base de données
        conn = sqlite3.connect('monavenir.db')     
        #pour récupérer les lignes sous forme de dictionnaire     
        conn.row_factory =  sqlite3.Row  
        #création d'un curseur pour parcourir la base
        cur = conn.cursor()
        #soumission d'une requête SQL avec paramètres
        cur.execute(f"SELECT * FROM {profil} WHERE login=? and password=? ;",(login, password))
        #récupération d'
        user = cur.fetchone()
        #fermeture du curseur
        cur.close()
        #fermeture de la connexion
        conn.close()
        if user:
            #dictionnaire de session
            session['user'] = dict(user)  #les objets de type ROW retournés ne sont pas sérialisables et stockables dans le dictionnaire du cookie de session  
            session['profil'] = profil    #on stocke le profil dans le cookie de session
            return render_template("{}.html".format(profil), user= user)        
    
#dispatcheur de route / URL
@app.route('/deconnexion')
def deconnexion():
    #on vide le dictionnaire de session
    print(session)     #debug
    session.clear()    #on vide le dictionnaire de session
    print(session)     #debug
    #redirection vers la route controlée par la fonction accueil
    #return render_template('/')
    return redirect(url_for('accueil'))

#dispatcheur de route / URL
@app.route('/interface')
def interface():
    "Controleur de la route '/interface' "
    if 'profil' in session and session['profil']:
        return render_template("{}.html".format(session['profil']))
    



#dispatcheur de route / URL
@app.route('/rechercheFormation')
def rechercheFormation():
    "Controleur de la route '/rechercheFormation' "
    conn = sqlite3.connect('monavenir.db')     
    conn.row_factory =  sqlite3.Row  #pour récupérer les lignes sous forme de dictionnaire     
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT type FROM superieur ;")
    list_type = cur.fetchall()
    cur.execute("SELECT DISTINCT commune FROM superieur ;")
    list_commune = cur.fetchall()
    conn.close()
    return render_template("rechercheFormation.html", list_type = list_type,  list_commune = list_commune)


#dispatcheur de route / URL
@app.route('/resultatRecherche', methods = ['POST'])
def resultatRecherche():
    "Controleur de la route '/resultatFRecherche' "
    if request.method == 'POST':
        result = request.form
        conn = sqlite3.connect('monavenir.db')     
        conn.row_factory =  sqlite3.Row  #pour récupérer les lignes sous forme de dictionnaire     
        cur = conn.cursor()
        if result['type'] == 'indifferent':
            if result['commune'] != 'indifferent':
                cur.execute('SELECT nom, idSuperieur, type, commune FROM superieur  WHERE commune = ?    ORDER BY type;', (result['commune'],))
            else:
                cur.execute('SELECT idSuperieur,nom, type, commune FROM superieur ORDER BY commune, type;')                
        elif result['commune'] == 'indifferent':
            cur.execute('SELECT idSuperieur,nom, type, commune FROM superieur WHERE type = ?  ORDER BY commune;',  (result['type'],))
        else:
            cur.execute('SELECT idSuperieur,nom, type, commune FROM superieur WHERE commune = ? and type = ?;', (result['commune'] , result['type']))
        liste_sup = cur.fetchall()
        conn.close()
        return render_template("resultatRecherche.html", liste_sup = liste_sup,  result = result)


# on ouvre un serveur en local sur le port 8000
app.run(debug = True, host='127.0.0.1', port=9000)
