sudo -E add-apt-repository ppa:ubuntugis/ubuntugis-unstable

sudo apt-get update

sudo apt-get install qgis

* QGIS > 2.8 nécessaire
* python 2.7

* Installation possible par le package OSGeo qui int�gre QGIS + python

#### Installation
* installer pyQT4 (PyQT4-dev sous linux)
* installer le module geoalchemy (utile pour les ORM qui g�rent la base de donn�es sqlite) et sphinx pour la doc autog�n�r�e
    * **Windows:**
        * installation avec pip : télécharger get-pip.py (https://bootstrap.pypa.io/get-pip.py) ou easy_install
		* **Pour installer geoalchemy et sphinx **, lancer cmd 'make install_lib' ou :
        	* cmd 'pip install geoalchemy' ou 'easy_install geoalchemy'
        	**ATTENTION : il faut une version 32 bit de python pour geoalchemy, �a semble ne pas fonctionner sinon**
        	* il faut ensuite r�trograder sqlalchemy (https://github.com/geoalchemy/geoalchemy2/issues/88) � la version 0.8.4 : 'pip install sqlalchemy==0.8.4'
			* de la m�me mani�re installer sphinx (pip install sphinx ou easy_install sphinx)
* cmd 'make deploy' dans le répertoire OutilNomade
* cmd make doc pour g�n�rer la doc sphinx
* cmd make db pour cr�er la base de donn�es sqlite vide : ceci �vite qu'elle soit cr��e pendant l'utilisation du plugin car c'est un peu long... Lors de l'utilisation du plugin, la cr�ation d'une nouvelle base carhab ne fait qu'une simple copie. Pour modifier la structure de la BD, modifier le script db_script.sql dans le r�pertoire db puis lancer 'make db'.

#### Environnement de dev
* Plugin eclipse 'pydev' : http://pydev.org/updates

#### Gestion des mises à jour dans le repository
Lorsqu'une release est prête:

* Modifier la version dans metadata.txt
* Générer SaisieCarhab.zip dans le répertoire de dépôt avec la commande 'make zip'
* Remplacer SaisieCarhab.zip dans le repository par celui généré précédamment
* Modifier la version dans le fichier SaisieCarhab.xml du repository publie la mise à jour. Renseigner dans ce même fichier les infos de mise à jour.