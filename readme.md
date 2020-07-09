# Application to filter, download and visualize Alouette-I data

Created by Hansen Liu & Wasiq Mohammad 

Last updated on 2020-04-20

## Background

The Alouette-I satellite (dates of operation: 1962-1972) was the first Canadian satellite launched into space. The goal 
of its main experiment was to understand the structure of the upper ionosphere. The data from the Alouette I 
satellite consists of hundreds of thousands of ionograms now stored digitally as image files. To understand trends in 
the ionogram data, it is necessary to examine the data at a large scale that is not possible by looking at each ionogram
 one at a time. 

This project is an application that allows users to filter through ionograms on
 multiple parameters and download either the selected ionograms’ extracted features as a CSV or the ionogram images 
 themselves. The application also allows users to visualize a summary of the data from their selected ionograms on both 
 a map and a line chart, forgoing the need for downloading the data for simple insights. 

This project can be used as a case study for the development of future satellite data applications so that the data from
 from these satellites are able to be obtained and analyzed at a larger scale and in a more user-friendly way.

## Quick start

The following commands can be done more easily if in a virtual environment (like conda) so it may be a good idea to install [Anaconda](https://www.anaconda.com/distribution/) beforehand. 

Git must be installed. On a Windows machine, installing Git Bash and running git commands from the Git Bash terminal is recommended.
A GitLab account that is on the Shared Services Canada-hosted Gitlab service is required to clone the repository. An 
account can be created here: https://gccode.ssc-spc.gc.ca/.

Cloning the repository:

        git clone https://gccode.ssc-spc.gc.ca/csa-data-centre-of-expertise/alouette-explorer-dash.git

For starting the application:

        pip install -r requirements.txt
        python app.py

Separate installation instructions for the production version of the app are provided in "Alouette Production Installation Guide.docx".

## Built with

 - [Plotly Dash](https://dash.plot.ly/) - The Python framework built on top of Flask used to develop the application. All components and visualizations on the web application are Dash objects that are created and updated in the callback functions in app.py. I would recommend that you look over Dash's comprehensive documentation (linked) if you are unsure how it works.
 
 - [Jupyter Notebook](https://jupyter-notebook-beginner-guide.readthedocs.io/en/latest/what_is_jupyter.html) - Used for data cleaning. 


## Navigation and files

 - app.py is the main application where each component and the layout of the application is defined 
 
 - controls.py contains the options for the some of the components (e.g. dropdowns)

- header_footer.py contains the html for the government of Canada header and footer. This html is injected into the main app.
 
 - /assets contains various files for the styling of the application (images, resizing, css)
 
 - /data contains the processed csv data from the feature extraction pipeline

 - /data_cleaning contains jupyter notebooks used to clean the extracted ionogram data

 - messages.pot and /translations contains translation information

 - config.py specifies the languages available for translation


## Accessibility and branding
 - Due to [Canada.ca branding requirements](https://wet-boew.github.io/themes-dist/GCWeb/index-en.html), much of the CSS of the application will need to be changed and the Government of Canada header and footer will need to be added
    - There will be stricter Government of Canada requirements when the CSA website gets merged with Canada.ca in March of 2020
    - More note on Government of Canada branding can be found here: [http://livelink/livelink/llisapi.dll?func=ll&objId=43843079&objAction=viewheader](http://livelink/livelink/llisapi.dll?func=ll&objId=43843079&objAction=viewheader)
 - Due to the [Government of Canada Standard on Web Accessibility](https://www.tbs-sct.gc.ca/pol/doc-eng.aspx?id=23601), there will likely need to be changes to the frontend or CSS
    - The [Web Experience Toolkit](https://wet-boew.github.io/v4.0-ci/index-en.html) can be used to help reach this standard, but it is not necessary
    - More notes on accessibility can be found here: [http://livelink/livelink/llisapi.dll?func=ll&objId=43801583&objAction=viewheader]([http://livelink/livelink/llisapi.dll?func=ll&objId=43801583&objAction=viewheader])
 
There will need to be changes in app.py to change colours and styles of the interactive visualizations as well as the HTML layout of the page. Most other changes will just be CSS.

## Header/Footer

- The government header/footer code is saved in a separate file (header_footer.py), and is directly injected into the dash app.

## Translations

 - Translations are tricky with Dash due to the way it renders the page. To learn how to make new translations, consult [https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-i18n-and-l10n]([https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xiii-i18n-and-l10n])

 - Each text element to be translated in dash has to be given a component ID (see Dash documentation for more details on this). The component is subsequently re-rendered on language switch. 

## Downloads

- The max number of ionograms that can be downloaded at once is 100 as of now. These ionograms are currently stored in memory before being sent to the user as a zip; this method may fail for a larger download.

## Roadmap

The current and previous roadmaps can be found on livelink for reference:
[http://livelink/livelink/llisapi.dll?func=ll&objId=39628342&objAction=viewheader]([http://livelink/livelink/llisapi.dll?func=ll&objId=39628342&objAction=viewheader])



## Authors
 - Hansen Liu
 - Wasiq Mohammmad


## Acknowledgments
 - Etienne Low-Decarie
 - Jenisha Patel
 - Cooper Ang
