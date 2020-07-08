from flask import *  #module pour développer une application web
import sqlite3       #module pour interagir avec une base de données sqlite

#création d'une instance de l'application
app = Flask(__name__)


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
            return render_template("{}.html".format(profil), user = user)


# on ouvre un serveur en local sur le port 8000
app.run(debug = True, host='127.0.0.1', port=8000)