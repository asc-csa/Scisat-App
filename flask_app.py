# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 11:47:42 2020

@author: Camille
"""

from flask import Flask

flask_app = Flask(__name__)

@flask_app.route('/')
def index():
    return 'Hello Flask app'
