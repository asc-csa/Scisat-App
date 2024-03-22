# This class represents a NetCDF file.
#
# @author Emiline Filion - Canadian Space Agency
#

import datetime as dt
import numpy as np
import pandas as pd
from scipy.io import netcdf
import warnings

warnings.filterwarnings("ignore")


# Gets the filename from the whole path (and remove the file extension)
def extract_filename(full_filename) :
    
    filename = full_filename.rsplit('\\',1)[1]
    filename = filename.replace("U:/", "")
    filename = filename.replace("/", "")
    return filename


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
        print("Getting data from NC file... This step takes several minutes")
        nc = netcdf.netcdf_file(self.full_filename,'r')
        
        # Filter data
        fillvalue1 = -999.
        months = np.copy(nc.variables['month'][:])
        years = np.copy(nc.variables['year'][:])
        days = np.copy(nc.variables['day'][:])
        hours = np.copy(nc.variables['hour'][:])

        lat = np.copy(nc.variables['latitude'][:])
        long = np.copy( nc.variables['longitude'][:])
        alt = np.copy(nc.variables['altitude'][:])

        # Get the concentration data
        data = np.copy(nc.variables[self.gaz][:])
        
        # Fill NAN values
        data[data == fillvalue1] = np.nan

        # Pick up data according to altitude
        data = data[:,alt_range[0]:alt_range[1]]
        df = pd.DataFrame(data,columns=alt[alt_range[0]:alt_range[1]])

        # Set the mean and standard deviation
        df[df>1e-5]=np.nan
        std=df.std()
        mn=df.mean()
        maxV = mn+3*std
        minV = mn-3*std

        df[df>maxV]=np.nan
        df[df<minV]=np.nan

        # Add the date column to the dataframe
        date=[]
        nbDays = len(days)
        nbTimestamps = len(hours)
        print('DEBUG: Number of days to loop: ' + str(nbDays))
        print('DEBUG: Number of timestamps to loop: ' + str(nbTimestamps))
        date = np.array([dt.datetime(int(years[i]), int(months[i]), int(days[i]), int(hours[i])) for i in range (nbDays)])

        # Add extra columns to the dataframe
        #data_meanAlt = np.nanmean(df,1)
        #data_std = np.nanstd(df,1)
        data_min = np.nanmin(df,1)
        data_max = np.nanmax(df,1)
        df['Minimum Concentration (parts per volume)'] = data_min
        df['Maximum Concentration (parts per volume)'] = data_max
        #df['Mean Altitude (Km)'] = data_meanAlt
        #df['Standard Deviation'+self.gaz] = data_std
        df['Date (UTC)'] = date
        df['Latitude (degrees)'] = lat
        df['Longitude (degrees)'] = long

        if start_date!=0 and end_date!=0 :
            df=df[np.where(df['Date (UTC)']>start_date,True,False)]
            df=df[np.where(df['Date (UTC)']<end_date,True,False)]

        # Filters the data based on min/max longitude/latitude
        df=df[np.where(df['Latitude (degrees)']>lat_min,True,False)]
        df=df[np.where(df['Latitude (degrees)']<lat_max,True,False)]
        df=df[np.where(df['Longitude (degrees)']>lon_min,True,False)]
        df=df[np.where(df['Longitude (degrees)']<lon_max,True,False)]

        return df
        
    
    def Debug_PrintProperties(self):
        
        print("---- Properties of " + self.filename + " ----")
        print("Gaz: " + self.gaz)
        print("Path to file: " + self.path)
        print("Full NC file: " + self.full_filename)
        print("Full CSV file: " + self.csv_filename)
