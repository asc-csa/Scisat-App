# -*- coding: utf-8 -*-
import dash
import cartopy.feature as cf
import configparser
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_dangerously_set_inner_html
import plotly.graph_objs as go
import pandas as pd
import datetime as dt
from dash.dependencies import Input, Output, State
import flask
from io import StringIO
from flask_babel import _ ,Babel
from flask import session, redirect, url_for

from scipy.io import netcdf #### <--- This is the library to import data
import numpy as np
import datetime

#==========================================================================================
# load data and transform as needed


external_stylesheets = ['https://wet-boew.github.io/themes-dist/GCWeb/assets/favicon.ico',
                        'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
                        'https://wet-boew.github.io/themes-dist/GCWeb/css/theme.min.css',
                        'https://wet-boew.github.io/themes-dist/GCWeb/wet-boew/css/noscript.min.css']  # Link to external CSS

external_scripts = [
    'https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.js',
    'https://wet-boew.github.io/themes-dist/GCWeb/wet-boew/js/wet-boew.min.js',
    'https://wet-boew.github.io/themes-dist/GCWeb/js/theme.min.js',
    'https://cdn.plot.ly/plotly-locale-de-latest.js',

]

LAT_MIN, LAT_MAX, LON_MIN, LON_MAX = -90, 90, -180, 180
START_DATE, END_DATE = None, None
GAZ_LIST = ""
ALT_RANGE = [0,150]
DEFAULT_DF = None

def get_config_dict():
    config = configparser.RawConfigParser()
    config.read('config.cfg')
    if not hasattr(get_config_dict, 'config_dict'):
        get_config_dict.config_dict = dict(config.items('TOKENS'))
    return get_config_dict.config_dict

if __name__ == '__main__':
     path_data=r"data"
     prefixe=""
#     app.run_server(debug=True)  # For development/testing
     from header_footer import gc_header_en, gc_footer_en, gc_header_fr, gc_footer_fr
     tokens = get_config_dict()



     app = dash.Dash(__name__,meta_tags=[{"name": "viewport", "content": "width=device-width"}],external_stylesheets=external_stylesheets,external_scripts=external_scripts,)
     app.title="SCISAT : application d’exploration des données de composition atmosphérique | data exploration application for atmospheric composition"
     server = app.server
     server.config['SECRET_KEY'] = tokens['secret_key']  # Setting up secret key to access flask session
     babel = Babel(server)  # Hook flask-babel to the app




else :

    path_data=r"applications/scisat/data"
    prefixe="/scisat"
    from applications.alouette.header_footer import gc_header_en, gc_footer_en, gc_header_fr, gc_footer_fr
    tokens = get_config_dict()
    app = dash.Dash(
    __name__,
    requests_pathname_prefix='/scisat/',
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    external_stylesheets=external_stylesheets,
    external_scripts=external_scripts,
)
    app.title="SCISAT : application d’exploration des données de composition atmosphérique | data exploration application for atmospheric composition"
    server = app.server
    server.config['SECRET_KEY'] = tokens['secret_key']  # Setting up secret key to access flask session
    babel = Babel(server)  # Hook flask-babel to the app



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
        Dataframe of all the gas concentrations with columns :
            altitudes (from 0.5 to 149.5), Mean on altitude (Alt_Mean), date,
            Latitude (lat) and Longitude (long)


    """
    if type(file)==list:
        file=file[0]

    gaz = file.strip().split('.')[0].strip().split('_')[3:]
    if len(gaz)>1:
        gaz = gaz[0]+'_'+gaz[1]
    else:
        print(gaz)
        gaz=gaz[0]

    name=path_to_files+'/'+file
    nc = netcdf.netcdf_file(name,'r')
    #Trier / définir rapido les donnéeset les variables
    fillvalue1 = -999.
    months=np.copy(nc.variables['month'][:])
    years = np.copy(nc.variables['year'][:])
    days = np.copy(nc.variables['day'][:])
    #hours = np.copy(nc.variables['hour'][:])

    lat = np.copy(nc.variables['latitude'][:])
    long =np.copy( nc.variables['longitude'][:])
    alt = np.copy(nc.variables['altitude'][:])

    data = np.copy(nc.variables[gaz][:]) #valeurs de concentration [ppv]
    data[data == fillvalue1] = np.nan #Remplacer les données vides

    data = data[:,alt_range[0]:alt_range[1]] #Choisir les données dans le range d'altitude

    df = pd.DataFrame(data,columns=alt[alt_range[0]:alt_range[1]])

    #Trie données abérrantes
    df[df>1e-5]=np.nan
    std=df.std()
    mn=df.mean()
    maxV = mn+3*std
    minV = mn-3*std
    df[df>maxV]=np.nan
    df[df<minV]=np.nan

    #Colonne de dates
    date=[]
    for i in range (len(days)):
        date.append(datetime.datetime(years[i],months[i],days[i]))#,hours[i]))

    data_meanAlt = np.nanmean(df,1) #Moyenne sur l'altitude #!!! À revérifier scientifiquement
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

    return df

# Dropdown options
#======================================================================================
# Controls for webapp
gaz_name_options = [
    {'label': _('Acetone'), 'value': 'ACEFTS_L2_v4p1_acetone.nc'},
    {'label': _('Acetylene'), 'value': 'ACEFTS_L2_v4p1_C2H2.nc'},
    {'label': _('Ethane'), 'value':  'ACEFTS_L2_v4p1_C2H6.nc'},
    {'label': _('Trichlorofluoromethane'), 'value': 'ACEFTS_L2_v4p1_CCl3F.nc'},
    {'label': _('Carbon tetrachloride'), 'value':  'ACEFTS_L2_v4p1_CCl4.nc'},

    {'label': _('Carbon tetrafluoride'), 'value':  'ACEFTS_L2_v4p1_CF4.nc'},
    {'label': _('Trichlorotrifluoroethane'), 'value':  'ACEFTS_L2_v4p1_CFC113.nc'},
    {'label': _('Chloromethane'), 'value':  'ACEFTS_L2_v4p1_CH3Cl.nc'},
    {'label': _('Acetonitrite'), 'value':  'ACEFTS_L2_v4p1_CH3CN.nc'},
    {'label': _('Methanol'), 'value':  'ACEFTS_L2_v4p1_CH3OH.nc'},
    {'label': _('Methane'), 'value':  'ACEFTS_L2_v4p1_CH4.nc'},

    {'label': _('Methane 212'), 'value':  'ACEFTS_L2_v4p1_CH4_212.nc'},
    {'label': _('Methane 311'), 'value':  'ACEFTS_L2_v4p1_CH4_311.nc'},
    {'label': _('Difluorochloromethane'), 'value':   'ACEFTS_L2_v4p1_CHF2Cl.nc'},
    {'label': _('Trifluoromethane'), 'value':  'ACEFTS_L2_v4p1_CHF3.nc'},
    {'label': _('Chlorine monoxide'), 'value':  'ACEFTS_L2_v4p1_ClO.nc'},
    {'label': _('Chlorine nitrate'), 'value':  'ACEFTS_L2_v4p1_ClONO2.nc'},

    {'label': _('Carbon monoxide'), 'value':  'ACEFTS_L2_v4p1_CO.nc'},
    {'label': _('Carbon dioxide'), 'value':  'ACEFTS_L2_v4p1_CO2.nc'},
    {'label': _('Carbon dioxide 627'), 'value':   'ACEFTS_L2_v4p1_CO2_627.nc'},
    {'label': _('Carbon dioxide 628'), 'value':  'ACEFTS_L2_v4p1_CO2_628.nc'},
    {'label': _('Carbon dioxide 636'), 'value':  'ACEFTS_L2_v4p1_CO2_636.nc'},
    {'label': _('Carbon dioxide 637'), 'value':  'ACEFTS_L2_v4p1_CO2_637.nc'},


    {'label': _('Carbon dioxide 638'), 'value':   'ACEFTS_L2_v4p1_CO2_638.nc'},
    {'label': _('Phosgene'), 'value':  'ACEFTS_L2_v4p1_COCl2.nc'},
    {'label': _('Carbonyl chlorine fluoride'), 'value':  'ACEFTS_L2_v4p1_COClF.nc'},
    {'label': _('Carbonyl fluoride'), 'value':   'ACEFTS_L2_v4p1_COF2.nc'},
    {'label': _('Carbon monoxide 27'), 'value':  'ACEFTS_L2_v4p1_CO_27.nc'},
    {'label': _('Carbon monoxide 28'), 'value':   'ACEFTS_L2_v4p1_CO_28.nc'},

     {'label': _('Carbon monoxide 36'), 'value':   'ACEFTS_L2_v4p1_CO_36.nc'},
    {'label': _('Carbon monoxide 38'), 'value':   'ACEFTS_L2_v4p1_CO_38.nc'},
    {'label': _('GLC'), 'value':    'ACEFTS_L2_v4p1_GLC.nc'},
    {'label': _('Formaldehyde'), 'value':   'ACEFTS_L2_v4p1_H2CO.nc'},
    {'label': _('Water'), 'value':   'ACEFTS_L2_v4p1_H2O.nc'},
    {'label': _('Hydrogen peroxide'), 'value':   'ACEFTS_L2_v4p1_H2O2.nc'},


     {'label': _('Water 162'), 'value':    'ACEFTS_L2_v4p1_H2O_162.nc'},
    {'label': _('Water 171'), 'value':    'ACEFTS_L2_v4p1_H2O_171.nc'},
    {'label': _('Water 181'), 'value':     'ACEFTS_L2_v4p1_H2O_181.nc'},
    {'label': _('Water 182'), 'value':   'ACEFTS_L2_v4p1_H2O_182.nc'},
    {'label': _('Hydrochlorofluorocarbon 141b'), 'value':    'ACEFTS_L2_v4p1_HCFC141b.nc'},
    {'label': _('Hydrochlorofluorocarbon 142b'), 'value':    'ACEFTS_L2_v4p1_HCFC142b.nc'},
    {'label': _('Hydrochloric acid'), 'value':     'ACEFTS_L2_v4p1_HCl.nc'},



    {'label': _('Hydrogen cyanide'), 'value':   'ACEFTS_L2_v4p1_HCN.nc'},
    {'label': _('Formic acid'), 'value':   'ACEFTS_L2_v4p1_HCOOH.nc'},
    {'label': _('Hydrogen fluoride'), 'value':    'ACEFTS_L2_v4p1_HF.nc'},
    {'label': _('Hydrofluorocarbon 134a'), 'value':   'ACEFTS_L2_v4p1_HFC134a.nc'},
    {'label': _('Nitric acid'), 'value':  'ACEFTS_L2_v4p1_HNO3.nc'},
    {'label': _('Nitric acid 156'), 'value':  'ACEFTS_L2_v4p1_HNO3_156.nc'},


    {'label': _('Peroxynitric acid'), 'value':   'ACEFTS_L2_v4p1_HO2NO2.nc'},
    {'label': _('Nitrogen'), 'value':  'ACEFTS_L2_v4p1_N2.nc'},
    {'label': _('Nitrous oxide'), 'value':  'ACEFTS_L2_v4p1_N2O.nc'},
    {'label': _('Dinitrogen pentaoxide'), 'value':    'ACEFTS_L2_v4p1_N2O5.nc'},
    {'label': _('Nitrous oxide 447'), 'value':   'ACEFTS_L2_v4p1_N2O_447.nc'},
    {'label': _('Nitrous oxide 448'), 'value':    'ACEFTS_L2_v4p1_N2O_448.nc'},

     {'label': _('Nitrous oxide 456'), 'value':    'ACEFTS_L2_v4p1_N2O_456.nc'},
    {'label': _('Nitrous oxide 546'), 'value':   'ACEFTS_L2_v4p1_N2O_546.nc'},
    {'label': _('Nitrous monoxide 447'), 'value':     'ACEFTS_L2_v4p1_NO.nc'},
    {'label': _('Nitrogen dioxide'), 'value':    'ACEFTS_L2_v4p1_NO2.nc'},
    {'label': _('Nitrogen dioxide 656'), 'value':    'ACEFTS_L2_v4p1_NO2_656.nc'},
    {'label': _('Oxygen'), 'value':    'ACEFTS_L2_v4p1_O2.nc'},


     {'label': _('Ozone'), 'value':     'ACEFTS_L2_v4p1_O3.nc'},
    {'label': _('Ozone 667'), 'value':     'ACEFTS_L2_v4p1_O3_667.nc'},
    {'label': _('Ozone 668'), 'value':     'ACEFTS_L2_v4p1_O3_668.nc'},
    {'label': _('Ozone 676'), 'value':   'ACEFTS_L2_v4p1_O3_676.nc'},
    {'label': _('Ozone 686'), 'value':     'ACEFTS_L2_v4p1_O3_686.nc'},
    {'label': _('Carbonyl sulfide'), 'value':     'ACEFTS_L2_v4p1_OCS.nc'},
     {'label': _('Carbonyl sulfide 623'), 'value':      'ACEFTS_L2_v4p1_OCS_623.nc'},


     {'label': _('Carbonyl sulfide 624'), 'value':      'ACEFTS_L2_v4p1_OCS_624.nc'},
    {'label': _('Carbonyl sulfide 632'), 'value':      'ACEFTS_L2_v4p1_OCS_632.nc'},
    {'label': _('Phosphorus'), 'value':      'ACEFTS_L2_v4p1_P.nc'},
    {'label': _('Polyacrylonitrile'), 'value':    'ACEFTS_L2_v4p1_PAN.nc'},
    {'label': _('Sulfur hexafluoride'), 'value':      'ACEFTS_L2_v4p1_SF6.nc'},
    {'label': _('Sulfur dioxide'), 'value':      'ACEFTS_L2_v4p1_SO2.nc'},
 #    {'label': _('Temperature'), 'value':    'ACEFTS_L2_v4p0_T.nc'} #!!! Est ce qu'on la met?

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
    title="Gas Concentration Overview",
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
                        html.A(
                            html.Button("", id="learn-more-button", className="dash_button"),
                            href="https://www.asc-csa.gc.ca/eng/satellites/scisat/about.asp",id='learn-more-link'
                        ),
                        html.A(
                            html.Button('FR', id='language-button', className="dash_button"),
                            href='/scisat/language/fr', id='language-link'
                        ),
                    ],
                    className="four columns",
                    id="button-div",
                    style={"text-align": "center"}
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
                                 html.P(id="description-1"),
                                 html.P(id="description-2"),
                                 html.A(
                                    html.P(id="github-link"),
                                    href = "https://github.com/asc-csa",
                                    title = "ASC-CSA Github"
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
            [
                html.Div(
                    [
                        html.Div(   #Gas Picker
                            [
                                html.Div([
                                    dbc.Alert(color="secondary", id="gas_alert", is_open=False, fade=False, style={"margin-top":"0.5em"}),
                                ]),
                                html.P(
                                    id="gas-text",
                                    className="control_label",
                                ),
                                html.Div([
                                html.Label(
                                    dcc.Dropdown(
                                        id="gaz_list",
                                        options= gaz_name_options,
                                        multi=False,
                                        value='ACEFTS_L2_v4p1_O3.nc',
                                        className="dcc_control",

                                    )
                                ),

                                  html.Span(children=html.P(id="gas_selection"),className="wb-inv")]),

                               html.Div([
                                html.Div([
                                    dbc.Alert(color="secondary", id="pos_alert", is_open=False, fade=False, style={"margin-top":"0.5em"}),
                                ]),
                                html.Div( #Latitude picker
                                    [
                                        html.P(
                                            id="latitude-text",
                                            className="control_label",
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
                                                style={"margin-left": "5px"},
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
                                                style={"margin-left": "5px"},
                                                debounce=True
                                            )
                                        ]),
                                      html.Span(children=html.P(id="lat_selection"),className="wb-inv")],
                                    className="one-half column"
                                ),
                                html.Div( #longitude picker
                                    [
                                        html.P(
                                            id="longitude-text",
                                            className="control_label",
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
                                                style={"margin-left": "5px"},
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
                                                style={"margin-left": "5px"},
                                                debounce=True
                                            ),
                                        ]),
                                     html.Span(children=html.P(id="lon_selection"),className="wb-inv") ],
                                 #   className="one-half column"
                                    ),
                            ],
                            id="map-options",
                            ), #End of map options
                                ]),
                        html.Div(
                            [dcc.Graph(id="selector_map",
                                       config={
                                           "displaylogo": False,
                                           "displayModeBar": False
                                       }
                                       )],
                        ),
                        html.Div ([html.P(id="Map_description", style={"margin-top": "2em"})]),   #!!!!!!! Tesssst
                    ],
                    id="left-column-1",
                    style={"flex-grow": 1},
                    className="six columns",
                    ),
                html.Div(
                    [  # Right side of container
                    html.Div([ #Year selection + download button
                                html.Div([
                                    dbc.Alert(color="secondary", id="date_alert", is_open=False, fade=False, style={"margin-top":"0.5em"}),
                                ]),
                                html.P(
                                    id="yearslider-text",
                                    className="control_label",
                                    ),

                                html.Div([
                                    html.Label(
                                        dcc.DatePickerRange(
                                            id='date_picker_range',
                                            start_date=dt.datetime(2004, 2, 1),
                                            end_date=dt.datetime(2020, 5, 5),
                                            min_date_allowed=dt.datetime(2004, 2, 1),
                                            max_date_allowed=dt.date.today(),
                                            start_date_placeholder_text='Select start date',
                                            end_date_placeholder_text='Select end date',
                                            display_format="DD/MM/Y",
                                            style={"margin-top": "5px"}
                                            ),
                                        ),
                                    html.Div(id='output-container-date-picker-range')
                                    , html.Span(children=html.P(id="date_selection"),className="wb-inv")],
                                    className="one-half column"),
                                html.Div([ #Download button
                                    html.Div([
                                        html.A(
                                            html.Button(id='download-button-1', n_clicks=0, className="dash_button", style={'padding': '0px 10px'}),
                                            id='download-link-1',
                                            # download='rawdata.csv',
                                            href="",
                                            target="_blank",
                                            ),
                                        html.Span(children=html.P(id="download_selection"),className="wb-inv")]

                                        ),
                                    ],
                                    id="cross-filter-options"
                                    ),  #End download Button
                            ]),
                        #Graphique Altitude
                        html.Div([ #Choix altitude
                                html.P(id="altitude-text",
                                        className="control_label"
                                        ),
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
                                ]), #End Altitude Choice
                        html.Div([
                            html.A(
                                html.Button(id='generate-button', n_clicks=0, className="dash_button", style={'padding': '0px 10px'}),
                                id='generate',
                                target="_blank",
                                ),
                            html.Span(children=html.P(id="generate_selection"),className="wb-inv")]),
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
                                ]),   #End description

                    ],
                    id="right-column-1",
                    style={"flex-grow": 1},
                    className="six columns",
                    ), #End right side of container
            ],
            className="row flex-display pretty_container twelve columns",
            style={"justify-content": "space-evenly"}
            ),
    ])


# Builds the layout for the map displaying the time series
def build_stats():
    return html.Div([
        html.Div([
                html.Div(
                    [
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
        html.Div([""], id='gc-header'),
        html.Div(
            [
                dcc.Store(id="aggregate_data"),
                html.Div(id="output-clientside"),  # empty Div to trigger javascript file for graph resizing

                build_header(),
                build_filtering(),
                build_stats(),
            ],
            id="mainContainer",
            style={"display": "flex", "flex-direction": "column", "margin": "auto", "width":"75%"},
        ),
        html.Div([""], id='gc-footer'),
        html.Div(id='none2', children=[], style={'display': 'none'}), # Placeholder element to trigger translations upon page load
    ]
)


# Helper functions

@app.callback(
    Output("pos_alert", "is_open"),
    [
        Input('lat_min','value'),
        Input('lat_max','value'),
        Input('lon_min','value'),
        Input('lon_max','value')
    ],
    [
        State("pos_alert", "is_open")
    ],
)
def update_ranges(lat_min,lat_max,lon_min,lon_max, is_open):
    global LAT_MIN, LAT_MAX, LON_MIN, lON_MAX
    s = False
    if pos_validation(lat_min, lat_max, lon_min, lon_max):
        LAT_MIN, LAT_MAX, LON_MIN, LON_MAX = lat_min, lat_max, lon_min, lon_max
    else:
        s = True
    return s

@app.callback(
    Output("date_alert", "is_open"),
    [   Input("date_picker_range", "start_date"),
        Input("date_picker_range", "end_date"),
        Input("gaz_list", "value")
    ],
    [
        State("date_alert", "is_open")
    ],
)
def update_dates(start_date, end_date, gaz_list, is_open):
    global START_DATE, END_DATE
    s = False
    if date_validation(start_date,end_date,gaz_list):
        START_DATE, END_DATE = start_date, end_date
    else:
        s = True
    return s

@app.callback(
    Output("gas_alert", "is_open"),
    [
        Input("gaz_list", "value"),
    ],
    [
        State("gas_alert", "is_open")
    ],
)
def update_gas(gaz_list, is_open):
    global GAZ_LIST
    s = False
    if gas_validation(gaz_list):
        GAZ_LIST = gaz_list
    else:
        s = True
    return s

@app.callback(
    Output("placeholder","value"),
    [Input("alt_range", "value")]
)
def update_alt(alt_range):
    global ALT_RANGE
    ALT_RANGE = alt_range
    return ""

@app.callback(
    [Output("selector_map", "figure"),Output("viz_chart", "figure"),Output("count_graph", "figure"),Output("download-link-1", "href"),Output("filtering_text", "children")],
    [Input("generate-button","n_clicks")]
)
def controller(n_clicks):
    global START_DATE, END_DATE, GAZ_LIST, LAT_MIN, LAT_MAX, LON_MIN, LON_MAX, ALT_RANGE
    df = data_reader(GAZ_LIST, r'data', START_DATE, END_DATE, LAT_MIN, LAT_MAX, LON_MIN, LON_MAX, ALT_RANGE)
    fig1 = generate_geo_map(df)
    fig2 = make_viz_chart(df)
    fig3 = make_count_figure(df)
    link = update_csv_link()
    nbr = update_filtering_text(df)
    return fig1, fig2, fig3, link, nbr

# Selectors -> !!! À voir ce qu'on veut rajouter ?
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


@app.callback(
    [Output('date_picker_range', 'min_date_allowed'),
    Output('date_picker_range', 'max_date_allowed'),
    Output('date_picker_range', 'start_date'),
    Output('date_picker_range', 'end_date')],

    [ Input("gaz_list", "value")]
    )
def update_picker(gaz_list):
     global DEFAULT_DF
     df = data_reader(gaz_list, r'data')
     DEFAULT_DF = databin(df,3)
     return df.date.min().to_pydatetime(),df.date.max().to_pydatetime(),df.date.min().to_pydatetime(),df.date.max().to_pydatetime()



# Selectors -> Image download link
#
#@app.callback(
#    Output("download-link-2", "href"),
#    [
#        Input("gaz_list", "value"),
#        Input('date_picker_range', "start_date"),
#        Input('date_picker_range', "end_date"),
#        Input("lat_min", "value"),
#        Input("lat_max", "value"),
#        Input("lon_min", "value"),
#        Input("lon_max", "value"),
#
#    ],
#)
#def update_images_link(gaz,date, lat_min, lat_max, lon_min, lon_max):
#    """Updates the link to the Ionogram images download
#
#    Returns
#    -------
#    link : str
#        Link that redirects to the Flask route to download the CSV based on selected filters
"""

    link = '/dash/downloadImages?start_date={}&end_date={}&lat_min={}&lat_max={}&lon_min={}&lon_max={}&ground_stations={}'\
        .format(start_date, end_date, lat_min, lat_max, lon_min, lon_max, ground_stations)  #!!!!! à corriger selon donnée

    return link


from io import BytesIO



@app.server.route('/dash/downloadImages')
def download_images():  #!!!!! à corriger selon donnée

    start_date = dt.datetime.strptime(flask.request.args.get('start_date').split('T')[0], '%Y-%m-%d')  # Convert strings to datetime objects
    end_date = dt.datetime.strptime(flask.request.args.get('end_date').split('T')[0], '%Y-%m-%d')

    lat_min = flask.request.args.get('lat_min')
    lat_max = flask.request.args.get('lat_max')
    lon_min = flask.request.args.get('lon_min')
    lon_max = flask.request.args.get('lon_max')

    gaz_list = flask.request.args.get('gaz_list') # parses a string representation of ground_stations


    df =data_reader(gaz_list,r'data',start_date,end_date,lat_min,lat_max,lon_min,lon_max)



    # Store the zip in memory
    memory_file = BytesIO()
    max_download = 100  # Temporary limit on number of ionograms that can be downloaded
    with ZipFile(memory_file, 'w') as zf:
        for index, row in dff.iterrows():
            if os.path.exists(row['file_path']) and max_download > 0:
                max_download -= 1
                zf.write(row['file_path'], arcname=row['file_name']+'.png')  # Write each image into the zip

        # Making the output csv from the filtered df
        csv_buffer = StringIO()
        dff.to_csv(csv_buffer, index=False)
        zf.writestr('Metadata_of_selected_ionograms.csv', csv_buffer.getvalue())

    memory_file.seek(0)

    return flask.send_file(memory_file, attachment_filename='Ionograms.zip', as_attachment=True)
"""


# Selectors -> CSV Link
def update_csv_link():
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
    global START_DATE, END_DATE, LAT_MIN, LAT_MAX, LON_MIN, LON_MAX, GAZ_LIST, ALT_RANGE
    link = prefixe+'/dash/downloadCSV?start_date={}&end_date={}&lat_min={}&lat_max={}&lon_min={}&lon_max={}&gaz_list={}&alt_range={}' \
            .format(START_DATE, END_DATE, LAT_MIN, LAT_MAX, LON_MIN, LON_MAX, GAZ_LIST, ALT_RANGE)

    return link

from flask import make_response



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
    df =data_reader(gaz_list,r'data',start_date,end_date,lat_min,lat_max,lon_min,lon_max,alt_range)

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

    return output



#============================================================================
# Selected Data by sliding mouse
#!!!!!!!!!!!!!!!!!!!
#@app.callback(
#    [Output("lat_min", "value"),
#    Output("lat_max", "value"),
#    Output("lon_min", "value"),
#    Output("lon_max", "value")],
#    [Input("selector_map", "selectedData"), Input("selector_map", "clickData")]
#)
#def update_bar_selector(value, clickData):
#    holder_lat = []
#    holder_lon = []
#    if clickData:
#        try:
#            holder_lat.append(str(int(clickData["points"][0]["lat"])))
#            holder_lon.append(str(int(clickData["points"][0]["long"])))
#        except KeyError:
#            ""
#    if value:
#        for x in value["points"]:
#            holder_lat.append(((x["lat"])))
#            holder_lon.append(((x["long"])))
#
#    holder_lat  = np.array( holder_lat)
#    holder_lon  = np.array( holder_lon)
#    if len(holder_lat)!=0 :
#        return int(np.min(holder_lat)),int(np.max(holder_lat)),int(np.min(holder_lon)),int(np.max(holder_lon))
#    else :
#        return -90,90,-180,180


# Clear Selected Data if Click Data is used
#@app.callback(
#    Output("selector_map", "selectedData"),
#    [Input("selector_map", "clickData")]
#    )
#def update_selected_data(clickData):
#    if clickData:
#        return {"points": []}

#============================================================================


# Selectors -> count graph
def make_count_figure(df):
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
    global ALT_RANGE
    concentration=df[ALT_RANGE[0]:ALT_RANGE[1]]
    # concentration=np.array(concentration,dtype=np.float32)
    # concentration=np.ma.masked_array(concentration, np.isnan(concentration))
    xx=concentration.mean(axis=0)
    err_xx=concentration.std(axis=0)

    # layout_count = copy.deepcopy(layout)
    data = [
        dict(
            type="scatter",
            x=xx,
            y=df.columns[ALT_RANGE[0]:ALT_RANGE[1]],
            error_x=dict(type='data', array=err_xx,thickness=0.5),#!!!!!!!!!! Ne semble pas marcher
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

    return figure


def pos_validation(lat_min,lat_max,lon_min,lon_max):
    try:
        s = ((lat_min < lat_max) and (lat_min >= -90) and (lat_max <= 90) and (lon_min < lon_max) and (lon_min >= -180) and (lon_max <= 180))
    except TypeError:
        s = False
    return s

def date_validation(start_date, end_date, gaz_list):
    start = dt.datetime.strptime(start_date.split('T')[0], '%Y-%m-%d')
    end = dt.datetime.strptime(end_date.split('T')[0], '%Y-%m-%d')
    df =data_reader(gaz_list,r'data')
    MIN_DATE=df.date.min().to_pydatetime()
    MAX_DATE=df.date.max().to_pydatetime()
    return ((start>=MIN_DATE) and (start <= end) and (start <= MAX_DATE) and (end >= MIN_DATE) and (end <= MAX_DATE))

def gas_validation(gaz_list):
    try:
        if type(gaz_list)==list:
            gaz_list=gaz_list[0]
        name=path_data+'/'+gaz_list
        nc = netcdf.netcdf_file(name,'r')
    except FileNotFoundError:
        return False
    return True

#=====================================================================
#this is where the graph are generated

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
    global DEFAULT_DF
    dft = DEFAULT_DF

    # We decide the binning that needs to be done, if any, based on lat/long range selected
    hm = True
    area = (df['lat'].max()-df['lat'].min())*(df['long'].max()-df['long'].min())
    if area<1800:
        hm = False
    elif area<16200 and area>=1800:
        df = databin(df,1)
    else:
        df = databin(df,3)

    # We collect the coordinates of all coastlines geometries from cartopy
    x_coords = []
    y_coords = []
    for coord_seq in cf.COASTLINE.geometries():
        x_coords.extend([k[0] for k in coord_seq.coords] + [np.nan])
        y_coords.extend([k[1] for k in coord_seq.coords] + [np.nan])

    # We create a heatmap of the binned data
    if hm:
        fig= go.Figure(
                    go.Heatmap(
                            showscale=True,
                            x=df['long'],
                            y=df['lat'],
                            z=df['Alt_Mean'],
                            zmax=dft['Alt_Mean'].max(),
                            zmin=dft['Alt_Mean'].min(),
                            #zsmooth='fast', # Turned off smoothing to avoid interpolations
                            opacity=1,
                            name = "",
                            hoverongaps = False,
                            hovertemplate = "Lat.: %{y}°<br>Long.: %{x}°<br>Concentration: %{z:.3e} ppv",
                            colorbar=dict(
                                title=dict(
                                    text=_("Gas Concentration [ppv] (mean on altitude and position) "),
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
                hovertemplate = "Lat.: %{y}°<br>Long.: %{x}°<br>Concentration: %{meta:.3e} ppv",
                marker= dict(
                    size=10,
                    color=df['Alt_Mean'],
                    cmin=dft['Alt_Mean'].min(),
                    cmax=dft['Alt_Mean'].max(),
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

    return fig


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
    to_bin = lambda x: np.round(x / step) * step
    # We map the current data into the bins
    df["lat"] = df['lat'].map(to_bin)
    df["long"] = df['long'].map(to_bin)
    # We return a mean value of all overlapping data to ensure there are no overlaps
    return df.groupby(["lat", "long"]).mean().reset_index()


# Selectors -> viz chart (95% CI)
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
    concentration =df.groupby('date')['Alt_Mean'].mean()
    concentration =  concentration.groupby(concentration.index.floor('D')).mean()
    bins=concentration
    date=df["date"].map(pd.Timestamp.date).unique()

    # bucketing the data
    """
    if x_axis_selection == 'timestamp':
        dff.index = dff["timestamp"]

        index_month = dt.date(dff.index.min().year, dff.index.min().month, 1)
        end_month = dt.date(dff.index.max().year, dff.index.max().month, 1)

        while index_month <= end_month:
            index_month_data = dff[(dff['timestamp'] > pd.Timestamp(index_month))
                                & (dff['timestamp'] < pd.Timestamp(index_month + relativedelta(months=1)))]
                # dff[index_month: index_month + relativedelta(months=1)]

            n = len(index_month_data[y_axis_selection])
            if n == 0:
                estimated_means.append(None)
                ci_upper_limits.append(None)
                ci_lower_limits.append(None)
            else:
                bin_mean = mean(index_month_data[y_axis_selection])
                std_err = sem(index_month_data[y_axis_selection])
                error_range = std_err * t.ppf((1 + confidence) / 2, n - 1)  # t.ppf should be 1.96 given big enough n value

                estimated_means.append(bin_mean)
                ci_upper_limits.append(bin_mean + error_range)
                ci_lower_limits.append(bin_mean - error_range if bin_mean - error_range >= 0 else 0)
                bins.append(index_month)

            index_month += relativedelta(months=1)

    elif x_axis_selection == 'latitude' or x_axis_selection == 'longitude':
        if x_axis_selection == 'latitude':
            step = 5
            index_range = range(-90,90,step)
        if x_axis_selection == 'longitude':
            step = 5
            index_range = range(-180, 180, step)


        for i in index_range:
            bin_data = dff[(dff[x_axis_selection] >= i)
                                & (dff[x_axis_selection] < i + step)]
                # dff[index_month: index_month + relativedelta(months=1)]

            n = len(bin_data[y_axis_selection])
            if n == 0:
                estimated_means.append(None)
                ci_upper_limits.append(None)
                ci_lower_limits.append(None)
            else:
                bin_mean = mean(bin_data[y_axis_selection])
                std_err = sem(bin_data[y_axis_selection])
                error_range = std_err * t.ppf((1 + confidence) / 2, n - 1)  # t.ppf should be 1.96 given big enough n value

                estimated_means.append(bin_mean)
                ci_upper_limits.append(bin_mean + error_range)
                ci_lower_limits.append(bin_mean - error_range if bin_mean - error_range >= 0 else 0)
                bins.append(i)
    """
    data = [
        dict(
            #mode="lines",
            name="",
            type="scatter",
            x=date,
            y=bins,
            #line_color="rgba(255,255,255,0)",
            fillcolor="rgba(255,255,255,0)",
            line={'color': 'rgb(18,99,168)'},
            connectgaps=True,
            showlegend=False,
        ),

    ]

    layout = dict(
        autosize=True,
        automargin=True,
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        # legend=dict(font=dict(size=10), orientation="h"),
        title=_("Time Series"),

        xaxis={"title": _('Date'), "automargin": True} ,

        yaxis =  dict(
           title = _("Concentration [ppv]"),
           automargin=True,
           showexponent = 'all',
           exponentformat = 'e'
           ),

        height=500,
        transition={'duration': 500},
    )

    figure = dict(data=data, layout=layout)

    return figure
"""
# Selectors -> viz map
@app.callback(
    Output("viz_map", "figure"),
    # [Input("visualize-button", "n_clicks")],
    [

        Input('date_picker_range', "value"),
        Input("stat_selection", "value"),
        Input("y_axis_selection_2", "value"),
        Input("lat_min", "value"),
        Input("lat_max", "value"),
        Input("lon_min", "value"),
        Input("lon_max", "value"),
        Input("gaz_list", "value"),
    ],
)


def make_viz_map(date, stat_selection, var_selection, lat_min, lat_max, lon_min, lon_max, ground_stations=None):
"""
"""
    Create and update a map visualizing the selected ionograms' values for the selected variable by ground station.

    The size of the ground station marker indicates the number of ionograms from that ground station.

    Parameters
    ----------

    date : str
        Ending date stored as a str

    stat_selection : string
        The type of average used for the size of the ground station markers stored as a string (e.g 'Mean')

    var_selection : string
        The variable corresponding to the size of the ground station markers on the maps elected by the dropdown stored
        as a string (e.g 'max_depth')

    lat_min : double
        Minimum value of the latitude stored as a double.

    lat_max : double
        Maximum value of the latitude stored as a double.

    lon_min : double
        Minimum value of the longitude stored as a double.

    lon_max : double
        Maximum value of the longitude stored as a double.

    ground_stations : list
        Ground station name strings stored in a list (e.g. ['Resolute Bay, No. W. Territories'])

    Returns
    -------
    dict
        A dictionary containing 2 key-value pairs: the selected data as an array of Plotly scattermapbox graph objects
        and the map's layout as a Plotly layout graph object.
"""
"""
    start_time = dt.datetime.now()

     # Convert strings to datetime objects
    date = dt.datetime.strptime(date.split('T')[0], '%Y-%m-%d')

    df =data_reader(gaz_list,r'data',start_date,end_date)

    traces = []
    for station_details, dfff in filtered_data.groupby(["station_name", "lat", "lon"]):
        trace = dict(
            station_name=station_details[0],
            lat=station_details[1],
            lon=station_details[2],
            count=len(dfff),
            mean=filtered_data.groupby(["station_name", "lat", "lon"])[var_selection].mean()[station_details[0]][0],
            median=filtered_data.groupby(["station_name", "lat", "lon"])[var_selection].median()[station_details[0]][0]
        )
        traces.append(trace)

    df_stations = pd.DataFrame(traces)

    stations = []
    if traces != []:

        lat = df_stations["lat"].tolist()
        lon = df_stations["lon"].tolist()
        station_names = df_stations["station_name"].tolist()
        if stat_selection == 'mean':
            stat_values = df_stations["mean"].tolist()
        elif stat_selection == 'median':
            stat_values = df_stations["median"].tolist()

        # Count mapping from aggregated data
        stat_metric_data = {}
        stat_metric_data["min"] = df_stations[stat_selection].min()
        stat_metric_data["max"] = df_stations[stat_selection].max()
        stat_metric_data["mid"] = (stat_metric_data["min"] + stat_metric_data["max"]) / 2
        stat_metric_data["low_mid"] = (stat_metric_data["min"] + stat_metric_data["mid"]) / 2
        stat_metric_data["high_mid"] = (stat_metric_data["mid"] + stat_metric_data["max"]) / 2

        for i in range(len(df_stations)):
            val = stat_values[i]
            station_name = station_names[i]

            station = go.Scattermapbox(
                lat=[lat[i]],
                lon=[lon[i]],
                mode="markers",
                marker=dict(
                    color='white',
                    showscale=False,
                    cmin=stat_metric_data["min"],
                    cmax=stat_metric_data["max"],
                    #size=1 + (val - stat_metric_data["min"] / 10),
                    size= 1 + 25 * ((val - stat_metric_data["min"]) + stat_metric_data["min"]) / stat_metric_data["mid"],
                            # 10 + (val - stat_metric_data["min"]) / 15,
                    colorbar=dict(
                        x=0.9,
                        len=0.7,
                        title=dict(
                            text="Ground Station Overview",
                            font={"color": "#737a8d", "family": "Open Sans"},
                        ),
                        titleside="top",
                        tickmode="array",
                        tickvals=[stat_metric_data["min"], stat_metric_data["max"]],
                        ticktext=[
                            stat_metric_data["min"],
                            stat_metric_data["max"],
                        ],
                        ticks="outside",
                        thickness=15,
                        tickfont={"family": "Open Sans", "color": "#737a8d"},
                    ),
                ),
                opacity=0.6,
                #selectedpoints=selected_index,
                selected=dict(marker={"color": "#ffff00"}),
                customdata=[(station_name)],
                hoverinfo="text",
                text=station_name
                + "<br>" + stat_selection + " " + var_selection + ":"
                + str(round(val, 2))
                + "<br>lat: " + str(lat[i])
                + "<br>lon: " + str(lon[i])
            )
            stations.append(station)

    else:
        station = go.Scattermapbox(
            lat=[],
            lon=[],
            mode="markers",
            marker=dict(
                color='#1263A8',
                showscale=False,
                size=0,
                colorbar=dict(
                    x=0.9,
                    len=0.7,
                    title=dict(
                        text="No Ground Stations Selected",
                        font={"color": "#737a8d", "family": "Open Sans"},
                    ),
                    titleside="top",
                    tickmode="array",
                    ticks="outside",
                    thickness=15,
                    tickfont={"family": "Open Sans", "color": "#737a8d"},
                ),
            ),
            opacity=0.8,
            selected=dict(marker={"color": "#ffff00"}),
            customdata=[],
            hoverinfo="text",
        )
        stations.append(station)

    layout = go.Layout(
        margin=dict(l=10, r=10, t=20, b=10, pad=5),
        plot_bgcolor="#171b26",
        paper_bgcolor="#171b26",
        clickmode="event+select",
        hovermode="closest",
        showlegend=False,
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token,
            #bearing=10,
            #center=go.layout.mapbox.Center(
            #    lat=df_stations.lat.mean(), lon=df_stations.lon.mean()
            #),
            #pitch=5,
            zoom=1,
            style="mapbox://styles/plotlymapbox/cjvppq1jl1ips1co3j12b9hex",
        ),
        height=500,
        transition={'duration': 500},
    )

    print(f'make_viz_map: {(dt.datetime.now()-start_time).total_seconds()}')

    return {"data": stations, "layout": layout}
"""

# Inject the static text here after translating
# The variables in controls.py are placed here; babel does not work for translation unless it is hard coded here, not sure why. Likely has to with the way Dash builds the web app.
@app.callback(
    [
        Output("page-title", "children"),
        Output("learn-more-button", "children"),
        Output("data-ratio", "children"),
        Output("description-1", "children"),
        Output("description-2", "children"),
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
        Output("pos_alert", "children"),
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
        Output("gas-text", "children"),
        Output("download-button-1", "children"),
        Output("gaz_list", "options"),
    ],
        [Input('none', 'children')], # A placeholder to call the translations upon startup
)
def translate_static(x):
    print('Translating...')
    return [
                _("SCISAT Data Visualisation"),
                _("Learn More About SCISAT"),
                _("Data selected"),
                _("Launched on August 12, 2003, SCISAT helps a team of Canadian and international scientists improve their understanding of the depletion of the ozone layer, with a special emphasis on the changes occurring over Canada and in the Arctic. "),
                _("This application provides users the ability to select, download and visualize SCISAT's data. "),
                _("Visit our Github page to learn more about our applications."),
                _("Select Data"),
                _("Generate"),
                _("Generate from selected data"),
                _("Graph of the gas concentration in parts per volume (ppv) visualized on a world map. Each dot represents the mean concentration on the selected dates, the altitude column as well as the position. The color indicates the mean gas concentration value."),
                _("Graph showing the gas concentration in parts per volume (ppv) over the selected altitude interval. The value represents the mean concentration over the latitudes and longitudes selected, as well as the selected dates."),
                _("Time series showing the evolution of the gas concentration in parts per volume (ppv). Each data point represents the daily overall mean concentration."),
                _("Selection of the gas"),
                _("Selection of the range of latitude "),
                _("Selection of the range of longitude"),
                _("Date selection"),
                _("Download the selected dataset"),
                _("Invalid values provided. Latitude values must be between -90 and 90. Longitude values must be between -180 and 180. Minimum values must be smaller than maximum values. All values must be round numbers that are multiples of 5."),
                _("Invalid dates provided. Try dates between 01/02/2004 (Feb. 1st 2004) and 05/05/2020 (May 5th 2020)."),
                _("Missing data. The gas selected has no associated data. Please contact asc.donnees-data.csa@canada.ca."),
                _("Filter by Latitude:"),
                _("Minimum latitude"),
                _("Maximum latitude"),
                _("Filter by Longitude:"),
                _("Minimum longitude"),
                _("Maximum longitude"),
                _("Select Altitude Range:"),
                _("Select Date:"),
                _("Select Gas:"),
                _('Download Summary Data as CSV'),
                #_('Download full data as netcdf'),
                # _("Select x-axis:"),
                # _("Select y-axis:"),
                #_("Select statistic:"),
                #_("Select plotted value:"),
    [  # Gas_options
    {'label': _('Acetone'), 'value': 'ACEFTS_L2_v4p1_C3H6O.nc'},
    {'label': _('Acetylene'), 'value': 'ACEFTS_L2_v4p1_C2H2.nc'},
    {'label': _('Ethane'), 'value':  'ACEFTS_L2_v4p1_C2H6.nc'},
    {'label': _('Dichlorodifluoromethane'), 'value': 'ACEFTS_L2_v4p1_CCl2F2.nc'},
    {'label': _('Trichlorofluoromethane'), 'value': 'ACEFTS_L2_v4p1_CCl3F.nc'},
    {'label': _('Carbon tetrachloride'), 'value':  'ACEFTS_L2_v4p1_CCl4.nc'},


    {'label': _('Carbon tetrafluoride'), 'value':  'ACEFTS_L2_v4p1_CF4.nc'},
    {'label': _('Trichlorotrifluoroethane'), 'value':  'ACEFTS_L2_v4p1_CFC113.nc'},
    {'label': _('Chloromethane'), 'value':  'ACEFTS_L2_v4p1_CH3Cl.nc'},
    {'label': _('Acetonitrite'), 'value':  'ACEFTS_L2_v4p1_CH3CN.nc'},
    {'label': _('Methanol'), 'value':  'ACEFTS_L2_v4p1_CH3OH.nc'},
    {'label': _('Methane'), 'value':  'ACEFTS_L2_v4p1_CH4.nc'},

    {'label': _('Methane 212'), 'value':  'ACEFTS_L2_v4p1_CH4_212.nc'},
    {'label': _('Methane 311'), 'value':  'ACEFTS_L2_v4p1_CH4_311.nc'},
    {'label': _('Difluorochloromethane'), 'value':   'ACEFTS_L2_v4p1_CHF2Cl.nc'},
    {'label': _('Trifluoromethane'), 'value':  'ACEFTS_L2_v4p1_CHF3.nc'},
    {'label': _('Chlorine monoxide'), 'value':  'ACEFTS_L2_v4p1_ClO.nc'},
    {'label': _('Chlorine nitrate'), 'value':  'ACEFTS_L2_v4p1_ClONO2.nc'},

    {'label': _('Carbon monoxide'), 'value':  'ACEFTS_L2_v4p1_CO.nc'},
    {'label': _('Carbon dioxide'), 'value':  'ACEFTS_L2_v4p1_CO2.nc'},
    {'label': _('Carbon dioxide 627'), 'value':   'ACEFTS_L2_v4p1_CO2_627.nc'},
    {'label': _('Carbon dioxide 628'), 'value':  'ACEFTS_L2_v4p1_CO2_628.nc'},
    {'label': _('Carbon dioxide 636'), 'value':  'ACEFTS_L2_v4p1_CO2_636.nc'},
    {'label': _('Carbon dioxide 637'), 'value':  'ACEFTS_L2_v4p1_CO2_637.nc'},


    {'label': _('Carbon dioxide 638'), 'value':   'ACEFTS_L2_v4p1_CO2_638.nc'},
    {'label': _('Phosgene'), 'value':  'ACEFTS_L2_v4p1_COCl2.nc'},
    {'label': _('Carbonyl chlorofluoride'), 'value':  'ACEFTS_L2_v4p1_COClF.nc'},
    {'label': _('Carbonyl fluoride'), 'value':   'ACEFTS_L2_v4p1_COF2.nc'},
    {'label': _('Carbon monoxide 27'), 'value':  'ACEFTS_L2_v4p1_CO_27.nc'},
    {'label': _('Carbon monoxide 28'), 'value':   'ACEFTS_L2_v4p_CO_28.nc'},

     {'label': _('Carbon monoxide 36'), 'value':   'ACEFTS_L2_v4p1_CO_36.nc'},
    {'label': _('Carbon monoxide 38'), 'value':   'ACEFTS_L2_v4p1_CO_38.nc'},
    {'label': _('GLC'), 'value':    'ACEFTS_L2_v4p1_GLC.nc'},
    {'label': _('Formaldehyde'), 'value':   'ACEFTS_L2_v4p1_H2CO.nc'},
    {'label': _('Water'), 'value':   'ACEFTS_L2_v4p1_H2O.nc'},
    {'label': _('Hydrogen peroxide'), 'value':   'ACEFTS_L2_v4p1_H2O2.nc'},


     {'label': _('Water 162'), 'value':    'ACEFTS_L2_v4p1_H2O_162.nc'},
    {'label': _('Water 171'), 'value':    'ACEFTS_L2_v4p1_H2O_171.nc'},
    {'label': _('Water 181'), 'value':     'ACEFTS_L2_v4p1_H2O_181.nc'},
    {'label': _('Water 182'), 'value':   'ACEFTS_L2_v4p1_H2O_182.nc'},
    {'label': _('Hydrochlorofluorocarbon 141b'), 'value':    'ACEFTS_L2_v4p1_HCFC141b.nc'},
    {'label': _('Hydrochlorofluorocarbon 142b'), 'value':    'ACEFTS_L2_v4p1_HCFC142b.nc'},
    {'label': _('Hydrochloric acid'), 'value':     'ACEFTS_L2_v4p1_HCl.nc'},

    {'label': _('Hydrogen cyanide'), 'value':   'ACEFTS_L2_v4p1_HCN.nc'},
    {'label': _('Formic acid'), 'value':   'ACEFTS_L2_v4p1_HCOOH.nc'},
    {'label': _('Hydrogen fluoride'), 'value':    'ACEFTS_L2_v4p1_HF.nc'},
    {'label': _('Hydrofluorocarbon 134a'), 'value':   'ACEFTS_L2_v4p1_HFC134a.nc'},
    {'label': _('Nitric acid'), 'value':  'ACEFTS_L2_v4p1_HNO3.nc'},
    {'label': _('Nitric acid 156'), 'value':  'ACEFTS_L2_v4p1_HNO3_156.nc'},


    {'label': _('Peroxynitric acid'), 'value':   'ACEFTS_L2_v4p1_HO2NO2.nc'},
    {'label': _('Nitrogen'), 'value':  'ACEFTS_L2_v4p1_N2.nc'},
    {'label': _('Nitrous oxide'), 'value':  'ACEFTS_L2_v4p1_N2O.nc'},
    {'label': _('Dinitrogen pentaoxide'), 'value':    'ACEFTS_L2_v4p1_N2O5.nc'},
    {'label': _('Nitrous oxide 447'), 'value':   'ACEFTS_L2_v4p1_N2O_447.nc'},
    {'label': _('Nitrous oxide 448'), 'value':    'ACEFTS_L2_v4p1_N2O_448.nc'},

     {'label': _('Nitrous oxide 456'), 'value':    'ACEFTS_L2_v4p1_N2O_456.nc'},
    {'label': _('Nitrous oxide 546'), 'value':   'ACEFTS_L2_v4p1_N2O_546.nc'},
    {'label': _('Nitrous monoxide 447'), 'value':     'ACEFTS_L2_v4p1_NO.nc'},
    {'label': _('Nitrogen dioxide'), 'value':    'ACEFTS_L2_v4p1_NO2.nc'},
    {'label': _('Nitrogen dioxide 656'), 'value':    'ACEFTS_L2_v4p1_NO2_656.nc'},
    {'label': _('Oxygen'), 'value':    'ACEFTS_L2_v4p1_O2.nc'},


     {'label': _('Ozone'), 'value':     'ACEFTS_L2_v4p1_O3.nc'},
    {'label': _('Ozone 667'), 'value':     'ACEFTS_L2_v4p1_O3_667.nc'},
    {'label': _('Ozone 668'), 'value':     'ACEFTS_L2_v4p1_O3_668.nc'},
    {'label': _('Ozone 676'), 'value':   'ACEFTS_L2_v4p1_O3_676.nc'},
    {'label': _('Ozone 686'), 'value':     'ACEFTS_L2_v4p1_O3_686.nc'},
    {'label': _('Carbonyl sulfide'), 'value':     'ACEFTS_L2_v4p1_OCS.nc'},
     {'label': _('Carbonyl sulfide 623'), 'value':      'ACEFTS_L2_v4p1_OCS_623.nc'},


     {'label': _('Carbonyl sulfide 624'), 'value':      'ACEFTS_L2_v4p1_OCS_624.nc'},
    {'label': _('Carbonyl sulfide 632'), 'value':      'ACEFTS_L2_v4p1_OCS_632.nc'},
    {'label': _('Phosphorus'), 'value':      'ACEFTS_L2_v4p1_P.nc'},
    {'label': _('Polyacrylonitrile'), 'value':    'ACEFTS_L2_v4p1_PAN.nc'},
    {'label': _('Sulfur hexafluoride'), 'value':      'ACEFTS_L2_v4p1_SF6.nc'},
    {'label': _('Sulfur dioxide'), 'value':      'ACEFTS_L2_v4p1_SO2.nc'},
    #{'label': _('T'), 'value':       'ACEFTS_L2_v4p0_T.nc'}#!!!!!
            ],  #End gas_options

    ]


# Translate the header and the footer by injecting raw HTML
@app.callback(
    [
        Output('gc-header', 'children'),
        Output('gc-footer', 'children')
    ],
    [Input('none2', 'children')]
)
def translate_header_footer(x):
    """ Translates the government header and footer
    """
    try: # On the first load of the webpage, there is a bug where the header won't load due to the session not being established yet. This try/except defaults the header/footer to english
        if session['language'] == 'fr':
            return [dash_dangerously_set_inner_html.DangerouslySetInnerHTML(gc_header_fr), dash_dangerously_set_inner_html.DangerouslySetInnerHTML(gc_footer_fr)]
        else:
            return [dash_dangerously_set_inner_html.DangerouslySetInnerHTML(gc_header_en), dash_dangerously_set_inner_html.DangerouslySetInnerHTML(gc_footer_en)]
    except:
        return [dash_dangerously_set_inner_html.DangerouslySetInnerHTML(gc_header_en), dash_dangerously_set_inner_html.DangerouslySetInnerHTML(gc_footer_en)]


@app.callback(
    [
        Output('language-button', 'children'),
        Output('language-link', 'href'),
        Output("learn-more-link", 'href')
    ],
    [Input('none2', 'children')]
)
def update_language_button(x):
    """Updates the button to switch languages
    """

    try:
        language = session['language']
    except KeyError:
        language = None
    if language == 'fr':
        return 'EN', prefixe+'/language/en','https://www.asc-csa.gc.ca/fra/satellites/scisat/a-propos.asp' #! Le code est bizarre et fait l'inverse
    else:
        return 'FR', prefixe+'/language/fr','https://www.asc-csa.gc.ca/eng/satellites/scisat/about.asp'


@babel.localeselector
def get_locale():
    # if the user has set up the language manually it will be stored in the session,
    # so we use the locale from the user settings
    try:
        language = session['language']
    except KeyError:
        language = None
    if language is not None:
        return language
    else:
        return 'en'


@app.server.route('/language/<language>')
def set_language(language=None):
    """Sets the session language, then refreshes the page
    """
    session['language'] = language

    return redirect(url_for('/'))





if __name__ == '__main__':
     #app.run_server(debug=True)  # For development/testing

     app.run_server(debug=False, host='0.0.0.0', port=8888)  # For the server
