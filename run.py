# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 10:59:37 2020

@author: Camille Roy et Jonathan Beaulieu-Emond
"""

import os 
from werkzeug.middleware.dispatcher  import DispatcherMiddleware
from werkzeug.serving import run_simple
from flask_app import flask_app

import numpy as np

# app1.enable_dev_tools(debug=True)
# app2.enable_dev_tools(debug=True)
liste=os.listdir('applications')



import importlib
dict1={}
for item in liste :
    	
    	temp=importlib.import_module(f"applications.{item}.{item}")
    	dict1['/'+item]=temp.server




application = DispatcherMiddleware(flask_app,dict1)


if __name__ == '__main__':
     #run_simple('localhost',8888, application)
     import logging
     logging.basicConfig(filename='error.log', level=logging.DEBUG)

     run_simple('0.0.0.0',8888, application)
