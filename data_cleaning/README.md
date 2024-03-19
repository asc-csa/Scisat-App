
- [Français](#application-pour-convertir-les-données-de-scisat)
- [English](#application-to-convert-scisat-data)

# Application pour convertir les données de SCISAT

## Contexte

Le satellite SCISAT, en orbite depuis le 12 août 2003, aide des équipes de scientifiques canadiens et internationaux à améliorer leur compréhension de la déplétion de la couche d'ozone, en se concentrant particulièrement sur les changements au Canada et en Arctique. 

Vous pouvez accéder à cette micro application en direct au https://donnees-data.asc-csa.gc.ca/scisat-fr. 

## Exécution
Les commandes suivantes peuvent être exécutées plus facilement dans un environnement virtuel (comme conda). Il peut donc être judicieux d'installer [Anaconda](https://www.anaconda.com/distribution/) au préalable.

Pour démarrer l'application :
- Créer un dossier nommé "data" et y mettre les fichiers .nc des données de SCISAT
>- Ces fichiers sont accessibles en suivant ce [lien](https://databace.scisat.ca/) vers l'accès aux données de niveau 2 de la mission ACE/SCISAT. Vous devrez remplir un formulaire décrivant votre demande de données, après quoi un courriel vous sera envoyé avec le lien vers les fichiers. Les fichiers à télécharger et à placer dans le dossier /data doivent avoir la convention de nommage suivante : 

>>>>>>ACEFTS_L2_v4p1\__FormuleChimiqueDuGaz_.nc

- Ajouter le fichier "config.cfg" que vous retrouverez sur [Livelink](http://livelink/livelink/llisapi.dll?func=ll&objId=36908608&objAction=browse&viewType=1) dans le même dossier que scisat.py
- D'abord, vous devrez créer un environment virtuel avec conda:
```
        pip install conda
        conda create -name venv
        conda activate venv
```
- Puis, dans l'[application dash](https://github.com/Camille-Jonathan-asc-csa/Scisat-App)
        
        pip install -r requirements.txt
        conda install -v venv -c conda-forge --file requirements.txt
        python scisat.py

Lors de l'exécution, l'[application](http://127.0.0.1:8888/scisat/) se trouve à cet endroit.

## Auteurs
 - Emiline Filion
 - Camille Roy
 
## Remerciements
 - Natasha Fee
 - Etienne Low-Decarie



# Application to convert SCISAT data

## Background

Launched on August 12, 2003, SCISAT helps a team of Canadian and international scientists improve their understanding of the depletion of the ozone layer, 
 with a special emphasis on the changes occurring over Canada and in the Arctic.

This project is an application that allows users to filter through the SCISAT data on
 multiple parameters and allows users to visualize a summary of the data from their selected parameters on a
 world map, a graph on the altitude, a time series, forgoing the need for downloading the data for simple insights. 

This project has been developped from the Alouette app, a case study for the development of future satellite data applications so that the data from
 from these satellites are able to be obtained and analyzed at a larger scale and in a more user-friendly way.

The live version of this micro application is available at https://donnees-data.asc-csa.gc.ca/scisat.

## Execution

The following commands can be done more easily if in a virtual environment (like conda) so it may be a good idea to install [Anaconda](https://www.anaconda.com/distribution/) beforehand. 

For starting the application:
- Create a folder named "data" and put the .nc files containing the SCISAT data
>- These files can be accessed by following this [link](https://databace.scisat.ca/) to the Level 2 data access of the ACE/SCISAT mission. You will need to complete a form describing your data request after which an email will be sent to you with the link to the files. The files to download and place in the /data folder should have the following naming convention: 

>>>>>>ACEFTS_L2_v4p1\__ChemicalFormulaOfGas_.nc

- Add the "config.cfg" file (found on [Livelink](http://livelink/livelink/llisapi.dll?func=ll&objId=36908608&objAction=browse&viewType=1)) in the folder where "scisat.py" is.
- First, you will have to create a conda virtual environment:
```
        pip install conda
        conda create -name venv
        conda activate venv
```
- Then, go to the [Dash application](https://github.com/Camille-Jonathan-asc-csa/Scisat-App)
        
        pip install -r requirements.txt
        conda -v venv -c conda-forge --file requirements.txt
        python scisat.py

The URL is [http://127.0.0.1:8888/scisat/)](http://127.0.0.1:8888/scisat/). Separate installation instructions for the production version of the app are provided in "SCISAT Production Installation Guide.docx".

## Authors
 - Emiline Filion
 - Camille Roy
 
## Acknowledgments
 - Natasha Fee
 - Etienne Low-Decarie
