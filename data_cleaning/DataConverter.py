# This script convert NC files (NetCDF) to CSV files.
# It uses the NetCDF module.
# SCISAT Data
#
# -*- coding: utf-8 -*-
# @author Emiline Filion - Canadian Space Agency
#

import datetime
import numpy as np
import pandas as pd
import glob
from NetCdfFile import netCdfFile
from scipy.io import netcdf #### <--- This is the library to import.
import matplotlib.pyplot as plt
import os
import matplotlib.dates as mdates
import sys


# Constants
INPUT_FOLDER = 'U:/Projects\Space Data\SCISAT\data/test'
OUTPUT_FOLDER = 'U:/Projects\Space Data\SCISAT\data/test'
os.environ['PROJ_LIB'] = INPUT_FOLDER


# Debut
print("\n*****************************")
print("******** SCISAT DATA ********")
print("*****************************")
print("Convert NetCDF files to CSV files")
print("Input folder: " + INPUT_FOLDER)

# Get the list of NC files to convert
nc_files = []
for file in glob.glob(INPUT_FOLDER + "\*.nc"):
    nc_files.append(file)
print("Found " + str(len(nc_files)) + " files.")

# Loop over all NC files
for nc_file in nc_files:

    # Open the PDF file
    print("\nConverting " + nc_file + "...")
    doc = netCdfFile(nc_file)
    
    # TODO: To watch for this
    #files = files[np.where(files!='ACEFTS_L2_v4p1_GLC.nc')]
    doc.Debug_PrintProperties()

    # Convert to CSV
    #doc.createHistogram(INPUT_FOLDER)
    csv_df = doc.convert2CSV()
    print("Saving the CSV file... (" + doc.csv_filename + ") This step takes several minutes")
    csv_df.to_csv(doc.csv_filename, index=False)
    print(nc_file + " fully converted to CSV")
    

# The End
print("*************************************")
print("The program ended successfully")
print(str(len(nc_files)) + " files converted to CSV")
print("Converted files are in the output file: " + OUTPUT_FOLDER)
print("Have a good day!\n")
sys.exit() 