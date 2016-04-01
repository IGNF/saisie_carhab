sudo -E add-apt-repository ppa:ubuntugis/ubuntugis-unstable

sudo apt-get update

sudo apt-get install qgis

* QGIS > 2.8 n�cessaire
* python 2.7

#### Installation
* installer pyQT4 (PyQT4-dev sous linux)
* cmd 'make deploy' dans le r�pertoire OutilNomade
* cmd make doc pour g�n�rer la doc sphinx
* cmd make db pour cr�er la base de donn�es sqlite vide : ceci �vite qu'elle soit cr��e pendant l'utilisation du plugin car c'est un peu long... Lors de l'utilisation du plugin, la cr�ation d'une nouvelle base carhab ne fait qu'une simple copie. Pour modifier la structure de la BD, modifier le script db_script.sql dans le r�pertoire db puis lancer 'make db'.

#### Environnement de dev
* Plugin eclipse 'pydev' : http://pydev.org/updates

#### Gestion des mises � jour dans le repository
Lorsqu'une release est pr�te:

* Modifier la version dans metadata.txt
* G�n�rer SaisieCarhab.zip dans le r�pertoire de d�p�t avec la commande 'make zip'
* Remplacer SaisieCarhab.zip dans le repository par celui g�n�r� pr�c�damment
* Modifier la version dans le fichier SaisieCarhab.xml du repository publie la mise à jour. Renseigner dans ce même fichier les infos de mise à jour.