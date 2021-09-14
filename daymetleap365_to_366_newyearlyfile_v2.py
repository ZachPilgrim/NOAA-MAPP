#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 15:01:40 2021

@author: loriwachowicz
"""
import datetime as dt
import netCDF4 as nc
import numpy as N

#change your file path where the files are located and where you want to save the new files
#file_path = '/Users/loriwachowicz/daymet_data_processing/precip-1/'
file_path = '/Volumes/Backups_ExtraData/precip-1/'


# read in sample file to get lat, lon dims    
sampleinfile = nc.Dataset(file_path+'daymet_v3_prcp_1981_puertorico.nc4','r')
lats2d = sampleinfile.variables['lat'][:,:]
lons2d = sampleinfile.variables['lon'][:,:]
x = sampleinfile.variables['x'][:]
y = sampleinfile.variables['y'][:]
sampletime_unit = sampleinfile.variables['time'].units
sampletime_cal = sampleinfile.variables['time'].calendar
precip_coords = sampleinfile.variables['prcp'].coordinates
precip_grid = sampleinfile.variables['prcp'].grid_mapping
precip_cells = sampleinfile.variables['prcp'].cell_methods

sampleinfile.close()

all_precip_days = []
all_times_ind = []


# change to include range of years 
for yr in range(1980,2020):
    
    prcp_366 = []
    tms_366 = []
    yr_str = str(yr)
    
    file_name = 'daymet_v3_prcp_'+yr_str+'_puertorico.nc4'
    
    infile = nc.Dataset(file_path+file_name,'r')
    #lats = infile.variables['lat'][:,:]
    #lons = infile.variables['lon'][:,:]
       
    times = N.copy(infile.variables['time'][:])
    time_unit = infile.variables['time'].units
    time_cal = infile.variables['time'].calendar
    
    times_fmt = N.array(nc.num2date(times,units=time_unit,calendar=time_cal,))
    
    #times_strs = [i.strftime("%Y%m%d") for i in times_fmt] # to display dates as string
    #times_strs = N.array(times_strs)
    times_last = str(times_fmt[-1])
    
    if times_last == yr_str+'-12-30 12:00:00':       
    #if len(times_fmt) == 366: # checks if a non-leap year, and adds Feb 29 to time series
        #dec30_ind = N.max(N.where(times_strs == yr_str+'1230')) # in 'yyyymmdd ' format (or can be whatever string format you choose that needs to match the strftime function
        dec30_ind = times[-1]
        #mar01_ind = N.max(N.where(times_strs == yr_str+'0101'))
        dprecip = N.copy(infile.variables['prcp'][-1,:,:]).squeeze()
        precip_all = N.copy(infile.variables['prcp'][:,:,:])
        #precip_coords = infile.variables['prcp'].coordinates
        #precip_grid = infile.variables['prcp'].grid_mapping
        #precip_cells = infile.variables['prcp'].cell_methods

        #precip = N.copy(infile.variables['prcp'][:,:,:])
        jan1_file = nc.Dataset(file_path+'daymet_v3_prcp_'+str(yr+1)+'_puertorico.nc4','r')
        jtimes = N.copy(jan1_file.variables['time'][:])
        jan1_ind = jtimes[0]
        jprecip = N.copy(jan1_file.variables['prcp'][0,:,:]).squeeze()
        
        dec31_ind = dec30_ind+1
        
        dec31 = N.mean([dprecip,jprecip],axis=0)
        dec31 = dec31[N.newaxis,:, :]
        
        
        prcp_366_con = N.concatenate([precip_all,dec31],axis=0)
        #tms_366_arr = N.array(tms_366)
        tms_366_con = N.append(times,dec31_ind)
        all_precip_days.append(prcp_366_con)
        all_times_ind.append(tms_366_con)
        
        #precip_feb29 = N.empty((precip_shape_ex.shape[0],precip_shape_ex.shape[1]))
        #precip_feb29[:,:] = N.nan         
        #precip_366 = N.insert(precip, (feb28_ind+1,), (N.nan),axis=0)
        #times_366 = N.insert(times_strs,feb28_ind+1, yr_str+'0229',axis=0)
        #times_ind_366 = times[]
    elif times_last == yr_str+'-12-31 12:00:00':    
    #elif len(times_fmt) == 365: # if you are reading in a yearly file that is already a leap year, it just reads in the precip, time vars as is.
        precip_coords = infile.variables['prcp'].coordinates
        precip_grid = infile.variables['prcp'].grid_mapping
        precip_cells = infile.variables['prcp'].cell_methods
        precip_366 = N.copy(infile.variables['prcp'][:,:,:])
        #times_366 = times_strs
        times_ind = times
        all_precip_days.append(precip_366)
        all_times_ind.append(times_ind)
        
    else:
        continue
    infile.close()
    #dates_int = [int(s) for s in times_366]
    
    
    
    #precip_reorder = N.moveaxis(precip_366, (0,), 2) #moves time dimension (index=0) to (index=2)
    
    
    
    # saves new file...change the file str name, if you wish

    #prcp_366_arr = N.array(prcp_366)
    #all_precip_days.append(prcp_366)
    #all_times_ind.append(tms_366)   
    
    
prcp_final = N.concatenate(all_precip_days,axis=0).squeeze()
times_inds_final = N.concatenate(all_times_ind).squeeze()
precip_reorder = N.moveaxis(prcp_final, (0,), 2) #moves time dimension (index=0) to (index=2)

nc_out = nc.Dataset(file_path + 'daymet_v3_prcp_1980-2019_w366dayLeapYr_LtLnTm_wProj_puertorico.nc4', 'w', format='NETCDF4')

lat = nc_out.createDimension('lat',(y.shape[0]))
lon = nc_out.createDimension('lon',(x.shape[0]))

lat2d = nc_out.createDimension('lat2d',(y.shape[0]))
lon2d = nc_out.createDimension('lon2d',(x.shape[0]))
time = nc_out.createDimension('time',(len(times_inds_final)))


latitudes = nc_out.createVariable('lat','f4',('lat'),fill_value=-9999.)
latitudes.units = 'm'
latitudes.standard_name = "y coordinate of projection"

latitudes2d = nc_out.createVariable('lat2d','f4',('lat','lon'),fill_value=-9999.)
latitudes2d.units = 'degrees_north'
latitudes2d.standard_name = "latitude"

longitudes = nc_out.createVariable('lon','f4',('lon'),fill_value=-9999.)
longitudes.units = 'm'
longitudes.standard_name = "x coordinate of projection"

longitudes2d = nc_out.createVariable('lon2d','f4',('lat','lon'),fill_value=-9999.)
longitudes2d.units = 'degrees_east'
longitudes2d.standard_name = "longitude"

tm = nc_out.createVariable('time','i',('time',))
tm.standard_name = 'time'
tm.calendar = 'standard'
tm.units = 'days since 1980-01-01 00:00:00 UTC'


latitudes[:] = y
longitudes[:] = x

latitudes2d[:,:] = lats2d[:,:]
longitudes2d[:,:] = lons2d[:,:]
#tm[:] = range(0,366)
#tm2[:] = dates_int
tm[:] = times_inds_final ## this will need to be changed. 
#starts from 366 days after Jan 1, 1980 (position=0)... 
#last number needs to be 366*num years you're processing +366 
#(in this case 2years+366 day offset, since starting calculations on Jan 1, 1981)


prcp_out = nc_out.createVariable('prcp','f4',('lat','lon','time',),fill_value=-9999.)
prcp_out.long_name = 'daily total precipitation'
prcp_out.units = 'mm'
prcp_out.coordinates = precip_coords
prcp_out.grid_mapping = precip_grid
prcp_out.cell_methods = precip_cells
prcp_out[:,:,:] = precip_reorder #(lat,lon,time)

nc_out.close()