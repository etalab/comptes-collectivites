# Données de comptes des collectivités

Scripts d'extraction et de remise en forme des données des comptes des collectivités.

Les données sont temporairement disponibles sur http://data.cquest.org/dgfip_comptes_collectivites/ afin d'obtenir un retour des ré-utilisateurs potentiels avant finalisation des scripts et publication officielle.


## download.py

Ce script python parcoure la hiérarchie d'un département afin de télécharger les fichiers .ods pour chaque année et chaque commune.

Il s'occupe de maintenir un contexte cohérent pour l'application distante (cookie + "flowKey" à passer en paramètre de chaque requête).


## ods2json.py

Ce script python extrait les données principales depuis les fichiers .ods pour les remettre sous forme de fichiers CSV ou json.

Il décompresse (unzip) le fichier .ods qui est un dossier contenant plusieurs fichiers xml dont **content.xml**

content.xml est ensuite parsé à l'aide de **lxml** pour extraire le contenu des cellules dans un tableau 2D ensuite utilisé pour générer une ligne de CSV ou de json.
