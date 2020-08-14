# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 16:42:33 2020

@author: Camille
"""


import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import app_Scisat


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/app_Scisat':
        return app_Scisat.layout
    # elif pathname == '/apps/app2':
    #     return app2.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)