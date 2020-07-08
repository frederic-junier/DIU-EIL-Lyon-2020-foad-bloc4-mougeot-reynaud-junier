# foad-bloc4-mougeot-reynaud-junier


## De quoi s'agit-il ?

- FOAD bloc 4 pour le DIU-EIL de Lyon 2019/2020
- Trinôme composé de Brigitte Mougeot, Véronique Reynaud et Frédéric Junier
- Code : BD4
- Thème : Base de données

## Descriptif

* __Objectif :__ 
    * créer un mini Parcoursup application web destinée à recueillir et gérer les vœux d'affectation de lycéens du Rhône  pour un établissement de l'enseignement supérieur dans le Rhône.
* __Liens :__
    *   [tous les fichiers nécessaires pour l'application](https://gitlab.com/frederic-junier/foad-bloc4-mougeot-reynaud-junier/-/tree/master/)        
    *   [Le document de synthèse de l'activité MonAvenir.pdf](docs_eleves/)
    *   [Les documents élèves pour l'étape 4](docs_eleves/etape4)
    *   [Les documents élèves pour l'étape 6](docs_eleves/etape6)


## Mode d'emploi 

Notre projet `monavenir` est constitué des fichiers suivants :

* Un script SQL  `creer_base_mona-avenir.sql` qui va créer les différentes tables de la base dont le scéham est donné ci-dessous :

```sql
    sqlite> .open monavenir.db
    sqlite> .schema
    CREATE TABLE admin(
        idAdmin INT PRIMARY KEY,  
        login TEXT  UNIQUE NOT NULL, 
        password TEXT NOT NULL,
        nom TEXT NOT NULL,
        prenom TEXT NOT NULL
    );
    CREATE TABLE lycee(
        idLycee INT PRIMARY KEY,  
        login TEXT UNIQUE NOT NULL, 
        password TEXT NOT NULL,
        nom TEXT NOT NULL,
        commune TEXT NOT NULL
    );
    CREATE TABLE superieur(
        idSuperieur INT PRIMARY KEY,  
        login TEXT UNIQUE NOT NULL, 
        password TEXT NOT NULL,
        nom TEXT NOT NULL,
        type TEXT,
        commune TEXT NOT NULL,
        latitude TEXT,
        longitude TEXT,
        nbAdmis INT NOT NULL CHECK(nbAdmis >= 0) DEFAULT 100,
        nbAppel INT NOT NULL CHECK(nbAppel >= 0)  DEFAULT 200,
        coefNote1 INT CHECK(0 <= coefNote1) DEFAULT 1,
        coefNote2 INT CHECK(0 <= coefNote2) DEFAULT 1,
        CHECK((0 < coefNote2 OR 0 < coefNote1) AND (nbAdmis <= nbAppel))
    );
    CREATE TABLE eleve(
        idEleve INT PRIMARY KEY,
        idLycee INT REFERENCES lycee(idLycee),
        login TEXT UNIQUE NOT NULL, 
        password TEXT NOT NULL,	
        nom TEXT NOT NULL,
        prenom TEXT NOT NULL,
        anneeNaissance INT NOT NULL,
        note1 FLOAT CHECK( 2 <= note1 <= 20 OR NULL),
        note2 FLOAT CHECK( 2 <= note2 <= 20 OR NULL)
    );
    CREATE TABLE candidature(
        idEleve INT NOT NULL REFERENCES eleve(idEleve),
        idSuperieur INT NOT NULL REFERENCES superieur(idSuperieur),
        statut TEXT CHECK (statut IN ('nonTraite', 'refuse', 'enAttente',  'admis', 'abandonne')) DEFAULT 'nonTraite',
        PRIMARY KEY(idEleve, idSuperieur)
    );
``` 



* Un script Python `peupler_base_csv.py` pour générer des fichiers csv dans un dossier `csv` avec les enregistrements qui vont peupler les différentes tables de la base. Certains éléments  (login ,password, noms d'élèves) sont générés aléatoirement avec le module `Faker`de Python, d'autres (noms des lycées, des établissements du supérieur, type d'établissements, coordonnées GPS) proviennent de deux fichiers en OpenData  : `superieur-rhone-data.csv` et `lycee-rhone-data.csv`. Seront créés dans un dossier `csv`:
  * un fichier élève par lycée peupler la table `eleve`
  * un fichier pour peupler la table `admin`
  * un fichier pour peupler la table `lycee`
  * un fichier pour peupler la table `superieur`


* Un script Python `peupler_base_bd.py` qui va exécuter le script SQL de création de la base puis va peupler ses différentes tables à partir des enregistrements stockés dans les fichiers csv. Le module Python `sqlite3` est utilisé.


* Un script   `main.py`  dont l'exécution lance un serveur HTTP et une interface Web de gestion de l'application. Le module Python `Flask` est utilisé. Tous les templates HTML nécessaires sont dans le dossier `templates`  et le dossier `static` pourra contenir les feuilles de style CSS.

* Pour construire la base de données, il faut exécuter dans l'ordre :
  * Première étape :le script `peupler_base_csv.py`  avec `python3 peupler_base_csv.py` ou `./peupler_base_csv.py`si le script a été rendu exécutable
  * Deuxième étape : le script  `peupler_base_bd.py`  ou `./peupler_base_bd.py` si le script a été rendu exécutable
  * Alternative : on peut utiliser le fichier Makefile avec la commande make : 
    * `make` ou `make all` effectuera toutes les actions nécessaires pour construire la base
    * `make clean` supprimera le dossier `csv` et la base `monavenir.db` 
    * `make fresh`  exécutera `make clean` puis `make all`

