
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


