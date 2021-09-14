#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 15:01:40 2021

@author: loriwachowicz
"""

import xarray as xr

#change your file path where the files are located and where you want to save the new files
file_path = 'C:/Users/flavi/OneDrive - University of Georgia/20-21_NOAA_RA/NOAA_RA/Data/Obj_1/NOAA_Clim_In/Lori_tests/TEST/input/'
#change your file path where the files are located and where you want to save the new files
#file_path = 'C:/Users/fdm13171/OneDrive - University of Georgia/20-21_NOAA_RA/NOAA_RA/Data/Obj_1/NOAA_Clim_In/Lori_tests/TEST/'

# use the combined daily file with all days 
#nc_file = file_path + 'daymet_v3_prcp_1980-1985_w366dayLeapYr_LtLnTm_wProj_puertorico_wLeapMask.nc4'
nc_file = file_path + 'daymet_v3_prcp_1980-2019_w366dayLeapYr_LtLnTm_wProj_puertorico.nc4'

ds = xr.open_dataset(nc_file) #reads in netcdf as an xarray object

#calculates monthly totals... skipna=True --> skips all missing values in the calculation; keep_attrs=True --> keeps metadata from previous file
monthly_data = ds.resample(time='m',restore_coord_dims=True).sum(skipna=True,keep_attrs=True)
monthly_data2 = monthly_data.transpose("lat", "lon", "time") #switches the order of the dimensions from time, lat, lon (which is how xarray reads the data) to lat, lon, time
# write out new file
monthly_data2.to_netcdf(path=file_path+'daymet_v3_prcp_1980-2019_w366dayLeapYr_LtLnTm_wProj_monTots_puertorico_v2.nc4',mode='w',)
