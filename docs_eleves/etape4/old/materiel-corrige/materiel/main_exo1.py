from flask import *  #module pour développer une application web
import sqlite3       #module pour interagir avec une base de données sqlite
import datetime      #module de gestion des dates

#création d'une instance de l'application
app = Flask(__name__)
#clef de session
app.secret_key = "clef secrète"

@app.route('/')
def accueil():
    "Controleur de la  route '/'"
    date = datetime.datetime.now()
    h = date.hour
    m = date.minute
    s = date.second
    return render_template("accueil1.html",  heure = h, minute = m, seconde = s)



# on ouvre un serveur en local sur le port 8000
app.run(debug = True, host='127.0.0.1', port=8000)
