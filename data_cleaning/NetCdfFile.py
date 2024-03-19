# This class represents a NetCDF file.
#
# @author Emiline Filion - Canadian Space Agency
#

import datetime as dt
import numpy as np
import pandas as pd
from scipy.io import netcdf #### <--- This is the library to import.
import matplotlib.pyplot as plt
import os
import matplotlib.dates as mdates


# Constants
path = r'C:\Users\Siavash\Documents\sci-sat' #PATH TO MY DATA FOLDER
path_to_folder = r'C:\Users\Siavash\Documents\sci-sat'


# Gets the filename from the whole path (and remove the file extension)
def extract_filename(full_filename) :
    
    filename = full_filename.rsplit('\\',1)[1]
    filename = filename.replace("U:/", "")
    filename = filename.replace("/", "")
    return filename


# Creates a time serie for visualisation
def initTimeSerie(df):

    fig, ax = plt.subplots(figsize=((35,7)))    #Create fig
    ax.plot(df['Alt_Mean'],'b.')     #Plot data
    
    return fig,ax


# Structure that defines a NetCDF document
class netCdfFile:
        
    def __init__(self, full_filename):
        
        self.full_filename = full_filename
        self.filename = extract_filename(full_filename)
        self.csv_filename = full_filename.replace(".nc", ".csv")
        self.path = full_filename.replace(self.filename, "")
        
        # Set the gaz
        gaz = self.filename.strip().split('.')[0].strip().split('_')[3:]
        if len(gaz)>1:
            self.gaz = gaz[0]+'_'+gaz[1]
        else:
            self.gaz = gaz[0]
                    
    
    def __eq__(self, filename):
        return self.filename == filename
    
    
    # Converts the NetCDF file to CSV and cleans data
    def convert2CSV(self, start_date=0,end_date=0,lat_min=-90,lat_max=90,lon_min=-180,lon_max=180,alt_range=[0,150]):
        """

        Parameters
        ----------
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
            Dataframe of all the gaz concentrations with columns :
                Altitudes (from 0.5 to 149.5), Mean on altitude (Alt_Mean), date,
                Latitude (lat) and Longitude (long)


        """
        
        # Open the NC file
        print("DEBUG: Entering convert2CSV()")
        print("Getting data from NC file... This step takes several minutes")
        nc = netcdf.netcdf_file(self.full_filename,'r')
        
        #Trier / définir rapido les données et les variables
        fillvalue1 = -999.
        months=np.copy(nc.variables['month'][:])
        years = np.copy(nc.variables['year'][:])
        days = np.copy(nc.variables['day'][:])

        lat = np.copy(nc.variables['latitude'][:])
        long =np.copy( nc.variables['longitude'][:])
        alt = np.copy(nc.variables['altitude'][:])

        #valeurs de concentration [ppv]
        data = np.copy(nc.variables[self.gaz][:])
        
        #Remplacer les données vides
        data[data == fillvalue1] = np.nan

        #Choisir les données dans l'intervalle de l'altitude
        data = data[:,alt_range[0]:alt_range[1]]

        df = pd.DataFrame(data,columns=alt[alt_range[0]:alt_range[1]])

        #Trie données abérrantes
        # TODO: This part takes a long time. We should optmize it. numpy.nan is too slow
        #slow
        df[df>1e-5]=np.nan
        #slow
        std=df.std()
        mn=df.mean()
        maxV = mn+3*std
        minV = mn-3*std
        # slow
        df[df>maxV]=np.nan
        #slow
        df[df<minV]=np.nan

        #Colonne de dates
        date=[]
        nbDays = len(days)
        date = np.array([dt.datetime(int(years[i]), int(months[i]), int(days[i])) for i in range (nbDays)])

        data_meanAlt = np.nanmean(df,1)
        df['Alt_Mean'] = data_meanAlt
        df['date'] = date
        df['lat'] = lat
        df['long'] = long

        if start_date!=0 and end_date!=0 :
            df=df[np.where(df['date']>start_date,True,False)]
            df=df[np.where(df['date']<end_date,True,False)]

        # Filters the data based on min/max longitude/latitude
        df=df[np.where(df['lat']>lat_min,True,False)]
        df=df[np.where(df['lat']<lat_max,True,False)]
        df=df[np.where(df['long']>lon_min,True,False)]
        df=df[np.where(df['long']<lon_max,True,False)]

        print("DEBUG: end of convert2CSV()")
        return df
        
    
    # Gets binary data from the file and returns a data frame
    def opendf(self, path_to_file, file_name):
        
        # Open the NC file
        print ("Entering opendf")
        print("path_to_file: " + path_to_file)
        print("file_name: " + file_name)
        nc = netcdf.netcdf_file(path_to_file+'//'+file_name,'r')

        # Get data from the file
        print("Getting data from NC file... This step takes several minutes")
        fillvalue = -999.      # Fill value from User Guide
        months=np.copy(nc.variables['month'][:])
        years = np.copy(nc.variables['year'][:])
        days = np.copy(nc.variables['day'][:])
        hours = np.copy(nc.variables['hour'][:])
        lat = np.copy(nc.variables['latitude'][:])
        long = np.copy( nc.variables['longitude'][:])
        alt = np.copy(nc.variables['altitude'][:])
        data = np.copy(nc.variables[self.gaz][:]) #valeurs de concentration [ppv]
        data_error = np.copy(nc.variables[self.gaz+'_error'][:])

        print("Looking if data is good...")
        if (len(np.where(data!=-999.0)[0])==0 & len(np.where(data!=-999.0)[1])==0):
            print('ERROR: No data found for this gaz: ' + self.gaz)
            return [],[]
        
        else: 
            print("Data looks good")
            data[data == fillvalue] = np.nan #Remplacer les données vides
            data_error[data_error == fillvalue] = np.nan #Remplacer les données vides

            # Initialize  the output dataframe
            print("Creating the data frame...")
            df = pd.DataFrame(data,columns=alt)
            dferr = pd.DataFrame(data_error,columns=alt)
            print("df equals")
            df.head()
            print("DEBUG: " + str(df))
            
            # Clean data by looping over each day
            print("Cleaning data...")
            date=[]
            for i in range (len(days)):
                date.append(dt.datetime(int(years[i]), int(months[i]), int(days[i])))
                
            # Fill colunms, the mean average is used for altitude
            data_meanAlt = np.nanmean(data,1) # TODO: To fix this line
            data_std = np.nanstd(data,1)
            df['Alt_Mean'] = data_meanAlt
            df['std '+self.gaz] = data_std
            df['date'] = date
            df['lat'] = lat
            df['long'] = long
            
            print ("End of opendf")
            return df,dferr


    def createHistogram(self, path):
        
        # Get data
        print ("Entering createHistogram")
        df,dferr = self.opendf(path, self.filename)
        #print(df)
        df.head()
        #print(dferr)
        dferr.head()
        if len(df)!=0:
        
            print ("The dataframe is good")
            dfff = df.copy()
            print("Here #1")
            # TODO: Why using 150 here?
            for i in range(150):
                dfff.iloc[:,i][dferr.iloc[:,i]==-888.]=np.nan
            
            print("Here #2")
            data=dfff.iloc[:,:150].values
            print("Here #3")
            data_meanAlt = np.nanmean(data,1) #moyenne sur l'altitude
            dfff['Alt_Mean'] = data_meanAlt
        
            print("Here #4")
            print(df)
            print(df.head())
            df = df.groupby(['date','lat','long']).mean()
            print("Here #5")
            datamean = df.rolling(window=50,center=True ).mean()
            datastd = df.rolling(window=50,center=True).std()
            datamed = df.rolling(window=50,center=True).median()
        
            print("Here #6")
            newdata = df.where(((df > datamean.sub(datastd.mul(2))) & (df < datamean.add(datastd.mul(2))))) #2xSTD
            newdata=newdata.reset_index()
            
            print("Setting up the histogram...")
            plt.hist(newdata.iloc[:,3:-2].values.ravel(),bins=100)# HISTOGRAM OF DATA DISTRIBUTION
            plt.grid()
            plt.xlabel('Concentration [ppv]')
            plt.ylabel('Distribution')
            plt.title(self.gaz+' Distribution Filter with window=50 and 2 x std ')
            plt.savefig(self.gaz+' Distribution Filter2xSTD.pdf')
            print("Ready to show the histogram...")
            plt.show()
            
        print ("End of createHistogram")

    
    # Converts the NetCDF file to CSV and cleans data
    def convert2CSVold(self):
        
        # CALLING THE FUNCTIONS TO CLEAN THE DATA WITH THE FILES.
        files = []

        #LOOP ON ALL FILES
        for i in os.listdir(path_to_folder):
            if i.endswith('.nc'):
                files.append(i)

        # ONLY ONE FILE
        # Take out Geoloc data
        files = np.array(files)
        files = files[np.where(files!='ACEFTS_L2_v4p1_GLC.nc')]

        for file in files[0:1]:
            self.createHistogram(path,file)

        #%% TEST WITH ONLY 1 FILE
        file = 'ACEFTS_L2_v4p1_O3.nc'
        newfile = file[:-3] + '.csv'
        gaz = file.strip().split('.')[0].strip().split('_')[3:]
        if len(gaz)!=1:
            gaz = gaz[0]+'_'+gaz[1]
        else : 
            gaz=gaz[0]
        df,dferr= self.opendf(path,file,gaz)

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
        plt.show()

        # VISUALISATION NO FILTER 
        dff = newdata.groupby('date').mean()
        fig,ax = initTimeSerie(dff)

        date_form = mdates.DateFormatter("%Y") # Define the date format for x axis
        ax.xaxis.set_major_formatter(date_form) 
        plt.grid(which='both',linestyle='--',linewidth=1.5) #add grid
        plt.xlabel('Year',fontsize=23)      #x-axis label
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.title('Filtering',fontsize=20)
        plt.show()
    
    
    def Debug_PrintProperties(self):
        
        print("---- Properties of " + self.filename + " ----")
        print("Gaz: " + self.gaz)
        print("Path to file: " + self.path)
        print("Full NC file: " + self.full_filename)
        print("Full CSV file: " + self.csv_filename)
        print('\n')
