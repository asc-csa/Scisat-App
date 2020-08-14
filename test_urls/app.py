# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 16:39:44 2020

@author: Camille
"""

import dash

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server
