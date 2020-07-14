# -*- coding: utf-8 -*-
"""
Created on Sun Jul 12 16:15:12 2020

@author: Camille
"""

import numpy as np
import pandas as pd
import datetime
from scipy.io import netcdf #### <--- This is the library to import.
import matplotlib.pyplot as plt
import os
os.environ['PROJ_LIB'] = r'c:\Users\Camille\anaconda3\pkgs\proj4-5.2.0-ha925a31_1\Library\share'

def opendf (path_to_file,file_name,gaz):
    nc = netcdf.netcdf_file(path_to_file+'//'+file_name,'r')

    #aller chercher les variables
    fillvalue = -999.      # Fill value from User Guide
    months=np.copy(nc.variables['month'][:])
    years = np.copy(nc.variables['year'][:])
    days = np.copy(nc.variables['day'][:])
    hours = np.copy(nc.variables['hour'][:])
    lat = np.copy(nc.variables['latitude'][:])
    long =np.copy( nc.variables['longitude'][:])
    alt = np.copy(nc.variables['altitude'][:])
    
    data = np.copy(nc.variables[gaz][:]) #valeurs de concentration [ppv]
    data_error = np.copy(nc.variables[gaz+'_error'][:])
    data[data == fillvalue] = np.nan #Remplacer les données vides
 #   data_error[data_error == fillvalue] = np.nan #Remplacer les données vides

    #Initialize Dataframe / Initialisation du DataFrame
    dfdata = pd.DataFrame(data,columns=alt)
    dferr = pd.DataFrame(data_error,columns=alt)
    
    df = pd.concat([dfdata, dferr], axis=1)
    #Data cleaning / Nettoyage des données
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
        date.append(datetime.datetime(years[i],months[i],days[i],hour=hours[i]))

    #Attribution des colonnes
    data_meanAlt = np.nanmean(data,1) #moyenne sur l'altitude
    df['mean O3'] = data_meanAlt
    df['date'] = date
    df['lat'] = lat
    df['long'] = long
    #df['error']=data_error
    return df

path = r'C:\Users\Camille\Documents\Uni\ASC\SciSat\ACE-FTS_L2_v4.0_NETCDF\NETCDF'
file = 'ACEFTS_L2_v4p0_O3.nc'
df = opendf(path,file,'O3')
