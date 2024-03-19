
- [Français](#application-pour-convertir-les-données-de-scisat)
- [English](#application-to-convert-scisat-data)

# Application pour convertir les données de SCISAT

## Contexte

Les données originales du satellite SCISAT sont dans le format NetCDF (NC). Ce format binaire est employé par la micro-application SCISAT. Le Portail des données ouvertes de l’Agence spatiale canadienne (ASC) contient aussi les jeux de données. Toutefois, ceux-ci sont dans le format CSV. Par conséquent, les données SCISAT doivent être converties du format NC au format CSV avant d’être publiées dans le portail des données ouvertes à l’aide de ce script. 

- Vous pouvez accéder à cette micro application en direct au https://donnees-data.asc-csa.gc.ca/scisat-fr. 
- Vous pouvez accéder au portail des données ouvertes au https://donnees-data.asc-csa.gc.ca/fr/dataset/02969436-8c0b-4e6e-ad40-781cdb43cf24. 

## Quand exécuter ce script?

Ce script doit être lancé chaque fois qu’une nouvelle version des données du satellite SCISAT est publiée.

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

The original SCISAT data is in NetCDF (NC) format. The SCISAT micro-application use this binary format directly. The Canadian Space Agency (CSA) Open Data Portal also contains SCISAT data. However, this one is in CSV format. Therefore, SCISAT data shall be converted from NC to CSV format before publishing to the Open Data Portal.

- The live version of this micro application is available at https://donnees-data.asc-csa.gc.ca/scisat.
- The Open Data Portal is available at https://donnees-data.asc-csa.gc.ca/dataset/02969436-8c0b-4e6e-ad40-781cdb43cf24. 

## When to run this script?

This script shall be run each time a new version of SCISAT data is released.

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
