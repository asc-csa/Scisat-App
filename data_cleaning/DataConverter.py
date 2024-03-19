# This script convert NC files (NetCDF) to CSV files.
# It uses the NetCDF module.
# SCISAT Data
#
# -*- coding: utf-8 -*-
# @author Emiline Filion - Canadian Space Agency
#

import numpy as np
import pandas as pd
import glob
from NetCdfFile import netCdfFile


# Constants
INPUT_FOLDER = 'C:\Temp/NETCDF_mol_v5p2'
OUTPUT_FOLDER = 'C:\Temp/NETCDF_mol_v5p2'


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
    doc.Debug_PrintProperties()

    # Convert to CSV
    csv_df = doc.convert2CSV()
    print("Saving the CSV file... (" + doc.csv_filename + ") This step takes several minutes")
    csv_df.to_csv(doc.csv_filename, index=False)
    print(nc_file + " fully converted to CSV")
    

# The End
print("\n*************************************")
print("The program ended successfully")
print(str(len(nc_files)) + " files converted to CSV")
print("Converted files are in the output file: " + OUTPUT_FOLDER)
print("Have a good day!\n")