- [Français](#application-dash-multiple)
- [English](#multiple-dash-application)

# Application Dash Multiple 
Pour filtrer, télécharger et visualiser les données d'Alouette-I et de SCISAT sur le même serveur.

## Contexte

Ce projet est une application qui permet aux utilisateurs de visualiser les données des satellites SCISAT et Alouette-I sans avoir besoin de télécharger les données préalablement. Cette application rend les données de ces satellites plus facilement accessible et elles peuvent donc être analysées sur une plus grande échelle. Pour plus d'information sur les satellites, voir le sous-dossier SCISAT ou voir https://github.com/asc-csa/AlouetteApp.

## Démarrage rapide

Les commandes suivantes peuvent être exécutées plus facilement dans un environnement virtuel (comme conda). Il peut donc être judicieux d'installer [Anaconda] (https://www.anaconda.com/distribution/) au préalable.

Pour démarrer l'application :

        pip install -r requirements.txt
        python run.py
## Construit avec

 - [Plotly Dash](https://dash.plot.ly/) - Le framework Python construit sur Flask a été utilisé pour développer l'application. Tous les composants et visualisations de l'application web sont des objets Dash qui sont créés et mis à jour dans les fonctions de rappel de l'application. Je vous recommande de consulter la documentation complète de Dash (lien) si vous n'êtes pas sûr de son fonctionnement.
 
 - [DispatcherMiddleware](https://werkzeug.palletsprojects.com/en/0.14.x/middlewares/) - Utilisé dans run.py pour expédier les deux applications (Alouette-I et SCISAT) sur le même serveur.

## Navigation et fichiers
 
 ```
Multiple Dash App
│   run.py
|   flask_app.py
│   requirements.txt    
│   readme.md
│   ...
|
└───scisat_app
│   │   scisat.py
│   │   ...
│   
└───alouette_app
│   │   alouette.py
│   |   ...
│
│ ...
```
 
 - [run.py](run.py) contient l'expéditeur pour rouler les deux applications sur le même serveur. 
 
 - [flask_app.py](flask_app.py) est la page d'accueil quand aucun satellite n'est spécifié. Elle devrait éventuellement être modifiée pour avoir des liens directs vers les applications.
 
  - [scisat.py](scisat_app/scisat.py) and [alouette.py](/alouette_app/alouette.py) sont les applications principales où chaque composantes ainsi que la présentation sont définis.

 - [requirements.txt](requirements.txt) spécifie les versions des librairies python utilisées pour les applications.
 
 - [/alouette_app](alouette_app) contient les fichiers nécessaires pour rouler l'application d'Alouette-I.
 
 - [/scisat_app](scisat_app) contient les fichiers nécessaires pour rouler l'application SCISAT.
 
 - [/data](data) contient les données csv traitées provenant du pipeline d'extraction des caractéristiques pour Alouette-I ainsi que les données brut pour SCISAT en format NetCDF. 


## En-tête/pied de page

- Le code de l'en-tête/du pied de page du gouvernement est enregistré dans un fichier séparé (header_footer.py), et est directement injecté dans l'application du tiret.

## Traductions

 - Les traductions sont délicates avec Dash en raison de la façon dont il rend la page. Pour savoir comment faire de nouvelles traductions, consultez [https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-i18n-and-l10n]([https://blog.miguelgrinberg.com/post/the-flask-

Traduit avec www.DeepL.com/Translator (version gratuite)

# English
# Multiple Dash Application 
To filter, download and visualize Alouette-I data and SCISAT Data on the same server

## Background

This project is an application that allows users to visualize satellite data from SCISAT and Alouette-I, without needing to download the data.
 It makes the data from these satellites more easily accessible and can be analyzed at a larger scale and in a more user-friendly way. For more information on the satellites, see the folder SCISAT or visit https://github.com/asc-csa/AlouetteApp.

## Quick start

The following commands can be done more easily if in a virtual environment (like conda) so it may be a good idea to install [Anaconda](https://www.anaconda.com/distribution/) beforehand. 

For starting the application:

        pip install -r requirements.txt
        python run.py

## Built with

 - [Plotly Dash](https://dash.plot.ly/) - The Python framework built on top of Flask used to develop the application. All components and visualizations on the web application are Dash objects that are created and updated in the callback functions in app.py. I would recommend that you look over Dash's comprehensive documentation (linked) if you are unsure how it works.
 
 - [DispatcherMiddleware](https://werkzeug.palletsprojects.com/en/0.14.x/middlewares/) - Used in run.py to dispatch both apps (SCISAT and Alouette-I) on the same server. 


## Navigation and files
```
Multiple Dash App
│   run.py
|   flask_app.py
│   requirements.txt    
│   readme.md
│   ...
|
└───scisat_app
│   │   scisat.py
│   │   ...
│   
└───alouette_app
│   │   alouette.py
│   |   ...
│
│ ...
```
 
 - [run.py](run.py) contains the dispatcher to run both apps on the same server
 
 - [flask_app.py](flask_app.py) is the welcoming page when no satellite is specified. It could later be modified to click directly on the links leading to the applications.
 
 - [scisat.py](scisat_app/scisat.py) and [alouette.py](alouette_app/alouette.py) are the main applications where each component and the layout of the application is defined 
 
 - [requirements.txt](requirements.txt) contains the python librairies used for the app.
 
 - [/alouette_app](alouette_app) contains the files to run the Alouette App.
 
 - [/scisat_app](scisat_app) contains the files to run the SCISAT App. 
 
 - [/data](data) contains the processed csv data from the feature extraction pipeline for Alouette as well as the NetCDF data for SCISAT.


## Accessibility and branding
 - Due to [Canada.ca branding requirements](https://wet-boew.github.io/themes-dist/GCWeb/index-en.html), much of the CSS of the application will need to be changed and the Government of Canada header and footer will need to be added
    - There will be stricter Government of Canada requirements when the CSA website gets merged with Canada.ca in March of 2020
    - More note on Government of Canada branding can be found here: [http://livelink/livelink/llisapi.dll?func=ll&objId=43843079&objAction=viewheader](http://livelink/livelink/llisapi.dll?func=ll&objId=43843079&objAction=viewheader)
 - Due to the [Government of Canada Standard on Web Accessibility](https://www.tbs-sct.gc.ca/pol/doc-eng.aspx?id=23601), there will likely need to be changes to the frontend or CSS
    - The [Web Experience Toolkit](https://wet-boew.github.io/v4.0-ci/index-en.html) can be used to help reach this standard, but it is not necessary
    - More notes on accessibility can be found here: [http://livelink/livelink/llisapi.dll?func=ll&objId=43801583&objAction=viewheader]([http://livelink/livelink/llisapi.dll?func=ll&objId=43801583&objAction=viewheader])
 
There will need to be changes in scisat.py and alouette.py to change colours and styles of the interactive visualizations as well as the HTML layout of the page. Most other changes will just be CSS.

## Header/Footer

- The government header/footer code is saved in a separate file (header_footer.py), and is directly injected into the dash app.

## Translations

 - Translations are tricky with Dash due to the way it renders the page. To learn how to make new translations, consult [https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-i18n-and-l10n]([https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-i18n-and-l10n])

 - Each text element to be translated in dash has to be given a component ID (see Dash documentation for more details on this). The component is subsequently re-rendered on language switch. 

## Downloads

- For Alouette: The max number of ionograms that can be downloaded at once is 100 as of now. These ionograms are currently stored in memory before being sent to the user as a zip; this method may fail for a larger download.

- For SCISAT : The download button is not yet activated. 

## Roadmap

The current and previous roadmaps can be found on livelink for reference:
[http://livelink/livelink/llisapi.dll?func=ll&objId=39628342&objAction=viewheader]([http://livelink/livelink/llisapi.dll?func=ll&objId=39628342&objAction=viewheader])



## Authors
- Camille Roy
- Jonathan Beaulieu-Emond

## Acknowledgments
 - Etienne Low-Decarie
 - Hansen Liu
 - Wasiq Mohammmad

