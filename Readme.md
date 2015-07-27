sudo -E add-apt-repository ppa:ubuntugis/ubuntugis-unstable

sudo apt-get update

sudo apt-get install qgis

* QGIS > 2.8 nÃ©cessaire
* python 2.7

* Installation possible par le package OSGeo qui intègre QGIS + python

#### Installation
* installer pyQT4 (PyQT4-dev sous linux)
* installer le module geoalchemy (utile pour les ORM qui gèrent la base de données sqlite) et sphinx pour la doc autogénérée
    * **Windows:**
        * installation avec pip : tÃ©lÃ©charger get-pip.py (https://bootstrap.pypa.io/get-pip.py) ou easy_install
		* **Pour installer geoalchemy et sphinx **, lancer cmd 'make install_lib' ou :
        	* cmd 'pip install geoalchemy' ou 'easy_install geoalchemy'
        	**ATTENTION : il faut une version 32 bit de python pour geoalchemy, ça semble ne pas fonctionner sinon**
        	* il faut ensuite rétrograder sqlalchemy (https://github.com/geoalchemy/geoalchemy2/issues/88) à la version 0.8.4 : 'pip install sqlalchemy==0.8.4'
			* de la même manière installer sphinx (pip install sphinx ou easy_install sphinx)
* cmd 'make deploy' dans le rÃ©pertoire OutilNomade
* cmd make doc pour générer la doc sphinx
* cmd make db pour créer la base de données sqlite vide : ceci évite qu'elle soit créée pendant l'utilisation du plugin car c'est un peu long... Lors de l'utilisation du plugin, la création d'une nouvelle base carhab ne fait qu'une simple copie. Pour modifier la structure de la BD, modifier le script db_script.sql dans le répertoire db puis lancer 'make db'.

#### Environnement de dev
* Plugin eclipse 'pydev' : http://pydev.org/updates

#### Gestion des mises Ã  jour dans le repository
Lorsqu'une release est prÃªte:

* Modifier la version dans metadata.txt
* GÃ©nÃ©rer SaisieCarhab.zip dans le rÃ©pertoire de dÃ©pÃ´t avec la commande 'make zip'
* Remplacer SaisieCarhab.zip dans le repository par celui gÃ©nÃ©rÃ© prÃ©cÃ©damment
* Modifier la version dans le fichier SaisieCarhab.xml du repository publie la mise Ã  jour. Renseigner dans ce mÃªme fichier les infos de mise Ã  jour.