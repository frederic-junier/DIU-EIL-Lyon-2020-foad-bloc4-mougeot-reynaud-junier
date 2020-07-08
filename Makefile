.PHONY : fresh clean all

all:
	[ ! -d "csv" ] && mkdir csv || echo "dossier csv deja créé"
	python3 generer_base_csv.py
	python3 peupler_base_bd.py    

clean:
	rm  -r csv

fresh: clean all