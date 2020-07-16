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
import matplotlib.dates as mdates
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
    data_error[data_error == fillvalue] = np.nan #Remplacer les données vides

    #Initialize Dataframe / Initialisation du DataFrame
    df = pd.DataFrame(data,columns=alt)
    dferr = pd.DataFrame(data_error,columns=alt)
   # df = pd.concat([df,dferr],axis=1)
   # df = pd.concat([dfdata, dferr], axis=1)
    #Data cleaning / Nettoyage des données
  
    #Colonne de dates
    date=[]
    for i in range (len(days)):
        date.append(datetime.datetime(years[i],months[i],days[i]))#,hour=hours[i]))

    #Attribution des colonnes
    data_meanAlt = np.nanmean(data,1) #moyenne sur l'altitude
    data_std = np.nanstd(data,1)
    df['mean O3'] = data_meanAlt
    df['std O3'] = data_std
    df['date'] = date
    df['lat'] = lat
    df['long'] = long
    #df['error']=data_error
    df=df.groupby('lat').mean()
  #  df=df.groupby(df.index.floor('D')).mean()
    df.reset_index(level=0, inplace=True)  
    df=df.groupby('long').mean()
    df.reset_index(level=0,inplace=True)
    return df,dferr

#Path to file (change directory)
path = r'C:\Users\Camille\Documents\Uni\ASC\SciSat\ACE-FTS_L2_v4.0_NETCDF\NETCDF'
file = 'ACEFTS_L2_v4p0_O3.nc'
df,dferr= opendf(path,file,'O3')

#%%
##############################################################################
#VisualisationS pour comparer avec et sans les données flaggées
##############################################################################

def time_series1(df):

    fig, ax = plt.subplots(figsize=((35,7)))    #Create fig
    ax.plot(df['mean O3'],'b.')     #Plot data
    
    return fig,ax

# VISUALISATION FILTRE RIEN

# newtemp=df[np.logical_and(df['lat']<latlim[1],df['lat']>latlim[0])]    
# dff=newtemp[np.logical_and(newtemp['long']<longlim[1],newtemp['long']>longlim[0])]
dff = df.groupby('date').mean()
fig,ax = time_series1(dff)

date_form = mdates.DateFormatter("%Y") # Define the date format for x axis
ax.xaxis.set_major_formatter(date_form) 
plt.grid(which='both',linestyle='--',linewidth=1.5) #add grid
plt.ylabel('O3 Concentration (ppv)',fontsize=23)    # y-axis label
plt.xlabel('Year',fontsize=23)      #x-axis label
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.title('No Filtering',fontsize=20)
plt.savefig('O3_NoFilter.png')
plt.show()

# VISUALISATION FILTRE FLAGGED ERRORS

dfff = df.copy()

for i in range(150):
    dfff.iloc[:,i][dferr.iloc[:,i]==-888.]=np.nan

data=dfff.iloc[:,:150].values
data_meanAlt = np.nanmean(data,1) #moyenne sur l'altitude
data_std = np.nanstd(data,1)
dfff['mean O3'] = data_meanAlt

dff = dfff.groupby('date').mean()

fig,ax = time_series1(dff)

date_form = mdates.DateFormatter("%Y") # Define the date format for x axis
ax.xaxis.set_major_formatter(date_form) 
plt.grid(which='both',linestyle='--',linewidth=1.5) #add grid
plt.ylabel('O3 Concentration (ppv)',fontsize=23)    # y-axis label
plt.xlabel('Year',fontsize=23)      #x-axis label
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.title('Filtering flagged data',fontsize=20)
plt.savefig('O3_FlaggedData.png')
plt.show()


#%%

# VISUALISATION FILTRE AVEC MOYENNE / STD


#va falloir que je fasse une boucle sur les 150 colonnes pck ca fuck up sinon.
dff = dfff.copy()


for i in range(150):
    dff.iloc[:,i][dff.iloc[:,i]>3e-5]=np.nan
    dff.iloc[:,i][dff.iloc[:,i]<-3e-5]=np.nan
    # std=dff.iloc[:,i].std()
    # mn=dff.iloc[:,i].mean()
    # maxV = mn+3*std
    # minV = mn-3*std
    # dff.iloc[:,i][dff.iloc[:,i]>maxV]=np.nan
    # dff.iloc[:,i][dff.iloc[:,i]<minV]=np.nan

data=dff.iloc[:,:150].values
data_meanAlt = np.nanmean(data,1) #moyenne sur l'altitude
data_std = np.nanstd(data,1)
dff['mean O3'] = data_meanAlt
 
# # newtemp=df[np.logical_and(df['lat']<latlim[1],df['lat']>latlim[0])]    
# # dff=newtemp[np.logical_and(newtemp['long']<longlim[1],newtemp['long']>longlim[0])]
dff = dff.groupby('date').mean()
fig,ax = time_series1(dff)

date_form = mdates.DateFormatter("%Y") # Define the date format for x axis
ax.xaxis.set_major_formatter(date_form) 
plt.grid(which='both',linestyle='--',linewidth=1.5) #add grid
plt.ylabel('O3 Concentration (ppv)',fontsize=23)    # y-axis label
plt.xlabel('Year',fontsize=23)      #x-axis label
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.title('Basic filtering with std',fontsize=20)
plt.savefig('O3_MaxMin.png')
plt.show()


#df.to_csv(r'C:\Users\Camille\Documents\GitHub\Scisat-App\data_cleaning\out.csv',index=False)