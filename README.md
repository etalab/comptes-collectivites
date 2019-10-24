# Données de comptes des collectivités

Scripts d'extraction et de remise en forme des données des comptes des collectivités.

Les données extraites sont disponibles sur http://data.cquest.org/dgfip_comptes_collectivites/


## batch_complet.sh

Script global de traitement, qui appelle les autres scripts dans l'ordre.


## download.py

Ce script python parcoure la hiérarchie d'un département afin de télécharger les fichiers .ods pour chaque année et chaque commune.

Il s'occupe de maintenir un contexte cohérent pour l'application distante (cookie + "flowKey" à passer en paramètre de chaque requête).


## ods2json.py

Ce script python extrait les données principales depuis les fichiers .ods pour les remettre sous forme de fichiers CSV ou json.

Il décompresse (unzip) le fichier .ods qui est un dossier contenant plusieurs fichiers xml dont **content.xml**

content.xml est ensuite parsé à l'aide de **lxml** pour extraire le contenu des cellules dans un tableau 2D ensuite utilisé pour générer une ligne de CSV ou de json.


## ods2json_batch.sh

Conversion de l'ensemble des fichiers .ods d'une année en un fichier .csv unique.


## Citation

Certains scripts utilise GNU Parallel:
  O. Tange (2011): GNU Parallel - The Command-Line Power Tool, 
  ;login: The USENIX Magazine, February 2011:42-47.
  http://www.gnu.org/s/parallel

