# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 12:45:19 2020

@author: Camille
"""

import numpy as np
import pandas as pd
import datetime
from scipy.io import netcdf #### <--- This is the library to import.
import matplotlib.pyplot as plt
import os
import matplotlib.dates as mdates
os.environ['PROJ_LIB'] = r'C:\Users\Siavash\Documents\sci-sat'

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

    if (len(np.where(data!=-999.0)[0])==0 & len(np.where(data!=-999.0)[1])==0):
        print('NO DATA FOUND FOR GAS: ' + gaz)
        return [],[]
    
    else: 
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
        df['Alt_Mean'] = data_meanAlt
        df['std '+gaz] = data_std
        df['date'] = date
        df['lat'] = lat
        df['long'] = long
            #df['error']=data_error
            # df=df.groupby('lat').mean()
  #   df=df.groupby(df.index.floor('D')).mean()
        # df.reset_index(level=0, inplace=True)  
        # df=df.groupby('long').mean()
        # df.reset_index(level=0,inplace=True)
        
        return df,dferr

def dohist(path,file):
    #Path to file (change directory)
    
    gaz = file.strip().split('.')[0].strip().split('_')[3:]
    if len(gaz)>1:
        gaz = gaz[0]+'_'+gaz[1]
    else:
        gaz=gaz[0]
    df,dferr= opendf(path,file,gaz)
    
    if len(df)!=0:
    
        # data = df[df.columns.values[:150]].values

        # plt.hist(data.ravel(),bins=100,range=(np.nanmin(data),np.nanmax(data)))
        # plt.grid()
        # plt.xlabel('Concentration [ppv]')
        # plt.ylabel('Distribution')
        # plt.title(gaz+' Distribution No Filter')
        # plt.savefig(gaz+' Distribution NoFilter.png')
        # plt.show()
    

    ##############################################################################
    #Visualizations to compare cleaned vs not cleaned data
    ##############################################################################
    
    # VISUALISATION FILTER FLAGGED ERRORS (-888)
    
        dfff = df.copy()
        
        for i in range(150):
            dfff.iloc[:,i][dferr.iloc[:,i]==-888.]=np.nan
        
        data=dfff.iloc[:,:150].values
        data_meanAlt = np.nanmean(data,1) #moyenne sur l'altitude
        dfff['Alt_Mean'] = data_meanAlt
        
        # fig = plt.figure()
        # plt.hist(data.ravel()[~np.isnan(data.ravel())],bins=100,range=(np.nanmin(data),np.nanmax(data)))
        # plt.grid()
        # plt.xlabel('Concentration [ppv]')
        # plt.ylabel('Distribution')
        # plt.title(gaz+' Distribution Filter only -888')
        # # pdf.savefig(fig)
        # plt.savefig(gaz+' Distribution Filter-888.pdf')

        # plt.show()
    
    
    # # VISUALISATION FILTER WITH MEAN AND STD, WINDOW = 50
        df = df.groupby(['date','lat','long']).mean()
        datamean = df.rolling(window=50,center=True ).mean()
        datastd = df.rolling(window=50,center=True).std()
        datamed = df.rolling(window=50,center=True).median()
      
        newdata = df.where(((df > datamean.sub(datastd.mul(2))) & (df < datamean.add(datastd.mul(2))))) #2xSTD
        newdata=newdata.reset_index()
        plt.hist(newdata.iloc[:,3:-2].values.ravel(),bins=100)# HISTOGRAM OF DATA DISTRIBUTION
        plt.grid()
        plt.xlabel('Concentration [ppv]')
        plt.ylabel('Distribution')
        plt.title(gaz+' Distribution Filter with window=50 and 2 x std ')
        plt.savefig(gaz+' Distribution Filter2xSTD.pdf')
        plt.show()
        
        # newdata = df.where(((df > datamed.sub(datastd.mul(3))) & (df < datamed.add(datastd.mul(3)))))
        # newdata=newdata.reset_index()
        # plt.hist(newdata.iloc[:,3:-2].values.ravel(),bins=100)#,range=(np.nanmin(newdata),np.nanmax(newdata)))
        # plt.grid()
        # plt.xlabel('Concentration [ppv]')
        # plt.ylabel('Distribution')
        # plt.title(gaz+' Distribution Filter with window=50 and 3 x MAD ')
        # plt.savefig(gaz+' Distribution Filter3xMAD.pdf')
        # plt.show()
        
        
        
path = r'C:\Users\Siavash\Documents\sci-sat' #PATH TO MY DATA FOLDER
#%%

# CALLING THE FUNCTIONS TO CLEAN THE DATA WITH THE FILES.

files = []
path_to_folder = r'C:\Users\Siavash\Documents\sci-sat'

#LOOP ON ALL FILES
for i in os.listdir(path_to_folder):
    if i.endswith('.nc'):
        files.append(i)

#ONLY ONE FILE
# file = 'ACEFTS_L2_v4p0_O3.nc'
# dohist(path,files[0])
# gaz = files[0].strip().split('.')[0].strip().split('_')[-1]
# df,dferr= opendf(path,files[0],gaz)
files = np.array(files)
files = files[np.where(files!='ACEFTS_L2_v4p1_GLC.nc')] #Take out Geoloc data
# files = files[np.where(files!='ACEFTS_L2_v4p0_T.nc')] #Take out Temperature data

for file in files[0:1]:
    dohist(path,file)


#%% TEST WITH ONLY 1 FILE

file = 'ACEFTS_L2_v4p1_O3.nc'
newfile = file[:-3] + '.csv'
gaz = file.strip().split('.')[0].strip().split('_')[3:]
if len(gaz)!=1:
    gaz = gaz[0]+'_'+gaz[1]
else : 
    gaz=gaz[0]
df,dferr= opendf(path,file,gaz)
# dohist(path,file)

df = df.groupby(['date','lat','long']).mean()
datamean = df.rolling(window=50,center=True,min_periods = 20 ).mean()
datastd = df.rolling(window=50,center=True,min_periods = 20).std()


"""
df math functions : 
add: +
sub: -
mul: *
div: /
mod: //
pow: %
"""
newdata = df.where(((df > datamean.sub(datastd.mul(1.5))) & (df < datamean.add(datastd.mul(1.5)))))
newdata=newdata.reset_index()
newdata.to_csv(newfile, encoding='utf-8', index=False)
print('test')
plt.hist(newdata.iloc[:,3:-2].values.ravel(),bins=100)#,range=(np.nanmin(newdata.iloc[:,3:-2]),np.nanmax(newdata.iloc[:,3:-2])))
plt.grid()
plt.xlabel('Concentration [ppv]')
plt.ylabel('Distribution')
plt.title(gaz+' Distribution with Filter')
# plt.savefig(gaz+' Distribution NoFilter.png')
plt.show()

#%% VISUALIZATION WITH TIME SERIES
def time_series1(df):

    fig, ax = plt.subplots(figsize=((35,7)))    #Create fig
    ax.plot(df['Alt_Mean'],'b.')     #Plot data
    
    return fig,ax

# VISUALISATION NO FILTER 

dff = newdata.groupby('date').mean()
fig,ax = time_series1(dff)

date_form = mdates.DateFormatter("%Y") # Define the date format for x axis
ax.xaxis.set_major_formatter(date_form) 
plt.grid(which='both',linestyle='--',linewidth=1.5) #add grid
# plt.ylabel('O3 Concentration (ppv)',fontsize=23)    # y-axis label
plt.xlabel('Year',fontsize=23)      #x-axis label
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.title('Filtering',fontsize=20)
# plt.savefig('_withFilter.png')
plt.show()

