# data_processing.py
# Source: [City of Seattle Open Data Portal](https://data.seattle.gov/)
# Last Updated: 2/18/2024
# Description: This script will be utilized to load, join, and clean City of Seattle
# Accessory Dwelling Unit (ADU) and American Community Survey (ACS) 5-Year Estimate Data
# in preparation for an analysis examining the recent landscape of ADUs in Seattle. 

# Setup

## Install Packages
# !pip install pyarrow
# !pip install geopandas
# !pip install rtree
# !pip install cenpy

## Load Packages

## General
from pprint import pprint # For tidy printing
import numpy as np 
import pandas as pd
import geopandas # for geospatial data
import matplotlib.pyplot as plt
import seaborn as sns

## Data Storage & Filepaths
import pyarrow.feather as feather
from pathlib import Path # For storing filepaths as a Path Object

## API Pulls
import cenpy # ACS Data
# import requests
# from io import StringIO
# import time # To record elapsed time

# Pull/Load Data

data_folder = Path.cwd() / 'data' 

# ADU Data
df_aadu = pd.read_csv(data_folder /'raw'/'Detached_Accessory_Dwelling_Units_(DADUs).csv')
df_dadu = pd.read_csv(data_folder /'raw'/'Attached_Accessory_Dwelling_Units_(AADUs).csv')

# Census Data
# https://www.census.gov/programs-surveys/acs/technical-documentation/table-shells.html
vars_acs = ['B11001_001E', 'B11001_002E', 'B11017_002E', 'B25001_001E', 'B25002_003E','B25003_002E', 'B25018_001E', 'B25024_002E', 'B25024_003E', 'B25027_002E', 'B25035_001E', 'B19061_001E', 'B19013_001E', 'B19083_001E']
vars_acs_desc = ['Total HH', 'Family HH', 'Multigen HH', 'Total Units', 'Total Vac Units', 'Total Owner Occupied Units', 'Median Rooms', 'Units DADU', 'Units AADU', 'Units Mortgage', 'Median Year Built', 'Agg HH Income', 'Median HH Income', 'Gini Income Ineq']
vars_acs_dict = dict(zip(vars_acs, vars_acs_desc))

acs_raw = (cenpy.products.ACS()
               .from_place('Seattle, WA',level='tract', variables= vars_acs))

del vars_acs, vars_acs_desc

# Explore Data
print(df_aadu.shape)
print(df_dadu.shape)

# Check if AADU and DADU Data have all the same varaibles
df_aadu.columns == df_dadu.columns

# Since all columns are similar -- will only examine one data set (for now)
df_aadu.head()
df_aadu.info()

# Append Data

# Concatenate the 2 Pandas Data Frames Together
df_adu = pd.concat([df_aadu, df_dadu], 
                   ignore_index = True, join='inner')

del df_aadu, df_dadu

# Clean Data (ADU)

# Subset to Variables of Interest
vars = ['Type of Dwelling Unit', 'Development Site Square Feet', 'Permit Value', 'Description of Work',
        'New Units Permitted', 'Demolished Units Permitted','Net Units Permitted', 'Sleeping Rooms Permitted',  
        'Application Date', 'Issued Date', 'Final Date', 'Most Recent Inspection Date', 
        'Project Address', 'Neighborhood', 'Council District', 'GEOID20',
        'Longitude', 'Latitude']

dat_adu = df_adu[vars]

# Assess Missingness
dat_adu.isnull().sum().sort_values(ascending=False)

# Convert all Column Names to Lowercase (w/o any spaces)
dat_adu.columns = dat_adu.columns.str.lower().str.replace(' ', '_')

# Properly Format Variables

## 1) Dates: Objects --> Date Time
vars_date = ['application_date', 'issued_date', 'final_date', 'most_recent_inspection_date']
dat_adu[vars_date] = (dat_adu[vars_date]
                      .apply(lambda var: 
                             pd.to_datetime(
                                 var.str.replace(r'\d{1,2}\:\d{2}\:\d{2} [AP]M','', regex = True).str.strip() # Use regex to remove time components, strip whitespace
                                 ))) 
                                                                                                    
### Breakout Dates into Day/Month/Year Components:
for col in dat_adu.columns:
    if col.endswith('_date'):
        dat_adu[f'{col}_day'] = dat_adu[col].dt.day
        dat_adu[f'{col}_month'] = dat_adu[col].dt.month
        dat_adu[f'{col}_year'] = dat_adu[col].dt.year


## 2) Categories: Objects --> Categorical Data
vars_cat = ['type_of_dwelling_unit', 'neighborhood','council_district']
dat_adu[vars_cat] = dat_adu[vars_cat].apply(lambda var: var.astype('category'))

# Correct Category Naming (ADU --> AADU)
dat_adu['type_of_dwelling_unit'] = dat_adu['type_of_dwelling_unit'].cat.rename_categories({'ADU':'AADU'})

## 3) Integers: Floats --> Integers
vars_int = ['demolished_units_permitted', 'net_units_permitted']
dat_adu[vars_int] = dat_adu[vars_int].apply(lambda var: var.astype('Int64')) # Using Int64 vs int64, as its a new format which allows for NA cells within an integer variable (int64 does not)


## 4) Subset GEOID to Census Tract (15 --> 11 digits); to permit left_join with ACS data
dat_adu['geoid20'] = dat_adu['geoid20'].astype('str').str[:-6]


## 5) Convert dat_adu to a GeoDataFrame --> Convert Latitude & Longitude coordinates into a point geometries. 
dat_adu = geopandas.GeoDataFrame(dat_adu, 
                                 geometry=geopandas.points_from_xy(dat_adu.longitude, dat_adu.latitude), crs="EPSG:4326")


del vars, vars_date, vars_cat, vars_int

# Feature Engineering (ADU)

## Calculate the time differences for the process steps of the ADU building workflow.
dat_adu = (dat_adu
        .assign(
           processing_time = (dat_adu['issued_date'] - dat_adu['application_date']).dt.days,
            build_time = (dat_adu['final_date'] - dat_adu['issued_date']).dt.days)
            )

# Clean Data (ACS)

## Provide Useful Column Names
acs_seattle = (acs_raw
               .drop(columns = ['state','county','tract'])
               .rename(columns = {'GEOID':'geoid20'})
               .rename(columns = vars_acs_dict)
               )

## Examine Data Types
acs_seattle.dtypes

#E Convert all Column Names to Lowercase (w/o any spaces) and add 'acs_' prefix
acs_seattle.columns = 'acs_' + acs_seattle.columns.str.lower().str.replace(' ','_')

## Convert 'geoid20' to string object (for joining later)
acs_seattle['acs_geoid20'] = acs_seattle['acs_geoid20'].astype('str')

## Create a separate data frame for geometries
acs_seattle_geom = acs_seattle[['acs_geoid20', 'acs_geometry']]

# Remove 'acs_geometry' from acs_seattle (cannot have 2 geometry columns)
acs_seattle = acs_seattle.drop('acs_geometry', axis='columns')

# Join ADU & ACS Data

dat_adu_acs = pd.merge(dat_adu, acs_seattle, 
                left_on = 'geoid20', right_on= 'acs_geoid20', how='left')



# Save Data

## ADU Data
dat_adu.to_feather(path = data_folder /'clean'/'adu_data.feather')

## ACS Data
feather.write_feather(df = acs_seattle, dest = data_folder /'clean'/'acs_data.feather') # Tabular Data
acs_seattle_geom.to_feather(path = data_folder /'clean'/'acs_geo.feather') # Geometries (Census Tract Polygons)

# Joined ADU & ACS Dataa
dat_adu_acs.to_feather(path = data_folder /'clean'/'adu_acs_data.feather')