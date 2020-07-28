# -*- coding: utf-8 -*-
import dash

import copy
import dash_core_components as dcc
import dash_html_components as html
import dash_dangerously_set_inner_html
import plotly.graph_objs as go
import pandas as pd
import datetime as dt
from dash.dependencies import Input, Output
import flask
from io import StringIO
from flask_babel import _ ,Babel
from flask import session, redirect, url_for
from header_footer import gc_header_en, gc_footer_en, gc_header_fr, gc_footer_fr
from scipy.io import netcdf #### <--- This is the library to import data
import numpy as np
import datetime


#==========================================================================================
# load data and transform as needed

def data_reader(file,path_to_files,start_date=0,end_date=0,lat_min=-90,lat_max=90,lon_min=-180,lon_max=180) :
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
        gaz=gaz[0]
    
    name=path_to_files+'//'+file
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
    
    df = pd.DataFrame(data,columns=alt)
    
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
    
    data_meanAlt = np.nanmean(data,1) #Somme sur l'altitude #!!! À revérifier scientifiquement
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
                    
    {'label': _('Acetone'), 'value': 'ACEFTS_L2_v4p0_acetone.nc'},
    {'label': _('Acetylene'), 'value': 'ACEFTS_L2_v4p0_C2H2.nc'},
    {'label': _('Ethane'), 'value':  'ACEFTS_L2_v4p0_C2H6.nc'},
    {'label': _('dichlorodifluoromethane'), 'value': 'ACEFTS_L2_v4p0_CCl2F2.nc'},
    {'label': _('trichlorofluoromethane'), 'value': 'ACEFTS_L2_v4p0_CCl3F.nc'},
    {'label': _('Carbon tetrachloride'), 'value':  'ACEFTS_L2_v4p0_CCl4.nc'},
    
    
    {'label': _('Carbon tetrafluoride'), 'value':  'ACEFTS_L2_v4p0_CF4.nc'},
    {'label': _('Trichlorotrifluoroethane'), 'value':  'ACEFTS_L2_v4p0_CFC113.nc'},
    {'label': _('Chloromethane'), 'value':  'ACEFTS_L2_v4p0_CH3Cl.nc'},
    {'label': _('Acetonitrite'), 'value':  'ACEFTS_L2_v4p0_CH3CN.nc'},
    {'label': _('Methanol'), 'value':  'ACEFTS_L2_v4p0_CH3OH.nc'},
    {'label': _('Methane'), 'value':  'ACEFTS_L2_v4p0_CH4.nc'},
    
    {'label': _('Methane 212'), 'value':  'ACEFTS_L2_v4p0_CH4_212.nc'},
    {'label': _('Methane 311'), 'value':  'ACEFTS_L2_v4p0_CH4_311.nc'},
    {'label': _('Difluorochloromethane'), 'value':   'ACEFTS_L2_v4p0_CHF2Cl.nc'},
    {'label': _('Trifluoromethane'), 'value':  'ACEFTS_L2_v4p0_CHF3.nc'},
    {'label': _('chlorine monoxide'), 'value':  'ACEFTS_L2_v4p0_ClO.nc'},
    {'label': _('Chlorine nitrate'), 'value':  'ACEFTS_L2_v4p0_ClONO2.nc'},
    
    {'label': _('Carbon monoxide'), 'value':  'ACEFTS_L2_v4p0_CO.nc'},
    {'label': _('Carbon dioxide'), 'value':  'ACEFTS_L2_v4p0_CO2.nc'},
    {'label': _('Carbon dioxide 627'), 'value':   'ACEFTS_L2_v4p0_CO2_627.nc'},
    {'label': _('Carbon dioxide 628'), 'value':  'ACEFTS_L2_v4p0_CO2_628.nc'},
    {'label': _('Carbon dioxide 636'), 'value':  'ACEFTS_L2_v4p0_CO2_636.nc'},
    {'label': _('Carbon dioxide 637'), 'value':  'ACEFTS_L2_v4p0_CO2_637.nc'},
    
    
    {'label': _('Carbon dioxide 638'), 'value':   'ACEFTS_L2_v4p0_CO2_638.nc'},
    {'label': _('Phosgene'), 'value':  'ACEFTS_L2_v4p0_COCl2.nc'},
    {'label': _('Carbonyl chlorine fluoride'), 'value':  'ACEFTS_L2_v4p0_COClF.nc'},
    {'label': _('Carbonyl fluoride'), 'value':   'ACEFTS_L2_v4p0_COF2.nc'},
    {'label': _('Carbon monoxide 27'), 'value':  'ACEFTS_L2_v4p0_CO_27.nc'},
    {'label': _('Carbon monoxide 28'), 'value':   'ACEFTS_L2_v4p0_CO_28.nc'},
    
     {'label': _('Carbon monoxide 36'), 'value':   'ACEFTS_L2_v4p0_CO_36.nc'},
    {'label': _('Carbon monoxide 38'), 'value':   'ACEFTS_L2_v4p0_CO_38.nc'},
    {'label': _('GLC'), 'value':    'ACEFTS_L2_v4p0_GLC.nc'},
    {'label': _('Formaldehyde'), 'value':   'ACEFTS_L2_v4p0_H2CO.nc'},
    {'label': _('Water'), 'value':   'ACEFTS_L2_v4p0_H2O.nc'},
    {'label': _('Hydrogen peroxide'), 'value':   'ACEFTS_L2_v4p0_H2O2.nc'},
    
    
     {'label': _('Water 162'), 'value':    'ACEFTS_L2_v4p0_H2O_162.nc'},
    {'label': _('Water 171'), 'value':    'ACEFTS_L2_v4p0_H2O_171.nc'},
    {'label': _('Water 181'), 'value':     'ACEFTS_L2_v4p0_H2O_181.nc'},
    {'label': _('Water 182'), 'value':   'ACEFTS_L2_v4p0_H2O_182.nc'},
    {'label': _('Hydrochlorofluorocarbon 141b'), 'value':    'ACEFTS_L2_v4p0_HCFC141b.nc'},
    {'label': _('Hydrochlorofluorocarbon 142b'), 'value':    'ACEFTS_L2_v4p0_HCFC142b.nc'},
    {'label': _('Hydrochloric acid'), 'value':     'ACEFTS_L2_v4p0_HCl.nc'},
     
     
     
    {'label': _('Hydrogen cyanide'), 'value':   'ACEFTS_L2_v4p0_HCN.nc'},
    {'label': _('Formic acid'), 'value':   'ACEFTS_L2_v4p0_HCOOH.nc'},
    {'label': _('Hydrogen fluoride'), 'value':    'ACEFTS_L2_v4p0_HF.nc'},
    {'label': _('Hydrofluorocarbon 134a'), 'value':   'ACEFTS_L2_v4p0_HFC134a.nc'},
    {'label': _('Nitric acid'), 'value':  'ACEFTS_L2_v4p0_HNO3.nc'},
    {'label': _('Nitric acid 156'), 'value':  'ACEFTS_L2_v4p0_HNO3_156.nc'},
    
    
    {'label': _('peroxynitric acid'), 'value':   'ACEFTS_L2_v4p0_HO2NO2.nc'},
    {'label': _('Nitrogen'), 'value':  'ACEFTS_L2_v4p0_N2.nc'},
    {'label': _('Nitrous oxide'), 'value':  'ACEFTS_L2_v4p0_N2O.nc'},
    {'label': _('dinitrogen pentaoxide'), 'value':    'ACEFTS_L2_v4p0_N2O5.nc'},
    {'label': _('Nitrous oxide 447'), 'value':   'ACEFTS_L2_v4p0_N2O_447.nc'},
    {'label': _('Nitrous oxide 448'), 'value':    'ACEFTS_L2_v4p0_N2O_448.nc'},
    
     {'label': _('Nitrous oxide 456'), 'value':    'ACEFTS_L2_v4p0_N2O_456.nc'},
    {'label': _('Nitrous oxide 546'), 'value':   'ACEFTS_L2_v4p0_N2O_546.nc'},
    {'label': _('Nitrous monoxide 447'), 'value':     'ACEFTS_L2_v4p0_NO.nc'},
    {'label': _('Nitrogen dioxide'), 'value':    'ACEFTS_L2_v4p0_NO2.nc'},
    {'label': _('Nitrogen dioxide 656'), 'value':    'ACEFTS_L2_v4p0_NO2_656.nc'},
    {'label': _('Oxygen'), 'value':    'ACEFTS_L2_v4p0_O2.nc'},
    
    
     {'label': _('Ozone'), 'value':     'ACEFTS_L2_v4p0_O3.nc'},
    {'label': _('Ozone 667'), 'value':     'ACEFTS_L2_v4p0_O3_667.nc'},
    {'label': _('Ozone 668'), 'value':     'ACEFTS_L2_v4p0_O3_668.nc'},
    {'label': _('Ozone 676'), 'value':   'ACEFTS_L2_v4p0_O3_676.nc'},
    {'label': _('Ozone 686'), 'value':     'ACEFTS_L2_v4p0_O3_686.nc'},
    {'label': _('Carbonyl sulfide'), 'value':     'ACEFTS_L2_v4p0_OCS.nc'},
     {'label': _('Carbonyl sulfide 623'), 'value':      'ACEFTS_L2_v4p0_OCS_623.nc'},
     
     
     {'label': _('Carbonyl sulfide 624'), 'value':      'ACEFTS_L2_v4p0_OCS_624.nc'},
    {'label': _('Carbonyl sulfide 632'), 'value':      'ACEFTS_L2_v4p0_OCS_632.nc'},
    {'label': _('Phosphorus'), 'value':      'ACEFTS_L2_v4p0_P.nc'},
    {'label': _('Polyacrylonitrile'), 'value':    'ACEFTS_L2_v4p0_PAN.nc'},
    {'label': _('Sulfur hexafluoride'), 'value':      'ACEFTS_L2_v4p0_SF6.nc'},
    {'label': _('Sulfur dioxide'), 'value':      'ACEFTS_L2_v4p0_SO2.nc'},
     {'label': _('T'), 'value':       'ACEFTS_L2_v4p0_T.nc'}#!!!!!
    
   ]




x_axis_options = [
    {'label': _('Date'), 'value': _('Date')},
    {'label': _('Latitude'), 'value': _('latitude [deg]')},
    {'label': _('Longitude'), 'value': _('longitude [deg]')}]

y_axis_options = [
    {'label': _('Concentration'), 'value': _('Concentration [ppv]')},
    {'label': _('Maximum Depth'), 'value': _('Maximum Depth')}]

year_dict = {}
for year in range(1962,1974):
    year_dict[year] = str(year)
lat_dict = {}
for lat in range(-90, 90+1, 15):
    lat_dict[lat] = str(lat)
lon_dict = {}
for lon in range(-180, 180+1, 30):
    lon_dict[lon] = str(lon)

#======================================================================================

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

app = dash.Dash(
    __name__,
   
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    external_stylesheets=external_stylesheets,
    external_scripts=external_scripts
)

server = app.server
server.config['SECRET_KEY'] = '78b81502f7e89045fe634e85d02f42c5'  # Setting up secret key to access flask session
babel = Babel(server)  # Hook flask-babel to the app


# Create global chart template
mapbox_access_token = "pk.eyJ1IjoiamFja2x1byIsImEiOiJjajNlcnh3MzEwMHZtMzNueGw3NWw5ZXF5In0.fk8k06T96Ml9CLGgKmk81w"

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
        accesstoken=mapbox_access_token,
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
                            href='/language/fr', id='language-link'
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


# Builds the layout and components for the inputs to filter the data, as well as the ionograms/month graph and the ground stations map
def build_filtering():
    return html.Div([
        html.Div(
            [
                html.Div(
                    [
                        html.H3(id="ionograms_text"),
                        html.P(id="ionograms-ratio")
                    ],
                    id="info-container",
                    className="mini_container three columns",
                    style={"text-align": "center"},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                 html.H6(id="description"),
                                 html.P(id="description-1"),
                                 html.P(id="description-2"),
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
                        html.Div(
                            [dcc.Graph(id="selector_map")],
                        ),
                        html.Div(
                            [
                                html.P(
                                    id="groundstations-text",
                                    className="control_label",
                                ),
                                html.Label(
                                    dcc.Dropdown(
                                        id="gaz_list",
                                        options= gaz_name_options,
                                        multi=False,
                                        value='ACEFTS_L2_v4p0_O3.nc',
                                        className="dcc_control",
                                    ),
                                ),
                                html.Div(
                                    [
                                        html.P(
                                            id="latitude-text",
                                            className="control_label",
                                        ),
                                        # dcc.RangeSlider(
                                        #     id="lat_slider",
                                        #     min=-90.0,
                                        #     max=90.0,
                                        #     value=[-90.0, 90.0],
                                        #     className="dcc_control",
                                        #     marks=lat_dict,
                                        # ),
                                        dcc.Input(
                                            id="lat_min",
                                            type='number',
                                            value=-90.0,
                                            placeholder="Min Latitude",
                                            min=-90.0,
                                            max=90.0,
                                            step=5,
                                            style={"margin-left": "5px"}
                                        ),
                                        dcc.Input(
                                            id="lat_max",
                                            type='number',
                                            value=90.0,
                                            placeholder="Max Latitude",
                                            min=-90.0,
                                            max=90.0,
                                            step=5,
                                            style={"margin-left": "5px"}
                                        ),
                                        html.H5(
                                            "", style={"margin-top": "30px"}
                                        ),
                                    ],
                                    className="one-half column"
                                ),
                                html.Div(
                                    [
                                        html.P(
                                            id="longitude-text",
                                            className="control_label",
                                        ),
     
                                        dcc.Input(
                                            id="lon_min",
                                            type='number',
                                            value=-180.0,
                                            placeholder="Min Longitude",
                                            min=-180.0,
                                            max=180.0,
                                            step=5,
                                            style={"margin-left": "5px"}
                                        ),
                                        dcc.Input(
                                            id="lon_max",
                                            type='number',
                                            value=180.0,
                                            placeholder="Max Longitude",
                                            min=-180.0,
                                            max=180.0,
                                            step=5,
                                            style={"margin-left": "5px"}
                                        ),
                                    ],
                                    className="one-half column"
                                ),
                                html.H5(
                                    "", style={"margin-top": "10px"}
                                ),
                            ],
                            id="map-options",
                        ),
                    ],
                    id="left-column-1",
                    style={"flex-grow": 1},
                    className="six columns",
                ),
                html.Div(
                    [
                        html.Div(
                            [dcc.Graph(id="count_graph")],
                            id="countGraphContainer",
                        ),
                        html.Div(
                            [
                                html.P(
                                    id="yearslider-text",
                                    className="control_label",
                                ),

                                html.Div([
                                    html.Label(
                                        dcc.DatePickerRange(
                                            id='date_picker_range',
                                            min_date_allowed=dt.datetime(1962, 9, 29),
                                            max_date_allowed=dt.datetime(1972, 12, 31),
                                            #initial_visible_month=dt.datetime(1962, 9, 29),
                                            start_date=dt.datetime(1962, 9, 29),
                                            end_date=dt.datetime(1972, 12, 31),
                                            start_date_placeholder_text='Select start date',
                                            end_date_placeholder_text='Select end date',
                                            style={"margin-top": "5px"}
                                        ),
                                    ),
                                    html.Div(id='output-container-date-picker-range')
                                ]),
                                html.H5(
                                    "", style={"margin-top": "30px", "margin-bottom": "25px"}
                                ),
                                html.Div(
                                    [
                                        html.A(
                                            html.Button(id='download-button-1', n_clicks=0, className="dash_button", style={'padding': '0px 10px'}),
                                            id='download-link-1',
                                            # download='rawdata.csv',
                                            href="",
                                            target="_blank",
                                        ),
                                       # html.A(
                                       #     html.Button(id='download-button-2',  n_clicks=0, className="dash_button", style={'padding': '0px 10px'}),
                                       #     id='download-link-2',
                                       #     style={"margin-left": "5px"},
                                       # )
                                    ],
                                ),
                            ],
                            id="cross-filter-options",
                        ),
                    ],
                    id="right-column-1",
                    style={"flex-grow": 1},
                    className="six columns",
                ),
            ],
            className="row flex-display pretty_container twelve columns",
            style={"justify-content": "space-evenly"}
        ),
    ])


# Builds the layout for the map displaying statistics as well as the confidence interval graph
def build_stats():
    return html.Div([
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [dcc.Graph(id="viz_chart")],
                            id="vizChartContainer",
                            #className="pretty_container",
                        ),
                    ],
                    id="left-column-3",
                    className="nine columns",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    id="x-axis-selection-text",
                                    className="control_label",
                                ),
                                html.Label(
                                    dcc.Dropdown(
                                        id="x_axis_selection_1",
                                        options=x_axis_options,
                                        multi=False,
                                        value=_('Date'),
                                        className="dcc_control",
                                    ),
                                ),
                                html.P(
                                    id="y-axis-selection-text",
                                    className="control_label",
                                ),
                                html.Label(
                                    dcc.Dropdown(
                                        id="y_axis_selection_1",
                                        options=y_axis_options,
                                        multi=False,
                                        value=_('Concentration [ppv]'),
                                        className="dcc_control",
                                    ),
                                ),
                            ],
                            #className="pretty_container",
                            id="viz-chart-options",
                        ),
                    ],
                    id="right-column-3",
                    className="three columns",
                ),
            ],
            className="row flex-display pretty_container",
            #style={"height": "500px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        #html.Div(
                        #    [dcc.Graph(id="viz_map")],
                        #    id="vizGraphContainer",
                        #),
                    ],
                    id="left-column-4",
                    className="nine columns",
                ),
                #html.Div(
                #    [
                #        html.Div(
                #            [
                #                html.P(
                #                    id="stat-selection-text",
                #                    className="control_label",
                #                ),
                #                html.Label(
                #                    dcc.Dropdown(
                #                        id="stat_selection",
                #                        options=[
                #                            {'label': 'Mean', 'value': 'mean'},
                #                            {'label': 'Median', 'value': 'median'}
                #                        ],
                #                        multi=False,
                #                        value='mean',
                #                        className="dcc_control",
                #                    ),
                #               ),
                #                html.P(
                #                    id="stat-y-axis-text",
                #                    className="control_label",
                #                ),
                #                html.Label(
                #                    dcc.Dropdown(
                #                        id="y_axis_selection_2",
                #                        options=y_axis_options,
                #                        multi=False,
                #                       value='max_depth',
                #                       className="dcc_control",
                #                  ),
                #                ),
                #            ],
                #            #className="pretty_container",
                #            id="map-viz-options",
                #        ),
                #   ],
                #    id="right-column-4",
                #    className="three columns",
                #),
            ],
            className="row flex-display pretty_container",
            #style={"height": "500px"},
        ),
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
    ],
)


# Helper functions


# Selectors -> !!! À voir ce qu'on veut rajouter ? 
@app.callback(
    Output("ionograms_text", "children"),
    [
        Input('date_picker_range', "start_date"),
        Input('date_picker_range', "end_date"),
        Input("lat_min", "value"),
        Input("lat_max", "value"),
        Input("lon_min", "value"),
        Input("lon_max", "value"),
        Input("gaz_list", "value"),
    ],
)
def update_ionograms_text(start_date, end_date, lat_min, lat_max, lon_min, lon_max,gaz_list):
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
        Gaz names strings stored in a list (e.g. ['Ozone'])

    Returns
    -------
    int
        The number of data points present in the dataframe after filtering
    """


    df =data_reader(gaz_list,r'data',start_date,end_date,lat_min,lat_max,lon_min,lon_max)

    return "{:n}".format(df.shape[0]) + " points" #!!!!!!!!!!


@app.callback(
    [Output('date_picker_range', 'min_date_allowed'),
    Output('date_picker_range', 'max_date_allowed'),
    Output('date_picker_range', 'start_date'),
    Output('date_picker_range', 'end_date')],
    
    [ Input("gaz_list", "value")]
    )

def update_picker(gaz_list):
     df =data_reader(gaz_list,r'data')
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
@app.callback(
    Output("download-link-1", "href"),
    [   Input("gaz_list", "value"),
        Input('date_picker_range', "start_date"),
        Input('date_picker_range', "end_date"),
        Input("lat_min", "value"),
        Input("lat_max", "value"),
        Input("lon_min", "value"),
        Input("lon_max", "value"),
       
    ],
)
def update_csv_link(gaz_list,start_date,end_date, lat_min, lat_max, lon_min, lon_max):
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
        Gaz names strings stored in a list (e.g. ['Ozone'])
        
    Returns
    -------
    link : str
        Link that redirects to the Flask route to download the CSV based on selected filters
    """

    link = '/dash/downloadCSV?start_date={}&end_date={}&lat_min={}&lat_max={}&lon_min={}&lon_max={}&gaz_list={}' \
            .format(start_date, end_date, lat_min, lat_max, lon_min, lon_max, gaz_list)
            
    

    return link

from flask import make_response
from dateutil.parser import parse


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
        Gaz name strings stored in a list (e.g. ['Ozone'])

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
    
    gaz_list= flask.request.args.get('gaz_list')
   
    #start_date =pd.Timestamp(parse(start_date))
    #end_date   =pd.Timestamp(parse(end_date))
    df =data_reader(gaz_list,r'data',start_date,end_date,lat_min,lat_max,lon_min,lon_max)

    # Making the output csv from the filtered df
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    output = make_response(csv_buffer.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=summary_data.csv"
    output.headers["Content-type"] = "text/csv"

    return output



#============================================================================
# Selected Data by sliding mouse
#!!!!!!!!!!!!!!!!!!!
@app.callback(
    [Output("lat_min", "value"),
    Output("lat_max", "value"),
    Output("lon_min", "value"),
    Output("lon_max", "value")],
    [Input("selector_map", "selectedData"), Input("selector_map", "clickData")]
)
def update_bar_selector(value, clickData):
    holder_lat = []
    holder_lon = []
    if clickData:
        holder_lat.append(str(int(clickData["points"][0]["lat"])))
        holder_lon.append(str(int(clickData["points"][0]["lon"])))
    if value:
        for x in value["points"]:
            holder_lat.append(((x["lat"])))
            holder_lon.append(((x["lon"])))
            
    holder_lat  = np.array( holder_lat)
    holder_lon  = np.array( holder_lon)
    if len(holder_lat)!=0 :
        return int(np.min(holder_lat)),int(np.max(holder_lat)),int(np.min(holder_lon)),int(np.max(holder_lon))
    else :
        return -90,90,-180,180
    

# Clear Selected Data if Click Data is used
@app.callback(
    Output("selector_map", "selectedData"),
    [Input("selector_map", "clickData")]
    )
def update_selected_data(clickData):
    if clickData:
        return {"points": []}
    
#============================================================================   
 
    
# Selectors -> count graph
    
@app.callback(
    Output("count_graph", "figure"),
    # [Input("visualize-button", "n_clicks")],
    [   Input('date_picker_range', "start_date"),
        Input('date_picker_range', "end_date"),
        Input("gaz_list", "value"),
        Input("lat_min", "value"),
        Input("lat_max", "value"),
        Input("lon_min", "value"),
        Input("lon_max", "value"),
        Input("gaz_list", "value"),
    ],
)
def make_count_figure(start_date,end_date,gaz_list, lat_min, lat_max, lon_min, lon_max, ground_stations=None):
    """Create and update the Gaz Concentration vs Altitude over the given time range.

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

    Returns
    -------
    dict
        A dictionary containing 2 key-value pairs: the selected data as an array of dictionaries and the graphic's
        layout as as a Plotly layout graph object. 
    """
    
    df =data_reader(gaz_list,r'data',start_date,end_date,lat_min,lat_max,lon_min,lon_max)
    concentration=df.values[:,0:150]
    concentration=np.array(concentration,dtype=np.float32)
    concentration=np.ma.masked_array(concentration, np.isnan(concentration))
    xx=concentration.mean(axis=0).data
    err_xx=concentration.std(axis=0).data
    
    layout_count = copy.deepcopy(layout)
    data = [
        dict(
            type="scatter",
            x=xx,
            y=df.columns[0:150],
            error_x=dict(type='data', array=err_xx,thickness=0.5),#!!!!!!!!!! Ne semble pas marcher
            name="Altitude",
            #orientation='h',
            color=xx,
             colorscale=[[0, 'red'],
            [1, 'blue']],   
            opacity=1,
          
        )
    ]
    
   

    layout_count["title"] = _("Mean concentration as a function of altitude")
    layout_count["xaxis"] = {"title": _("Mean Concentration [ppv]"), "automargin": True}
    layout_count["yaxis"] = {"title": _("Altitude [km] "), "automargin": True}
    #layout_count["dragmode"] = "select"
    layout_count['clickmode']="event+select",
    layout_count['hovermode']="closest",
    layout_count["showlegend"] = False
    layout_count["autosize"] = True
    layout_count["transition"] = {'duration': 500}

    fig = dict(data=data, layout=layout_count)

    return fig


#=====================================================================
#this is where the graph are generated

#app callback is used to get the variables from the user input
@app.callback(
    Output("selector_map", "figure"),
    # [Input("visualize-button", "n_clicks")],
    [   Input("date_picker_range", "start_date"),
        Input("date_picker_range", "end_date"),
        Input("gaz_list", "value"),
        Input("lat_min", "value"),
        Input("lat_max", "value"),
        Input("lon_min", "value"),#!!!!!! à remplacer lorsque le click-select est pret
        Input("lon_max", "value"),
       
    ],
)

def generate_geo_map(start_date,end_date,gaz_list, lat_min, lat_max, lon_min, lon_max):
    """Create and update the map of gaz concentrations for selected variables.

    The color of the data points indicates the mean gaz concentration at that coordinate.


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

 

    Returns
    -------
    dict
        A dictionary containing 2 key-value pairs: the selected data as an array of Plotly scattermapbox graph objects
        and the map's layout as a Plotly layout graph object.
    """

    df = data_reader(gaz_list,r'data',start_date,end_date,lat_min,lat_max,lon_min,lon_max)
    
    # Group data by latitude and longitude 
    df=df.groupby(['lat','long']).mean().reset_index()

    # Graph
    fig =go.Figure( go.Scattermapbox(
        lat=df['lat'][df['Alt_Mean']<0.0003],
        lon=df['long'][df['Alt_Mean']<0.0003],
        mode="markers",
        marker=dict(
            color=df['Alt_Mean'][df['Alt_Mean']<0.0003],
            colorscale=[[0, 'blue'],
            [1, 'red']],
            cmin=0,
            cmax=max(df['Alt_Mean'][df['Alt_Mean']<0.0003]),
            showscale=True,
            
            size=5,
            colorbar=dict(
                title=dict(
                    text=_("Gaz Concentration [ppv] (mean on altitude and position) "),#!!! description à mettre dans le caption au lieu de sur le côté
                ),
                titleside="right",     
                
        ),
        opacity=0.8,
        )
    )
)
    
    fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10, pad=5),
        clickmode="event+select",
        hovermode="closest",
        showlegend=False,  
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token
            #style="mapbox://styles/plotlymapbox/cjvppq1jl1ips1co3j12b9hex", #!!!!!! changer le stype de la map?
        ),
        transition={'duration': 500},
    )
    
    return fig


# Selectors -> viz chart (95% CI)
@app.callback(
    Output("viz_chart", "figure"),
    # [Input("visualize-button", "n_clicks")],
    [
       
        Input("date_picker_range", "start_date"),
        Input("date_picker_range", "end_date"),
        Input("x_axis_selection_1", "value"),
        Input("y_axis_selection_1", "value"),
        Input("lat_min", "value"),
        Input("lat_max", "value"),
        Input("lon_min", "value"),
        Input("lon_max", "value"),
        Input("gaz_list", "value"),
    ],
)
def make_viz_chart(start_date,end_date, x_axis_selection, y_axis_selection, lat_min, lat_max, lon_min, lon_max, gaz_list):
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

    Returns
    -------
    dict
        A dictionary containing 2 key-value pairs: the selected data as an array of dictionaries and the chart's layout
        as a Plotly layout graph object.
    """
    
    df =data_reader(gaz_list,r'data',start_date,end_date,lat_min,lat_max,lon_min,lon_max)
    
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
        title=_("Data Visualization "),
        
        xaxis={"title": x_axis_selection, "automargin": True},
        yaxis={"title": y_axis_selection, "automargin": True},
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
        Output("ionograms-ratio", "children"),
        Output("description-1", "children"),
        Output("description-2", "children"),
        Output("select-data", "children"),
        Output("latitude-text", "children"),
        Output("longitude-text", "children"),
        Output("yearslider-text", "children"),
        Output("groundstations-text", "children"),
        Output("download-button-1", "children"),
        #("download-button-2", "children"),
        Output("x-axis-selection-text", "children"),
        Output("y-axis-selection-text", "children"),
        #Output("stat-selection-text", "children"),
        #Output("stat-y-axis-text", "children"),
        Output("gaz_list", "options"),
        Output("x_axis_selection_1", "options"),
        Output("y_axis_selection_1", "options"),
        #Output("y_axis_selection_2", "options"),
        #Output("stat_selection", "options"),
    ],
        [Input('none', 'children')], # A placeholder to call the translations upon startup
)
def translate_static(x):
    print('Translating...')
    return [
                _("Scisat data visualisation"),
                _("Learn More About SciSat"),
                _("data selected"),
                #_("Launched in 1962, Alouette I sent signals with different frequencies into the topmost layer of the atmosphere, known as the ionosphere, and collected data on the depth these frequencies travelled. The results of this were sent to ground stations around the world and stored in films as ionogram images, which have now been digitized. The ionograms Alouette I provided were used to fuel hundreds of scientific papers at the time. Although ionosphere data from more recent years is readily available, the data from Alouette I’s ionograms are the only ones available for this time period. Barriers for accessing, interpreting and analyzing the data at a larger scale have prevented this data's usage. "),
                _("Launched on August 12, 2003, SCISAT helps a team of Canadian and international scientists improve their understanding of the depletion of the ozone layer, with a special emphasis on the changes occurring over Canada and in the Arctic. "),
                _("This application provides users the ability to select, download and visualize Scisat's data. "),
                _("Select Data"),
                _("Filter by latitude:"),
                _("Filter by longitude:"),
                _("select date:"),
                _("Select gas:"),
                _('Download Summary Data as CSV'),
                #_('Download full data as netcdf'),
                _("Select x-axis:"),
                _("Select y-axis:"),
                #_("Select statistic:"),
                #_("Select plotted value:"),
                [  # Ground_station_options
                     {'label': _('Acetone'), 'value': 'ACEFTS_L2_v4p0_acetone.nc'},
    {'label': _('Acetylene'), 'value': 'ACEFTS_L2_v4p0_C2H2.nc'},
    {'label': _('Ethane'), 'value':  'ACEFTS_L2_v4p0_C2H6.nc'},
    {'label': _('dichlorodifluoromethane'), 'value': 'ACEFTS_L2_v4p0_CCl2F2.nc'},
    {'label': _('trichlorofluoromethane'), 'value': 'ACEFTS_L2_v4p0_CCl3F.nc'},
    {'label': _('Carbon tetrachloride'), 'value':  'ACEFTS_L2_v4p0_CCl4.nc'},
    
    
    {'label': _('Carbon tetrafluoride'), 'value':  'ACEFTS_L2_v4p0_CF4.nc'},
    {'label': _('Trichlorotrifluoroethane'), 'value':  'ACEFTS_L2_v4p0_CFC113.nc'},
    {'label': _('Chloromethane'), 'value':  'ACEFTS_L2_v4p0_CH3Cl.nc'},
    {'label': _('Acetonitrite'), 'value':  'ACEFTS_L2_v4p0_CH3CN.nc'},
    {'label': _('Methanol'), 'value':  'ACEFTS_L2_v4p0_CH3OH.nc'},
    {'label': _('Methane'), 'value':  'ACEFTS_L2_v4p0_CH4.nc'},
    
    {'label': _('Methane 212'), 'value':  'ACEFTS_L2_v4p0_CH4_212.nc'},
    {'label': _('Methane 311'), 'value':  'ACEFTS_L2_v4p0_CH4_311.nc'},
    {'label': _('Difluorochloromethane'), 'value':   'ACEFTS_L2_v4p0_CHF2Cl.nc'},
    {'label': _('Trifluoromethane'), 'value':  'ACEFTS_L2_v4p0_CHF3.nc'},
    {'label': _('chlorine monoxide'), 'value':  'ACEFTS_L2_v4p0_ClO.nc'},
    {'label': _('Chlorine nitrate'), 'value':  'ACEFTS_L2_v4p0_ClONO2.nc'},
    
    {'label': _('Carbon monoxide'), 'value':  'ACEFTS_L2_v4p0_CO.nc'},
    {'label': _('Carbon dioxide'), 'value':  'ACEFTS_L2_v4p0_CO2.nc'},
    {'label': _('Carbon dioxide 627'), 'value':   'ACEFTS_L2_v4p0_CO2_627.nc'},
    {'label': _('Carbon dioxide 628'), 'value':  'ACEFTS_L2_v4p0_CO2_628.nc'},
    {'label': _('Carbon dioxide 636'), 'value':  'ACEFTS_L2_v4p0_CO2_636.nc'},
    {'label': _('Carbon dioxide 637'), 'value':  'ACEFTS_L2_v4p0_CO2_637.nc'},
    
    
    {'label': _('Carbon dioxide 638'), 'value':   'ACEFTS_L2_v4p0_CO2_638.nc'},
    {'label': _('Phosgene'), 'value':  'ACEFTS_L2_v4p0_COCl2.nc'},
    {'label': _('Carbonyl chlorine fluoride'), 'value':  'ACEFTS_L2_v4p0_COClF.nc'},
    {'label': _('Carbonyl fluoride'), 'value':   'ACEFTS_L2_v4p0_COF2.nc'},
    {'label': _('Carbon monoxide 27'), 'value':  'ACEFTS_L2_v4p0_CO_27.nc'},
    {'label': _('Carbon monoxide 28'), 'value':   'ACEFTS_L2_v4p0_CO_28.nc'},
    
     {'label': _('Carbon monoxide 36'), 'value':   'ACEFTS_L2_v4p0_CO_36.nc'},
    {'label': _('Carbon monoxide 38'), 'value':   'ACEFTS_L2_v4p0_CO_38.nc'},
    {'label': _('GLC'), 'value':    'ACEFTS_L2_v4p0_GLC.nc'},
    {'label': _('Formaldehyde'), 'value':   'ACEFTS_L2_v4p0_H2CO.nc'},
    {'label': _('Water'), 'value':   'ACEFTS_L2_v4p0_H2O.nc'},
    {'label': _('Hydrogen peroxide'), 'value':   'ACEFTS_L2_v4p0_H2O2.nc'},
    
    
     {'label': _('Water 162'), 'value':    'ACEFTS_L2_v4p0_H2O_162.nc'},
    {'label': _('Water 171'), 'value':    'ACEFTS_L2_v4p0_H2O_171.nc'},
    {'label': _('Water 181'), 'value':     'ACEFTS_L2_v4p0_H2O_181.nc'},
    {'label': _('Water 182'), 'value':   'ACEFTS_L2_v4p0_H2O_182.nc'},
    {'label': _('Hydrochlorofluorocarbon 141b'), 'value':    'ACEFTS_L2_v4p0_HCFC141b.nc'},
    {'label': _('Hydrochlorofluorocarbon 142b'), 'value':    'ACEFTS_L2_v4p0_HCFC142b.nc'},
    {'label': _('Hydrochloric acid'), 'value':     'ACEFTS_L2_v4p0_HCl.nc'},
     
     
     
    {'label': _('Hydrogen cyanide'), 'value':   'ACEFTS_L2_v4p0_HCN.nc'},
    {'label': _('Formic acid'), 'value':   'ACEFTS_L2_v4p0_HCOOH.nc'},
    {'label': _('Hydrogen fluoride'), 'value':    'ACEFTS_L2_v4p0_HF.nc'},
    {'label': _('Hydrofluorocarbon 134a'), 'value':   'ACEFTS_L2_v4p0_HFC134a.nc'},
    {'label': _('Nitric acid'), 'value':  'ACEFTS_L2_v4p0_HNO3.nc'},
    {'label': _('Nitric acid 156'), 'value':  'ACEFTS_L2_v4p0_HNO3_156.nc'},
    
    
    {'label': _('peroxynitric acid'), 'value':   'ACEFTS_L2_v4p0_HO2NO2.nc'},
    {'label': _('Nitrogen'), 'value':  'ACEFTS_L2_v4p0_N2.nc'},
    {'label': _('Nitrous oxide'), 'value':  'ACEFTS_L2_v4p0_N2O.nc'},
    {'label': _('dinitrogen pentaoxide'), 'value':    'ACEFTS_L2_v4p0_N2O5.nc'},
    {'label': _('Nitrous oxide 447'), 'value':   'ACEFTS_L2_v4p0_N2O_447.nc'},
    {'label': _('Nitrous oxide 448'), 'value':    'ACEFTS_L2_v4p0_N2O_448.nc'},
    
     {'label': _('Nitrous oxide 456'), 'value':    'ACEFTS_L2_v4p0_N2O_456.nc'},
    {'label': _('Nitrous oxide 546'), 'value':   'ACEFTS_L2_v4p0_N2O_546.nc'},
    {'label': _('Nitrous monoxide 447'), 'value':     'ACEFTS_L2_v4p0_NO.nc'},
    {'label': _('Nitrogen dioxide'), 'value':    'ACEFTS_L2_v4p0_NO2.nc'},
    {'label': _('Nitrogen dioxide 656'), 'value':    'ACEFTS_L2_v4p0_NO2_656.nc'},
    {'label': _('Oxygen'), 'value':    'ACEFTS_L2_v4p0_O2.nc'},
    
    
     {'label': _('Ozone'), 'value':     'ACEFTS_L2_v4p0_O3.nc'},
    {'label': _('Ozone 667'), 'value':     'ACEFTS_L2_v4p0_O3_667.nc'},
    {'label': _('Ozone 668'), 'value':     'ACEFTS_L2_v4p0_O3_668.nc'},
    {'label': _('Ozone 676'), 'value':   'ACEFTS_L2_v4p0_O3_676.nc'},
    {'label': _('Ozone 686'), 'value':     'ACEFTS_L2_v4p0_O3_686.nc'},
    {'label': _('Carbonyl sulfide'), 'value':     'ACEFTS_L2_v4p0_OCS.nc'},
     {'label': _('Carbonyl sulfide 623'), 'value':      'ACEFTS_L2_v4p0_OCS_623.nc'},
     
     
     {'label': _('Carbonyl sulfide 624'), 'value':      'ACEFTS_L2_v4p0_OCS_624.nc'},
    {'label': _('Carbonyl sulfide 632'), 'value':      'ACEFTS_L2_v4p0_OCS_632.nc'},
    {'label': _('Phosphorus'), 'value':      'ACEFTS_L2_v4p0_P.nc'},
    {'label': _('Polyacrylonitrile'), 'value':    'ACEFTS_L2_v4p0_PAN.nc'},
    {'label': _('Sulfur hexafluoride'), 'value':      'ACEFTS_L2_v4p0_SF6.nc'},
    {'label': _('Sulfur dioxide'), 'value':      'ACEFTS_L2_v4p0_SO2.nc'},
     {'label': _('T'), 'value':       'ACEFTS_L2_v4p0_T.nc'}#!!!!!
                   
    
     
                ],
                [  # x_axis_options
                     {'label': _('Date'), 'value': _('Date')},
                     {'label': _('Latitude'), 'value': _('latitude [deg]')},
                     {'label': _('Longitude'), 'value': _('longitude [deg]')}
                ],
                [  # y_axis_options
                    {'label': _('Concentration'), 'value': _('Concentration [ppv]')},
                    {'label': _('Maximum Depth'), 'value': _('Maximum Depth')}
                ],
                #[  # y_axis_selection_2
                #    {'label': _('Minimum Frequency'), 'value': 'fmin'},
                #    {'label': _('Maximum Depth'), 'value': 'max_depth'}
                #],
                #[  # stat_selection
                #    {'label': _('Mean'), 'value': 'mean'},
                #    {'label': _('Median'), 'value': 'median'}
                #],
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

    language = session['language']
    if language == 'fr':
        return 'EN', '/language/en','https://www.asc-csa.gc.ca/fra/satellites/scisat/a-propos.asp' #! Le code est bizarre et fait l'inverse
    else:
        return 'FR', '/language/fr','https://www.asc-csa.gc.ca/eng/satellites/scisat/about.asp'


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
    return 'en'



@app.server.route('/language/<language>')
def set_language(language=None):
    """Sets the session language, then refreshes the page
    """

    session['language'] = language

    return redirect(url_for('/'))


# Main
if __name__ == '__main__':
    app.run_server(debug=True)  # For development/testing
    # app.run_server(debug=False, host='0.0.0.0', port=8888)  # For the server







