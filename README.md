# The FreeCAD Ader Workbench

![L'Avion](/doc/resources/avion_ader.png)

Cet atelier comprend des outils pour faciliter le dessin d'un avion.  
AVERTISSEMENT : atelier en cours de développement, usage uniquement expérimental.  

## Prerequisites
* FreeCAD >= v 1.0.0  


## Installation
Copier le dossier Ader dans le dossier des add-ons et relancer FreeCAD.  
Nota : sous Windows les addons sont dans %AppData%\FreeCAD\Mod  

## Quickstart
Cliquez sur le bouton "Nouveau" pour créer un nouvel avion. Donnez un nom à votre projet, indiquez les longueur, largeur et hauteur du fuselage.  En option un nom de fichier CPACS, voir remarque ci-dessous
Ader créé deux esquisses, vue de face et vue de haut, pour le fuselage et une feuille de spécifications pou les caractéristiques de votre projet  

## Usage
### Construction du fuselage
Modifiez les esquisses vue de face et de haut du fuselage. Utilisez la fonction "Sections" pour créer des plans de coupe du fuselage. Positionnez ces plans (clic droit > Transformer) puis utilisez la fonction "Cadres" pour avoir des couples ajustés dans le plan respectif, cadre qu'on peut retravailler? Construire le fuselage avec la fonction lissage.  

### Construction aile / empennage
Remplissez la fiche de spécifications :  
![Specs](/doc/resources/ader_spec.png)  
Pour les profils donnez le nom du fichier dat. Les fichers .dat, compilés par l'UUIC (https://m-selig.ae.illinois.edu/ads/coord_database.html), sont dans le répertoire dat_profiles de l'atelier.  

Cliquez sur le bouton "Construire" pour construire obtenir l'aile et l'empennage.  
![Build](/doc/resources/ader_build.png)  
  
Après construction tous les profils et cadres sont modifiables par le sketcher.  
Vous pouvez aussi ajouter des profils, cadres, nacelles (formes de moindre traînée https://fr.wikipedia.org/wiki/Corps_de_moindre_tra%C3%AEn%C3%A9e).  


Une documentation utilisateur est disponible dans le dossier doc de l'atelier.  

Cet atelier se nomme Ader en hommage à Clément Ader, pionnier de l'aviation. En souhaitant qu'il ait une suite aussi riche que l'aviation depuis M. Ader.  
![Ader-Clement](/doc/resources/clement_ader_1891.png)  

Si vous vous intéressez à la conception avion, l'adhésion à l'association Inter-Action http://inter-action-aero.fr/ est fortement recommandée !

## Feedback


## Roadmap
Le développement des fonctions de base se fait en fonction de mon temps disponible pour ce projet.
Si vous souhaitez participer au projet vous êtes les bienvenus.
Une documentation programmeur est disponible dans le dossier doc de l'atelier.  
Nota : à l'origine il était prévu de permettre l'échange de fichier à la norme CPACS (https://cpacs.de/) qui décrit un avion (et plus) sous forme d'un fichier xml. Un début de code a été écrit, à compléter par un volontaire.  
 

## Release Notes


## License
MIT
See [LICENSE](LICENSE) file

#Illustrations 
Wikipedia Creative Commons.
