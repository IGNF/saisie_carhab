sudo -E add-apt-repository ppa:ubuntugis/ubuntugis-unstable

sudo apt-get update

sudo apt-get install qgis

* QGIS > 2.8 nécessaire
* python 2.7

#### Installation
* installer pyQT4 (PyQT4-dev sous linux)
* cmd 'make deploy' dans le répertoire OutilNomade
* cmd make doc pour générer la doc sphinx
* cmd make db pour créer la base de données sqlite vide : ceci évite qu'elle soit créée pendant l'utilisation du plugin car c'est un peu long... Lors de l'utilisation du plugin, la création d'une nouvelle base carhab ne fait qu'une simple copie. Pour modifier la structure de la BD, modifier le script db_script.sql dans le répertoire db puis lancer 'make db'.

#### Environnement de dev
* Plugin eclipse 'pydev' : http://pydev.org/updates

#### Gestion des mises à  jour dans le repository
Lorsqu'une release est prête:

* Modifier la version dans metadata.txt
* Générer SaisieCarhab.zip dans le répertoire de dépôt avec la commande 'make zip'
* Remplacer SaisieCarhab.zip dans le repository par celui généré précédamment
* Modifier la version dans le fichier SaisieCarhab.xml du repository publie la mise Ã  jour. Renseigner dans ce mÃªme fichier les infos de mise Ã  jour.