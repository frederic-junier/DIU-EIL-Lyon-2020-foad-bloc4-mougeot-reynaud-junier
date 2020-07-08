DROP TABLE  IF EXISTS admin;
DROP TABLE  IF EXISTS lycee;
DROP TABLE  IF EXISTS superieur;
DROP TABLE  IF EXISTS eleve;
DROP TABLE  IF EXISTS candidature;

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



 

