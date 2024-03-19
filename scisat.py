# -*- coding: utf-8 -*-
import dash
import cartopy.feature as cf
import configparser
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import datetime as dt
from dash.dependencies import Input, Output, State
import flask
from io import StringIO
from flask_babel import _ ,Babel
from flask import session, redirect, url_for, make_response
import urllib.parse
import dash_table as dst
from dash_table.Format import Format, Scheme
from scipy.io import netcdf #### <--- This is the library to import data
import numpy as np
from os import path
import os.path


class CustomDash(dash.Dash):

    analytics_code = ''
    analytics_footer = ''
    lang = ''
    header = ''
    footer = ''
    meta_html = ''
    app_header = ''
    app_footer = ''

    def set_analytics(self, code):
        self.analytics_code = code

    def set_analytics_footer(self, code):
        self.analytics_footer = code

    def set_lang(self, lang):
        self.lang = lang

    def set_header(self, header):
        self.header = header

    def set_footer(self, footer):
        self.footer = footer

    def set_meta_tags(self, meta_html):
        self.meta_html = meta_html

    def set_app_header(self, header):
        self.app_header = header

    def set_app_footer(self, footer):
        self.app_footer = footer

    def interpolate_index(self, **kwargs):
        # Inspect the arguments by printing them
        return '''
        <!DOCTYPE html>
        <html lang='{lang}'>
            <head>
                {metas}
                {meta}
                {analytics}
                {favicon}
                <title>
                {title}
                </title>
                <style id='dash_components_css'></style>
                {css}
            </head>
            <body id='wb-cont'>
                {header}
                <main property="mainContentOfPage" typeof="WebPageElement" class="container">
                    {app_header}
                    {app_entry}
                    {app_footer}
                </main>
                <div class="global-footer">
                    <footer id="wb-info">
                    {footer}
                    {config}
                    {scripts}
                    {renderer}
                    {analytics_footer}
                    </footer>
                </div>
            </body>
        </html>
        '''.format(
            app_entry=kwargs['app_entry'],
            config=kwargs['config'],
            scripts=kwargs['scripts'],
            renderer=kwargs['renderer'],
            metas = kwargs['metas'],
            favicon = kwargs['favicon'],
            css = kwargs['css'],
            title = kwargs['title'],
            analytics = self.analytics_code,
            analytics_footer = self.analytics_footer,
            meta = self.meta_html,
            lang = self.lang,
            header = self.header,
            footer = self.footer,
            app_header = self.app_header,
            app_footer = self.app_footer
            )


#==========================================================================================
# load data and transform as needed


external_stylesheets = [
    'https://canada.ca/etc/designs/canada/wet-boew/css/wet-boew.min.css',
    'https://canada.ca/etc/designs/canada/wet-boew/css/theme.min.css',
    'https://use.fontawesome.com/releases/v5.8.1/css/all.css'
]  # Link to external CSS

external_scripts = [
    '//ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js',
    'https://canada.ca/etc/designs/canada/wet-boew/js/wet-boew.min.js',
    'https://canada.ca/etc/designs/canada/wet-boew/js/theme.min.js',
    'assets/scripts.js'
]

DATA_VERSION = 'ACEFTS_L2_v5p2'

# Loads the config file
def get_config_dict():
    config = configparser.RawConfigParser()
    #config.read('config.cfg')
    config.read('/home/ckanportal/App-Launcher/config.cfg')
    DATA_VERSION = config['SCISAT']['DATA_VERSION']
    print("SCISAT Data version: " + DATA_VERSION)
    if not hasattr(get_config_dict, 'config_dict'):
        get_config_dict.config_dict = dict(config.items('TOKENS'))
    return get_config_dict.config_dict

def generate_meta_tag(name, content):
    return "<meta name=\"" + name + "\" content=\"" + content + "\">"

def generate_meta_tag_with_title(name, content, title):
    return "<meta name=\"" + name + "\" title=\"" + title + "\" content=\"" + content + "\">"

# Runs the application based on what executed this file.
if __name__ == '__main__':
    from header_footer import gc_header_en, gc_footer_en, gc_header_fr, gc_footer_fr, app_title_en, app_title_fr, app_footer_en, app_footer_fr
    from config import Config
    #print ('DEBUG: SCISAT Main Block used')
    if(path.exists(os.path.dirname(os.path.abspath(__file__)) + r"/analytics.py")):
        from .analytics import analytics_code, analytics_footer
    else:
        analytics_code = '<h1>Did not load things</h1>'
        analytics_footer = '<h1>Did not load things footer</h1>'
    app_config = Config()

    path_data=app_config.DATA_PATH
    prefixe= app_config.APP_PREFIX

    tokens = get_config_dict()
    app = CustomDash(
        __name__,
        meta_tags=[{"name": "viewport", "content": "width=device-width"}],
        external_stylesheets=external_stylesheets,
        external_scripts=external_scripts,
        # analytics = analytics_code
    )

else :
    from .header_footer import gc_header_en, gc_footer_en, gc_header_fr, gc_footer_fr, app_title_en, app_title_fr, app_footer_en, app_footer_fr
    from .config import Config
    #print ('DEBUG: SCISAT Alternate Block used')
    if(path.exists(os.path.dirname(os.path.abspath(__file__)) + r"/analytics.py")):
        from .analytics import analytics_code, analytics_footer
    else:
        analytics_code = ''
        analytics_footer = ''
    app_config = Config()

    path_data=app_config.DATA_PATH
    prefixe= app_config.APP_PREFIX

    tokens = get_config_dict()
    app = CustomDash(
        __name__,
        requests_pathname_prefix=prefixe,
        meta_tags=[{"name": "viewport", "content": "width=device-width"}],
        external_stylesheets=external_stylesheets,
        external_scripts=external_scripts,
        # analytics = analytics_code
        )

meta_html = ''
if app_config.DEFAULT_LANGUAGE == 'en':
    app.set_header(gc_header_en)
    app.set_footer(gc_footer_en)
    meta_html += generate_meta_tag(
        'description',
        'Explore the composition of the Earth’s atmosphere with data from the SCISAT satellite! SCISAT has been monitoring the atmospheric concentrations of ozone and 70 other gases since 2003.'
        )
    meta_html += generate_meta_tag('keywords', '')

    meta_html += generate_meta_tag('dcterms.title', 'SCISAT : data exploration application for atmospheric composition')
    meta_html += generate_meta_tag_with_title('dcterms.language', 'eng', 'ISO639-2')
    meta_html += generate_meta_tag('dcterms.creator', 'Canadian Space Agency')
    meta_html += generate_meta_tag('dcterms.accessRights', '2')
    meta_html += generate_meta_tag('dcterms.service', 'CSA-ASC')

    app.title="SCISAT : data exploration application for atmospheric composition"
    app.set_app_header(app_title_en)
    app.set_app_footer(app_footer_en)
else:
    app.set_header(gc_header_fr)
    app.set_footer(gc_footer_fr)
    meta_html += generate_meta_tag(
        'description',
        "Explorez la composition de l’atmosphère terrestre avec les données du satellite SCISAT! SCISAT surveille les concentrations atmosphériques d'ozone et de 70 gaz supplémentaires depuis 2003."
        )
    meta_html += generate_meta_tag('keywords', '')

    meta_html += generate_meta_tag('dcterms.title', 'SCISAT : application d’exploration des données de composition atmosphérique ')
    meta_html += generate_meta_tag_with_title('dcterms.language', 'fra', 'ISO639-2')
    meta_html += generate_meta_tag('dcterms.creator', 'Agence spatiale canadienne')
    meta_html += generate_meta_tag('dcterms.accessRights', '2')
    meta_html += generate_meta_tag('dcterms.service', 'CSA-ASC')

    app.title="SCISAT : application d’exploration des données de composition atmosphérique"
    app.set_app_header(app_title_fr)
    app.set_app_footer(app_footer_fr)

app.set_meta_tags(meta_html)
app.set_analytics(analytics_code)
app.set_analytics_footer(analytics_footer)
app.set_lang(app_config.DEFAULT_LANGUAGE)
server = app.server
server.config['SECRET_KEY'] = tokens['secret_key']  # Setting up secret key to access flask session
babel = Babel(server)  # Hook flask-babel to the app


# Loads data file based on values provided into a pandas dataframe.
def data_reader(file,path_to_files,start_date=0,end_date=0,lat_min=-90,lat_max=90,lon_min=-180,lon_max=180,alt_range=[0,150]) :
    """

    Parameters
    ----------
    file : String
        Name of data file.

    path_to_files : String
        Path to the data files.

    start_date : Datetime, optional
        First day in the date range selected by user. The default is the first day of data available.

    end_date : Datetime, optional
        Last day in the date range selected by user. The default is the last day of data available.

    lat_min : float, optional
        Minimum latitude selected by user. The default is -90.

    lat_max : float, optional
        Maximum latitude selected by user. The default is 90.

    lon_min : float, optional
        Minimum longitude selected by user. The default is -180.

    lon_max : float, optional
        Maximum longitude selected by user. The default is 180.

    alt_range : List
        Range of alitutudes selected. Default is [0,150]

    Returns
    -------
    df : DATAFRAME
        Dataframe of all the gaz concentrations with columns :
            Altitudes (from 0.5 to 149.5), Mean on altitude (Alt_Mean), date,
            Latitude (lat) and Longitude (long)


    """
    
    if data_reader.page_df.size != 0:
        return data_reader.page_df

    #print('\nDEBUG: entering data_reader()')
    #start_time1 = time.time()
    
    print("SCISAT Data version: " + DATA_VERSION)
    print('data_reader() -> file: ' + file)
    #print('data_reader() -> datareader path: ' + path_to_files)
    
    if type(file)==list:
        file=file[0]

    gaz = file.strip().split('.')[0].strip().split('_')[3:]
    if len(gaz)>1:
        gaz = gaz[0]+'_'+gaz[1]
    else:
        gaz=gaz[0]

    name=path_to_files+'/'+file
    nc = netcdf.netcdf_file(name,'r')

    #print('DEBUG: data_reader() - Time spent so far (#1): ' + str(time.time() - start_time1))
    
    #Trier / définir rapido les données et les variables
    fillvalue1 = -999.
    months=np.copy(nc.variables['month'][:])
    years = np.copy(nc.variables['year'][:])
    days = np.copy(nc.variables['day'][:])

    lat = np.copy(nc.variables['latitude'][:])
    long =np.copy( nc.variables['longitude'][:])
    alt = np.copy(nc.variables['altitude'][:])

    #valeurs de concentration [ppv]
    data = np.copy(nc.variables[gaz][:])
    
    #Remplacer les données vides
    data[data == fillvalue1] = np.nan

    #Choisir les données dans l'intervalle de l'altitude
    data = data[:,alt_range[0]:alt_range[1]]

    df = pd.DataFrame(data,columns=alt[alt_range[0]:alt_range[1]])
    #print('DEBUG: Number of elements in the dataframe: ' + str(df.size))
    #print('DEBUG: data_reader() - Time spent so far (#2): ' + str(time.time() - start_time1))

    #Trie données abérrantes
    # TODO: This part takes a long time. We should optmize it. numpy.nan is too slow
    #slow
    df[df>1e-5]=np.nan
    #slow
    std=df.std()
    mn=df.mean()
    maxV = mn+3*std
    minV = mn-3*std
    # slow
    df[df>maxV]=np.nan
    #slow
    df[df<minV]=np.nan

    #print('DEBUG: data_reader() - Time spent so far (#3): ' + str(time.time() - start_time1))

    #Colonne de dates
    date=[]
    nbDays = len(days)
    #print('DEBUG: Number of days to loop: ' + str(nbDays))
    date = np.array([dt.datetime(int(years[i]), int(months[i]), int(days[i])) for i in range (nbDays)])
    #print('DEBUG: data_reader() - Time spent so far (#4): ' + str(time.time() - start_time1))

    data_meanAlt = np.nanmean(df,1)
    df['Alt_Mean'] = data_meanAlt
    df['date'] = date
    df['lat'] = lat
    df['long'] = long

    if start_date!=0 and end_date!=0 :
        df=df[np.where(df['date']>start_date,True,False)]
        df=df[np.where(df['date']<end_date,True,False)]

    #filters the data based on min/max longitude/latitude
    df=df[np.where(df['lat']>lat_min,True,False)]
    df=df[np.where(df['lat']<lat_max,True,False)]
    df=df[np.where(df['long']>lon_min,True,False)]
    df=df[np.where(df['long']<lon_max,True,False)]

    #print('DEBUG: end of data_reader() - TOTAL Time spent: ' + str(time.time() - start_time1) + '\n\n')
    data_reader.page_df = df
    return df
data_reader.page_df = pd.DataFrame()

# Returns a binned dataframe with the provided steps.
def databin(df, step):
    """
    Create data bins of specified steps in terms of longitude and latitude.

    Parameters
    ----------


    start_date : Datetime
        First day in the date range selected by user. The default is the first day of data available.

    end_date : Datetime
        Last day in the date range selected by user. The default is the last day of data available.

    lat_min : float
        Minimum value of the latitude stored as a float.

    lat_max : float
        Maximum value of the latitude stored as a float.

    lon_min : float
        Minimum value of the longitude stored as a float.

    lon_max : float
        Maximum value of the longitude stored as a float.

    gaz_list : list
        Gas name strings stored in a list (e.g. ['Ozone'])

    alt_range : List
        Range of altitudes

    step : float
        Size of bins in terms of lat/long degrees

    Returns
    -------
    Dataframe
        A dataframe contained the binned data provided in steps of specified degrees.
    """
    # We create a binning map
    #print('\n\nDEBUG: entering databin()')
    #start_time1 = time.time()
    to_bin = lambda x: np.round(x / step) * step
    #print('DEBUG: databin() - Time spent so far (#1): ' + str(time.time() - start_time1))
    
    # We map the current data into the bins
    # TODO: This part takes a long time, but it looks like we already use the optimized way
    df["lat"] = df['lat'].map(to_bin)
    df["long"] = df['long'].map(to_bin)
    
    # We return a mean value of all overlapping data to ensure there are no overlaps
    #print('DEBUG: end of databin() - TOTAL Time spent: ' + str(time.time() - start_time1) + '\n\n')
    return df.groupby(["lat", "long"]).mean().reset_index()


# Dropdown options
#======================================================================================
# Controls for webapp
gaz_name_options = [
    {'label': _('Acetone'), 'value': DATA_VERSION + '_acetone.nc'},
    {'label': _('Acetylene'), 'value': DATA_VERSION + '_C2H2.nc'},
    {'label': _('Ethane'), 'value':  DATA_VERSION + '_C2H6.nc'},
    {'label': _('Trichlorofluoromethane'), 'value': DATA_VERSION + '_CCl3F.nc'},
    {'label': _('Carbon tetrachloride'), 'value':  DATA_VERSION + '_CCl4.nc'},

    {'label': _('Carbon tetrafluoride'), 'value':  DATA_VERSION + '_CF4.nc'},
    {'label': _('Trichlorotrifluoroethane'), 'value':  DATA_VERSION + '_CFC113.nc'},
    {'label': _('Chloromethane'), 'value':  DATA_VERSION + '_CH3Cl.nc'},
    {'label': _('Acetonitrite'), 'value':  DATA_VERSION + '_CH3CN.nc'},
    {'label': _('Methanol'), 'value':  DATA_VERSION + '_CH3OH.nc'},
    {'label': _('Methane'), 'value':  DATA_VERSION + '_CH4.nc'},

    {'label': _('Methane 212'), 'value':  DATA_VERSION + '_CH4_212.nc'},
    {'label': _('Methane 311'), 'value':  DATA_VERSION + '_CH4_311.nc'},
    {'label': _('Difluorochloromethane'), 'value':   DATA_VERSION + '_CHF2Cl.nc'},
    {'label': _('Trifluoromethane'), 'value':  DATA_VERSION + '_CHF3.nc'},
    {'label': _('Chlorine monoxide'), 'value':  DATA_VERSION + '_ClO.nc'},
    {'label': _('Chlorine nitrate'), 'value':  DATA_VERSION + '_ClONO2.nc'},

    {'label': _('Carbon monoxide'), 'value':  DATA_VERSION + '_CO.nc'},
    {'label': _('Carbon dioxide'), 'value':  DATA_VERSION + '_CO2.nc'},
    {'label': _('Carbon dioxide 627'), 'value':   DATA_VERSION + '_CO2_627.nc'},
    {'label': _('Carbon dioxide 628'), 'value':  DATA_VERSION + '_CO2_628.nc'},
    {'label': _('Carbon dioxide 636'), 'value':  DATA_VERSION + '_CO2_636.nc'},
    {'label': _('Carbon dioxide 637'), 'value':  DATA_VERSION + '_CO2_637.nc'},


    {'label': _('Carbon dioxide 638'), 'value':   DATA_VERSION + '_CO2_638.nc'},
    {'label': _('Phosgene'), 'value':  DATA_VERSION + '_COCl2.nc'},
    {'label': _('Carbonyl chlorine fluoride'), 'value':  DATA_VERSION + '_COClF.nc'},
    {'label': _('Carbonyl fluoride'), 'value':   DATA_VERSION + '_COF2.nc'},
    {'label': _('Carbon monoxide 27'), 'value':  DATA_VERSION + '_CO_27.nc'},
    {'label': _('Carbon monoxide 28'), 'value':   DATA_VERSION + '_CO_28.nc'},

     {'label': _('Carbon monoxide 36'), 'value':   DATA_VERSION + '_CO_36.nc'},
    {'label': _('Carbon monoxide 38'), 'value':   DATA_VERSION + '_CO_38.nc'},
    {'label': _('GLC'), 'value':    DATA_VERSION + '_GLC.nc'},
    {'label': _('Formaldehyde'), 'value':   DATA_VERSION + '_H2CO.nc'},
    {'label': _('Water'), 'value':   DATA_VERSION + '_H2O.nc'},
    {'label': _('Hydrogen peroxide'), 'value':   DATA_VERSION + '_H2O2.nc'},


     {'label': _('Water 162'), 'value':    DATA_VERSION + '_H2O_162.nc'},
    {'label': _('Water 171'), 'value':    DATA_VERSION + '_H2O_171.nc'},
    {'label': _('Water 181'), 'value':     DATA_VERSION + '_H2O_181.nc'},
    {'label': _('Water 182'), 'value':   DATA_VERSION + '_H2O_182.nc'},
    {'label': _('Hydrochlorofluorocarbon 141b'), 'value':    DATA_VERSION + '_HCFC141b.nc'},
    {'label': _('Hydrochlorofluorocarbon 142b'), 'value':    DATA_VERSION + '_HCFC142b.nc'},
    {'label': _('Hydrochloric acid'), 'value':     DATA_VERSION + '_HCl.nc'},



    {'label': _('Hydrogen cyanide'), 'value':   DATA_VERSION + '_HCN.nc'},
    {'label': _('Formic acid'), 'value':   DATA_VERSION + '_HCOOH.nc'},
    {'label': _('Hydrogen fluoride'), 'value':    DATA_VERSION + '_HF.nc'},
    {'label': _('Hydrofluorocarbon 134a'), 'value':   DATA_VERSION + '_HFC134a.nc'},
    {'label': _('Nitric acid'), 'value':  DATA_VERSION + '_HNO3.nc'},
    {'label': _('Nitric acid 156'), 'value':  DATA_VERSION + '_HNO3_156.nc'},


    {'label': _('Peroxynitric acid'), 'value':   DATA_VERSION + '_HO2NO2.nc'},
    {'label': _('Nitrogen'), 'value':  DATA_VERSION + '_N2.nc'},
    {'label': _('Nitrous oxide'), 'value':  DATA_VERSION + '_N2O.nc'},
    {'label': _('Dinitrogen pentaoxide'), 'value':    DATA_VERSION + '_N2O5.nc'},
    {'label': _('Nitrous oxide 447'), 'value':   DATA_VERSION + '_N2O_447.nc'},
    {'label': _('Nitrous oxide 448'), 'value':    DATA_VERSION + '_N2O_448.nc'},

     {'label': _('Nitrous oxide 456'), 'value':    DATA_VERSION + '_N2O_456.nc'},
    {'label': _('Nitrous oxide 546'), 'value':   DATA_VERSION + '_N2O_546.nc'},
    {'label': _('Nitrous monoxide 447'), 'value':     DATA_VERSION + '_NO.nc'},
    {'label': _('Nitrogen dioxide'), 'value':    DATA_VERSION + '_NO2.nc'},
    {'label': _('Nitrogen dioxide 656'), 'value':    DATA_VERSION + '_NO2_656.nc'},
    {'label': _('Oxygen'), 'value':    DATA_VERSION + '_O2.nc'},


     {'label': _('Ozone'), 'value':     DATA_VERSION + '_O3.nc'},
    {'label': _('Ozone 667'), 'value':     DATA_VERSION + '_O3_667.nc'},
    {'label': _('Ozone 668'), 'value':     DATA_VERSION + '_O3_668.nc'},
    {'label': _('Ozone 676'), 'value':   DATA_VERSION + '_O3_676.nc'},
    {'label': _('Ozone 686'), 'value':     DATA_VERSION + '_O3_686.nc'},
    {'label': _('Carbonyl sulfide'), 'value':     DATA_VERSION + '_OCS.nc'},
     {'label': _('Carbonyl sulfide 623'), 'value':      DATA_VERSION + '_OCS_623.nc'},


     {'label': _('Carbonyl sulfide 624'), 'value':      DATA_VERSION + '_OCS_624.nc'},
    {'label': _('Carbonyl sulfide 632'), 'value':      DATA_VERSION + '_OCS_632.nc'},
    {'label': _('Phosphorus'), 'value':      DATA_VERSION + '_P.nc'},
    {'label': _('Polyacrylonitrile'), 'value':    DATA_VERSION + '_PAN.nc'},
    {'label': _('Sulfur hexafluoride'), 'value':      DATA_VERSION + '_SF6.nc'},
    {'label': _('Sulfur dioxide'), 'value':      DATA_VERSION + '_SO2.nc'},
 #    {'label': _('Temperature'), 'value':    'ACEFTS_L2_v5p0_T.nc'} #!!! Est ce qu'on la met?

   ]
#======================================================================================


# Create global chart template
mapbox_access_token = tokens['scisat_mapbox_token']

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Gas concentration overview",
    mapbox=dict(
        style="light",
        # center=dict(lon=-78.05, lat=42.54),
        zoom=2,
    ),
    transition={'duration': 500},
)


# Builds the layout for the header
def build_header():
    return html.Div(
            [
                html.Div([], className="one column"),
                html.Div(
                    [
                        html.H1(
                            "",
                            style={"margin-bottom": "10px", "margin-left": "15%"},
                            id="page-title"),
                    ],
                    className="six columns",
                    id="title",
                ),
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("csa-logo.png"),
                            id="csa-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin": "25px",
                            },
                            alt="CSA Logo"
                        )
                    ],
                    className="one column",
                ),
                html.Div(
                    [
                        html.A(
                            html.Span("", id="learn-more-button"),
                            href="https://www.asc-csa.gc.ca/eng/satellites/scisat/about.asp",
                            id='learn-more-link',
                            className="btn btn-primary"
                        ),
                        html.A(
                            html.Span('FR', id='language-button'),
                            href='/scisat/language/fr',
                            id='language-link',
                            className="btn btn-primary"
                        ),
                    ],
                    className="four columns",
                    id="button-div",
                    style={"display": "flex", "justify-content": "space-around"}
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        )


# Builds the layout and components for the inputs to filter the data
def build_filtering():
    return html.Div([
        html.Div(
            [
                html.Div(
                    [
                        html.H2(id="filtering_text"),
                        html.P(id="data-ratio"),
                        html.P(id='placeholder')
                    ],
                    id="info-container",
                    className="mini_container three columns",
                    style={"text-align": "center"},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                 dcc.Markdown(id="description-1"),
                                 dcc.Markdown(id="description-2"),
                                 dcc.Markdown(id="description-3"),
                                 dcc.Markdown(id="description-4"),
                                 html.P(
                                    html.A(
                                        id="github-link",
                                        href = "https://github.com/asc-csa",
                                        title = "ASC-CSA Github"
                                    )
                                 )
                            ],
                            id="description_div",
                        ),
                    ],
                    id="description-container",
                    className="container-display mini_container nine columns",
                ),
            ],
            className="row flex-display twelve columns"
        ),

        html.Div(
            [
                html.H3(
                   id="select-data"
                ),
            ],
            style={"margin-top": "10px", "margin-left": "auto", "margin-right": "auto", "text-align": "center"},
            className="twelve columns"
        ),

        html.Div(
            html.Form(
            [
                html.Section(
                    [
                        html.H2(
                            id='error_header'
                        ),
                        html.Ul(
                            id='form_errors'
                        )
                    ],
                    id='filter_errors',
                    hidden=True,
                    className='alert alert-danger'
                ),
                html.Div(
                    [
                        html.Div(
                        [
                            html.Div(
                                className='label label-danger',
                                id="gas_alert",
                                hidden=True
                            )
                        ],
                        className="error"
                    ),
                        html.Div(
                            [
                                html.Label(
                                    id="gas_selection",
                                    htmlFor='gaz_list_dropdown',
                                    className="control_label",
                                ),
                                dcc.Dropdown(
                                    id="gaz_list",
                                    options= gaz_name_options,
                                    placeholder=_('Select a gas'),
                                    multi=False,
                                    value=DATA_VERSION + '_O3.nc',
                                    className="dcc_control",
                                    label = 'Label test'

                                ),

                                # html.Span(children=html.P(),className="wb-inv")
                            ],
                            role='listbox',
                            **{'aria-label': 'Gas Dropdown'}

                        )
                    ],
                    style={"textAlign":"left"}
                ),
                html.Div(
                    [
                    html.Div(
                        className="error"
                    ),
                    # dbc.Alert(
                    #     color="secondary",
                    #     id="pos_alert",
                    #     is_open=False,
                    #     fade=False,
                    #     style={"margin-top":"0.5em"},
                    #     className='dash-alert dash-alert-danger'
                    # )
                    ]
                ),
                html.Div([
                    html.Div( #Latitude picker
                        [
                            html.Label(
                                id="latitude-text",
                                className="control_label",
                                style={"textAlign":"left"}
                            ),
                            html.Div(
                                className='label label-danger',
                                id="lat_alert",
                                hidden=True
                            ),
                            html.Div([
                                html.Label(
                                    id = "lat_min-text",
                                    htmlFor = "lat_min",
                                    hidden = True
                                ),
                                dcc.Input(
                                    id="lat_min",
                                    type='number',
                                    value=-90.0,
                                    placeholder="Min Latitude",
                                    min=-90.0,
                                    max=90.0,
                                    step=5,
                                    debounce=True
                                ),
                                html.Label(
                                    id = "lat_max-text",
                                    htmlFor = "lat_max",
                                    hidden = True
                                ),
                                dcc.Input(
                                    id="lat_max",
                                    type='number',
                                    value=90.0,
                                    placeholder="Max Latitude",
                                    min=-90.0,
                                    max=90.0,
                                    step=5,
                                    debounce=True
                                )
                            ]),
                            html.Div(children=html.P(id="lat_selection"),className="wb-inv")
                        ],
                        className="col-md-4",
                    ),
                    html.Div( #longitude picker
                        [
                            html.Label(
                                id="longitude-text",
                                className="control_label",
                                style ={"textAlign":"left"}
                            ),
                            html.Div(
                                className='label label-danger',
                                id="lon_alert",
                                hidden=True
                            ),
                            html.Div([
                                html.Label(
                                    htmlFor="lon_min",
                                    id= "lon_min-text",
                                    hidden = True
                                ),
                                dcc.Input(
                                    id="lon_min",
                                    type='number',
                                    value=-180.0,
                                    placeholder="Min Longitude",
                                    min=-180.0,
                                    max=180.0,
                                    step=5,
                                    debounce=True
                                ),
                                html.Label(
                                    htmlFor="lon_max",
                                    id= "lon_max-text",
                                    hidden = True
                                ),
                                dcc.Input(
                                    id="lon_max",
                                    type='number',
                                    value=180.0,
                                    placeholder="Max Longitude",
                                    min=-180.0,
                                    max=180.0,
                                    step=5,
                                    debounce=True
                                ),
                            ]),
                            html.Div(children=html.P(id="lon_selection"),className="wb-inv")
                        ],
                        className="col-md-4",
                        style={"textAlign":"left"}
                    ),
                    html.Div(
                        [ #Year selection + download button
                            html.Div([
                                html.Div(id="date_alert", hidden=True, style={"margin-top":"0.5em"}, className='label label-danger'),
                            ]),
                            html.Label(
                                id="yearslider-text",
                                className="control_label"
                                ),

                            html.Div(
                                [
                                    dcc.DatePickerRange(
                                        id='date_picker_range',
                                        start_date=dt.datetime(2004, 2, 1),
                                        end_date=dt.datetime(2020, 5, 5),
                                        min_date_allowed=dt.datetime(2004, 2, 1),
                                        max_date_allowed=dt.date.today(),
                                        start_date_placeholder_text=_('Select start date'),
                                        end_date_placeholder_text=_('Select end date'),
                                        display_format="Y-MM-DD",
                                        start_date_aria_label = _('Start Date'),
                                        end_date_aria_label = _('End Date'),
                                        ),
                                    html.Div(id='output-container-date-picker-range'),
                                    html.Div(children=html.P(id="date_selection"),className="wb-inv")
                                ]
                                ),
                        ],
                        className="col-md-12 col-lg-4",
                    ),
                ],
                className='row align-items-start ',
                style={"textAlign":"left"}
                ),
                html.Hr(),
                html.Div([ #Choix altitude
                        html.Label(id="altitude-text"),
                        dcc.RangeSlider(
                            id='alt_range',
                            marks = {i: "{}".format(i) for i in np.append(np.arange(0.5,149.5,10),149.5)},
                            min=0,
                            max=150,
                            step=1,
                            value=[0, 150] ,
                           # tooltip = { 'always_visible': True }
                           ),
                        html.Div(id='output-container-alt-picker-range'),
                        ],style={"margin-top":"75px"}),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Div(
                                            html.Span(
                                                id='generate-button',
                                                n_clicks=0,
                                                style={
                                                    'padding': '0px 10px',
                                                    'display': 'inline-block',
                                                    'padding' : '6px 22px'
                                                },
                                                className="btn btn-primary",
                                                role = 'button',
                                                tabIndex=0
                                            ),
                                            style={
                                                "text-align": "center"
                                            },
                                            id='generate',
                                        ),
                                        html.Div(
                                            children=html.P(
                                            id="generate_selection"
                                            ),
                                            className="wb-inv"
                                        )
                                    ],
                                    style={'text-align': 'center'}
                                )
                            ],
                            className="one-half column",
                            style={"textAlign":"right"}
                        ),
                        html.Div(
                            [ #Download button
                                html.Div(
                                    [
                                        html.A(
                                            html.Span(
                                                id='download-button-1',
                                                n_clicks=0,
                                                style={'padding': '0px 10px'}
                                            ),
                                            id='download-link-1',
                                            # download='rawdata.csv',
                                            href="",
                                            target="_blank",
                                            className="btn btn-primary"
                                        ),
                                        html.Div(
                                            children=html.P(id="download_selection"),
                                            className="wb-inv"
                                        )
                                    ]

                                ),
                            ],
                            id="cross-filter-options",
                            className="one-half column"
                        )
                    ],
                    style={"margin-top":"30px"}
                )
            ],
            ),
            className="pretty_container twelve column wb-frmvld",
            style={"justify-content": "space-evenly"}
            )
    ])

def detail_table(id, id2):
    #next button pagnation, for some reason the pages are 0 indexed but the dispalyed page isn't
    @app.callback(
        [
            Output( id, 'page_current'),
            Output( id+'-btn-1-a', 'data-value'),
            Output( id+'-btn-2-a', 'data-value'),
            Output( id+'-btn-3-a', 'data-value'),
            Output( id+'-btn-1-a', "children"),
            Output( id+'-btn-2-a', "children"),
            Output( id+'-btn-3-a', "children"),
            Output( id+'-btn-1-a', "aria-label"),
            Output( id+'-btn-2-a', "aria-label"),
            Output( id+'-btn-3-a', "aria-label"),
            Output( id+'-btn-1-a', "aria-current"),
            Output( id+'-btn-2-a', "aria-current"),
            Output( id+'-btn-3-a', "aria-current"),
            Output( id+'-btn-1', "className"),
            Output( id+'-btn-2', "className"),
            Output( id+'-btn-prev-a', 'children'),
            Output( id+'-btn-next-a', 'children'),
            Output( id+'-btn-prev-a', "aria-label"),
            Output( id+'-btn-next-a', "aria-label"),
            Output( id+'-navigation', "aria-label"),
        ],
        [
            Input( id+'-btn-prev', 'n_clicks'),
            Input( id+'-btn-1', 'n_clicks'),
            Input( id+'-btn-2', 'n_clicks'),
            Input( id+'-btn-3', 'n_clicks'),
            Input( id+'-btn-next', 'n_clicks')
        ],
        [
            State( id, 'page_current'),
            State( id+'-btn-1-a', 'data-value'),
            State( id+'-btn-2-a', 'data-value'),
            State( id+'-btn-3-a', 'data-value'),
        ]
    )
    
    def update_table_next(btn_prev, btn_1, btn_2, btn_3, btn_next, curr_page, btn1_value, btn2_value, btn3_value):
        session['language'] = app_config.DEFAULT_LANGUAGE
        ctx = dash.callback_context
        btn1_current = 'false'
        btn2_current = 'false'
        btn3_current = 'false'

        btn1_class = ''
        btn2_class = ''

        btn1_aria = ''
        btn2_aria = ''
        btn3_aria = ''

        if ctx.triggered:
            start_page = curr_page
            # curr_page = curr_page + 1
            #print(ctx.triggered)
            if ctx.triggered[0]['prop_id'] == id+'-btn-next.n_clicks':
                curr_page += 1
            if ctx.triggered[0]['prop_id'] == id+'-btn-1.n_clicks':
                curr_page = btn1_value
            if ctx.triggered[0]['prop_id'] == id+'-btn-2.n_clicks':
                curr_page = btn2_value
            if ctx.triggered[0]['prop_id'] == id+'-btn-3.n_clicks':
                curr_page = btn3_value
            if ctx.triggered[0]['prop_id'] == id+'-btn-prev.n_clicks':
                curr_page -= 1

            if curr_page < 0:
                curr_page = 0

        aria_prefix = _('Goto page ')

        if curr_page < 1:
            btn1_value = curr_page
            btn2_value = curr_page+1
            btn3_value = curr_page+2
            btn1_current = 'true'
            btn1_class = 'active'
            btn1_aria = aria_prefix + str(btn1_value+1) + ', ' + _('Current Page')
            btn2_aria = aria_prefix + str(btn2_value+1)
            btn3_aria = aria_prefix + str(btn3_value+1)
        else:
            btn1_value = curr_page -1
            btn2_value = curr_page
            btn3_value = curr_page + 1
            btn2_current = 'true'
            btn2_class = 'active'
            btn1_aria = aria_prefix + str(btn1_value+1)
            btn2_aria = aria_prefix + str(btn2_value+1) + ', ' + _('Current Page')
            btn3_aria = aria_prefix + str(btn3_value+1)

        # print('curr_page: '+ str(curr_page))

        return [
            curr_page,
            btn1_value,
            btn2_value,
            btn3_value,
            btn1_value+1,
            btn2_value+1,
            btn3_value+1,
            btn1_aria,
            btn2_aria,
            btn3_aria,
            btn1_current,
            btn2_current,
            btn3_current,
            btn1_class,
            btn2_class,
            _('Previous'),
            _('Next'),
            _('Goto Previous Page'),
            _('Goto Next Page'),
            _('Pagination Navigation')
        ]

    return html.Div([
        html.Details(
            [
                html.Summary(id=id2),
                html.Div(
                    dst.DataTable(
                        id=id,
                        page_size= 10,
                        page_current = 0
                    ),
                    style={"margin":"4rem"}
                ),
                html.Nav(
                    html.Ul(
                        [
                            html.Li(
                                html.A(
                                    _('Previous'),
                                    id=id+'-btn-prev-a',
                                    className='page-prev',
                                    **{'aria-label': _('Goto Previous Page'), 'data-value': -1}
                                ),
                                id=id+'-btn-prev',
                                n_clicks=0,
                                tabIndex=0
                            ),
                            html.Li(
                                html.A(
                                    '1',
                                    id=id+'-btn-1-a',
                                    **{'aria-label': _("Goto page 1, Current Page"), 'aria-current': _('true'), 'data-value': 0}
                                ),
                                id=id+'-btn-1',
                                n_clicks=0,
                                tabIndex=0
                            ),
                            html.Li(
                                html.A(
                                    '2',
                                    id=id+'-btn-2-a',
                                    **{'aria-label': _('Goto page 2'), 'data-value': 1}
                                ),
                                className='active',
                                id=id+'-btn-2',
                                n_clicks=0,
                                tabIndex=0
                            ),
                            html.Li(
                                html.A(
                                    '3',
                                    id=id+'-btn-3-a',
                                    **{'aria-label': _('Goto page 3'), 'data-value': 2}
                                ),
                                id=id+'-btn-3',
                                n_clicks=0,
                                tabIndex=0
                            ),
                            html.Li(
                                html.A(
                                    'Next',
                                    id=id+'-btn-next-a',
                                    className='page-next',
                                    **{'aria-label': _('Goto Next Page'), 'data-value': -2}
                                ),
                                id=id+'-btn-next',
                                n_clicks=0,
                                tabIndex=0
                            )
                        ],
                        className = 'pagination'
                    ),
                    **{'aria-label': _('Pagination Navigation')},
                    role = _('navigation'),
                    className = 'table_pagination',
                    id = id+'-navigation'
                )
            ]
        )
    ])

# Builds the layout for the map displaying the time series
def build_stats():
    return html.Div([
        html.Div([
                html.Div(
                    [
                    html.Div(
                        [dcc.Graph(id="selector_map",
                                   config={
                                       "displaylogo": False,
                                       "displayModeBar": False
                                   }
                                   )],
                    ),
                    html.Div ([html.P(id="Map_description", style={"margin-top": "2em"})]),
                    detail_table('world-table','world-table-text'),
                    html.Div([ # Altitude graph
                        html.Div([ # Graphique
                            dcc.Graph(id="count_graph",
                                      config={
                                          "displaylogo": False,
                                          "displayModeBar": False
                                      }
                                      )],
                                 id="countGraphContainer",
                                 ),
                        ]), #End Altitude Graph
                        html.Div ([ #Altitude graph description
                            html.P(id = "Altitude_description", style={"margin-top":"2em"})
                            ]),
                    detail_table('altitude-table', 'altitude-table-text'),
                    html.Div([
                        dcc.Graph(id="viz_chart",
                                  config={
                                      "displaylogo": False,
                                      "displayModeBar": False
                                  }
                                  )
                            ]),

                    html.Div ([
                       html.P( id = "TimeS_description", style = {"margin-top":"2em"})
                               ]),
                    detail_table('time-table', 'time-table-text'),
                    ],
                    id="vizChartContainer",
                    className="pretty_container",
                    ),
            ]),

        html.Div(id='none', children=[], style={'display': 'none'}), # Placeholder element to trigger translations upon page load
        ])

# Create app layout
app.layout = html.Div(
    [
        html.Div(
            [
                dcc.Store(id="aggregate_data"),
                html.Div(id="output-clientside"),  # empty Div to trigger javascript file for graph resizing

                build_filtering(),
                build_stats(),
            ],
            id="mainContainer",
            style={"display": "flex", "flex-direction": "column", "margin": "auto", "width":"95%"},
        ),
        html.Div(id='none2', children=[], style={'display': 'none'}), # Placeholder element to trigger translations upon page load
    ]
)


#=======================================================================================================================
# Input functions and validation functions

# Update global values of lat/long using validation
@app.callback(
    Output("lat_alert", "hidden"),
    [
        Input('lat_min','value'),
        Input('lat_max','value')
    ]
)

def update_lat_alert(lat_min,lat_max):
    s = True
    if not lat_validation(lat_min, lat_max):
        s = False
    return s

# Update global values of lat/long using validation
@app.callback(
    Output("lon_alert", "hidden"),
    [
        Input('lon_min','value'),
        Input('lon_max','value')
    ]
)

def update_lon_alert(lon_min,lon_max):
    s = True
    if not lon_validation(lon_min, lon_max):
        s = False
    return s

# Update error list
@app.callback(
    [
        Output("filter_errors", "hidden"),
        Output("form_errors", 'children'),
        Output("error_header", 'children')
    ],
    [
        Input("lat_alert", "hidden"),
        Input("lon_alert", "hidden"),
        Input("gas_alert", "hidden"),
        Input("date_alert", "hidden")
    ],
)

def update_error_list( lat_alert, lon_alert, gas_alert, date_alert):
    s = False
    errors = []
    if not lat_alert or not lon_alert or not gas_alert or not date_alert:
        if not gas_alert:
            errors.append(
                html.Li(
                    html.A(
                        _("Missing data. The gas selected has no associated data. Please contact asc.donnees-data.csa@canada.ca."),
                        href="#gas_alert",
                    )
                )
            )
        if not lat_alert:
            errors.append(
                html.Li(
                    html.A(
                        _("Invalid values provided. Latitude values must be between -90 and 90. Minimum values must be smaller than maximum values. All values must be round numbers that are multiples of 5."),
                        href="#lat_alert"
                    )
                )
            )
        if not lon_alert:
            errors.append(
                html.Li(
                    html.A(
                        _("Invalid values provided. Longitude values must be between -180 and 180. Minimum values must be smaller than maximum values. All values must be round numbers that are multiples of 5."),
                        href="#lon_alert"
                    )
                )
            )
        if not date_alert:
            errors.append(
                html.Li(
                    html.A(
                        _("Invalid dates provided. Try dates between 04/02/2004 (Feb. 4th 2004) and 02/02/2024 (Feb. 2nd 2024)."),
                        href="#date_alert"
                    )
                )
            )
    else:
        s = True
    return [
        s,
        errors,
        _('The form could not be submitted because errors were found.')
    ]

# Update global date values using validation
@app.callback(
    Output("date_alert", "hidden"),
    [   Input("date_picker_range", "start_date"),
        Input("date_picker_range", "end_date"),
        Input("gaz_list", "value")
    ]
)

def update_dates(start_date, end_date, gaz_list):
    s = True
    if not date_validation(start_date,end_date,gaz_list):
        s = False
    return s

# Update gas value using validation
@app.callback(
    Output("gas_alert", "hidden"),
    [
        Input("gaz_list", "value"),
    ],
    [
        State("gas_alert", "hidden")
    ],
)
def update_gas(gaz_list, is_open):
    s = True
    if not gas_validation(gaz_list):
        s = False
    return s

# Update altitude range. The output is used as a placeholder because Dash does not allow to have no output on callbacks.
@app.callback(
[
    Output("placeholder","data-value"),
    Output("alt_range","slider_labels"),
],
    [Input("alt_range", "value")]
)
def update_alt(alt_range):
    return [
        "",
        [_('Altitude Maximum'),_('Altitude Minimum')]
        ]

# Lat/long validation
def pos_validation(lat_min,lat_max,lon_min,lon_max):
    try:
        s = ((lat_min < lat_max) and (lat_min >= -90) and (lat_max <= 90) and (lon_min < lon_max) and (lon_min >= -180) and (lon_max <= 180))
    except TypeError:
        s = False
    return s

# Lat/long validation
def lat_validation(lat_min,lat_max):
    try:
        s = ((lat_min < lat_max) and (lat_min >= -90) and (lat_max <= 90))
    except TypeError:
        s = False
    return s

# Lat/long validation
def lon_validation(lon_min,lon_max):
    try:
        s = ((lon_min < lon_max) and (lon_min >= -180) and (lon_max <= 180))
    except TypeError:
        s = False
    return s

# Date validation
def date_validation(start_date, end_date, gaz_list):
    start = dt.datetime.strptime(start_date.split('T')[0], '%Y-%m-%d')
    end = dt.datetime.strptime(end_date.split('T')[0], '%Y-%m-%d')
    #print('\nReading data from date_validation()')
    df = data_reader(gaz_list, path_data)
    MIN_DATE=df['date'].min().to_pydatetime()
    MAX_DATE=df['date'].max().to_pydatetime()
    return ((start>=MIN_DATE) and (start <= end) and (start <= MAX_DATE) and (end >= MIN_DATE) and (end <= MAX_DATE))

# Gas validation
def gas_validation(gaz_list):
    try:
        if type(gaz_list)==list:
            gaz_list=gaz_list[0]
        #print('Path to data:')
        #print(path_data)
        name=path_data+'/'+gaz_list
        nc = netcdf.netcdf_file(name,'r')
    except FileNotFoundError:
        return False
    return True

# Computes the mean value into a dataframe
def compute_mean_concentration(df: pd.DataFrame, startindex, buffer_size):
    """Computes the mean value into a dataframe.

    Parameters
    ----------

    df : DateFrame
        Input dataframe. It shall contain the 'Alt_Mean' column.

    startindex : integer
        Computation goes from the star index for n values where n is the buffer size.

    buffer_size : integer
        Size of the buffer to use for mean computation. e.g. 200

    Returns
    -------
    float
        The concentration mean (ppv).
    """
    
    average = 0.0
    nb_nan = 0
    for index, row in df.iloc[startindex:].iterrows():
        
        if(index < (startindex + buffer_size)):
            try:
                # Regular case
                average = average + row['Alt_Mean']
            except:
                # NaN
                nb_nan = nb_nan + 1
        else:
            break
    
    # Compute the average
    if (buffer_size - nb_nan) <= 0:
        return 0
    return float(average) / float(buffer_size - nb_nan)

# Extracts the first & last concentration from the dataframe
def create_mean_time_series(df: pd.DataFrame):
    
    """Creates the dataframe for the mean concentration time series

    Parameters
    ----------

    df : DateFrame
        Input dataframe. It shall contain the 'Alt_Mean' column.

    Returns
    -------
    Dataframe
        Dataframe that contains the concentration means (ppv) according to the time slot.
    """
    nb_data = len(df.index)
    if nb_data < 5:
        # Less than 5 data -> use the first & last value
        return {"date": [df.iloc[1]['date'], df.iloc[nb_data-1]['date']],
                "Alt_Mean": [df.iloc[1]['Alt_Mean'], df.iloc[nb_data-1]['Alt_Mean']]}
    else:
        # Compute the buffer size 4 the mean computation
        buffer_size = int(nb_data / 2.4)
        if buffer_size > 400:
            #max buffer size
            buffer_size = 400
            
        first_value = compute_mean_concentration(df, 0, buffer_size)
        last_value = compute_mean_concentration(df, nb_data-buffer_size-1, buffer_size)
        return {"date": [df.iloc[1]['date'], df.iloc[nb_data-1]['date']],
                "Alt_Mean": [first_value, last_value]}

#=======================================================================================================================
# This section is for graph generation. The 3 graphs are generated here.

# This generates the concentration v.s. altitude figure
def make_count_figure(df, alt_range):
    """Create and update the Gas Concentration vs Altitude over the given time range.

    Parameters
    ----------

    start_date : Datetime
        First day in the date range selected by user. The default is the first day of data available.

    end_date : Datetime
        Last day in the date range selected by user. The default is the last day of data available.


    lat_min : float
        Minimum value of the latitude stored as a float.

    lat_max : float
        Maximum value of the latitude stored as a float.

    lon_min : float
        Minimum value of the longitude stored as a float.

    lon_max : float
        Maximum value of the longitude stored as a float.

    gaz_list : list
        Ground station name strings stored in a list (e.g. ['Ozone'])

    alt_range : List
        Range of altitudes

    Returns
    -------
    dict
        A dictionary containing 2 key-value pairs: the selected data as an array of dictionaries and the graphic's
        layout as as a Plotly layout graph object.
    """
    #print('\nDEBUG: entering make_count_figure()')
    #start_time1 = time.time()

    concentration=df[alt_range[0]:alt_range[1]]
    xx=concentration.mean(axis=0)
    err_xx=concentration.std(axis=0)

    # layout_count = copy.deepcopy(layout)
    data = [
        dict(
            type="scatter",
            x=xx,
            y=concentration.columns[0:alt_range[1]-alt_range[0]],
            error_x=dict(type='data', array=err_xx,thickness=0.5),
            name=_("Altitude"),
            #orientation='h',
            # color=xx,
             # colorscale=[[0, 'red'],
            # [1, 'blue']],
            # opacity=1,

        )
    ]

    layout = dict(
        autosize=True,
        automargin=True,
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        # legend=dict(font=dict(size=10), orientation="h"),
       # title=_(" "),

        xaxis=dict(title= _("Concentration [ppv]"),
                   automargin= True,
                   showexponent = 'all',
                   exponentformat = 'e'
                   ),

        yaxis =  dict(
           title = _("Altitude [km]"),
           automargin=True,
           ),

        height=450,
        transition={'duration': 500},
    )

    figure = dict(data=data, layout=layout)
    table_data= []
    min = int(np.floor(alt_range[0]))
    max = int(np.floor(alt_range[1]))
    for i in range(0, max-min):
        template = {"alt":'', 'int_min':'', 'mean':'', 'int_max':''}
        template["alt"] = min + i + 0.5
        template["int_min"]= xx[i]-err_xx[i]
        template["mean"]=xx[i]
        template["int_max"]=xx[i]+err_xx[i]
        if template["int_min"] < 0:
            template["int_min"]= 0
        if template["mean"] < 0:
            template["mean"]= 0
        table_data.append(template)
    columns=[{"name":_("Altitude (km)"), "id":"alt"},
            {"name":_("Min. confidence interval concentration (ppv)"), "id":"int_min","type":"numeric","format":Format(precision=3, scheme=Scheme.exponent)},
            {"name":_("Mean concentration (ppv)"),"id":"mean","type":"numeric","format":Format(precision=3, scheme=Scheme.exponent)},
            {"name":_("Max. confidence interval concentration (ppv)"), "id":"int_max","type":"numeric","format":Format(precision=3, scheme=Scheme.exponent)}]
    
    #print('DEBUG: end of make_count_figure() - Time spent: ' + str(time.time() - start_time1) + '\n')

    return [figure, columns, table_data]

# This generates the geographical representation of the data
def generate_geo_map(df):
    """Create and update the map of gas concentrations for selected variables.

    The color of the data points indicates the mean gas concentration at that coordinate.

    Parameters
    ----------

    start_date : Datetime
        First day in the date range selected by user. The default is the first day of data available.

    end_date : Datetime
        Last day in the date range selected by user. The default is the last day of data available.

    lat_min : float
        Minimum value of the latitude stored as a float.

    lat_max : float
        Maximum value of the latitude stored as a float.

    lon_min : float
        Minimum value of the longitude stored as a float.

    lon_max : float
        Maximum value of the longitude stored as a float.

    gaz_list : list
        Gas name strings stored in a list (e.g. ['Ozone'])

    alt_range : List
        Range of altitudes

    Returns
    -------
    dict
        A dictionary containing 2 key-value pairs: the selected data as an array of Plotly scattermapbox graph objects
        and the map's layout as a Plotly layout graph object.
    """

    #print('\nDEBUG: entering generate_geo_map()')
    #start_time1 = time.time()

    # We decide the binning that needs to be done, if any, based on lat/long range selected
    hm = True
    area = (df['lat'].max()-df['lat'].min())*(df['long'].max()-df['long'].min())
    if area<1800:
        hm = False
    elif area<16200 and area>=1800:
        df = databin(df,1)
    else:
        df = databin(df,3)

    #print('DEBUG: generate_geo_map() - Time spent so far (#1): ' + str(time.time() - start_time1))

    # We collect the coordinates of all coastlines geometries from cartopy
    x_coords = []
    y_coords = []
    for coord_seq in cf.COASTLINE.geometries():
        x_coords.extend([k[0] for k in coord_seq.coords] + [np.nan])
        y_coords.extend([k[1] for k in coord_seq.coords] + [np.nan])

    #print('DEBUG: generate_geo_map() - Time spent so far (#2): ' + str(time.time() - start_time1))

    # We create a heatmap of the binned data
    if hm:
        fig= go.Figure(
                    go.Heatmap(
                            showscale=True,
                            x=df['long'],
                            y=df['lat'],
                            z=df['Alt_Mean'],
                            zmax=df['Alt_Mean'].max(),
                            zmin=df['Alt_Mean'].min(),
                            #zsmooth='fast', # Turned off smoothing to avoid interpolations
                            opacity=1,
                            name = "",
                            hoverongaps = False,
                            hovertemplate = "Latitude: %{y}°<br>Longitude: %{x}°<br>Concentration: %{z:.3e} ppv",
                            colorbar=dict(
                                title=dict(
                                    text=_("Gas concentration [ppv] (mean on altitude and position) "),
                                ),
                                titleside="right",
                                showexponent = 'all',
                                exponentformat = 'e'
                            ),
                            colorscale= [[0.0, '#313695'], [0.07692307692307693, '#3a67af'], [0.15384615384615385, '#5994c5'], [0.23076923076923078, '#84bbd8'],
                             [0.3076923076923077, '#afdbea'], [0.38461538461538464, '#d8eff5'], [0.46153846153846156, '#d6ffe1'], [0.5384615384615384, '#fef4ac'],
                              [0.6153846153846154, '#fed987'], [0.6923076923076923, '#fdb264'], [0.7692307692307693, '#f78249'], [0.8461538461538461, '#e75435'],
                               [0.9230769230769231, '#cc2727'], [1.0, '#a50026']],
                        )
                    )
    else:
        fig = go.Figure(
            go.Scatter(
                name="",
                showlegend=False,
                x=df['long'],
                y=df['lat'],
                meta=df['Alt_Mean'],
                mode="markers",
                hovertemplate = "Latitude: %{y}°<br>Longitude: %{x}°<br>Concentration: %{meta:.3e} ppv",
                marker= dict(
                    size=10,
                    color=df['Alt_Mean'],
                    cmin=df['Alt_Mean'].min(),
                    cmax=df['Alt_Mean'].max(),
                    colorscale= [[0.0, '#313695'], [0.07692307692307693, '#3a67af'], [0.15384615384615385, '#5994c5'], [0.23076923076923078, '#84bbd8'],
                     [0.3076923076923077, '#afdbea'], [0.38461538461538464, '#d8eff5'], [0.46153846153846156, '#d6ffe1'], [0.5384615384615384, '#fef4ac'],
                      [0.6153846153846154, '#fed987'], [0.6923076923076923, '#fdb264'], [0.7692307692307693, '#f78249'], [0.8461538461538461, '#e75435'],
                       [0.9230769230769231, '#cc2727'], [1.0, '#a50026']],
                    colorbar=dict(
                        title=dict(
                            text=_("Gas Concentration [ppv] (mean on altitude and position) "),
                        ),
                        titleside="right",
                        showexponent = 'all',
                        exponentformat = 'e'
                    ),
                )

            )
        )

    #print('DEBUG: generate_geo_map() - Time spent so far (#3): ' + str(time.time() - start_time1))

    # We set the layout for margins and paddings
    fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10, pad=5),
        clickmode="event+select",
        hovermode="closest",
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token
        ),
        transition={'duration': 500},
        xaxis = dict(range=[df['long'].min()-1.5,df['long'].max()+1.5]),
        yaxis = dict(range=[df['lat'].min()-1.5,df['lat'].max()+1.5])
    )

    # We turn off the axes
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)

    # This makes sure pixels are square so that we can accurately lay our data on an equirectangular map. We also set the background color to white
    fig['layout']['yaxis']['scaleanchor']='x'
    fig['layout'].update(plot_bgcolor='white')
    
    # We add the coastlines on top of our heatmap and skip hoverinfo so that it does not overlap heatmap labels
    fig.add_trace(
        go.Scatter(
            x = x_coords,
            y = y_coords,
            name="",
            showlegend=False,
            mode = 'lines',
            hoverinfo = "skip",
            line = dict(color='black')))

    # Here, we set the attributes that pertain to the text table
    data = df[['lat','long','Alt_Mean']].to_dict('records')
    columns = [{"name":_("Latitude (°)"), "id":"lat"},{"name":_("Longitude (°)"),"id":"long"},{"name":_("Mean concentration (ppv)"),"id":"Alt_Mean","type":"numeric","format":Format(precision=3, scheme=Scheme.exponent)}]
    
    #print('DEBUG: end of generate_geo_map() - Time spent: ' + str(time.time() - start_time1) + '\n')
    return [fig, columns, data]

# This removes the negative concentrations from the data frame
def remove_nagative_concentrations(df):
    """Remove the negative concentrations from the data frame.

    Parameters
    ----------

    start_date : Datetime
        First day in the date range selected by user. The default is the first day of data available.

    end_date : Datetime
        Last day in the date range selected by user. The default is the last day of data available.

    x_axis_selection : string
        The chart's x-axis parameter selected by the dropdown stored as a string (e.g 'timestamp')

    y_axis_selection : string
        The chart's y-axis parameter selected by the dropdown stored as a string (e.g 'max_depth')

    lat_min : float
        Minimum value of the latitude stored as a float.

    lat_max : float
        Maximum value of the latitude stored as a float.

    lon_min : float
        Minimum value of the longitude stored as a float.

    lon_max : float
        Maximum value of the longitude stored as a float.

    gaz_list : list
        Gas name strings stored in a list (e.g. ['Ozone'])

    alt_range : List
        Range of altitudes

    Returns
    -------
    dict
        Data frame that does not have negative concentrations anymore
    """
    
    # Ignore negative concentration
    #print ('Ignore negative concentrations')
    previous_concentration = 0
    for row in df.index:
        if df['Alt_Mean'][row] >= 0:
            previous_concentration = df['Alt_Mean'][row]
        if df['Alt_Mean'][row] < 0:
            #print('Date: ', df['date'][row], 'Alt_Mean: ', the_concentration)
            if previous_concentration < 0:
                print('ERROR: Negative previous concentration found.')
            df.at[row, 'Alt_Mean'] = previous_concentration
             
    return df

# This generate the time series chart.
def make_viz_chart(df):#, x_axis_selection='Date', y_axis_selection='Concentration [ppv]'):
    """Create and update the chart for visualizing gas concentration based on varying x and y-axis selection.

    Parameters
    ----------

    start_date : Datetime
        First day in the date range selected by user. The default is the first day of data available.

    end_date : Datetime
        Last day in the date range selected by user. The default is the last day of data available.

    x_axis_selection : string
        The chart's x-axis parameter selected by the dropdown stored as a string (e.g 'timestamp')

    y_axis_selection : string
        The chart's y-axis parameter selected by the dropdown stored as a string (e.g 'max_depth')

    lat_min : float
        Minimum value of the latitude stored as a float.

    lat_max : float
        Maximum value of the latitude stored as a float.

    lon_min : float
        Minimum value of the longitude stored as a float.

    lon_max : float
        Maximum value of the longitude stored as a float.

    gaz_list : list
        Gas name strings stored in a list (e.g. ['Ozone'])

    alt_range : List
        Range of altitudes

    Returns
    -------
    dict
        A dictionary containing 2 key-value pairs: the selected data as an array of dictionaries and the chart's layout
        as a Plotly layout graph object.
    """
    #print('\nDEBUG: entering make_viz_chart()')
    #start_time1 = time.time()

    df.sort_values(by=['date'], inplace=True)
    concentration = df.groupby('date')['Alt_Mean'].mean()
    concentration = concentration.groupby(concentration.index.floor('D')).mean()
    concentration = concentration.dropna()
    df_tmp = df.groupby(['date'])['Alt_Mean'].mean().reset_index()
    concentration_mean = pd.DataFrame(create_mean_time_series(df_tmp))
    mean_dates = concentration_mean["date"]
    mean_concentrations = concentration_mean['Alt_Mean']

    bins=concentration
    date=df["date"].map(pd.Timestamp.date).unique()

    # Plot data
    figure = go.Figure(
            go.Scatter(
            name="",
            type="scatter",
            x=date,
            y=bins,
            fillcolor="rgba(255,255,255,0)",
            line={'color': 'rgb(18,99,168)'},
            connectgaps=True,
            showlegend=False))

    figure.update_layout(
        autosize=True,
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        #title=_("Time series"),
        xaxis={"title": _('Date'), "gridcolor":"#D8D8D8"} ,
        yaxis =  dict(
           title = _("Concentration [ppv]"),
           showexponent = 'all',
           exponentformat = 'e',
           gridcolor="#D8D8D8"
           ),
        height=500,
        transition={'duration': 500},
    )
    
    # Add the mean line (the red line)
    first_mean_concentration = concentration_mean.iloc[0]['Alt_Mean']
    last_mean_concentration = concentration_mean.iloc[1]['Alt_Mean']
    overall_trend = " ↗↘ "
    if first_mean_concentration > last_mean_concentration:
        print('going down')
        overall_trend = " ↘ "
    elif first_mean_concentration < last_mean_concentration:
        print('going up')
        overall_trend = " ↗ "
    else:
        print('going straight')
        overall_trend = ' -- '

    figure.add_trace(
        go.Scatter(
            x = mean_dates,
            y = mean_concentrations,
            name="",
            showlegend=False,
            line = dict(color='firebrick')))
    
    figure.update_xaxes(showgrid=True)
    figure.update_yaxes(showgrid=True)

    # Create the table
    table_data = []
    for index, value in bins.items():
        template = {"date":index.strftime("%Y-%m-%d"), 'conc':value, 'trend':overall_trend}
        table_data.append(template)
    columns = [{'name':_('Date'),'id':'date'},{'name':_("Mean concentration (ppv)"),'id':'conc','type':'numeric',"format":Format(precision=3, scheme=Scheme.exponent)},{'name':_("Overall trend"),'id':'trend','type':'string'}]
    
    #print('DEBUG: end of make_viz_chart() - Time spent: ' + str(time.time() - start_time1) + '\n')
    return [figure, columns, table_data]

#=======================================================================================================================
#  Controller and other major callback function.

# The controller generates all figures, links and numbers from the input parameters provided. It is called by pressing the "Generate" button
@app.callback(
    [
        Output("selector_map", "figure"),
        Output("world-table", "columns"),
        Output("world-table", "data"),
        Output("viz_chart", "figure"),
        Output("time-table","columns"),
        Output("time-table","data"),
        Output("count_graph", "figure"),
        Output("altitude-table","columns"),
        Output("altitude-table","data"),
        Output("download-link-1", "href"),
        Output("filtering_text", "children")
    ],
    [
        Input("generate-button","n_clicks"),
        Input("gaz_list","value")
    ],
    [
        State("gaz_list","value"),
        State("lat_min","value"),
        State("lat_max", "value"),
        State("lon_min", "value"),
        State("lon_max", "value"),
        State("alt_range", "value"),
        State("date_picker_range", "start_date"),
        State("date_picker_range", "end_date"),
        State("lat_alert", "hidden"),
        State("lon_alert", "hidden"),
        State("gas_alert", "hidden"),
        State("date_alert", "hidden")
    ]
)

def controller(n_clicks, gaz_list, act_gaz_list, lat_min, lat_max, lon_min, lon_max, alt_range, start_date, end_date, lat_alert, lon_alert, gas_alert, date_alert):
    if (lat_alert or lon_alert or date_alert):
        #print('\nReading data from controller()')
        df = data_reader(act_gaz_list, path_data, start_date, end_date, lat_min, lat_max, lon_min, lon_max, alt_range)
        df = remove_nagative_concentrations(df)
        [fig1, columns1, data1] = generate_geo_map(df)
        [fig2, columns2, data2] = make_viz_chart(df)
        [fig3, columns3, data3] = make_count_figure(df, alt_range)
        link = update_csv_link(start_date, end_date, lat_min, lat_max, lon_min, lon_max, act_gaz_list, alt_range)
        nbr = update_filtering_text(df)
    else:
        df, fig1, columns1, data1, fig2, columns2, data2, fig3, columns3, data3, link, nbr = None, None, None, None, None, None, None, None, None, None, None, 0

    return fig1, columns1, data1, fig2, columns2, data2, fig3, columns3, data3, link, nbr

# This function calculates the number of points selected
def update_filtering_text(df):
    """Update the component that counts the number of data points selected.

    Parameters
    ----------
    start_date : Datetime
        First day in the date range selected by user. The default is the first day of data available.

    end_date : Datetime
        Last day in the date range selected by user. The default is the last day of data available.

    lat_min : float
        Minimum value of the latitude stored as a float.

    lat_max : float
        Maximum value of the latitude stored as a float.

    lon_min : float
        Minimum value of the longitude stored as a float.

    lon_max : float
        Maximum value of the longitude stored as a float.

    gaz_list : list
        Gas names strings stored in a list (e.g. ['Ozone'])

    alt_range : List
        Range of altitudes

    Returns
    -------
    int
        The number of data points present in the dataframe after filtering
    """

    return "{:n}".format(df.shape[0]) + " points" #!!!!!!!!!!

# This function sets the max/min allowed dates when switching gas
@app.callback(
    [Output('date_picker_range', 'min_date_allowed'),
    Output('date_picker_range', 'max_date_allowed'),
    Output('date_picker_range', 'start_date'),
    Output('date_picker_range', 'end_date')],

    [ Input("gaz_list", "value")]
    )
    
def update_picker(gaz_list):
    #print('\nReading data from update_picker()')
    data_reader.page_df = pd.DataFrame()
    df = data_reader(gaz_list, path_data)
    START_DATE = df.date.min().to_pydatetime()
    END_DATE = df.date.max().to_pydatetime()
    return START_DATE, END_DATE, START_DATE, END_DATE

# This function updates the link that is opened when pressing the download button
def update_csv_link(start_date, end_date, lat_min, lat_max, lon_min, lon_max, gaz_list, alt_range):
    """Updates the link to the CSV download

    Parameters
    ----------

    start_date : Datetime
        First day in the date range selected by user. The default is the first day of data available.

    end_date : Datetime
        Last day in the date range selected by user. The default is the last day of data available.

    lat_min : float
        Minimum value of the latitude stored as a float.

    lat_max : float
        Maximum value of the latitude stored as a float.

    lon_min : float
        Minimum value of the longitude stored as a float.

    lon_max : float
        Maximum value of the longitude stored as a float.

    gaz_list : list
        Gas names strings stored in a list (e.g. ['Ozone'])

    Returns
    -------
    link : str
        Link that redirects to the Flask route to download the CSV based on selected filters
    """
    #print('\nDEBUG: entering update_csv_link()')
    #start_time1 = time.time()

    link = prefixe+'/dash/downloadCSV?start_date={}&end_date={}&lat_min={}&lat_max={}&lon_min={}&lon_max={}&gaz_list={}&alt_range={}' \
            .format(start_date, end_date, lat_min, lat_max, lon_min, lon_max, gaz_list, alt_range)
    values = {
        'start_date': start_date,
        'end_date': end_date,
        'lat_min': lat_min,
        'lat_max': lat_max,
        'lon_min': lon_min,
        'lon_max': lon_max,
        'gaz_list': gaz_list,
        'alt_range': alt_range
    }
    link = prefixe + '/dash/downloadCSV?' + urllib.parse.urlencode(values)
    
    #print('DEBUG: end of update_csv_link() - Time spent: ' + str(time.time() - start_time1) + '\n')
    return link

#=======================================================================================================================
# Routing

# Flask route that handles the CSV downloads. This allows for larger files to be passed,
# as well as avoiding generating the CSV until the download is desired
@app.server.route('/dash/downloadCSV')
def download_csv():
    """Generates the CSV and sends it to the user

    args
    ----------

    start_date : Datetime
        First day in the date range selected by user. The default is the first day of data available.

    end_date : Datetime
        Last day in the date range selected by user. The default is the last day of data available.


    lat_min : float
        Minimum value of the latitude stored as a float.

    lat_max : float
        Maximum value of the latitude stored as a float.

    lon_min : float
        Minimum value of the longitude stored as a float.

    lon_max : float
        Maximum value of the longitude stored as a float.

    gaz_list : list
        Gas name strings stored in a list (e.g. ['Ozone'])

    alt_range : List
        Range of altitudes

    Returns
    -------
    output : CSV
        CSV file based on the applied filters
    """

    #print('\nDEBUG: entering download_csv()')
    #start_time1 = time.time()

    lat_min    = float(flask.request.args.get('lat_min'))
    lat_max    = float(flask.request.args.get('lat_max'))
    lon_min    = float(flask.request.args.get('lon_min'))
    lon_max    = float(flask.request.args.get('lon_max'))
    start_date = flask.request.args.get('start_date')
    end_date   = flask.request.args.get('end_date')
    alt_range   = flask.request.args.get('alt_range')
    gaz_list= flask.request.args.get('gaz_list')

    #start_date =pd.Timestamp(parse(start_date))
    #end_date   =pd.Timestamp(parse(end_date))

    #Pre-processing of alt_range
    alt_range = alt_range.replace(" ", "")
    alt_range = alt_range[1:-1].split(',')
    alt_range[0] = int(alt_range[0])
    alt_range[1] = int(alt_range[1])
    #print('Reading data from download_csv()')
    df =data_reader(gaz_list,path_data,start_date,end_date,lat_min,lat_max,lon_min,lon_max,alt_range)

    # Making the output csv from the filtered df
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    output = make_response(csv_buffer.getvalue())
    try:
        language = session['language']
    except KeyError:
        language = 'en'
    if language == 'fr':
        output.headers["Content-Disposition"] = "attachment; filename=résumé_données.csv"
    else:
        output.headers["Content-Disposition"] = "attachment; filename=summary_data.csv"
    output.headers["Content-type"] = "text/csv"
    
    #print('DEBUG: end of download_csv() - Time spent: ' + str(time.time() - start_time1) + '\n')

    return output

#============================================================================
# Translation

# Inject the static text here after translating
# The variables in controls.py are placed here; babel does not work for translation unless it is hard coded here, not sure why. Likely has to with the way Dash builds the web app.
@app.callback(
    [
        Output("data-ratio", "children"),
        Output("description-1", "children"),
        Output("description-2", "children"),
        Output("description-3", "children"),
        Output("description-4", "children"),
        Output("github-link", "children"),
        Output("select-data", "children"),
        Output("generate-button","children"),
        Output("generate_selection", "children"),
        Output("Map_description","children"),
        Output("Altitude_description","children"),
        Output("TimeS_description","children"),
        Output("gas_selection", "children"),
        Output("lat_selection", "children"),
        Output("lon_selection", "children"),
        Output("date_selection", "children"),
        Output("download_selection", "children"),
        Output("lat_alert", "children"),
        Output("lon_alert", "children"),
        Output("date_alert", "children"),
        Output("gas_alert", "children"),
        Output("latitude-text", "children"),
        Output("lat_min-text", "children"),
        Output("lat_max-text", "children"),
        Output("longitude-text", "children"),
        Output("lon_min-text", "children"),
        Output("lon_max-text", "children"),
        Output("altitude-text","children"),
        Output("yearslider-text", "children"),
        Output("download-button-1", "children"),
        Output("date_picker_range", "start_date_placeholder_text"),
        Output("date_picker_range", "end_date_placeholder_text"),
        Output("date_picker_range", "start_date_aria_label"),
        Output("date_picker_range", "end_date_aria_label"),
        Output("world-table-text","children"),
        Output("altitude-table-text","children"),
        Output("time-table-text","children"),
        Output("gaz_list", "options"),
    ],
        [Input('none', 'children')], # A placeholder to call the translations upon startup
)

def translate_static(x):
    #print('Translating...')
    return [
                _("Data selected"),
                _("Launched on August 12, 2003, SCISAT helps a team of Canadian and international scientists improve their understanding of the depletion of the ozone layer, with a special emphasis on the changes occurring over Canada and in the Arctic. "),
                _("This application provides users the ability to select, download and visualize SCISAT's data. The dataset can also be accessed in [CSA's Open Government Portal](https://data.asc-csa.gc.ca/dataset/02969436-8c0b-4e6e-ad40-781cdb43cf24)."),
                _("The authoritative source data for the Atmospheric Chemistry Experiment (ACE), also known as SCISAT, is available on the [ACE site](http://www.ace.uwaterloo.ca/data.php) (external site only available in English). "),
                _("Please read this [Important Mission Information Document](http://www.ace.uwaterloo.ca/ACE-FTS_v2.2/ACEFTSPublicReleaseDocumentation.pdf) before using the ACE/SCISAT data. Please refer to the relevant scientific literature when interpreting SCISAT data."),
                _("Visit our Github page to learn more about our applications."),
                _("Select data"),
                _("Update"),
                _("Update with selected data"),
                _("Graph of the gas concentration in parts per volume (ppv) visualized on a world map. Each dot represents the mean concentration on the selected dates, the altitude column as well as the position. The color indicates the mean gas concentration value."),
                _("Graph showing the gas concentration in parts per volume (ppv) over the selected altitude interval. The value represents the mean concentration over the selected latitudes, longitudes and dates. Error bars are 95% confidence intervals around the mean."),
                _("Time series showing the evolution of the gas concentration in parts per volume (ppv). Each data point represents the daily overall mean concentration. The red line shows the overall trend, which indicates if the gas concentration is increasing or decreasing during the selected time period (↗ or ↘)."),
                _("Select gas:"),
                _("Selection of the range of latitude "),
                _("Selection of the range of longitude"),
                _("Date selection"),
                _("Download the selected dataset"),
                _("Invalid values provided. Latitude values must be between -90 and 90. Minimum values must be smaller than maximum values. All values must be round numbers that are multiples of 5."),
                _("Invalid values provided. Longitude values must be between -180 and 180. Minimum values must be smaller than maximum values. All values must be round numbers that are multiples of 5."),
                _("Invalid dates provided. Try dates between 01/02/2004 (Feb. 1st 2004) and 05/05/2020 (May 5th 2020)."),
                _("Missing data. The gas selected has no associated data. Please contact asc.donnees-data.csa@canada.ca."),
                _("Filter by latitude:"),
                _("Minimum latitude"),
                _("Maximum latitude"),
                _("Filter by longitude:"),
                _("Minimum longitude"),
                _("Maximum longitude"),
                _("Select altitude range:"),
                _("Select date:"),
                _('Download summary data as CSV'),
                _('Select start date'),
                _('Select end date'),
                _('Start Date'),
                _('End Date'),
                _("Text version - World map of mean gas concentrations"),
                _("Text version - Mean gas concentration as a function of altitude"),
                _("Text version - Mean gas concentration over time"),
                #_('Download full data as netcdf'),
                # _("Select x-axis:"),
                # _("Select y-axis:"),
                #_("Select statistic:"),
                #_("Select plotted value:"),
    [  # Gas_options
    {'label': _('Acetone'), 'value': DATA_VERSION + '_C3H6O.nc'},
    {'label': _('Acetylene'), 'value': DATA_VERSION + '_C2H2.nc'},
    {'label': _('Ethane'), 'value':  DATA_VERSION + '_C2H6.nc'},
    {'label': _('Dichlorodifluoromethane'), 'value': DATA_VERSION + '_CCl2F2.nc'},
    {'label': _('Trichlorofluoromethane'), 'value': DATA_VERSION + '_CCl3F.nc'},
    {'label': _('Carbon tetrachloride'), 'value':  DATA_VERSION + '_CCl4.nc'},


    {'label': _('Carbon tetrafluoride'), 'value':  DATA_VERSION + '_CF4.nc'},
    {'label': _('Trichlorotrifluoroethane'), 'value':  DATA_VERSION + '_CFC113.nc'},
    {'label': _('Chloromethane'), 'value':  DATA_VERSION + '_CH3Cl.nc'},
    {'label': _('Acetonitrite'), 'value':  DATA_VERSION + '_CH3CN.nc'},
    {'label': _('Methanol'), 'value':  DATA_VERSION + '_CH3OH.nc'},
    {'label': _('Methane'), 'value':  DATA_VERSION + '_CH4.nc'},

    {'label': _('Methane 212'), 'value':  DATA_VERSION + '_CH4_212.nc'},
    {'label': _('Methane 311'), 'value':  DATA_VERSION + '_CH4_311.nc'},
    {'label': _('Difluorochloromethane'), 'value':   DATA_VERSION + '_CHF2Cl.nc'},
    {'label': _('Trifluoromethane'), 'value':  DATA_VERSION + '_CHF3.nc'},
    {'label': _('Chlorine monoxide'), 'value':  DATA_VERSION + '_ClO.nc'},
    {'label': _('Chlorine nitrate'), 'value':  DATA_VERSION + '_ClONO2.nc'},

    {'label': _('Carbon monoxide'), 'value':  DATA_VERSION + '_CO.nc'},
    {'label': _('Carbon dioxide'), 'value':  DATA_VERSION + '_CO2.nc'},
    {'label': _('Carbon dioxide 627'), 'value':   DATA_VERSION + '_CO2_627.nc'},
    {'label': _('Carbon dioxide 628'), 'value':  DATA_VERSION + '_CO2_628.nc'},
    {'label': _('Carbon dioxide 636'), 'value':  DATA_VERSION + '_CO2_636.nc'},
    {'label': _('Carbon dioxide 637'), 'value':  DATA_VERSION + '_CO2_637.nc'},


    {'label': _('Carbon dioxide 638'), 'value':   DATA_VERSION + '_CO2_638.nc'},
    {'label': _('Phosgene'), 'value':  DATA_VERSION + '_COCl2.nc'},
    {'label': _('Carbonyl chlorofluoride'), 'value':  DATA_VERSION + '_COClF.nc'},
    {'label': _('Carbonyl fluoride'), 'value':   DATA_VERSION + '_COF2.nc'},
    {'label': _('Carbon monoxide 27'), 'value':  DATA_VERSION + '_CO_27.nc'},
    {'label': _('Carbon monoxide 28'), 'value':   'ACEFTS_L2_v5p_CO_28.nc'},

     {'label': _('Carbon monoxide 36'), 'value':   DATA_VERSION + '_CO_36.nc'},
    {'label': _('Carbon monoxide 38'), 'value':   DATA_VERSION + '_CO_38.nc'},
    {'label': _('GLC'), 'value':    DATA_VERSION + '_GLC.nc'},
    {'label': _('Formaldehyde'), 'value':   DATA_VERSION + '_H2CO.nc'},
    {'label': _('Water'), 'value':   DATA_VERSION + '_H2O.nc'},
    {'label': _('Hydrogen peroxide'), 'value':   DATA_VERSION + '_H2O2.nc'},


     {'label': _('Water 162'), 'value':    DATA_VERSION + '_H2O_162.nc'},
    {'label': _('Water 171'), 'value':    DATA_VERSION + '_H2O_171.nc'},
    {'label': _('Water 181'), 'value':     DATA_VERSION + '_H2O_181.nc'},
    {'label': _('Water 182'), 'value':   DATA_VERSION + '_H2O_182.nc'},
    {'label': _('Hydrochlorofluorocarbon 141b'), 'value':    DATA_VERSION + '_HCFC141b.nc'},
    {'label': _('Hydrochlorofluorocarbon 142b'), 'value':    DATA_VERSION + '_HCFC142b.nc'},
    {'label': _('Hydrochloric acid'), 'value':     DATA_VERSION + '_HCl.nc'},

    {'label': _('Hydrogen cyanide'), 'value':   DATA_VERSION + '_HCN.nc'},
    {'label': _('Formic acid'), 'value':   DATA_VERSION + '_HCOOH.nc'},
    {'label': _('Hydrogen fluoride'), 'value':    DATA_VERSION + '_HF.nc'},
    {'label': _('Hydrofluorocarbon 134a'), 'value':   DATA_VERSION + '_HFC134a.nc'},
    {'label': _('Nitric acid'), 'value':  DATA_VERSION + '_HNO3.nc'},
    {'label': _('Nitric acid 156'), 'value':  DATA_VERSION + '_HNO3_156.nc'},


    {'label': _('Peroxynitric acid'), 'value':   DATA_VERSION + '_HO2NO2.nc'},
    {'label': _('Nitrogen'), 'value':  DATA_VERSION + '_N2.nc'},
    {'label': _('Nitrous oxide'), 'value':  DATA_VERSION + '_N2O.nc'},
    {'label': _('Dinitrogen pentaoxide'), 'value':    DATA_VERSION + '_N2O5.nc'},
    {'label': _('Nitrous oxide 447'), 'value':   DATA_VERSION + '_N2O_447.nc'},
    {'label': _('Nitrous oxide 448'), 'value':    DATA_VERSION + '_N2O_448.nc'},

     {'label': _('Nitrous oxide 456'), 'value':    DATA_VERSION + '_N2O_456.nc'},
    {'label': _('Nitrous oxide 546'), 'value':   DATA_VERSION + '_N2O_546.nc'},
    {'label': _('Nitrous monoxide 447'), 'value':     DATA_VERSION + '_NO.nc'},
    {'label': _('Nitrogen dioxide'), 'value':    DATA_VERSION + '_NO2.nc'},
    {'label': _('Nitrogen dioxide 656'), 'value':    DATA_VERSION + '_NO2_656.nc'},
    {'label': _('Oxygen'), 'value':    DATA_VERSION + '_O2.nc'},


     {'label': _('Ozone'), 'value':     DATA_VERSION + '_O3.nc'},
    {'label': _('Ozone 667'), 'value':     DATA_VERSION + '_O3_667.nc'},
    {'label': _('Ozone 668'), 'value':     DATA_VERSION + '_O3_668.nc'},
    {'label': _('Ozone 676'), 'value':   DATA_VERSION + '_O3_676.nc'},
    {'label': _('Ozone 686'), 'value':     DATA_VERSION + '_O3_686.nc'},
    {'label': _('Carbonyl sulfide'), 'value':     DATA_VERSION + '_OCS.nc'},
     {'label': _('Carbonyl sulfide 623'), 'value':      DATA_VERSION + '_OCS_623.nc'},


     {'label': _('Carbonyl sulfide 624'), 'value':      DATA_VERSION + '_OCS_624.nc'},
    {'label': _('Carbonyl sulfide 632'), 'value':      DATA_VERSION + '_OCS_632.nc'},
    {'label': _('Phosphorus'), 'value':      DATA_VERSION + '_P.nc'},
    {'label': _('Polyacrylonitrile'), 'value':    DATA_VERSION + '_PAN.nc'},
    {'label': _('Sulfur hexafluoride'), 'value':      DATA_VERSION + '_SF6.nc'},
    {'label': _('Sulfur dioxide'), 'value':      DATA_VERSION + '_SO2.nc'},
    #{'label': _('T'), 'value':       'ACEFTS_L2_v5p0_T.nc'}#!!!!!
            ],  #End gas_options

    ]


@babel.localeselector
def get_locale():
    # if the user has set up the language manually it will be stored in the session,
    # so we use the locale from the user settings
    # try:
    #     language = session['language']
    # except KeyError:
    #     language = None
    # if language is not None:
    #     return language
    # else:
    #     return 'en'
    return app_config.DEFAULT_LANGUAGE


@app.server.route('/language/<language>')
def set_language(language=None):
    """Sets the session language, then refreshes the page
    """
    session['language'] = app_config.DEFAULT_LANGUAGE

    return redirect(url_for('/'))


# Main
if __name__ == '__main__':
     #app.run_server(debug=True)  # For development/testing

     app.run_server(debug=False, host='0.0.0.0', port=8888)  # For the server

print('Scisat loaded.')
