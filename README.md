![scisat satellite](scisat_banner.jpg)

- [Français](#application-pour-filtrer-et-visualiser-les-données-de-scisat)
- [English](#application-to-filter-and-visualize-scisat-data)

# Application pour filtrer et visualiser les données de SCISAT

## Contexte

Le satellite SCISAT, en orbite depuis le 12 août 2003, aide des équipes de scientifiques canadiens et internationaux à améliorer leur compréhension de la déplétion de la couche d'ozone, en se concentrant particulièrement sur les changements au Canada et en Arctique. 

Vous pouvez accéder à cette micro application en direct au https://donnees-data.asc-csa.gc.ca/scisat-fr. 

![interface de l'application](Capture_app.PNG)

## Démarrage rapide
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

## Construit avec:

 - [Plotly Dash](https://dash.plot.ly/) - Le framework Python construit sur Flask a été utilisé pour développer l'application. Tous les composants et visualisations de l'application web sont des objets Dash qui sont créés et mis à jour dans les fonctions de rappel de l'application. Je vous recommande de consulter la documentation complète de Dash (lien) si vous n'êtes pas sûr de son fonctionnement.

## Navigation et fichiers

 - [scisat.py](scisat.py) est l'application principale où chaque composant et la présentation de l'application sont définis 
 
 - [controls.py](controls.py) contient les options pour certains des composants (par exemple, les dropdowns)

 - [header_footer.py](header_footer.py) contient le html pour l'en-tête et le pied de page du gouvernement du Canada. Ce html est injecté dans l'application principale.
 
 - [/assets](assets) contient différents fichiers pour le style de l'application (images, redimensionnement, css)
 
 - [/data](data) contient les données csv traitées provenant du pipeline d'extraction des caractéristiques

 - [/data_cleaning](data_cleaning) contient des scripts pythons utilisés pour nettoyer les données extraites

 - [messages.pot](message.pot) et [/translations](translations) contient des informations sur la traduction

 - [config.py](config.py) précise les langues disponibles pour la traduction

## Accessibilité et Marque
 - En raison des [exigences relatives à la marque Canada.ca](https://wet-boew.github.io/themes-dist/GCWeb/index-en.html), une grande partie du CSS de l'application devra être modifiée et l'en-tête et le pied de page du gouvernement du Canada devront être ajoutés
    - Les exigences du gouvernement du Canada seront plus strictes lorsque le site Web de la CSA sera fusionné avec Canada.ca en mars 2020
    - Pour plus d'informations sur l'image de marque du gouvernement du Canada, cliquez ici : [http://livelink/livelink/llisapi.dll?func=ll&objId=43843079&objAction=viewheader](http://livelink/livelink/llisapi.dll?func=ll&objId=43843079&objAction=viewheader)
 - En raison de la [norme du gouvernement du Canada sur l'accessibilité du Web](https://www.tbs-sct.gc.ca/pol/doc-eng.aspx?id=23601), il faudra probablement apporter des modifications au frontal ou au CSS
    - Le [Web Experience Toolkit](https://wet-boew.github.io/wet-boew/docs/versions/dwnld-fr.html) peut être utilisé pour aider à atteindre cette norme, mais il n'est pas nécessaire
    - Vous trouverez ici d'autres notes sur l'accessibilité : [http://livelink/livelink/llisapi.dll?func=ll&objId=43801583&objAction=viewheader](http://livelink/livelink/llisapi.dll?func=ll&objId=43801583&objAction=viewheader)
 
Il faudra apporter des modifications à app.py pour changer les couleurs et les styles des visualisations interactives ainsi que la mise en page HTML de la page.

## En-tête/Pied de page

- Le code de l'en-tête/du pied de page du gouvernement est enregistré dans un fichier séparé (header_footer.py), et est directement injecté dans l'application Dash.

## Traductions

 - Les traductions sont délicates avec Dash en raison de la façon dont Dash rend la page. Pour savoir comment faire de nouvelles traductions, consultez [https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-i18n-and-l10n]([https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-i18n-and-l10n])

 - Chaque élément de texte à traduire dans Dash doit recevoir un identifiant de composant (voir la documentation sur Dash pour plus de détails à ce sujet). Le composant est ensuite rendu à nouveau lors du changement de langue. 

## Auteurs
 - Camille Roy
 - Jonathan Beaulieu-Emond
 
## Remerciements
 - Etienne Low-Decarie
 - Hansen Liu & Wasiq Mohammad 

# Application to filter and visualize SCISAT data

## Background

Launched on August 12, 2003, SCISAT helps a team of Canadian and international scientists improve their understanding of the depletion of the ozone layer, 
 with a special emphasis on the changes occurring over Canada and in the Arctic.

This project is an application that allows users to filter through the SCISAT data on
 multiple parameters and allows users to visualize a summary of the data from their selected parameters on a
 world map, a graph on the altitude, a time series, forgoing the need for downloading the data for simple insights. 

This project has been developped from the Alouette app, a case study for the development of future satellite data applications so that the data from
 from these satellites are able to be obtained and analyzed at a larger scale and in a more user-friendly way.

The live version of this micro application is available at https://donnees-data.asc-csa.gc.ca/scisat.

## Quick start

The following commands can be done more easily if in a virtual environment (like conda) so it may be a good idea to install [Anaconda](https://www.anaconda.com/distribution/) beforehand. 

![interface de l'application](Capture_app.PNG)

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

Separate installation instructions for the production version of the app are provided in "SCISAT Production Installation Guide.docx".

## Built with

 - [Plotly Dash](https://dash.plot.ly/) - The Python framework built on top of Flask used to develop the application. All components and visualizations on the web application are Dash objects that are created and updated in the callback functions in app.py. I would recommend that you look over Dash's comprehensive documentation (linked) if you are unsure how it works.

## Navigation and files

 - [scisat.py](scisat.py) is the main application where each component and the layout of the application is defined 
 
 - [controls.py](controls.py) contains the options for the some of the components (e.g. dropdowns)

 - [header_footer.py](header_footer.py) contains the html for the government of Canada header and footer. This html is injected into the main app.
 
 - [/assets](assets) contains various files for the styling of the application (images, resizing, css)
 
 - [/data](data) contains the raw data in NetCDF format

 - [/data_cleaning](data_cleaning) contains python scripts used to clean the extracted data

 - [messages.pot](message.pot) and [/translations](translations) contains translation information

 - [config.py](config.py) specifies the languages available for translation


## Accessibility and branding
 - Due to [Canada.ca branding requirements](https://wet-boew.github.io/themes-dist/GCWeb/index-en.html), much of the CSS of the application will need to be changed and the Government of Canada header and footer will need to be added
    - There will be stricter Government of Canada requirements when the CSA website gets merged with Canada.ca in March of 2020
    - More note on Government of Canada branding can be found here: [http://livelink/livelink/llisapi.dll?func=ll&objId=43843079&objAction=viewheader](http://livelink/livelink/llisapi.dll?func=ll&objId=43843079&objAction=viewheader)
 - Due to the [Government of Canada Standard on Web Accessibility](https://www.tbs-sct.gc.ca/pol/doc-eng.aspx?id=23601), there will likely need to be changes to the frontend or CSS
    - The [Web Experience Toolkit](https://wet-boew.github.io/wet-boew/docs/versions/dwnld-en.html) can be used to help reach this standard, but it is not necessary
    - More notes on accessibility can be found here: [http://livelink/livelink/llisapi.dll?func=ll&objId=43801583&objAction=viewheader](http://livelink/livelink/llisapi.dll?func=ll&objId=43801583&objAction=viewheader)
 
There will need to be changes in app.py to change colours and styles of the interactive visualizations as well as the HTML layout of the page.

## Header/Footer

- The government header/footer code is saved in a separate file (header_footer.py), and is directly injected into the dash app.

## Translations

 - Translations are tricky with Dash due to the way it renders the page. To learn how to make new translations, consult [https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-i18n-and-l10n]([https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-i18n-and-l10n])

 - Each text element to be translated in dash has to be given a component ID (see Dash documentation for more details on this). The component is subsequently re-rendered on language switch. 

## Authors
 - Camille Roy
 - Jonathan Beaulieu-Emond
 
## Acknowledgments
 - Etienne Low-Decarie
 - Hansen Liu & Wasiq Mohammad 
