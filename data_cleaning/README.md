
- [Français](#application-pour-convertir-les-données-de-scisat)
- [English](#application-to-convert-scisat-data)

# Application pour convertir les données de SCISAT

## Contexte

Les données originales du satellite SCISAT sont dans le format NetCDF (NC). Ce format binaire est employé par la micro-application SCISAT. Le Portail des données ouvertes de l’Agence spatiale canadienne (ASC) contient aussi les jeux de données. Toutefois, ceux-ci sont dans le format CSV. Par conséquent, les données SCISAT doivent être converties du format NC au format CSV avant d’être publiées dans le portail des données ouvertes à l’aide de ce script. 

- Vous pouvez accéder à cette micro application en direct au https://donnees-data.asc-csa.gc.ca/scisat-fr. 
- Vous pouvez accéder au portail des données ouvertes au https://donnees-data.asc-csa.gc.ca/fr/dataset/02969436-8c0b-4e6e-ad40-781cdb43cf24. 

## Navigation et fichiers

 - [DataConverter.py](DataConverter.py) est le script principal. Il s'agit du point de départ.
 
 - [NetCdfFile.py](NetCdfFile.py) est une classe qui représente un fichier dans le format NetCDF. La classe possède une fonction pour convertir son contenu dans le format CSV.

## Quand exécuter ce script?

Ce script doit être lancé chaque fois qu’une nouvelle version des données du satellite SCISAT est publiée.

## Exécution
Veuillez suivre ces étapes pour lancer le script :
- Dans un premier temps, assurez-vous de disposer de tous les fichiers de la nouvelle version des données dans le format NC. Sinon, transférez les fichiers sur votre ordnateur dans un répertoire spécifique. (ex: C:\Temp\SCISAT_DATA)
- Démarrez VS Code sur votre ordinateur.
- Ouvrez le fichier [DataConverter.py](DataConverter.py) dans VS Code.
- Dans le haut du fichier, éditer la valeur de la constante INPUT_FOLDER afin qu'elle représente le répertoire où se trouvent les fichiers dans le format NetCDF.
- De même, éditer la valeur de la constante OUTPUT_FOLDER afin qu'elle représente le répertoire où vous souhaitez que les fichiers convertis dans le format CSV s'y trouvent après l'exécution.
- Lancez l'exécution du script dans VS Code. Patientez le traitement.

Lors de l'exécution, le fenêtre de sortie affiche l'évolution et l'endroit où se trouvent les fichiers convertis dans le format CSV.

## Auteurs
 - Emiline Filion
 - Camille Roy
 
## Remerciements
 - Natasha Fee
 - Etienne Low-Decarie



# Application to convert SCISAT data

## Background

The original SCISAT data is in NetCDF (NC) format. The SCISAT micro-application uses this binary format directly. The Canadian Space Agency (CSA) Open Data Portal also hosts SCISAT data, but it is in CSV format. Therefore, SCISAT data must be converted from NC to CSV format before publishing to the Open Data Portal.

- The live version of this micro application is available at https://donnees-data.asc-csa.gc.ca/scisat.
- The Open Data Portal is available at https://donnees-data.asc-csa.gc.ca/dataset/02969436-8c0b-4e6e-ad40-781cdb43cf24. 

## When to run this script?

This script shall be run each time a new version of SCISAT data is released.

## Navigation and files

 - [DataConverter.py](DataConverter.py) is the main script. Everything starts here.
 
 - [NetCdfFile.py](NetCdfFile.py) is a class that represents a file in NetCDF format. The class has a method to convert its contents to CSV format.

## Execution

Please follow these steps to run the script:
- Make sure to have all the files of the latest version of the data in NC format. Otherwise, transfer the files to your computer in a specific directory. (e.g: C:\Temp\SCISAT_DATA)
- Start VS Code on your computer.
- Open [DataConverter.py](DataConverter.py) in VS Code.
- At the top of the file, edit the value of INPUT_FOLDER so that it represents the directory where the files in the NetCDF format are located.
- Likewise, edit the value of OUTPUT_FOLDER so that it represents the directory where you want the files converted to CSV format to be located after execution.
- Run the script in VS Code. Wait for the processing to complete.

While running, the terminal shows the progress and location of the converted files in CSV format.

## Authors
 - Emiline Filion
 - Camille Roy
 
## Acknowledgments
 - Natasha Fee
 - Etienne Low-Decarie
