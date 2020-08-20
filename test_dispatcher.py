# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 10:59:37 2020

@author: Camille
"""
from werkzeug.middleware.dispatcher  import DispatcherMiddleware
from werkzeug.serving import run_simple
from flask_app import flask_app
import scisat_app.scisat as scisat
import alouette_app.alouette as alouette

# app1.enable_dev_tools(debug=True)
# app2.enable_dev_tools(debug=True)

application = DispatcherMiddleware(flask_app,{
    '/scisat_app/scisat': scisat.server,
    '/alouette_app/alouette': alouette.server,
})


if __name__ == '__main__':
    # run_simple('localhost',8888, application)
    run_simple('0.0.0.0',8888, application)